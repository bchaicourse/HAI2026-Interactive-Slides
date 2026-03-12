import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Handoff
from autogen_agentchat.messages import TextMessage, HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.conditions import HandoffTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()


async def main():
    client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        parallel_tool_calls=False,
    )

    researcher = AssistantAgent(
        "Researcher",
        model_client=client,
        handoffs=[
            Handoff(target="Writer",
                    description="After researching, hand off to Writer"),
        ],
        system_message="""\
You are a Researcher. Gather 3 key facts about the topic in bullet points.
Then hand off to Writer.""",
    )

    writer = AssistantAgent(
        "Writer",
        model_client=client,
        handoffs=[
            Handoff(target="user",
                    description="After writing, return to user"),
        ],
        system_message="""\
You are a Writer. Take the Researcher's facts and write a short paragraph.
Then hand off to user.""",
    )

    team = Swarm(
        [researcher, writer],
        termination_condition=HandoffTermination(target="user"),
        max_turns=10,
    )

    async for msg in team.run_stream(task="Tell me about the history of coffee."):
        if isinstance(msg, TextMessage) and msg.source != "user":
            print(f"[{msg.source}] {msg.content}")
            print()
        elif isinstance(msg, HandoffMessage) and msg.target != "user":
            print(f"[{msg.source}] *Handing off to {msg.target}...*")
            print()


asyncio.run(main())
