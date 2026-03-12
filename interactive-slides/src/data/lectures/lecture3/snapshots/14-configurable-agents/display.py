"""Display helper for agent messages in Streamlit."""

import hashlib

import streamlit as st

_COLORS = [
    "#4A90D9", "#D94A7A", "#50B86C", "#D9A24A",
    "#9B59B6", "#1ABC9C", "#E67E22", "#3498DB",
]


def _agent_color(name):
    idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(_COLORS)
    return _COLORS[idx]


def display_message(source, text):
    """Render a single agent message as a chat bubble."""
    with st.chat_message("assistant"):
        color = _agent_color(source)
        st.markdown(
            f'<span style="color:{color};font-weight:700">'
            f'{source.replace("_", " ")}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(text)
