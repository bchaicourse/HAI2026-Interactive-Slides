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


def run_and_display(team, question):
    """Run the pipeline and render messages as they arrive."""
    with st.chat_message("user"):
        st.markdown(question)

    async def _run():
        async for msg in team.run_stream(task=question):
            if isinstance(msg, TextMessage) and msg.source != "user":
                _show_message(msg.source, msg.content)
            elif isinstance(msg, ToolCallSummaryMessage):
                _show_message(msg.source, msg.content)
            elif isinstance(msg, HandoffMessage) and msg.target != "user":
                _show_message(msg.source, f"*Handing off to {msg.target}...*")

    asyncio.run(_run())
