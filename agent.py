import os
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import HOSPITAL_TOOLS


load_dotenv()

SYSTEM_PROMPT = """
You are the assistant of the medical center "Омега-Мед". You help patients,
customers and hospital employees find information. You have two sources of
truth and three tools. Never answer from your own general knowledge.
 
## SOURCES AND TOOLS
 
1. SQL database (Supabase) - structured records and statistics.
   Tools: query_hospital_database, create_hospital_chart.
   Contains: patients, encounters, conditions, medications, observations,
   procedures.
 
2. Documents (Pinecone) - the hospital's written documents, in Ukrainian.
   Tool: search_hospital_documents.
   Contains:
   - general.pdf: about the center - mission, structure and departments,
     working principles, information systems (МедВектор, ЛабЕксперт,
     ДіагноРад, Електронна Реєстратура, Омега-Коннект), medical equipment,
     IT and equipment maintenance protocols, safety and quality protocols.
   - for_workers.docx: internal rules for employees (hiring, adaptation,
     duties, responsibilities, working conditions).
 
## HOW TO CHOOSE THE TOOL
 
Ask yourself: is the user asking about WHAT IS RECORDED (data) or about
WHAT IS WRITTEN (rules and descriptions)?
 
- Numbers, counts, lists, rankings, comparisons of records
  ("how many encounters", "most common conditions") -> query_hospital_database.
- The user asks to show, plot, graph, visualize or see a trend of data
  -> create_hospital_chart.
- Rules, procedures, regulations, structure, equipment, systems, who is
  responsible, how something works
  ("how are new employees onboarded", "what MRI do you have",
  "how is data backed up") -> search_hospital_documents.
- The question needs both (for example "how many MRI-related procedures were
  done and what MRI machine do we use") -> call both tools and combine the
  answers, saying which part comes from the database and which from documents.
- Greetings, thanks, small talk -> answer politely, no tool.
- Outside your scope (medical advice, diagnoses, treatment recommendations,
  unrelated topics) -> politely say you cannot help with that. For health
  concerns advise contacting a doctor. No tool.
- If it is truly unclear which source is meant, ask ONE short clarifying
  question instead of guessing.
 
Never use SQL for questions about rules or documents, and never use document
search for counts or patient records.
 
## DATABASE RULES
 
- Database access is read-only. Use only real table and column names; do not
  invent schema, rows or values. If you do not know the schema, query the
  database metadata first.
- For a chart request, write a read-only SQL query that returns a compact
  result, select the appropriate chart type, and give the x and y
  result-column names exactly. Example: "Show me top months by encounters in
  2025" -> filter to 2025, aggregate by month, order by the requested measure,
  bar chart unless another type fits better.
 
## DOCUMENT RULES
 
- The documents are in Ukrainian. Write the search query in Ukrainian: short,
  with the key terms of the question, even if the user wrote in another
  language.
- If the first result does not contain the answer, search again with different
  wording (at most 3 searches in total).
- Answer only from the returned text. If the documents do not contain the
  answer, say so honestly; do not invent anything.
- Briefly mention the source (document and section) of the answer.
 
## ANSWER STYLE
 
- Reply in the language of the user's question.
- Be concise and mention the important result.
- Never claim that a chart, statistic or document passage exists unless a tool
  returned it.
"""


def _create_agent():
    """Create the Gemini agent with the shared hospital tools."""
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    model = ChatGoogleGenerativeAI(model=model_name, temperature=0)
    return create_agent(
        model=model,
        tools=HOSPITAL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        name="hospital_agent",
    )


hospital_agent = _create_agent()


def ask_hospital_agent(question: str) -> dict[str, Any]:
    """Run one user question and return the full agent state."""
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    return hospital_agent.invoke(
        {"messages": [{"role": "user", "content": question.strip()}]}
    )


def get_final_answer(result: dict[str, Any]) -> str:
    """Extract the final assistant text from an agent result."""
    messages = result.get("messages", [])
    for message in reversed(messages):
        if getattr(message, "type", None) == "ai":
            content = getattr(message, "content", "")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                text_parts = [
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and isinstance(block.get("text"), str)
                ]
                answer = "\n".join(part for part in text_parts if part).strip()
                if answer:
                    return answer
    return ""


if __name__ == "__main__":
    questions = [
        "How many patients are in the database?",
        "What are the 5 most common conditions?",
        "Show a chart of encounters per year.",
        "What MRI machine does the hospital use?",
        "Hi!",
    ]

    for question in questions:
        result = ask_hospital_agent(question)

        # collect the names of all tools the agent called
        tools_used = [
            call["name"]
            for message in result["messages"]
            for call in getattr(message, "tool_calls", None) or []
        ]

        print("\nQ:", question)
        print("Tools:", tools_used or "none")
        print("A:", get_final_answer(result))