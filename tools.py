import re
from typing import Literal

import pandas as pd
import plotly.express as px
from langchain_core.tools import tool

from sql_db import engine, get_sql_database


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


HOSPITAL_TOOLS = [query_hospital_database, create_hospital_chart]