"""Display helper for agent messages in Streamlit."""

import asyncio
import hashlib

import streamlit as st
from autogen_agentchat.messages import (
    HandoffMessage,
    TextMessage,
    ToolCallSummaryMessage,
)

_COLORS = [
    "#4A90D9", "#D94A7A", "#50B86C", "#D9A24A",
    "#9B59B6", "#1ABC9C", "#E67E22", "#3498DB",
]


def _agent_color(name):
    idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(_COLORS)
    return _COLORS[idx]


def _show_message(source, text):
    with st.chat_message("assistant"):
        color = _agent_color(source)
        st.markdown(
            f'<span style="color:{color};font-weight:700">'
            f'{source.replace("_", " ")}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(text)


def _build_transcript(question, history):
    """Build a plain-text transcript from the conversation history."""
    lines = ["Decision Support Report", "=" * 40, "", "Question:", question, ""]
    for source, text in history:
        lines.append(f"--- {source.replace('_', ' ')} ---")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def run_and_display(team, question):
    """Run the pipeline and render messages as they arrive."""
    with st.chat_message("user"):
        st.markdown(question)

    history = []

    async def _run():
        async for msg in team.run_stream(task=question):
            if isinstance(msg, TextMessage) and msg.source != "user":
                _show_message(msg.source, msg.content)
                history.append((msg.source, msg.content))
            elif isinstance(msg, ToolCallSummaryMessage):
                _show_message(msg.source, msg.content)
                history.append((msg.source, msg.content))
            elif isinstance(msg, HandoffMessage) and msg.target != "user":
                _show_message(msg.source, f"*Handing off to {msg.target}...*")
                history.append((msg.source, f"Handing off to {msg.target}..."))

    asyncio.run(_run())

    if history:
        st.session_state.run_question = question
        st.session_state.run_history = history
        transcript = _build_transcript(question, history)
        st.download_button(
            "Download Transcript",
            data=transcript,
            file_name="decision_support.txt",
            mime="text/plain",
        )


def show_previous_run():
    """Re-render a completed run from session state."""
    question = st.session_state.get("run_question")
    history = st.session_state.get("run_history")
    if not question or not history:
        return

    with st.chat_message("user"):
        st.markdown(question)
    for source, text in history:
        _show_message(source, text)

    transcript = _build_transcript(question, history)
    st.download_button(
        "Download Transcript",
        data=transcript,
        file_name="decision_support.txt",
        mime="text/plain",
    )
