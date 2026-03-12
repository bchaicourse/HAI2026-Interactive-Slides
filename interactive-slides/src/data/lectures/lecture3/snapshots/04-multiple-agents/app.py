import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
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
        system_message=(
            "You always see the bright side. Give 2-3 bullet points on why "
            "this is a great idea. Be brief."
        ),
    )

    pessimist = AssistantAgent(
        "Pessimist",
        model_client=client,
        system_message=(
            "You always see the risks and downsides. Give 2-3 bullet points on "
            "what could go wrong. Be brief."
        ),
    )

    question = "I'm thinking about quitting my job to start a bakery."

    print("--- Optimist ---")
    result = await optimist.run(task=question)
    print(result.messages[-1].content)

    print()
    print("--- Pessimist ---")
    result = await pessimist.run(task=question)
    print(result.messages[-1].content)


asyncio.run(main())
