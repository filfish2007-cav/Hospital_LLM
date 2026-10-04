---
applyTo: '**'
---

# Hospital AI Intelligence Platform - Project Instructions

Use `README.md` as the authoritative project context. Preserve its architecture, naming, responsibilities, and development order when generating code, answering questions, or reviewing changes.

## Architecture

This is a Python hospital assistant using Streamlit, LangChain, Google Gemini, Supabase PostgreSQL, and Pinecone.

The Gemini/LangChain agent has exactly two primary tools:

1. **SQL tool** - queries structured hospital data in Supabase PostgreSQL.
2. **RAG tool** - retrieves relevant passages from hospital documents stored in Pinecone.

The agent chooses the SQL tool, the RAG tool, or both. Do not implement tool routing with hard-coded keyword `if/else` checks. Do not add a separate analytics tool. Analytical questions should use SQL retrieval or aggregation, with results displayed or processed by the application as needed.

```text
Streamlit app.py
        ↓
Gemini/LangChain agent.py
      ↙   ↘
 SQL tool  RAG tool
    ↓          ↓
Supabase   Pinecone
PostgreSQL  documents
```

## File responsibilities

- `app.py`: Streamlit chat interface, conversation history, user input, and response display. Keep database, ingestion, embedding, agent, and complex query logic out of the UI.
- `agent.py`: Gemini model configuration, system prompt, agent creation, tool registration, and conversation execution.
- `tools.py`: The two agent-facing tools: read-only SQL querying and hospital-document retrieval.
- `sql_db.py`: Load `SUPABASE_DATABASE_URL`, create the SQLAlchemy engine, and expose LangChain `SQLDatabase`. Do not duplicate this connection elsewhere.
- `vector_db.py`: Separate Pinecone ingestion script. Read PDF/DOCX documents, extract and chunk text, create embeddings, add metadata, upsert vectors, and save vector/source mappings. Do not run ingestion automatically on every Streamlit start.
- `database_analysis.ipynb`: Offline Pandas cleaning, validation, exploratory analysis, and export of cleaned hospital data before loading it into Supabase. It is not runtime chatbot logic.
- `data/hospital/`: Source hospital documents.
- `data/csv/`: Cleaned structured datasets when used by the project.
- `vector_ids.json`: Pinecone vector IDs and source metadata.

Do not create unnecessary files or abstractions. Do not add a separate `analytics.py` unless a concrete requirement justifies it; analytics are not a third agent tool.

## Required imports and integrations

Use the project environment and existing package versions. Prefer these integrations and import paths:

```python
import streamlit as st
import pandas
import matplotlib
import dotenv
import os
import json
import plotly

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from pinecone import Pinecone
from pinecone import ServerlessSpec
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    BaseMessage,
    trim_messages,
)
```

Use `GoogleSerperAPIWrapper` only if an explicit project requirement adds web search. The default architecture has only SQL and RAG tools and must not silently introduce web search.

## Data and database rules

- Use `.env` for `GEMINI_API_KEY`, `PINECONE_API_KEY`, `PINECONE_INDEX_NAME`, and `SUPABASE_DATABASE_URL`.
- Never hard-code credentials or commit `.env`.
- Use LangChain `SQLDatabase` for Supabase access.
- Keep normal agent database operations read-only: allow `SELECT`, joins, filtering, grouping, ordering, and aggregations; reject destructive statements such as `DROP`, `DELETE`, `UPDATE`, `INSERT`, and `ALTER`.
- Do not invent database columns, records, policies, or statistics. Inspect the actual schema and dataset first.
- Use Pinecone for unstructured document content and Supabase for structured relational facts.
- RAG responses must be based on retrieved chunks and useful source metadata.

## Coding conventions

- Inspect existing files before changing them.
- Make precise changes and preserve working behavior.
- Keep responsibilities separated and reuse existing connections/configuration.
- Prefer clear, simple, typed Python over unnecessary abstractions.
- Surface configuration and runtime errors clearly; do not silently swallow failures.
- Do not add dependencies unless they are required and update `requirements.txt` when dependencies change.
- Keep README documentation consistent with the actual architecture.
- Validate changed code with the smallest relevant existing check.

## Development order

Follow this order unless a concrete dependency requires otherwise:

1. Clean and validate relational data in the notebook.
2. Create the Supabase schema and load cleaned data.
3. Create/configure the Pinecone index using the selected embedding dimension.
4. Implement document ingestion in `vector_db.py`.
5. Implement `sql_db.py` access and the read-only SQL tool.
6. Implement the RAG tool and runtime Pinecone search.
7. Create the Gemini agent and register exactly the SQL and RAG tools.
8. Connect the agent to Streamlit.
9. Test SQL-only, RAG-only, and combined questions.

The application must clearly distinguish retrieved facts from model-generated explanations and state when the available data is insufficient.
