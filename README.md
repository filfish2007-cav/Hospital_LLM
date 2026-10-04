# 🏥 Hospital AI Intelligence Platform

> An AI-first hospital assistant that answers questions from structured hospital data and hospital documents through one Streamlit interface.

The Hospital AI Intelligence Platform combines Gemini, LangChain, Supabase PostgreSQL, Pinecone, and Streamlit. Its agent has **two tools only**:

- **SQL tool** — queries the structured hospital database in Supabase.
- **RAG tool** — retrieves relevant hospital-document content from Pinecone.

The agent selects the right tool for a question, or uses both when the answer needs both database facts and document context.

---

## ✨ What Can It Do?

### 📊 Structured hospital data — SQL tool

The cleaned hospital CSVs are loaded into **Supabase PostgreSQL**. The SQL tool can answer database questions about patients, encounters, conditions, medications, observations, and procedures.

Examples:

> "What medications was patient X prescribed?"

> "How many emergency encounters are in the dataset?"

> "What are the most common recorded conditions?"

### 📄 Hospital documents — RAG tool

Hospital documents are chunked, embedded, and stored in **Pinecone**. The RAG tool retrieves relevant passages before the model answers questions about policies and hospital information.

Examples:

> "What are the hospital visiting hours?"

> "What is the policy for emergency admissions?"

### 🔀 Questions that need both tools

Some questions combine a fact from the database with policy information from documents.

> "What encounters did patient X have, and what is the relevant follow-up policy?"

The agent can query Supabase for the encounter data, retrieve the policy from Pinecone, and produce one grounded answer.

---

## 🧠 Architecture

```text
                         USER
                           │
                           ▼
                    ┌────────────┐
                    │ Streamlit  │
                    │   app.py   │
                    └─────┬──────┘
                          │
                          ▼
                    ┌────────────┐
                    │ Gemini /   │
                    │ LangChain  │
                    │   Agent    │
                    └─────┬──────┘
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
       ┌──────────┐               ┌──────────┐
       │ SQL Tool │               │ RAG Tool │
       └────┬─────┘               └────┬─────┘
            ▼                          ▼
     Supabase PostgreSQL             Pinecone
     structured hospital data      hospital documents
```

The agent does not use a separate analytics tool. It routes every request to the SQL tool, the RAG tool, or both.

---

## 🔍 Example Interactions

| User request | Tool route |
|---|---|
| "What are the visiting hours?" | RAG / Pinecone |
| "How many emergency encounters are there?" | SQL / Supabase |
| "What medications was this patient prescribed?" | SQL / Supabase |
| "What is the follow-up policy for this patient's condition?" | SQL + RAG |
| "Which procedures are recorded for patient X?" | SQL / Supabase |

---

## 🏗️ Project Structure

```text
hospital-ai/
│
├── app.py                       # Streamlit application
├── agent.py                     # Gemini/LangChain AI agent
├── tools.py                     # SQL and RAG tools available to the agent
├── sql_db.py                    # Supabase/PostgreSQL connection
├── vector_db.py                 # Pinecone document ingestion
│
├── database_analysis.ipynb      # Data cleaning & exploratory analysis
│
├── data/
│   ├── hospital/                 # Hospital documents
│   └── csv/                      # Structured hospital datasets
│
├── vector_ids.json              # Vector/source metadata
│
├── requirements.txt
├── .env                         # Local secrets
├── .gitignore
└── README.md
```

### Separation of responsibilities

**`app.py`**  
The Streamlit chat interface.

**`agent.py`**  
The central orchestration layer. It decides whether a question needs SQL, RAG, or both.

**`tools.py`**  
Defines the two tools exposed to the agent: one for SQL database queries and one for document retrieval.

**`sql_db.py`**  
Connects the SQL tool to the Supabase PostgreSQL database.

**`vector_db.py`**  
Processes hospital documents and stores their embeddings in Pinecone.

**`database_analysis.ipynb`**  
Cleans, validates, explores, and exports the original hospital datasets before they are loaded into Supabase.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core application |
| **Google Gemini** | Natural-language reasoning and final responses |
| **LangChain** | Agent and two-tool orchestration |
| **Supabase / PostgreSQL** | Structured hospital data and SQL queries |
| **Pinecone** | Vector search over hospital documents |
| **Pandas** | Dataset cleaning and validation |
| **Streamlit** | User interface |

---

## 🔄 Data Pipeline

### Structured data

```text
Raw hospital CSVs
      ↓
Cleaning & validation notebook
      ↓
Cleaned CSVs
      ↓
Supabase PostgreSQL
      ↓
SQL tool
      ↓
Gemini agent
```

### Hospital documents

```text
PDF / DOCX documents
      ↓
vector_db.py
      ↓
Text extraction and chunking
      ↓
Embeddings
      ↓
Pinecone
      ↓
RAG tool
      ↓
Gemini agent
```

---

## 🔐 Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name
SUPABASE_DATABASE_URL=your_database_url
```

> Never commit `.env` or API keys to GitHub.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Hospital_LLM
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env`, then add the required keys and database connection string.

### 5. Prepare the data sources

Before starting the app:

1. Run the cleaning notebook and export the cleaned hospital CSVs.
2. Create the Supabase schema and import the cleaned CSVs.
3. Run document ingestion to populate the Pinecone index.

### 6. Run the application

```bash
streamlit run app.py
```

---

## 🧪 Example Questions

### Document knowledge

> What are the hospital visiting hours?

### Database knowledge

> How many inpatient encounters are recorded?

> What conditions are most common in the dataset?

### Combined knowledge

> What medication did patient X receive, and what does the hospital policy say about follow-up?

---

## 🎯 Design Goals

- Retrieval-Augmented Generation (RAG)
- Tool-using AI agents
- Natural-language SQL
- Relational database design
- Data cleaning and validation
- Grounded responses from structured and unstructured sources
- Modular software architecture
- LLM integration with external data sources

The goal is not just a chatbot. It is a practical example of an LLM acting as an interface to a relational database and a document knowledge base.

---

## 🔒 Security & Reliability

- API keys stay outside source control in `.env`.
- Structured data and document knowledge remain separate sources.
- The agent uses retrieved SQL results and document passages to ground its answers.
- Normal user questions are read-only; they do not modify hospital data.
- The application should clearly say when the available data cannot support an answer.

---

## 🚧 Project Status

- [x] Clean and validate hospital datasets
- [ ] Load the cleaned relational data into Supabase
- [ ] Implement Pinecone document ingestion
- [ ] Implement the RAG tool
- [ ] Implement the SQL tool
- [ ] Integrate the Gemini/LangChain agent
- [ ] Build the Streamlit interface
- [ ] Test SQL-only, RAG-only, and combined questions
- [ ] Deploy the application

---

## 📌 Project Goal

Build one hospital intelligence interface where users can ask natural-language questions and receive answers grounded in either the hospital database, hospital documents, or both.

> Ask a question. Let the agent choose SQL, RAG, or both—and answer using the right evidence.

### Author

**Filip Rybkin**  
AI / Data / Software Engineering Project
