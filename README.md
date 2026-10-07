# 🏥 Hospital AI Assistant

**Ask a hospital's database and its documents in plain language. One agent, three tools, grounded answers.**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-agent-1C3C3C)
![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google&logoColor=white)
![Postgres](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white)
![Pinecone](https://img.shields.io/badge/Pinecone-vector%20DB-000000)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)

<!-- TODO: replace with a real GIF/screenshot -->
> **🔗 Live demo:** `https://hospitalllm-rcttxruzkbigz4dnmp5mbr.streamlit.app`
>
> ![demo](docs/demo.gif)

---

## The idea

A hospital keeps its knowledge in two very different places:

- **Records** (patients, visits, diagnoses, prescriptions) live in a relational database.
- **Rules and descriptions** (equipment, IT systems, safety protocols, employee handbook) live in PDFs and Word files.

People need both, and normally they need a different tool for each. This project puts a single chat in front of them. The LLM decides, per question, whether to **query the database**, **search the documents**, **draw a chart**, or **combine sources**. It answers only from what the tools return.

## Who is it for?

This is an **operational assistant for hospital staff and management**, not a clinical decision tool.

| Who | What they need | Where the answer comes from |
|---|---|---|
| **Managers & analysts** | Workload, trends, costs, case mix | Database + charts |
| **Clinicians & nurses** (lookup only) | A patient's recorded conditions, medications, procedures | Database |
| **New employees & HR** | Onboarding, working hours, leave, internal rules | Documents |
| **IT, facilities & quality teams** | Information systems, equipment, maintenance, safety protocols | Documents |

## What you can ask

Not sure where to start? Try any of these. You can ask in any language, and the agent picks the source itself.

### 📊 Management & analytics

| Question | Why someone asks it |
|---|---|
| *"How many encounters per month in 2023?"* (returns a line chart) | Staffing and capacity planning |
| *"Which encounter types are the most common?"* | Understanding the case mix: emergency vs. inpatient vs. outpatient |
| *"Average claim cost by encounter type"* | Budget and cost control |
| *"Top 10 most common conditions"* | Spotting what the hospital treats most |

### 🩺 Patient record lookup

| Question | Why someone asks it |
|---|---|
| *"What medications has patient X been prescribed?"* | Quick history check before a visit |
| *"Which procedures are recorded for patient X?"* | Reviewing past care |

### 📄 Staff & operations (from internal documents)

| Question | Why someone asks it |
|---|---|
| *"How does onboarding work for a new employee?"* | New hires find the rules without interrupting HR |
| *"How do I request leave?"* | Self-service for routine HR questions |
| *"What MRI equipment do we have and how is it maintained?"* | Facilities and equipment staff |
| *"What are the safety and quality protocols?"* | Compliance and audit preparation |

### 🔀 Both sources in one answer

*"How many MRI-related procedures were done, and what MRI machine do we use?"* The agent queries the database, searches the documents, and states which part of the answer came from where.

### 🚫 What it will not do

- **Medical advice.** Questions like *"Should I take ibuprofen?"* or *"How should I treat this patient?"* are politely declined with a pointer to a doctor. This is intentional: the assistant only reports what is recorded in the hospital's own data and documents, and it is not a validated clinical tool.
- **Anything outside its data.** If the database and documents don't contain the answer, it says so instead of guessing.
- **Changing data.** Access is read-only.

<!-- TODO: add 2-3 screenshots here -->

---

## How it works

```mermaid
flowchart TD
    U([User]) --> UI[Streamlit chat<br/>app.py]
    UI --> A{{Gemini agent<br/>LangChain · agent.py}}
    A -->|records & statistics| T1[query_hospital_database]
    A -->|trends & distributions| T2[create_hospital_chart]
    A -->|rules & descriptions| T3[search_hospital_documents]
    T1 --> DB[(Supabase<br/>PostgreSQL)]
    T2 --> DB
    T3 --> VDB[(Pinecone<br/>hospital docs)]
    DB --> A
    VDB --> A
    A --> UI
```

**The routing is done by the model, not by `if/else` keyword rules.** The system prompt teaches one distinction: *is the user asking about what is **recorded** (data) or what is **written** (rules)?* Guardrails in the prompt: no answers from general knowledge, at most 3 document searches per question, one clarifying question if the source is truly unclear, and no medical advice.

### The three tools

| Tool | Source | What it does |
|---|---|---|
| `query_hospital_database` | Supabase PostgreSQL | Runs a validated, read-only SQL query and returns the rows |
| `create_hospital_chart` | Supabase PostgreSQL | Runs a read-only query and returns a Plotly figure (bar, line, pie, scatter, histogram) |
| `search_hospital_documents` | Pinecone | Semantic search over the documents (top 5 sections), returned with file and section name |

---

## Data

Everything in the repo is **synthetic**. No real patients.

**Structured data** is a [Synthea](https://github.com/synthetichealth/synthea)-style export: 6 tables (`patients`, `encounters`, `conditions`, `medications`, `observations`, `procedures`), roughly 160k rows in total, dominated by observations. The notebook [`DataCleaning_EDA.ipynb`](DataCleaning_EDA.ipynb) audits and cleans it: key and foreign-key checks, duplicate removal, date-order and code consistency, numeric sanity ranges, privacy review, and a focused EDA. Then it exports CSVs ready for Postgres.

### What is an "encounter"?

An **encounter** is one interaction between a patient and the healthcare system: a check-up, a clinic visit, an emergency call, a hospital stay. Every condition, medication, observation and procedure is linked to the encounter in which it was recorded. Encounters come in several classes:

| Class | Meaning |
|---|---|
| `wellness` | Preventive check-up |
| `ambulatory` | Scheduled outpatient visit |
| `outpatient` | Clinic visit |
| `urgentcare` | Walk-in urgent care |
| `emergency` | Emergency department or ambulance |
| `inpatient` | Hospital admission |
| `snf` | Skilled nursing facility stay |
| `hospice` | End-of-life care |

So "how many encounters per month" is a workload metric, and "emergency encounters" means emergency-class visits only.

**Documents** are two Ukrainian-language files for the fictional center "Омега-Мед":

- `general.pdf`: the center, its systems, equipment, maintenance, safety and quality (5 sections)
- `for_workers.docx`: the employee handbook, from hiring to termination (12 sections)

Documents are split by numbered section, embedded with `gemini-embedding-001`, and stored in a cosine-metric Pinecone index.

---

## Quickstart

**Prerequisites:** Python 3.11+, a [Gemini API key](https://aistudio.google.com/apikey), a [Pinecone](https://www.pinecone.io/) account, a [Supabase](https://supabase.com/) project.

```bash
git clone https://github.com/filfish2007-cav/Hospital_LLM.git
cd Hospital_LLM
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                # then fill in your keys
```

### 1. Prepare the database

1. Run `DataCleaning_EDA.ipynb` and export the cleaned CSVs.
2. In Supabase, create the six tables and import the CSVs (Table Editor → Import, or `\copy` via `psql`).
3. Create a **read-only role** for the app (see [Safety](#-safety)).

### 2. Index the documents

```bash
python vector_db.py
```

Creates the `hospital-docs` index if needed (3072 dimensions, cosine) and uploads the document sections. Run it once, not on every app start. Re-running adds duplicate vectors, so clear the index first if you re-ingest.

### 3. Run the app

```bash
streamlit run app.py
```

### Configuration

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Chat model and embeddings |
| `PINECONE_API_KEY` | Vector database |
| `SUPABASE_DATABASE_URL` | SQLAlchemy URL, e.g. `postgresql+psycopg2://user:pass@host:5432/postgres?sslmode=require` |
| `GEMINI_MODEL` | *(optional)* override the default chat model |

---

## ☁️ Deploy on Streamlit Community Cloud

1. Push the repo to GitHub.
2. On [share.streamlit.io](https://share.streamlit.io) choose **Create app**, pick this repo, branch `main`, file `app.py`.
3. Under **Advanced settings → Secrets**, paste the variables above as top-level TOML keys:

   ```toml
   GEMINI_API_KEY = "..."
   PINECONE_API_KEY = "..."
   SUPABASE_DATABASE_URL = "postgresql+psycopg2://..."
   ```
4. Use Supabase's **pooler** connection string, since Streamlit Cloud connects over IPv4.

Every `git push` to `main` redeploys the app automatically.

---

## 🔒 Safety

An agent that writes its own SQL is a risk surface, so there are several layers:

- **Query validation.** Only a single `SELECT`/`WITH` statement passes. Write/DDL keywords, comments and multiple statements are rejected before execution.
- **Read-only database role (recommended, required for a public deployment).** The validator is a second line of defense. The first should be the database itself:

  ```sql
  create role hospital_reader login password '<generated>';
  alter role hospital_reader set default_transaction_read_only = on;
  alter role hospital_reader set statement_timeout = '10s';
  grant usage on schema public to hospital_reader;
  grant select on public.encounters, public.conditions, public.medications,
                  public.observations, public.procedures to hospital_reader;
  -- patients: grant column-level access, excluding SSN / drivers / passport
  ```
- **Grounded answers.** The prompt forbids answers from the model's own knowledge. If the tools return nothing, the agent says so.
- **Scope limits.** Medical advice, diagnoses and off-topic requests are declined.
- **Secrets** stay in `.env` / Streamlit Secrets, never in git.

> The dataset is synthetic. A real deployment would also need authentication, audit logging and compliance work (GDPR/HIPAA).

---

## Project structure

```text
Hospital_LLM/
├── app.py                  # Streamlit chat UI: history, charts, tool badges
├── agent.py                # Gemini model, system prompt, agent assembly
├── tools.py                # The 3 tools + SQL validation
├── sql_db.py               # SQLAlchemy engine + LangChain SQLDatabase
├── vector_db.py            # One-off ingestion: docs → sections → embeddings → Pinecone
├── DataCleaning_EDA.ipynb  # Data audit, cleaning, EDA, CSV export
├── data/
│   ├── hospital_csvs/      # Structured data
│   └── hospital_docs/      # PDF/DOCX sources + ingested vector IDs
├── requirements.txt
└── .env.example
```

---

## Known limitations

- **Section-level chunking.** Each document section is one vector. Long sections dilute the embedding and cost more context tokens. Smaller overlapping chunks are the planned fix.
- **Ingestion is not idempotent.** Vector IDs are random, so re-running `vector_db.py` duplicates entries.
- **Text-to-SQL is probabilistic.** Complex joins can still go wrong, and there is no automated accuracy measurement yet.
- **Documents are Ukrainian only.** The agent translates the search query, which can lose precision.
- **No authentication or rate limiting** in the app itself.

## Roadmap

- [x] Data audit, cleaning and EDA notebook
- [x] Text-to-SQL tool with query validation
- [x] Chart generation tool (Plotly)
- [x] RAG over PDF/DOCX with Pinecone
- [x] Streamlit chat with history and tool badges
- [ ] Starter-question buttons in the UI so users can discover what the bot can do
- [ ] Evaluation set (tool routing + SQL correctness) with published scores
- [ ] Read-only DB role + enforced `LIMIT` on every query
- [ ] Overlapping chunks and idempotent ingestion
- [ ] Schema injection into the prompt, with few-shot SQL examples
- [ ] Response streaming and tracing (Langfuse / LangSmith)
- [ ] Tests and CI

---

## Author

**Filip Rybkin**, built as a hands-on project in LLM agents, RAG and natural-language SQL.
[LinkedIn](https://www.linkedin.com/in/YOUR-PROFILE) · [GitHub](https://github.com/filfish2007-cav)
