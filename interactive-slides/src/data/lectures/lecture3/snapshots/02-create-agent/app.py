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

    agent = AssistantAgent(
        "TechExplainer",
        model_client=client,
        system_message="You are an expert at explaining technical concepts in simple terms. Keep answers to 2-3 sentences.",
    )

    result = await agent.run(task="What is a multi-agent system?")

    print("=== All Messages ===")
    for msg in result.messages:
        print(msg)

    print("\n=== Final Answer ===")
    final_answer = result.messages[-1].content
    print(final_answer)


asyncio.run(main())
