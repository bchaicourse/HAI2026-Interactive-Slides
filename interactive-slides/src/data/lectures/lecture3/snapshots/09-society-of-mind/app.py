import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent, SocietyOfMindAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()


async def main():
    client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # Inner team: Optimist and Pessimist debate
    optimist = AssistantAgent(
        "Optimist",
        model_client=client,
        system_message="""\
You always see the bright side. Keep to 1-2 sentences.
After hearing Pessimist at least once, synthesize and say DONE.""",
    )

    pessimist = AssistantAgent(
        "Pessimist",
        model_client=client,
        system_message="""\
You always see the risks. Keep to 1-2 sentences.
Do NOT say DONE yourself.""",
    )

    debate = RoundRobinGroupChat(
        [optimist, pessimist],
        termination_condition=TextMentionTermination("DONE"),
        max_turns=6,
    )

    debate_team = SocietyOfMindAgent(
        "Debate_Team",
        team=debate,
        model_client=client,
        description="A team that debates pros and cons",
    )

    # Outer team: Debate_Team → Summarizer
    summarizer = AssistantAgent(
        "Summarizer",
        model_client=client,
        system_message="Read the debate summary and give a final 2-3 sentence recommendation.",
    )

    outer = RoundRobinGroupChat(
        [debate_team, summarizer],
        max_turns=2,
    )

    async for msg in outer.run_stream(
        task="I'm thinking about quitting my job to start a bakery."
    ):
        if isinstance(msg, TextMessage) and msg.source != "user":
            print(f"[{msg.source}] {msg.content}")
            print()


asyncio.run(main())
