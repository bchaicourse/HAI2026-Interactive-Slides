"""Decision Support System — Presets + Configurable Pipeline (AutoGen)."""

import uuid

import streamlit as st
from dotenv import load_dotenv

import tab_agents
import tab_pipeline
from builder import build_pipeline
from defaults import PRESETS
from display import run_and_display

load_dotenv()

st.set_page_config(page_title="Decision Support", layout="wide")
st.title("Decision Support System")

# ── Preset Selector ──

st.caption("Load a preset to get started, then customize in the tabs below.")

preset_names = list(PRESETS.keys())
cols = st.columns(len(preset_names))
for i, name in enumerate(preset_names):
    preset = PRESETS[name]
    with cols[i]:
        if st.button(f"**{name}**", use_container_width=True, key=f"preset_{i}",
                      help=preset["description"]):
            st.session_state.agents = [
                {**a, "id": str(uuid.uuid4())} for a in preset["agents"]
            ]
            st.session_state.pipeline = [
                {**s, "id": str(uuid.uuid4())} for s in preset["pipeline"]
            ]
            st.rerun()

st.divider()

# ── Session State (default preset if not loaded) ──

if "agents" not in st.session_state:
    default = PRESETS[preset_names[0]]
    st.session_state.agents = [
        {**a, "id": str(uuid.uuid4())} for a in default["agents"]
    ]

if "pipeline" not in st.session_state:
    default = PRESETS[preset_names[0]]
    st.session_state.pipeline = [
        {**s, "id": str(uuid.uuid4())} for s in default["pipeline"]
    ]

# ── Tabs ──

t_agents, t_pipeline, t_run = st.tabs(
    ["1. Define Agents", "2. Build Pipeline", "3. Run"]
)

tab_agents.render(t_agents)
tab_pipeline.render(t_pipeline)

# ── Tab 3: Run ──

with t_run:
    summary = "  →  ".join(
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
