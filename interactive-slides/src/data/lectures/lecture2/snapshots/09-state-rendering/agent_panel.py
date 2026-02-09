import streamlit as st
import json
from pydantic import BaseModel, Field
from typing import Optional
from movie_tool import get_tools, query_movie_db


# ── State ──

DEFAULT_STATE = {
    "agent_phase": "idle",
    "agent_events": [],
    "agent_messages": [],
    "agent_tools": [],
    "agent_df": None,
}

def get_state(key):
    return st.session_state.get(key, DEFAULT_STATE[key])

def set_state(key, value):
    st.session_state[key] = value

def restart_agent(user_question, filtered_df):
    set_state("agent_phase", "thinking")
    set_state("agent_events", [])
    set_state("agent_messages", [
        {"role": "system", "content": "You are a data analyst with access to a tool that executes Python code on a movie database."},
        {"role": "user", "content": user_question},
    ])
    set_state("agent_tools", get_tools(filtered_df))
    set_state("agent_df", filtered_df)


# ── Logic ──

def run_step(client):
    phase = get_state("agent_phase")
    messages = get_state("agent_messages")

    if phase == "thinking":
        class Reasoning(BaseModel):
            reason: str = Field(description="Your reasoning about what you know so far and what to do next")
            use_tool: bool = Field(description="True if you need to run code, False if you can give the final answer")
            answer: Optional[str] = Field(default=None, description="Your final answer in one short paragraph. Only provide when use_tool is False.")

        response = client.chat.completions.parse(
            model="gpt-4o-mini", messages=messages, response_format=Reasoning,
        )
        reasoning = response.choices[0].message.parsed
        messages.append({"role": "assistant", "content": reasoning.reason})

        if reasoning.use_tool:
            get_state("agent_events").append({"type": "thought", "thought": reasoning.reason})
            set_state("agent_phase", "acting")
        else:
            get_state("agent_events").append({"type": "answer", "thought": reasoning.reason, "answer": reasoning.answer})
            set_state("agent_phase", "done")

    elif phase == "acting":
        tools = get_state("agent_tools")
        df = get_state("agent_df")

        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=tools, parallel_tool_calls=False,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            set_state("agent_phase", "done")
            return

        messages.append(msg)
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            result = query_movie_db(args["code"], df)
            messages.append({"role": "tool", "content": result, "tool_call_id": tc.id})
            get_state("agent_events").append({
                "type": "action", "name": tc.function.name,
                "code": args["code"], "result": result,
            })

        set_state("agent_phase", "thinking")


# ── Rendering ──

def render_events():
    for event in get_state("agent_events"):
        if event["type"] == "thought":
            st.markdown(f"**Thought:** {event['thought']}")
        elif event["type"] == "action":
            st.markdown(f"**Action:** `{event['name']}`")
            st.code(event["code"], language="python")
            st.markdown("**Observation:**")
            st.code(event["result"], language="text")
            st.divider()
        elif event["type"] == "answer":
            st.markdown(f"**Thought:** {event['thought']}")

def render_panel():
    st.subheader("Analysis Results")
    container = st.container(height=600)
    with container:
        phase = get_state("agent_phase")

        if phase == "idle":
            st.info("Enter a question and click 'Analyze' to see results.")

        elif phase in ("thinking", "acting"):
            with st.expander("Agent Reasoning Trace", expanded=True):
                render_events()
            st.spinner("Agent is thinking...")

        elif phase == "done":
            with st.expander("Agent Reasoning Trace", expanded=False):
                render_events()
            events = get_state("agent_events")
            if events and events[-1].get("answer"):
                st.write("**Answer:**")
                st.write(events[-1]["answer"])


# ── Lifecycle ──

def agent_panel(client, analyze_button, user_question, filtered_df):
    # Phases: idle -> thinking <-> acting -> done
    if analyze_button and user_question:
        restart_agent(user_question, filtered_df)

    render_panel()

    if get_state("agent_phase") in ("thinking", "acting"):
        run_step(client)
        st.rerun()
