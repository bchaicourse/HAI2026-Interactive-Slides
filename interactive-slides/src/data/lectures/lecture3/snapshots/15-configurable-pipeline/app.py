"""Decision Support System — Configurable Multi-Agent Pipeline (AutoGen)."""

import uuid

import streamlit as st
from dotenv import load_dotenv

import tab_agents
import tab_pipeline
from builder import build_pipeline
from defaults import DEFAULT_AGENTS, DEFAULT_PIPELINE
from display import run_and_display

load_dotenv()

st.set_page_config(page_title="Decision Support", layout="wide")
st.title("Decision Support System")
st.caption(
    "Define your own agents, assemble them into a team pipeline, "
    "and get multi-perspective advice on any decision."
)

# ── Session State ──

if "agents" not in st.session_state:
    st.session_state.agents = [
        {**a, "id": str(uuid.uuid4())} for a in DEFAULT_AGENTS
    ]

if "pipeline" not in st.session_state:
    st.session_state.pipeline = [
        {**s, "id": str(uuid.uuid4())} for s in DEFAULT_PIPELINE
    ]

# ── Tabs ──

t_agents, t_pipeline, t_run = st.tabs(
    ["1. Define Agents", "2. Build Pipeline", "3. Run"]
)

tab_agents.render(t_agents)
tab_pipeline.render(t_pipeline)

# ── Tab 3: Run ──

with t_run:
    summary = "  ->  ".join(
        s.get("agent_name") or s.get("team_name", "?")
        for s in st.session_state.pipeline
    )
    st.markdown(f"**Pipeline:** {summary}")

    question = st.text_area(
        "What decision are you facing?",
        value=(
            "I have two weeks of vacation saved up and can't decide how to spend it. "
            "Part of me wants to solo backpack through Southeast Asia, "
            "but I also feel like I should use the time to finally learn to cook properly. "
            "How should I spend my precious time off?"
        ),
        height=120,
    )

    if st.button("Get Decision Support", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                with st.spinner("Building pipeline..."):
                    team, _ = build_pipeline(
                        st.session_state.agents,
                        st.session_state.pipeline,
                    )
                run_and_display(team, question)
            except Exception as e:
                st.error(f"Error: {e}")
                import traceback
                st.code(traceback.format_exc())
