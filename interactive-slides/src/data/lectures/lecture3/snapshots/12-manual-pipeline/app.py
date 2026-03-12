"""Decision Support — Sequential Pipeline."""

import asyncio
import os

import streamlit as st
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient

from display import display_message
from wiki_tool import search_wikipedia

load_dotenv()

st.set_page_config(page_title="Decision Support", layout="wide")
st.title("Decision Support System")

question = st.text_area(
    "What decision are you facing?",
    value=(
        "I have two weeks of vacation saved up and can't decide how to spend it. "
        "Part of me wants to solo backpack through Southeast Asia, "
        "but I also feel like I should use the time to finally learn to cook properly."
    ),
    height=120,
)

if st.button("Get Advice", type="primary", use_container_width=True):
    client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    wiki_tool = FunctionTool(
        search_wikipedia,
        description="Search Wikipedia for factual information about any topic.",
    )

    clarifier = AssistantAgent(
        "Clarifier",
        model_client=client,
        system_message=(
            "You take a vague decision and reframe it into a clear problem statement.\n\n"
            "1. Identify the core dilemma.\n"
            "2. List 2-3 key constraints (time, money, relationships, etc.).\n\n"
            "Keep it brief. Do NOT suggest solutions."
        ),
    )

    researcher = AssistantAgent(
        "Researcher",
        model_client=client,
        tools=[wiki_tool],
        system_message=(
            "You research relevant facts to inform the decision. "
            "Use the search_wikipedia tool to look up topics. "
            "Only report what you learned from the tool, nothing else. "
            "Keep it to 3-5 short bullet points."
        ),
        reflect_on_tool_use=True,
    )

    advisor = AssistantAgent(
        "Advisor",
        model_client=client,
        system_message=(
            "Read all previous context and give a final 2-3 sentence recommendation. "
            "Be decisive and actionable."
        ),
    )

    team = RoundRobinGroupChat(
        [clarifier, researcher, advisor],
        max_turns=3,
    )

    async def run():
        with st.chat_message("user"):
            st.markdown(question)
        async for msg in team.run_stream(task=question):
            if isinstance(msg, TextMessage) and msg.source != "user":
                display_message(msg.source, msg.content)

    asyncio.run(run())
