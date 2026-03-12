import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


async def main():
    client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    multiply_tool = FunctionTool(multiply, description="Multiply two numbers")

    agent = AssistantAgent(
        "Calculator",
        model_client=client,
        tools=[multiply_tool],
        system_message="Use the provided tools to solve math problems.",
        reflect_on_tool_use=True,
    )

    result = await agent.run(task="What is 4839281574 * 7291048365?")
    for msg in result.messages:
        print(msg)


asyncio.run(main())
