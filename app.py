import plotly.io as pio
import streamlit as st

# the agent is created in agent.py (it also loads the .env file)
from agent import hospital_agent, get_final_answer

# ---------------------------------------------------------
# page
# ---------------------------------------------------------
st.set_page_config(page_title="Омега-Мед assistant", page_icon="🏥")

st.title("🏥 Омега-Мед assistant")
st.caption(
    """
**💬 You can ask about:**

- Patients and visits
- Medications, diagnoses, and procedures
- Hospital statistics and data analysis
- Charts and visualizations
- Hospital policies and internal documents
- Equipment, departments, and information systems

⚠️ *This assistant does not provide medical diagnoses or treatment recommendations.*
"""
)

# ---------------------------------------------------------
# history of the chat (global memory in streamlit)
#
# every message is a dict:
# {"role": "user" / "assistant", "content": text,
#  "charts": [plotly json, ...], "tools": [tool names]}
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()


def show_message(message, index):
    """Draw one message: text, then charts, then the tools that were used."""
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # the chart tool returns a plotly figure as json -> turn it back into a figure
        for i, chart_json in enumerate(message.get("charts", [])):
            figure = pio.from_json(chart_json)
            st.plotly_chart(figure, key=f"chart_{index}_{i}")

        if message.get("tools"):
            st.caption("🔧 Tools used: " + ", ".join(message["tools"]))


# ---------------------------------------------------------
# show the old messages
# ---------------------------------------------------------
for index, message in enumerate(st.session_state.messages):
    show_message(message, index)

# ---------------------------------------------------------
# new message from the user
# ---------------------------------------------------------
user_text = st.chat_input("Ask the hospital assistant...")

if user_text:
    # add the question to the history and show it
    st.session_state.messages.append({"role": "user", "content": user_text})
    show_message(st.session_state.messages[-1], len(st.session_state.messages) - 1)

    # the agent gets only the text of the last 10 messages
    # (chart json is big, it would make the agent slow)
    agent_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[-10:]
    ]

    try:
        with st.spinner("Thinking..."):
            result = hospital_agent.invoke({"messages": agent_messages})
    except Exception as error:
        st.session_state.messages.pop()   # remove the question that failed
        st.error(f"Something went wrong: {error}")
        st.stop()

    # look through everything the agent did in this turn
    tools = []
    charts = []

    for msg in result["messages"]:
        # which tools were called
        for call in getattr(msg, "tool_calls", None) or []:
            tools.append(call["name"])

        # the result of the chart tool = plotly json (skip if the tool failed)
        if (
            msg.type == "tool"
            and msg.name == "create_hospital_chart"
            and getattr(msg, "status", None) != "error"
        ):
            charts.append(msg.content)

    answer = {
        "role": "assistant",
        "content": get_final_answer(result) or "Done.",
        "charts": charts,
        "tools": list(dict.fromkeys(tools)),   # remove repeats, keep the order
    }

    st.session_state.messages.append(answer)
    show_message(answer, len(st.session_state.messages) - 1)