"""Decision Support — Agent with Wikipedia Tool."""

import asyncio
import os

import streamlit as st
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
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

    advisor = AssistantAgent(
        "Advisor",
        model_client=client,
        tools=[wiki_tool],
        system_message=(
            "You help people make decisions. First, use the search_wikipedia tool "
            "to research relevant facts. Then give a balanced, actionable "
            "recommendation in 2-3 short paragraphs grounded in what you found."
        ),
        reflect_on_tool_use=True,
    )

    async def run():
        with st.chat_message("user"):
            st.markdown(question)
        result = await advisor.run(task=question)
        for msg in result.messages:
            if isinstance(msg, TextMessage) and msg.source != "user":
                display_message(msg.source, msg.content)

    asyncio.run(run())
