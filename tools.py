import re
from typing import Literal
from functools import lru_cache
import os
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from sql_db import engine, get_sql_database

load_dotenv()

INDEX_NAME = "hospital-docs"


_READ_ONLY_SQL = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)
_FORBIDDEN_SQL = re.compile(
    r"\b(ALTER|CREATE|DELETE|DROP|GRANT|INSERT|TRUNCATE|UPDATE|"
    r"REVOKE|REPLACE|MERGE)\b",
    re.IGNORECASE,
)


def _validate_read_only_query(sql_query: str) -> str:
    """Validate and normalize a single read-only SQL statement."""
    query = sql_query.strip()

    if not query:
        raise ValueError("SQL query cannot be empty.")

    if not _READ_ONLY_SQL.match(query):
        raise ValueError("Only SELECT or WITH queries are allowed.")

    if _FORBIDDEN_SQL.search(query):
        raise ValueError("The database tool only allows read-only SQL queries.")

    if "--" in query or "/*" in query or "*/" in query:
        raise ValueError("SQL comments and multiple statements are not allowed.")

    if ";" in query:
        if not query.endswith(";") or query.count(";") != 1:
            raise ValueError("Only one SQL statement is allowed.")
        query = query[:-1].rstrip()

    return query


@tool
def query_hospital_database(sql_query: str) -> str:
    """Run a read-only SQL query against the hospital Supabase database.

    Use this tool for structured hospital data such as patients, encounters,
    conditions, medications, observations, procedures, and counts. Generate
    SQL using only tables and columns returned by the database schema.
    """
    query = _validate_read_only_query(sql_query)
    return str(get_sql_database().run(query))


@tool
def create_hospital_chart(
    sql_query: str,
    chart_type: Literal["bar", "line", "pie", "scatter", "histogram"],
    x_column: str,
    y_column: str = "",
    title: str = "",
) -> str:
    """Query Supabase and create a Plotly chart for the user's request.

    Use this for trends, comparisons, distributions, and proportions. The SQL
    query must return the columns named by x_column and y_column. The result
    is a JSON Plotly figure specification that Streamlit can render with
    st.plotly_chart().
    """
    query = _validate_read_only_query(sql_query)
    dataframe = pd.read_sql_query(query, engine)

    if dataframe.empty:
        raise ValueError("The database query returned no rows to chart.")

    missing_columns = [
        column
        for column in (x_column, y_column if y_column else None)
        if column and column not in dataframe.columns
    ]
    if missing_columns:
        raise ValueError(
            f"Chart columns not found in query result: {', '.join(missing_columns)}"
        )

    chart_title = title or "Hospital data"

    if chart_type == "bar":
        figure = px.bar(dataframe, x=x_column, y=y_column or None, title=chart_title)
    elif chart_type == "line":
        figure = px.line(dataframe, x=x_column, y=y_column or None, title=chart_title)
    elif chart_type == "pie":
        figure = px.pie(
            dataframe,
            names=x_column,
            values=y_column or None,
            title=chart_title,
        )
    elif chart_type == "scatter":
        if not y_column:
            raise ValueError("Scatter charts require a y_column.")
        figure = px.scatter(dataframe, x=x_column, y=y_column, title=chart_title)
    elif chart_type == "histogram":
        figure = px.histogram(dataframe, x=x_column, title=chart_title)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    return figure.to_json()


@lru_cache(maxsize=1)
def get_vector_store() -> PineconeVectorStore:
    """Connect to the Pinecone index with the hospital documents (only once)."""
    embedding = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",  # must be the same model as when uploading
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    return PineconeVectorStore(index=pc.Index(INDEX_NAME), embedding=embedding)


@tool
def search_hospital_documents(query: str) -> str:
    """Search the hospital's internal text documents (vector database).

    The documents are written in Ukrainian and contain these indexed sections:

    - general.pdf, about Medical Center "Омега-Мед":
      1) general information about the medical center;
      2) hospital information systems;
      3) medical equipment and infrastructure;
      4) technical maintenance and operation protocols; and
      5) safety and quality protocols.
    - for_workers.docx, an internal employee handbook:
      1) introduction and general provisions;
      2) hiring and onboarding;
      3) working hours and time tracking;
      4) pay;
      5) leave;
      6) business travel;
      7) training and professional development;
      8) disciplinary responsibility and internal rules;
      9) occupational health and safety;
      10) confidentiality and information protection;
      11) communication and feedback; and
      12) termination of employment.

    Use this tool for questions about the medical center, its systems,
    equipment, infrastructure, maintenance, safety and quality protocols, or
    employee rules and employment procedures. Do NOT use it for patient
    records, database counts, or statistics; those belong to the SQL database.
    Do not assume that a topic is covered if it is not supported by retrieved
    sections.

    :param query: short search phrase in Ukrainian with the key terms
    :return: the most relevant document sections with their sources
    """
    results = get_vector_store().similarity_search(query, k=5)

    if not results:
        return "No relevant documents found."

    parts = []
    for doc in results:
        source = (
            f"[Document: {doc.metadata.get('file_name')} | "
            f"Section: {doc.metadata.get('block_name')}]"
        )
        parts.append(f"{source}\n{doc.page_content}")

    return "\n\n---\n\n".join(parts)


HOSPITAL_TOOLS = [
    query_hospital_database,
    create_hospital_chart,
    search_hospital_documents,
]


