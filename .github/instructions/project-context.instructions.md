---
applyTo: ""
---

# Hospital AI Intelligence Platform — Project Context

## 1. Project Overview

This project is a **Hospital AI Intelligence Platform** built with Python, LangChain, Gemini, Pinecone, Supabase PostgreSQL, Pandas, Plotly, and Streamlit.

The platform combines:

1. **AI chatbot**
2. **Hospital document RAG**
3. **Relational hospital database**
4. **SQL-based data access**
5. **Data analytics**
6. **AI-driven visualizations**
7. **Interactive Streamlit dashboard**

The key architectural principle is:

> **AI is the central intelligence layer. The dashboard is not a separate static dashboard. It is an AI-driven interface that displays answers, analytics, metrics, charts, and tables generated from the user's requests.**

The system must be designed as one integrated platform rather than as separate chatbot and dashboard applications.

---

# 2. Core Architecture

The high-level architecture is:

```text
                         USER
                           │
                           ▼
                      ┌─────────┐
                      │ app.py  │
                      │Streamlit│
                      └────┬────┘
                           │
                           ▼
                     ┌───────────┐
                     │ agent.py  │
                     │ Gemini AI │
                     └─────┬─────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
          SQL TOOL      RAG TOOL    ANALYTICS TOOL
              │            │            │
              ▼            ▼            ▼
          Supabase      Pinecone    analytics.py
          PostgreSQL    Vector DB   Pandas/Plotly
              │            │            │
              └────────────┼────────────┘
                           ▼
                         Gemini
                           │
                  ┌────────┴────────┐
                  ▼                 ▼
              AI ANSWER        VISUALIZATION
                  │                 │
                  └────────┬────────┘
                           ▼
                         app.py
                           │
                           ▼
                          USER
```

The AI agent decides which tools are required for each request.

The system must **not automatically call every tool for every question**.

---

# 3. Project Structure

The target project structure is:

```text
hospital-ai/
│
├── app.py
├── agent.py
├── tools.py
├── sql_db.py
├── vector_db.py
├── analytics.py
├── database_analysis.ipynb
│
├── data/
│   ├── hospital/
│   │   ├── hospital_rules.pdf
│   │   └── hospital_information.docx
│   │
│   └── csv/
│       ├── patients.csv
│       ├── doctors.csv
│       ├── appointments.csv
│       ├── treatments.csv
│       └── billing.csv
│
├── vector_ids.json
│
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
└── .github/
    └── instructions/
        └── project-context.instructions.md
```

The exact hospital document filenames may differ depending on the provided dataset, but the architectural roles remain the same.

---

# 4. File Responsibilities

## app.py

`app.py` is the **Streamlit presentation layer**.

It is responsible for:

- Starting the Streamlit application
- Rendering the chat interface
- Displaying chat history
- Accepting user questions
- Sending user questions to `agent.py`
- Displaying AI responses
- Displaying generated metrics
- Displaying tables
- Displaying charts
- Rendering the AI-driven dashboard

`app.py` should contain UI logic, not database implementation or complex AI logic.

Do NOT put the following directly into `app.py` unless absolutely necessary:

- Pinecone connection logic
- Supabase connection logic
- Embedding generation
- SQL agent implementation
- Large data-cleaning operations
- RAG implementation
- Complex analytics algorithms
- The main system prompt

The UI should communicate with the backend through the agent/tools architecture.

---

# 5. agent.py

`agent.py` is the **central AI orchestration layer**.

It contains:

- Gemini model configuration
- System prompt
- LangChain agent configuration
- Tool registration
- Agent execution logic
- Conversation context/memory if needed

The agent should be capable of deciding which tool(s) to use based on the user's request.

The agent should NOT be hardcoded to use one specific tool for every request.

Conceptually:

```text
User question
      ↓
Gemini Agent
      ↓
Determine required information
      ↓
Select tool(s)
      ↓
Receive tool results
      ↓
Reason over results
      ↓
Generate final response
```

The agent can use:

- SQL Tool
- RAG Tool
- Analytics Tool

It may use multiple tools for one request.

---

# 6. tools.py

`tools.py` contains the tools exposed to the AI agent.

The tools should provide a clean interface between Gemini and the underlying systems.

Potential tools include:

```text
query_hospital_database()
search_hospital_documents()
analyze_hospital_data()
```

The exact function names can be changed if a better naming scheme is needed.

The important rule is that `tools.py` should contain **agent-facing tool functions**, while the underlying implementation remains in dedicated modules.

Architecture:

