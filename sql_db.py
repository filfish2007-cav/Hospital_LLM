import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


# Load the Supabase connection string from the project-level .env file.
load_dotenv(Path(__file__).with_name(".env"))

DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "SUPABASE_DATABASE_URL is not set. Add the Supabase PostgreSQL "
        "connection string to .env."
    )

# Create the SQLAlchemy engine used to communicate with PostgreSQL.
engine: Engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Wrap the engine in LangChain's SQLDatabase interface for the SQL tool.
sql_database = SQLDatabase(engine)


def get_sql_database() -> SQLDatabase:
    """Return the shared LangChain SQL database instance."""
    return sql_database


if __name__ == "__main__":
    # Run a connection check only when this module is executed directly.
    with engine.connect():
        print("Supabase PostgreSQL connection successful.")
