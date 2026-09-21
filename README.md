# 🏥 Hospital AI Chatbot

An AI-powered hospital assistant built with **Python, LangChain, Google Gemini, Pinecone, Supabase PostgreSQL, and Streamlit**.

The chatbot combines two different knowledge sources:

- 📚 **Pinecone Vector Database** — for searching hospital documents and policies using semantic search.
- 🗄️ **Supabase PostgreSQL Database** — for structured hospital data such as doctors, departments, schedules, and appointments.

A **LangChain agent powered by Google Gemini** decides which tool to use based on the user's question and combines information from both sources when necessary.

---

## ✨ Project Overview

The goal of this project is to build a hospital chatbot capable of answering both **document-based** and **database-based** questions.

For example:

> **"What are the hospital visiting rules?"**

The agent searches the hospital documents stored in Pinecone.

> **"Which cardiologists are working tomorrow?"**

The agent queries the relational PostgreSQL database.

> **"Which cardiologists are working tomorrow and what are the visiting rules?"**

The agent can use **both tools**, then combine the results into one understandable response.

### Core architecture

```text
                         ┌─────────────────────┐
                         │      Streamlit      │
                         │     Chat Interface  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Gemini +          │
                         │   LangChain Agent   │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
          ┌──────────────────┐             ┌──────────────────┐
          │ Vector DB Tool   │             │   SQL DB Tool    │
          └────────┬─────────┘             └────────┬─────────┘
                   │                                │
                   ▼                                ▼
          ┌──────────────────┐             ┌──────────────────┐
          │     Pinecone     │             │ Supabase         │
          │  Vector Database │             │ PostgreSQL       │
          └────────┬─────────┘             └────────┬─────────┘
                   │                                │
                   ▼                                ▼
          Hospital Documents              Structured Hospital
                                          Data / Relationships
```

---

# 🧠 Main Features

## 1. AI Hospital Assistant

The chatbot uses **Google Gemini** through LangChain to understand natural-language questions and determine what information is required.

The agent can:

- understand natural-language questions;
- select the appropriate tool;
- search hospital documentation;
- query structured hospital data;
- use both data sources when required;
- combine retrieved information into a single response.

---

## 2. 📚 Pinecone Vector Database

Hospital documents are converted into searchable vector representations.

The ingestion process:

```text
Hospital Documents
       ↓
Read Documents
       ↓
Split into Sections
       ↓
Add Metadata
       ↓
Generate Embeddings
       ↓
Store in Pinecone
       ↓
Save Vector IDs + Source Information
```

Each section contains metadata such as:

- source file name;
- section name;
- ingestion/current timestamp;
- vector ID.

A separate JSON file is used to keep track of the created vectors and their sources.

This allows the chatbot to perform **semantic search** instead of relying only on exact keyword matches.

---

## 3. 🗄️ Supabase PostgreSQL Database

Structured hospital information is stored in a relational PostgreSQL database hosted by **Supabase**.

The database contains multiple related tables connected through primary and foreign keys.

Example conceptual structure:

```text
Departments
     │
     ├──────────────┐
     ▼              ▼
  Doctors        Schedules
     │
     ▼
Appointments
```

The exact tables and relationships depend on the hospital dataset and database design.

The chatbot accesses this database through LangChain's `SQLDatabase` functionality.

This allows the agent to generate and execute SQL queries for questions involving structured information.

---

# 🤖 Agent Tool Selection

The chatbot has two main tools.

### Vector Search Tool

Used for questions about information contained in hospital documents.

Examples:

```text
"What are the visiting hours?"

"What are the rules for hospital visitors?"

"What documents are required for admission?"
```

### SQL Database Tool

Used for questions involving structured hospital data.

Examples:

```text
"Which doctors work in cardiology?"

"Which doctors are available tomorrow?"

"How many doctors work in each department?"
```

### Combined Questions

Some questions require both tools.

Example:

```text
"Which cardiologists are working tomorrow and what are
the visiting rules for their patients?"
```

The agent can:

```text
Question
   ↓
Understand requirements
   ↓
SQL Tool ────────→ Find cardiologists/schedule
   │
   └── Vector Tool → Find visiting rules
              ↓
        Gemini combines results
              ↓
          Final answer
```

---

# 🖥️ Streamlit Interface

The chatbot is presented through a simple Streamlit web interface.

The interface is responsible for:

- displaying the application;
- displaying conversation history;
- accepting user questions;
- sending questions to the LangChain agent;
- displaying the generated response.

The Streamlit layer does **not** contain database ingestion logic.

This keeps the user interface separate from the application's backend architecture.

---

# 📁 Project Structure

```text
hospital-chatbot/
│
├── .github/
│   └── instructions/
│       └── project-context.instructions.md
|
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml
|
│
├── data/
│   ├── hospital/
│   │   ├── for_workers.docx
│   │   ├── general.pdf
│   │
│   └── vector_ids.json
│
├── app.py
├── agent.py
├── tools.py
├── vector_db.py
├── sql_db.py
│
├── database_analysis.ipynb
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## File Responsibilities

| File | Responsibility |
|---|---|
| `app.py` | Streamlit user interface |
| `agent.py` | Gemini/LangChain agent configuration and system instructions |
| `tools.py` | Vector search and SQL database tools |
| `vector_db.py` | Hospital document ingestion into Pinecone |
| `sql_db.py` | Supabase PostgreSQL / LangChain SQLDatabase configuration |
| `database_analysis.ipynb` | Data cleaning, exploration and basic analytics |
| `data/hospital/` | Source hospital documents |
| `data/vector_ids.json` | Vector IDs and source metadata |
| `.streamlit/config.toml` | Streamlit application settings |
| `.streamlit/secrets.toml` | Local Streamlit secrets; never commit this file |
| `requirements.txt` | Python dependencies |
| `.env` | API keys and database credentials |
| `README.md` | Project documentation |

---

# 🧹 Data Analysis & Cleaning

Before using structured data in the relational database, the dataset is inspected and cleaned using:

- **Pandas**
- **Matplotlib**
- Jupyter Notebook

The analysis includes:

- checking data types;
- identifying missing values;
- identifying duplicates;
- checking invalid values;
- basic descriptive statistics;
- simple visualizations;
- documenting relevant observations.

The notebook is kept separate from the application code so that exploratory analysis does not become part of the chatbot runtime.

---

# 🔐 Environment Variables

API keys and database credentials should **never be hardcoded** into Python files or committed to GitHub.

Create a local `.env` file containing the required credentials.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key

PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_pinecone_index

SUPABASE_DATABASE_URL=your_postgresql_connection_string
```

The exact variables should match those used by the implementation.

Add `.env` and `.venv` to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone <repository-url>
cd hospital-chatbot
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create `.env` and add the required Gemini, Pinecone, and Supabase credentials.

---

# 🗃️ Database Setup

The project uses two different databases for two different purposes.

### Pinecone

Pinecone stores vector representations of hospital document sections.

Before running the chatbot, the hospital documents must be processed by the vector database ingestion pipeline.

Conceptually:

```bash
python vector_db.py
```

This process:

1. reads the hospital documents;
2. splits them into sections;
3. creates embeddings;
4. adds metadata;
5. uploads the vectors to Pinecone;
6. saves vector/source information.

### Supabase

The relational PostgreSQL database must be created and populated separately.

It should contain the required hospital tables and relationships.

The application then connects to this database through `sql_db.py`.

---

# ▶️ Running the Application

After configuring the environment and databases:

```bash
streamlit run app.py
```

The Streamlit interface will open in the browser.

---

# 💬 Example Questions

### 📚 Document / Vector Search

```text
What are the hospital visiting rules?

What are the visiting hours?

What are the admission requirements?
```

### 🗄️ SQL Database

```text
Which doctors work in the cardiology department?

Which doctors are available tomorrow?

How many doctors work in each department?
```

### 🔀 Combined Search

```text
Which cardiologists are working tomorrow and what are
the visiting rules for their patients?
```

The last type of question demonstrates the main advantage of the agent architecture: **the chatbot can combine structured and unstructured information.**

---

# 🧪 Testing

The application should be tested with at least three categories of questions.

### Test 1 — Vector Database

Ask a question whose answer exists in the hospital documents.

Expected behavior:

```text
User
 ↓
Agent
 ↓
Vector Search Tool
 ↓
Pinecone
 ↓
Relevant document sections
 ↓
Gemini response
```

### Test 2 — SQL Database

Ask a question whose answer exists in the relational database.

Expected behavior:

```text
User
 ↓
Agent
 ↓
SQL Tool
 ↓
Supabase PostgreSQL
 ↓
Query result
 ↓
Gemini response
```