```text
agent.py
   ↓
tools.py
   ↓
┌──────────────┬───────────────┬───────────────┐
SQL            RAG             Analytics
↓              ↓               ↓
sql_db.py      Pinecone        analytics.py
```

Do not duplicate database connection logic inside every tool.

---

# 7. sql_db.py

`sql_db.py` is responsible for the connection between the Python/LangChain application and the Supabase PostgreSQL database.

Responsibilities:

- Load Supabase database configuration
- Create the LangChain `SQLDatabase`
- Provide database access to the SQL tool
- Handle database connection configuration

Conceptual architecture:

```text
.env
 ↓
SUPABASE_DATABASE_URL
 ↓
sql_db.py
 ↓
SQLDatabase
 ↓
tools.py
 ↓
agent.py
```

`sql_db.py` should NOT contain:

- Streamlit UI
- Gemini configuration
- Pinecone logic
- Document embeddings
- Data-cleaning notebooks
- The main agent prompt

The database itself is hosted by Supabase/PostgreSQL.

---

# 8. vector_db.py

`vector_db.py` is responsible primarily for **creating/populating the Pinecone vector database** from hospital documents.

It should:

1. Read hospital documents
2. Extract text
3. Split documents into meaningful sections/chunks
4. Generate embeddings
5. Add metadata
6. Insert vectors into Pinecone
7. Save IDs/source information to `vector_ids.json`

Metadata should include useful information such as:

```text
file_name
section_name
created_at
```

Potential architecture:

```text
PDF / DOCX
    ↓
vector_db.py
    ↓
text extraction
    ↓
section/chunk splitting
    ↓
embeddings
    ↓
Pinecone
```

`vector_db.py` is primarily a **data ingestion/setup script**.

It should NOT re-ingest all documents every time the Streamlit application starts.

The vector database should normally be populated separately before running the application.

---

# 9. Pinecone Runtime Search

The runtime RAG flow should conceptually be:

```text
User question
      ↓
agent.py
      ↓
RAG Tool
      ↓
Pinecone similarity search
      ↓
Relevant document sections
      ↓
Gemini
      ↓
Answer
```

If a separate RAG search helper/module is needed, it may be introduced, but do not unnecessarily create extra files.

Keep the architecture simple.

---

# 10. analytics.py

`analytics.py` is the **runtime analytics layer**.

Its purpose is to transform structured database results into useful analytical results.

Potential responsibilities:

- Calculate KPIs
- Calculate percentages/rates
- Compare departments
- Calculate trends
- Aggregate time-series data
- Compare categories
- Prepare data for charts
- Create Plotly visualizations when appropriate

Examples:

```text
calculate_cancellation_rate()
calculate_department_statistics()
calculate_monthly_trends()
compare_departments()
```

The exact functions should be based on actual project requirements and data.

Do not create dozens of unnecessary analytics functions before understanding the dataset.

---

# 11. Analytics Architecture

The preferred flow is:

```text
User
 ↓
agent.py
 ↓
SQL Tool
 ↓
Supabase
 ↓
Structured data
 ↓
analytics.py
 ↓
Metrics / analytical results
 ↓
Plotly / Streamlit
 ↓
Dashboard
```

For database-scale aggregation, prefer SQL when appropriate.

Use Pandas when it is useful for:

- Data transformation
- Data analysis
- Calculations
- Smaller result sets
- Runtime analytical operations

Do not unnecessarily download the entire database into Pandas for every user question.

---

# 12. database_analysis.ipynb

`database_analysis.ipynb` is the **data preparation and exploratory analysis environment**.

It is primarily used before deployment/runtime.

Responsibilities:

- Load Kaggle/CSV data
- Inspect datasets
- Detect missing values
- Detect duplicates
- Check invalid values
- Check inconsistent categories
- Validate relationships
- Clean data
- Transform data
- Explore distributions
- Perform exploratory data analysis
- Generate useful statistical insights
- Prepare data for Supabase

Example workflow:

```text
CSV files
   ↓
Pandas
   ↓
Data inspection
   ↓
Cleaning
   ↓
Validation
   ↓
Normalization / transformation
   ↓
Supabase
```

The notebook is NOT the main runtime backend.

Do not move all notebook logic into the Streamlit application.

---

# 13. Supabase Database

Supabase/PostgreSQL stores structured hospital information.

Potential tables:

```text
patients
doctors
departments
appointments
treatments
billing
```

The actual schema must be based on the selected dataset.

Relationships should be properly represented using primary keys and foreign keys where appropriate.

The database should support SQL questions such as:

```text
How many patients are registered?

How many appointments happened last month?

Which department has the most appointments?

Which doctors belong to Cardiology?

What is the average treatment cost?

What is the cancellation rate?
```

