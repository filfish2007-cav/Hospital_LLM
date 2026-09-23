# 🏥 Hospital AI Intelligence Platform

> **An AI-first hospital analytics platform that connects structured hospital data, unstructured documents, and interactive analytics through a single intelligent interface.**

The **Hospital AI Intelligence Platform** combines **Gemini, LangChain, Supabase PostgreSQL, Pinecone, Pandas, Plotly, and Streamlit** to create an AI system capable of answering questions, retrieving hospital information, analyzing operational data, and generating visual insights.

Instead of building a chatbot and a separate static dashboard, this project puts **AI at the center of the entire experience**.

---

## ✨ What Can It Do?

The platform can work with two different types of hospital knowledge:

### 📊 Structured Data

Stored in **Supabase PostgreSQL**:

- Patients
- Doctors
- Departments
- Appointments
- Treatments
- Billing
- Other relational hospital data

This allows the AI to answer questions such as:

> "How many appointments did Cardiology have last month?"

> "Which department has the most appointments?"

> "Show the appointment trend over the last six months."

---

### 📄 Unstructured Documents

Stored in **Pinecone** through a RAG pipeline:

- Hospital rules
- Visiting hours
- Patient information
- Department information
- Hospital policies
- Other PDF/DOCX documents

This allows questions such as:

> "What are the hospital visiting hours?"

> "What are the patient visiting rules?"

---

### 🤖 AI-Driven Analytics

The AI can combine database queries with analytics and visualization.

For example:

> **"Analyze appointment cancellations over the last six months and show me the trend."**

The system can:

1. Query the hospital database
2. Calculate relevant metrics
3. Generate a visualization
4. Explain the results in natural language
5. Display everything inside the Streamlit interface

---

## 🧠 Architecture

The platform follows an **AI-first architecture**:

```text
                         USER
                           │
                           ▼
                     ┌──────────┐
                     │ Streamlit│
                     │  app.py  │
                     └────┬─────┘
                          │
                          ▼
                    ┌───────────┐
                    │ Gemini AI │
                    │ agent.py  │
                    └─────┬─────┘
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          SQL Tool     RAG Tool    Analytics Tool
             │            │            │
             ▼            ▼            ▼
         Supabase      Pinecone    Pandas/Plotly
         PostgreSQL    Vector DB      Analytics
             │            │            │
             └────────────┼────────────┘
                          ▼
                    AI Interpretation
                          │
                    ┌─────┴─────┐
                    ▼           ▼
                 Answer     Visualization
                    │           │
                    └─────┬─────┘
                          ▼
                    Streamlit UI
```

The AI agent decides which tools are necessary for each request.

---

## 🔍 Example Interactions

| User request | System |
|---|---|
| "What are the visiting hours?" | Pinecone RAG |
| "How many Cardiology appointments were there?" | SQL + Supabase |
| "Show appointment trends." | SQL + Analytics + Plotly |
| "Which doctors work in Cardiology and what are the visiting hours?" | SQL + RAG |
| "Analyze cancellation rates." | SQL + Analytics + AI explanation |

This allows the same interface to handle **information retrieval, database questions, and analytical requests**.

---

## 🏗️ Project Structure

```text
hospital-ai/
│
├── app.py                       # Streamlit application
├── agent.py                     # Gemini/LangChain AI agent
├── tools.py                     # Tools available to the agent
├── sql_db.py                    # Supabase/PostgreSQL connection
├── vector_db.py                 # Pinecone document ingestion
├── analytics.py                 # Runtime analytics & visualizations
│
├── database_analysis.ipynb      # Data cleaning & exploratory analysis
│
├── data/
│   ├── hospital/               # Hospital documents
│   └── csv/                    # Structured hospital datasets
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
User interface and dashboard.

**`agent.py`**  
Central AI orchestration and tool selection.

**`tools.py`**  
Connects the AI agent to SQL, RAG, and analytics capabilities.

**`sql_db.py`**  
Provides access to the Supabase PostgreSQL database.

**`vector_db.py`**  
Processes hospital documents and populates Pinecone.

**`analytics.py`**  
Performs analytical calculations and prepares visualizations.

**`database_analysis.ipynb`**  
Cleans, validates, and explores the original datasets.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core application |
| **Google Gemini** | AI reasoning and natural-language responses |
| **LangChain** | Agent and tool orchestration |
| **Supabase / PostgreSQL** | Structured hospital data |
| **Pinecone** | Vector database for hospital documents |
| **Pandas** | Data cleaning and analysis |
| **Plotly** | Interactive visualizations |
| **Streamlit** | Web interface and dashboard |

---

## 🔄 Data Pipeline

### Structured Data

```text
CSV Dataset
     ↓
