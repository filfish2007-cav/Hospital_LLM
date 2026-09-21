# Hospital AI Chatbot

An agent-based hospital chatbot built with Python, Streamlit, LangChain, Gemini, Pinecone, and Supabase PostgreSQL.

## Architecture

The chatbot uses two knowledge sources:

- **Pinecone** stores unstructured hospital documents such as policies, procedures, FAQs, and visiting rules.
- **Supabase PostgreSQL** stores structured data such as doctors, departments, schedules, patients, and appointments.

The Gemini-powered LangChain agent is the central decision-maker. It receives the user's question from Streamlit, chooses the vector search tool, the SQL tool, or both, and generates the final answer.

```text
User
  |
  v
Streamlit (app.py)
  |
  v
Gemini LangChain Agent (agent.py)
  |                         |
  v                         v
Vector Search Tool       SQL Database Tool
  |                         |
  v                         v
Pinecone                 Supabase PostgreSQL
  \_________________________ __________________/
                            v
                    Final answer in Streamlit
```

For example, a question about doctors working tomorrow uses the SQL tool. A question about visiting rules uses the vector search tool. A question asking for both uses both tools sequentially, and the agent combines their results.

## Project structure

```text
.
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
└── README.md
```

### `app.py`

The Streamlit user interface. It displays the chat, stores conversation history, accepts questions, and sends them to the agent. It does not create databases, ingest documents, or contain database logic.

### `agent.py`

Creates and configures the Gemini LangChain agent. It contains the system instructions and registers the vector search and SQL tools. The agent decides which tool or combination of tools is needed; tool selection is not hard-coded with keyword checks.

### `tools.py`

Defines the tools available to the agent:

- The **vector search tool** embeds a question, searches the existing Pinecone index, and returns relevant document context.
- The **SQL tool** exposes the Supabase database through LangChain's `SQLDatabase`, allowing the agent to query structured hospital data.

### `vector_db.py`

An ingestion/setup script run separately from Streamlit. It reads documents from `data/hospital/`, splits them into sections, creates Gemini-compatible embeddings, stores the sections in Pinecone, and adds `file_name`, `section_name`, and `current_time` metadata.

### `data/vector_ids.json`

Stores each Pinecone vector ID together with its source file and section name. Pinecone remains the actual vector database.

### `sql_db.py`

Configures the connection from Supabase PostgreSQL to LangChain's `SQLDatabase`. It contains SQL infrastructure only, not the agent or Streamlit UI.

### `database_analysis.ipynb`

Uses Pandas and Matplotlib to inspect, clean, validate, and analyze the relational data before it is used by the chatbot.

### Data flow

```text
Hospital documents
  -> vector_db.py
  -> Gemini embeddings
  -> Pinecone
  -> vector search tool in tools.py
  -> agent.py

Supabase PostgreSQL
  -> sql_db.py
  -> LangChain SQLDatabase
  -> SQL tool in tools.py
  -> agent.py

User question
  -> app.py
  -> agent.py
  -> one or both tools
  -> final response
  -> app.py
```

Pinecone ingestion is performed separately and is not repeated every time the Streamlit application starts.

## Requirements

- Python 3.10+
- Streamlit
- LangChain
- `langchain-google-genai`
- `langchain-community`
- `langchain-core`
- Pinecone and `langchain-pinecone`
- Pandas
- Matplotlib
- `python-dotenv`
- A PostgreSQL driver supported by the selected Supabase connection
- Google Gemini API key
- Pinecone API key and index
- Supabase PostgreSQL database