### Test 3 — Both Sources

Ask a question requiring information from both databases.

Expected behavior:

```text
User
 ↓
Agent
 ├──→ Vector Search
 │
 └──→ SQL Query
       ↓
Combined information
       ↓
Gemini
       ↓
Final response
```

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Main programming language |
| **LangChain** | Agent and tool orchestration |
| **Google Gemini** | Large language model |
| **Google Generative AI Embeddings** | Document embeddings |
| **Pinecone** | Vector database |
| **Supabase** | PostgreSQL database hosting |
| **SQLDatabase** | LangChain interface for SQL |
| **Streamlit** | Web chatbot interface |
| **Pandas** | Data cleaning and analysis |
| **Matplotlib** | Data visualization |
| **Jupyter Notebook** | Exploratory data analysis |

---

# 🏗️ Design Principles

The project follows several important architectural principles.

### Separation of concerns

Each component has a specific responsibility:

```text
UI
 ↓
Agent
 ↓
Tools
 ↓
Databases
```

The Streamlit interface should not contain database ingestion logic.

### Two knowledge sources

Unstructured and structured information are deliberately separated:

```text
Hospital Documents → Pinecone
Structured Data     → PostgreSQL
```

### Agent-driven tool selection

The chatbot should determine which source is appropriate instead of forcing every question through the same database.

### Secure configuration

Credentials belong in environment variables and should never be committed to the repository.

### Simple architecture

The project should remain understandable and maintainable rather than introducing unnecessary abstractions or services.

---

# ⚠️ Security & Privacy

This project is intended as an educational AI application.

Do not commit:

- API keys;
- database passwords;
- private connection strings;
- `.env` files;
- sensitive patient information.

For a real-world medical application, additional requirements would be necessary, including authentication, authorization, audit logging, data protection, validation, monitoring, and appropriate regulatory compliance.

The chatbot should therefore **not be treated as a replacement for professional medical advice or a production clinical system.**

---

# 🎯 Project Goals

The completed project should demonstrate the ability to:

- build a LangChain agent;
- integrate Google Gemini;
- create and query a Pinecone vector database;
- process and embed documents;
- work with PostgreSQL/Supabase;
- use LangChain `SQLDatabase`;
- create agent tools;
- combine structured and unstructured information;
- clean and analyze data with Pandas;
- visualize data with Matplotlib;
- build a Streamlit chatbot;
- manage configuration securely with environment variables.

---

# ✅ Definition of Done

The project is considered complete when:

- [ ] Hospital documents are stored and processed.
- [ ] Documents are split into meaningful sections.
- [ ] Sections contain appropriate metadata.
- [ ] Embeddings are stored in Pinecone.
- [ ] Vector IDs and source information are saved.
- [ ] Supabase PostgreSQL database is created.
- [ ] Multiple relational tables and relationships are implemented.
- [ ] Structured data is cleaned and analyzed.
- [ ] LangChain `SQLDatabase` connects to Supabase.
- [ ] Vector search is available as an agent tool.
- [ ] SQL querying is available as an agent tool.
- [ ] Gemini agent can select the appropriate tool.
- [ ] Agent can use both tools for combined questions.
- [ ] Streamlit chatbot works.
- [ ] Secrets are stored outside the repository.
- [ ] The application has been tested with vector, SQL, and combined questions.

---

## 🚀 Final Architecture

The complete system can be summarized as:

```text
                  ┌─────────────────────┐
                  │      USER           │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │     STREAMLIT       │
                  │    CHAT INTERFACE   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   GEMINI AGENT      │
                  │     + LANGCHAIN     │
                  └──────────┬──────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
       ┌─────────────────┐       ┌─────────────────┐
       │ VECTOR TOOL     │       │    SQL TOOL     │
       └────────┬────────┘       └────────┬────────┘
                │                         │
                ▼                         ▼
       ┌─────────────────┐       ┌─────────────────┐
       │    PINECONE     │       │    SUPABASE     │
       │  Vector Search  │       │   PostgreSQL    │
       └────────┬────────┘       └────────┬────────┘
                │                         │
                ▼                         ▼
       Hospital Documents        Structured Hospital
                                  Data & Relationships
```

**Hospital AI Chatbot — combining semantic document search and structured hospital data through an intelligent LangChain agent.**