Do not invent database fields that do not exist in the actual dataset unless the schema is intentionally extended.

---

# 14. Hospital Documents

Hospital documents contain unstructured information such as:

- Visiting hours
- Hospital rules
- Patient rights
- Emergency procedures
- Department information
- Hospital policies
- General hospital information

These documents should be stored in:

```text
data/hospital/
```

They are processed by `vector_db.py` and stored in Pinecone.

---

# 15. Two Different Types of Knowledge

The system has two fundamentally different information sources.

## Structured knowledge

Stored in:

```text
Supabase PostgreSQL
```

Examples:

```text
patients
doctors
appointments
billing
treatments
```

Used for:

- Counting
- Filtering
- Aggregation
- Relationships
- Statistics
- Trends
- Numerical questions

---

## Unstructured knowledge

Stored in:

```text
Pinecone
```

Examples:

```text
hospital policies
rules
visiting hours
department descriptions
patient information
```

Used for:

- Semantic search
- Document retrieval
- Policy questions
- Information contained in PDFs/DOCX files

---

# 16. Agent Tool Selection

The agent should choose tools according to the user's intent.

Examples:

### Document question

```text
"What are the hospital visiting hours?"
```

Use:

```text
RAG Tool
 ↓
Pinecone
```

---

### SQL question

```text
"How many appointments did Cardiology have last month?"
```

Use:

```text
SQL Tool
 ↓
Supabase
```

---

### Analytics question

```text
"Show appointment trends over the last six months."
```

Use:

```text
SQL Tool
 ↓
Supabase
 ↓
Analytics Tool
 ↓
Visualization
```

---

### Combined question

```text
"Which doctors work in Cardiology and what are the visiting hours?"
```

Use:

```text
SQL Tool
     ↓
Supabase

RAG Tool
     ↓
Pinecone

Both results
     ↓
Gemini
     ↓
Final answer
```

---

# 17. AI-Driven Dashboard

The dashboard is NOT supposed to be a collection of permanently hardcoded charts.

The main concept is:

> **The user asks the AI what they want to analyze, and the system produces the relevant analytical result and visualization.**

Example:

```text
User:
"Analyze appointment cancellations over the last 6 months."
```

System:

```text
agent.py
   ↓
SQL Tool
   ↓
Supabase
   ↓
analytics.py
   ↓
cancellation metrics
   ↓
Plotly chart
   ↓
Gemini explanation
   ↓
Streamlit dashboard
```

The UI may display:

```text
AI Analysis
────────────────────────

Cancellation rate increased
from 8% to 14.2%.

📊 Trend Chart

📌 KPIs
Total appointments
Cancelled appointments
Cancellation rate
```

The AI should receive structured metrics/data for reasoning.

Do NOT send screenshots of the dashboard to the AI as the normal architecture.

---

# 18. AI + Dashboard Principle

The dashboard exists because visualizations are useful for:

- Trends
- Comparisons
- Distributions
- KPIs
- Time series
- Department comparisons
- Operational analytics

The chatbot provides explanations.

The dashboard provides visual understanding.

They must work together.

Do NOT build:

```text
Static Dashboard + unrelated Chatbot
```

Prefer:

```text
AI Agent
   ↓
Data
   ↓
Analytics
   ↓
Visualization
   ↓
AI Explanation
   ↓
Integrated Streamlit Interface
```

---

# 19. Example End-to-End Request

User asks:

```text
"Analyze appointment cancellations and show me the trend."
```

Expected architecture:

```text
1. app.py
   receives the question

2. app.py
   sends question to agent.py

3. agent.py
   determines SQL + analytics are required

4. tools.py
   exposes the required tools

5. SQL Tool
   queries Supabase

6. Supabase
   returns appointment data

7. analytics.py
   calculates cancellation metrics

8. analytics.py / Plotly
   prepares visualization

9. agent.py / Gemini
   interprets the analytical results

10. app.py
    displays:
       - AI explanation
       - KPIs
       - chart
       - relevant table if useful
```

---

# 20. Example Multi-Tool Request

User:

```text
"Which doctors work in Cardiology and what are the hospital's visiting hours?"
```

Expected flow:

```text
app.py
 ↓
agent.py
 ↓
 ├── SQL Tool → Supabase
 │
 └── RAG Tool → Pinecone
 ↓
Gemini combines results
 ↓
app.py
 ↓
Answer
```

The agent should only use the tools necessary for the question.

---

# 21. Environment Variables

Secrets must be stored in `.env`.

Potential variables:

