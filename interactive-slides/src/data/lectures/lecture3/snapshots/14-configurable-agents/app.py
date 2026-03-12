"""Decision Support — Configurable Agents."""

import asyncio
import os
import uuid

import streamlit as st
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent, SocietyOfMindAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient

import tab_agents
from defaults import DEFAULT_AGENTS
from display import display_message
from wiki_tool import search_wikipedia

load_dotenv()

st.set_page_config(page_title="Decision Support", layout="wide")
st.title("Decision Support System")
st.caption(
    "Define your own agents, then run them in a fixed pipeline: "
    "Clarifier → Researcher → Debate_Team → Advisor."
)

# ── Session State ──

if "agents" not in st.session_state:
    st.session_state.agents = [
        {**a, "id": str(uuid.uuid4())} for a in DEFAULT_AGENTS
    ]

# ── Tabs ──

t_agents, t_run = st.tabs(["1. Define Agents", "2. Run"])

tab_agents.render(t_agents)

# ── Run Tab ──

with t_run:
    question = st.text_area(
        "What decision are you facing?",
        value=(
            "I have two weeks of vacation saved up and can't decide how to spend it. "
            "Part of me wants to solo backpack through Southeast Asia, "
            "but I also feel like I should use the time to finally learn to cook properly."
        ),
        height=120,
    )

    if st.button("Get Decision Support", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                client = OpenAIChatCompletionClient(
                    model="gpt-4o-mini",
                    api_key=os.getenv("OPENAI_API_KEY"),
                )
                wiki_tool = FunctionTool(
                    search_wikipedia,
                    description="Search Wikipedia for factual information.",
                )

                # Build agents from session state
                agents = {}
                for cfg in st.session_state.agents:
                    kwargs = {}
                    if cfg.get("has_wiki_tool"):
                        kwargs["tools"] = [wiki_tool]
                        kwargs["reflect_on_tool_use"] = True
                    if cfg.get("description"):
                        kwargs["description"] = cfg["description"]
                    agents[cfg["name"]] = AssistantAgent(
                        cfg["name"],
                        model_client=client,
                        system_message=cfg.get("system_message", ""),
                        **kwargs,
                    )

                # Fixed pipeline: Clarifier → Researcher → Debate_Team → Advisor
                debate = RoundRobinGroupChat(
                    [agents["Optimist"], agents["Pessimist"]],
                    max_turns=4,
                )
                debate_team = SocietyOfMindAgent(
                    "Debate_Team",
                    team=debate,
                    model_client=client,
                    description="Debates pros and cons",
                )

                team = RoundRobinGroupChat(
                    [agents["Clarifier"], agents["Researcher"], debate_team, agents["Advisor"]],
                    max_turns=4,
                )

                async def run():
                    with st.chat_message("user"):
                        st.markdown(question)
                    async for msg in team.run_stream(task=question):
                        if isinstance(msg, TextMessage) and msg.source != "user":
                            display_message(msg.source, msg.content)

                asyncio.run(run())
            except KeyError as e:
                st.error(f"Missing agent: {e}. The fixed pipeline requires agents named Clarifier, Researcher, Optimist, Pessimist, and Advisor.")
            except Exception as e:
                st.error(f"Error: {e}")
                import traceback
                st.code(traceback.format_exc())