Pandas
     ↓
Cleaning & Validation
     ↓
database_analysis.ipynb
     ↓
Supabase PostgreSQL
     ↓
SQL Tool
     ↓
Gemini Agent
```

### Hospital Documents

```text
PDF / DOCX
     ↓
vector_db.py
     ↓
Text Extraction
     ↓
Section Splitting
     ↓
Embeddings
     ↓
Pinecone
     ↓
RAG Tool
     ↓
Gemini Agent
```

---

## 📈 AI-Driven Dashboard

The dashboard is designed around the user's question rather than a collection of predefined charts.

For example:

```text
User:
"Analyze appointment cancellations over the last 6 months."
```

The system can produce:

```text
┌─────────────────────────────────────┐
│ 🤖 AI Analysis                      │
│                                     │
│ Cancellation rates increased over   │
│ the selected period...              │
├─────────────────────────────────────┤
│ 📈 Cancellation Trend               │
│                                     │
│          [Interactive Chart]        │
│                                     │
├─────────────────────────────────────┤
│ KPIs                                │
│                                     │
│ Total Appointments     3,430       │
│ Cancelled              382         │
│ Cancellation Rate      11.1%       │
└─────────────────────────────────────┘
```

The visualization is therefore part of the **AI workflow**, rather than a separate static analytics page.

---

## 🔐 Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name
SUPABASE_DATABASE_URL=your_database_url
```

> **Never commit `.env` or API keys to GitHub.**

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd hospital_docs-ai
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

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

Create `.env` and add the required API keys and database connection.

### 5. Prepare the databases

Before running the application:

- Clean and validate the structured dataset
- Populate the Supabase PostgreSQL database
- Process hospital documents
- Populate the Pinecone vector database

### 6. Run the application

```bash
streamlit run app.py
```

---

## 🧪 Example Questions

Once the application is running, try:

### Hospital information

> What are the hospital visiting hours?

### Database

> How many appointments were scheduled last month?

### Comparison

> Compare appointment volumes between Cardiology and Neurology.

### Analytics

> Show the appointment trend for the last six months.

### Combined knowledge

> Which doctors work in Cardiology and what are the visiting rules?

### Deeper analysis

> Analyze appointment cancellations and explain the trend.

---

## 🎯 Design Goals

The project focuses on several practical AI engineering concepts:

- **Retrieval-Augmented Generation (RAG)**
- **Tool-using AI agents**
- **Natural-language SQL**
- **Relational database design**
- **Data cleaning and validation**
- **Exploratory data analysis**
- **AI-driven analytics**
- **Interactive data visualization**
- **Modular software architecture**
- **LLM + external data integration**

The goal is not simply to build a chatbot, but to demonstrate how an LLM can act as an **interface to multiple information and analytics systems**.

---

## 🔒 Security & Reliability

The platform is designed with several basic safeguards:

- API keys stored outside source code
- `.env` excluded from version control
- Structured data separated from document knowledge
- Database operations separated from the UI
- AI responses grounded in retrieved information
- Analytics based on actual database results
- No intentional modification of production data through normal user queries

The AI should not invent hospital statistics or policies when the required information is unavailable.

---

## 🚧 Project Status

This project is being developed as an **AI engineering and analytics project**, with the architecture designed to support incremental development.

Current development priorities:

- [ ] Prepare and clean hospital datasets
- [ ] Build Supabase relational database
- [ ] Implement Pinecone document ingestion
- [ ] Implement RAG search
- [ ] Implement SQL agent tool
- [ ] Implement analytics layer
- [ ] Integrate Gemini agent
- [ ] Build Streamlit interface
- [ ] Add AI-driven visualizations
- [ ] Test multi-tool queries
- [ ] Deploy the application

---

## 💡 Why This Architecture?

This project uses:

```text
                 AI Agent
                /   |   \
              SQL  RAG  Analytics
                \   |   /
                 Streamlit
```

The AI becomes the **orchestration layer** connecting hospital data, documents, analytics, and visualization.

This makes the platform capable of moving from:

**Question → Data → Analysis → Visualization → Explanation**

within a single user interaction.

---

## 📌 Project Goal

The long-term goal is to create a unified hospital intelligence interface where users can interact with hospital information using natural language instead of manually searching documents, writing SQL queries, or building charts themselves.

> **Ask the question. Let the AI find the data, analyze it, visualize it, and explain it.**

---

### Author

**Filip Rybkin**

AI / Data / Software Engineering Project