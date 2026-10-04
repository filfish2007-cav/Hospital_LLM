import os
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import HOSPITAL_TOOLS


load_dotenv()

SYSTEM_PROMPT = """
You are the hospital data assistant. Answer only with facts supported by the
hospital Supabase database and the results returned by your tools.

Use query_hospital_database for ordinary structured-data questions, including
counts, filters, joins, rankings, and comparisons. Use
create_hospital_chart when the user asks to show, plot, graph, visualize, or
trend database data. For a chart request, write a read-only SQL query that
returns a compact result suitable for visualization, select the appropriate
chart type, and provide the x and y result-column names exactly.

For requests such as "Show me top months by encounters in 2025", filter the
query to 2025, aggregate by month, order by the requested measure, and use a
bar chart unless another chart type is more appropriate. Use the real table
and column names in the database; do not invent schema, rows, or values. If
you do not know the schema, query the database metadata first.

After a tool call, answer the user's question concisely and mention the
important result. Never claim that a chart or statistic exists unless the
tool returned data for it. Database access is read-only.
"""


def _create_agent():
    """Create the Gemini agent with the shared hospital tools."""
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
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


# if __name__ == "__main__":
#     example_questions = (
#         "How many encounters are recorded?",
#         "Show me top months by encounters in 2025.",
#         "Which conditions are most common?",
#     )
#
#     for example in example_questions:
#         print(f"\nUser: {example}")
#         result = ask_hospital_agent(example)
#         print(f"Assistant: {get_final_answer(result)}")