---
applyTo: '**'
---
# Hospital AI Chatbot - Project Context

## Project overview

This project is a hospital chatbot built with Python, LangChain, Gemini, Pinecone, Supabase PostgreSQL, and Streamlit.

The chatbot answers questions using two knowledge sources:

1. Unstructured hospital documents stored in a Pinecone vector database.
2. Structured relational data stored in a Supabase PostgreSQL database.

A Gemini-powered LangChain agent decides which tool to use. It must be able to use the vector database, the SQL database, or both tools sequentially for the same question when necessary. Streamlit provides the user interface.

Do not turn this into a simple chatbot that manually selects a database with `if/else` keyword checks. The agent must be the central decision-making component.

## Required technologies

Use:

- Python
- Streamlit
- LangChain
- Gemini models through `langchain-google-genai`
- Gemini embeddings through `GoogleGenerativeAIEmbeddings`
- Pinecone and `langchain-pinecone`
- Supabase PostgreSQL
- LangChain `SQLDatabase`
- Pandas
- Matplotlib
- `python-dotenv`

Use the installed LangChain version's current agent functionality, preferably `create_agent`.

## Repository structure and responsibilities

Prefer this simple structure:

```text
hospital-chatbot/
├── app.py
├── agent.py
├── tools.py
├── vector_db.py
├── sql_db.py
├── database_analysis.ipynb
├── data/
│   ├── hospital/
│   └── vector_ids.json
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

Do not create unnecessary abstraction files such as `utils.py`, `config.py`, `models.py`, `schemas.py`, or `prompts.py` unless the project becomes large enough to genuinely require them. Keep the project readable and portfolio/student-project sized.

### `app.py`

Keep this file limited to the Streamlit UI: page configuration, chatbot interface, chat history, user input, displaying responses, and calling the agent. Do not put Pinecone ingestion, document chunking, database cleaning, SQL schema creation, raw SQL business logic, or embedding generation here.

### `agent.py`

Create and configure the Gemini LangChain agent here. Include the Gemini chat model, system instructions, agent creation, registration of the vector and SQL tools, and message/history handling when needed. The agent must decide which tool is appropriate and must be able to use both tools sequentially.

### `tools.py`

Define the tools exposed to the Gemini agent:

1. A vector search tool that embeds a query, searches the existing Pinecone index, and returns useful document context. It must not recreate or re-ingest Pinecone on every call.
2. An SQL database tool that gives the agent access to structured hospital information through LangChain's `SQLDatabase`, rather than relying on one hard-coded query per possible question.

### `vector_db.py`

Keep Pinecone ingestion/setup separate from Streamlit. Read every hospital document, split it into sections, add current time to metadata, generate embeddings, store each section in Pinecone, and save each generated ID with its section name and file name.

At minimum, vector metadata must identify:

```text
file_name
section_name
current_time
```

### `data/vector_ids.json`

Store the mapping between Pinecone vector IDs and their source file and section information. Pinecone remains the actual vector database; this file is only the required ID/source mapping.

### `sql_db.py`

Keep Supabase PostgreSQL connection/configuration and the LangChain `SQLDatabase` setup here. Do not turn this file into another chatbot or agent. Keep SQL infrastructure separate from the agent.

## Supabase relational database

The relational database must be hosted on Supabase and contain multiple related tables with primary keys, foreign keys where appropriate, and realistic hospital data. Possible entities include `doctors`, `departments`, `schedules`, `appointments`, and `patients`.

The schema should support questions such as:

- Which doctors work in cardiology?
- What doctors are working tomorrow?
- Which department does a particular doctor belong to?
- What appointments are scheduled?
- Which doctors have appointments at a particular time?

Base the final schema on the course SQL/database exercises instead of making it unnecessarily complicated.

Never put Supabase credentials in source code. Use environment variables.

## Database analysis notebook

`database_analysis.ipynb` should demonstrate database inspection and cleaning using Pandas and Matplotlib. Include, as appropriate:

1. Loading or connecting to data.
2. Inspecting tables and data types.
3. Checking missing values, duplicates, invalid values, and inconsistent values.
4. Cleaning and validating the data.
5. Basic descriptive statistics.
6. Pandas analysis.
7. Matplotlib visualizations.
8. Short conclusions.

The analysis need not be advanced; its purpose is to demonstrate data preparation and basic data quality review.

## Agent behavior

Use the vector database for hospital policies, instructions, FAQs, procedures, rules, and other unstructured document content.

Use the SQL database for doctors, departments, schedules, appointments, structured hospital records, and relationships between entities.

Use both tools only when both sources are needed. For example, for “Who is working in cardiology tomorrow and what are the visiting rules for patients there?”, query SQL for the schedule, search Pinecone for visiting rules, and combine the results in Gemini. Do not automatically call both tools for every question.

## Environment and dependencies

Secrets must be environment variables. Use consistent names such as:

```text
GEMINI_API_KEY
PINECONE_API_KEY
PINECONE_INDEX_NAME
SUPABASE_DATABASE_URL
```

Include `.env` in `.gitignore`; never commit real API keys or database passwords. Create `.env.example` when useful.

`requirements.txt` should contain only dependencies needed for the application, including Streamlit, Pandas, Matplotlib, `python-dotenv`, `langchain-google-genai`, LangChain core/community packages, Pinecone/LangChain Pinecone packages, and the appropriate PostgreSQL driver. `GoogleSerperAPIWrapper` and web search are not required because the architecture has exactly two primary knowledge tools.

## Design principles

Keep the project modular, readable, simple enough to understand, logically separated, and easy to run and demonstrate.

- Do not duplicate database connections or agent initialization.
- Do not recreate Pinecone indexes whenever Streamlit starts.
- Do not mix Streamlit UI logic with ingestion.
- Do not hard-code tool selection with keywords.
- Do not add unrelated AI services or frameworks.
- Do not introduce additional abstraction without a concrete reason.
- Preserve existing working code and inspect the project before changing it.
- If existing code conflicts with this architecture, explain the conflict before making a large structural change.

## Implementation priority

When implementing missing functionality, prefer this order:

1. Prepare and clean relational data.
2. Create the Supabase relational schema.
3. Create and populate Pinecone.
4. Implement `SQLDatabase` access.
5. Implement the vector search tool.
6. Implement the SQL tool.
7. Create the Gemini agent.
8. Connect the agent to Streamlit.
9. Test individual tools.
10. Test combined agent queries.
11. Prepare the README and demo.

Do not prioritize UI polishing before the underlying tools work correctly.

## Testing scenarios

Test at least:

- Vector-only: “What are the hospital's visiting rules?” should use vector search and Pinecone.
- SQL-only: “Which doctors are working in the cardiology department tomorrow?” should use the SQL tool and Supabase.
- Combined: “Who is working in cardiology tomorrow and what are the visiting rules for patients?” should use both tools and produce one combined response.

## Definition of done

The project is complete when hospital documents can be ingested into Pinecone, are split into sections, include current time/file/section metadata, and have IDs saved in `data/vector_ids.json`; Supabase has multiple related tables; relational data is inspected and cleaned in a Pandas/Matplotlib notebook; LangChain `SQLDatabase` is used; vector and SQL tools exist; Gemini is the agent model; the agent can select either tool or both when required; Streamlit provides the chat UI; secrets use environment variables; the repository has a clear README; and the project runs without source changes for each query.

When modifying this repository, first inspect the existing structure and code. Do not rewrite working code unnecessarily, change the architecture without a concrete reason, introduce additional frameworks, or skip the separation of responsibilities described above. The target architecture has exactly two primary knowledge sources:

```text
Pinecone Vector Database + Supabase SQL Database
```

They are connected through LangChain tools and exposed through a Streamlit application.
