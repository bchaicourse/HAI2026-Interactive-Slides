import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()


async def main():
    client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    financial_advisor = AssistantAgent(
        "FinancialAdvisor",
        model_client=client,
        description="Expert in budgeting, savings, startup costs, and financial planning",
        system_message="""\
You are a financial advisor. Give practical money-related advice in 1-2 sentences.
Do NOT say DONE.""",
    )

    lifestyle_coach = AssistantAgent(
        "LifestyleCoach",
        model_client=client,
        description="Expert in work-life balance, personal fulfillment, and well-being",
        system_message="""\
You are a lifestyle coach. Give advice on personal fulfillment and well-being in 1-2 sentences.
Do NOT say DONE.""",
    )

    business_strategist = AssistantAgent(
        "BusinessStrategist",
        model_client=client,
        description="Expert in market analysis, competition, and business growth strategies",
        system_message="""\
You are a business strategist. Give advice on market positioning and growth in 1-2 sentences.
Do NOT say DONE.""",
    )

    summarizer = AssistantAgent(
        "Summarizer",
        model_client=client,
        description="Wraps up by synthesizing all expert advice into a final recommendation",
        system_message="""\
Synthesize all the expert advice into 2-3 sentences of actionable recommendation.
End with DONE.""",
    )

    team = SelectorGroupChat(
        [financial_advisor, lifestyle_coach, business_strategist, summarizer],
        model_client=client,
        termination_condition=TextMentionTermination("DONE"),
        max_turns=6,
    )

    async for msg in team.run_stream(
        task="I'm thinking about quitting my job to start a bakery."
    ):
        if isinstance(msg, TextMessage) and msg.source != "user":
            print(f"[{msg.source}] {msg.content}")
            print()


asyncio.run(main())
