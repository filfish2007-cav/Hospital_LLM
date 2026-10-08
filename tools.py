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


def _pretty(name: str) -> str:
    return name.replace("_", " ").strip().capitalize()


def _to_numeric_if_possible(series: pd.Series) -> pd.Series:
    """Postgres SUM/AVG return Decimal (dtype=object); convert to numbers."""
    if series.dtype == object:
        try:
            return pd.to_numeric(series)
        except (ValueError, TypeError):
            return series
    return series


@tool
def create_hospital_chart(
    sql_query: str,
    chart_type: Literal["bar", "line", "pie", "scatter", "histogram"],
    x_column: str,
    y_column: str = "",
    color_column: str = "",
    barmode: Literal["stack", "group"] = "stack",
    title: str = "",
) -> str:
    """<paste the full docstring from my earlier message here: the HOW TO CALL,
    COLUMN ROLES, CHART TYPES sections and the encounters-by-type example>
    """
    query = _validate_read_only_query(sql_query)
    df = pd.read_sql_query(query, engine)

    if df.empty:
        raise ValueError("The query returned no rows. Check filters and retry.")

    available = ", ".join(df.columns)
    for role, col in (("x_column", x_column), ("y_column", y_column),
                      ("color_column", color_column)):
        if col and col not in df.columns:
            raise ValueError(
                f"{role}='{col}' is not in the query result. "
                f"Available columns: {available}. Use the exact aliases from "
                f"your SELECT, not the literal word '{role}'."
            )

    df = df.apply(_to_numeric_if_possible)

    if chart_type in ("bar", "line", "pie", "scatter") and not y_column:
        raise ValueError(f"{chart_type} charts require y_column (a numeric column).")
    if y_column and not pd.api.types.is_numeric_dtype(df[y_column]):
        raise ValueError(
            f"y_column='{y_column}' is not numeric (e.g. {df[y_column].iloc[0]!r}). "
            f"If it is a category, make it color_column and add "
            f"COUNT(*) AS <name> as y_column."
        )
    if chart_type == "scatter" and not pd.api.types.is_numeric_dtype(df[x_column]):
        raise ValueError("scatter charts need a numeric x_column.")

    # integer years would get ticks like 2021.5 on bar/line axes
    if chart_type in ("bar", "line") and pd.api.types.is_integer_dtype(df[x_column]):
        df[x_column] = df[x_column].astype(str)

    color = color_column or None
    chart_title = title or "Hospital data"
    labels = {c: _pretty(c) for c in (x_column, y_column, color_column) if c}

    if chart_type == "bar":
        long_names = not color and df[x_column].astype(str).str.len().max() > 18
        if long_names:  # horizontal bars keep long category names readable
            fig = px.bar(df, x=y_column, y=x_column, orientation="h",
                         labels=labels, title=chart_title)
            fig.update_yaxes(categoryorder="total ascending")
        else:
            fig = px.bar(df, x=x_column, y=y_column, color=color,
                         barmode=barmode, labels=labels, title=chart_title)
    elif chart_type == "line":
        fig = px.line(df, x=x_column, y=y_column, color=color, markers=True,
                      labels=labels, title=chart_title)
    elif chart_type == "pie":
        fig = px.pie(df, names=x_column, values=y_column,
                     labels=labels, title=chart_title)
    elif chart_type == "scatter":
        fig = px.scatter(df, x=x_column, y=y_column, color=color,
                         labels=labels, title=chart_title)
    else:  # histogram
        fig = px.histogram(df, x=x_column, color=color,
                           labels=labels, title=chart_title)

    return fig.to_json()


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


