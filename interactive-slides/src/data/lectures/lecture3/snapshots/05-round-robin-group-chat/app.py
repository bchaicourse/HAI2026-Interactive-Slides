import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
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

    optimist = AssistantAgent(
        "Optimist",
        model_client=client,
        system_message="""\
You are part of a two-agent debate. You always see the bright side.
Keep each response to 1-2 sentences. Be concise and direct.
After hearing Pessimist at least twice, say DONE to end the conversation.""",
    )

    pessimist = AssistantAgent(
        "Pessimist",
        model_client=client,
        system_message="""\
You are part of a two-agent debate. You always see the risks and downsides.
Keep each response to 1-2 sentences. Be concise and direct.
Do NOT say DONE yourself — only Optimist ends the conversation.""",
    )

    team = RoundRobinGroupChat(
        [optimist, pessimist],
        termination_condition=TextMentionTermination("DONE"),
        max_turns=10,
    )

    async for msg in team.run_stream(
        task="I'm thinking about quitting my job to start a bakery."
    ):
        if isinstance(msg, TextMessage) and msg.source != "user":
            print(f"[{msg.source}] {msg.content}")
            print()


asyncio.run(main())