```text
GEMINI_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
SUPABASE_DATABASE_URL=
```

Never hardcode API keys, passwords, tokens, or database credentials.

Never commit `.env` to GitHub.

`.gitignore` should include:

```text
.env
.venv/
__pycache__/
.ipynb_checkpoints/
```

---

# 22. Dependencies

Potential technologies:

```text
Python
Streamlit
LangChain
Google Gemini
Pinecone
Supabase / PostgreSQL
Pandas
Plotly
python-dotenv
```

Only add dependencies that are actually required.

Keep `requirements.txt` synchronized with the implementation.

---

# 23. Coding Principles

When generating or modifying code:

1. Preserve the existing architecture.
2. Do not move logic randomly between files.
3. Keep responsibilities separated.
4. Avoid unnecessary abstractions.
5. Prefer simple, readable Python.
6. Reuse existing connections/configuration.
7. Do not duplicate API/database initialization.
8. Do not hardcode secrets.
9. Use clear function names.
10. Add comments only where they improve understanding.
11. Do not create unnecessary files.
12. Do not rewrite working code without a reason.
13. Follow the existing project style.
14. Check existing files before introducing new implementations.
15. If the actual dataset differs from the assumed structure, adapt the implementation to the real dataset.

---

# 24. Agent Safety and Reliability

The AI must not hallucinate database results or document content.

If the answer requires information from Supabase, Pinecone, or analytics, the appropriate tool should be used.

If the requested information cannot be found, the agent should clearly state that the available data does not contain enough information.

Do not invent:

- Patients
- Doctors
- Appointments
- Hospital rules
- Statistics
- Medical information
- Database values

The AI should distinguish between:

```text
retrieved facts
```

and:

```text
AI-generated explanation/interpretation
```

---

# 25. SQL Safety

The SQL layer should be implemented carefully.

The agent should not be given unrestricted ability to perform destructive operations.

Avoid allowing normal user requests to:

```text
DROP TABLE
DELETE data
UPDATE production records
ALTER database schema
```

The intended use is primarily:

```text
SELECT
JOIN
GROUP BY
WHERE
ORDER BY
aggregations
```

The database should be treated as a source of hospital information for the AI platform.

---

# 26. RAG Quality

RAG should retrieve relevant document sections rather than dumping entire documents into the model.

Metadata should help identify:

```text
source file
section
timestamp
```

The final answer should be based on retrieved content.

If relevant information cannot be retrieved, the model should not fabricate it.

---

# 27. Data Flow Summary

## Initial data preparation

```text
Kaggle CSV
   ↓
database_analysis.ipynb
   ↓
Pandas cleaning
   ↓
Validated/normalized data
   ↓
Supabase
```

## Document ingestion

```text
Hospital PDF/DOCX
   ↓
vector_db.py
   ↓
Text extraction
   ↓
Section splitting
   ↓
Embeddings
   ↓
Pinecone
```

## Runtime

```text
User
 ↓
app.py
 ↓
agent.py
 ↓
tools.py
 ↓
 ┌───────────────┬───────────────┬───────────────┐
 │               │               │
 ▼               ▼               ▼
SQL             RAG          Analytics
 │               │               │
 ▼               ▼               ▼
Supabase       Pinecone      Data/Plotly
 │               │               │
 └───────────────┴───────────────┘
                 ↓
              Gemini
                 ↓
        Answer + Visualization
                 ↓
              app.py
                 ↓
                User
```

---

# 28. Development Order

Build the project incrementally.

Recommended order:

### Phase 1 — Data

1. Obtain hospital CSV dataset.
2. Inspect it in `database_analysis.ipynb`.
3. Clean and validate it.
4. Design relational schema.
5. Create Supabase tables.
6. Load cleaned data.

### Phase 2 — Documents

7. Add hospital PDF/DOCX documents.
8. Implement `vector_db.py`.
9. Split documents into meaningful sections.
10. Generate embeddings.
11. Populate Pinecone.
12. Save vector IDs/source metadata.

### Phase 3 — Backend

13. Implement `sql_db.py`.
14. Implement RAG access.
15. Implement `analytics.py`.
16. Implement `tools.py`.
17. Implement `agent.py`.

### Phase 4 — UI

18. Implement Streamlit `app.py`.
19. Add chat interface.
20. Add AI responses.
21. Add tables.
22. Add AI-driven charts.
23. Add dashboard components.

### Phase 5 — Integration

24. Test SQL questions.
25. Test RAG questions.
26. Test analytics questions.
27. Test multi-tool questions.
28. Test AI-generated visualizations.
29. Improve prompts and error handling.
