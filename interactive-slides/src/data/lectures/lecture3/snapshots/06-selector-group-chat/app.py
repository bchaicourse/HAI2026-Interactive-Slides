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

    optimist = AssistantAgent(
        "Optimist",
        model_client=client,
        description="Sees the bright side and highlights opportunities",
        system_message="""\
You always see the bright side. Keep to 1-2 sentences.
Do NOT say DONE yourself.""",
    )

    pessimist = AssistantAgent(
        "Pessimist",
        model_client=client,
        description="Plays devil's advocate and identifies risks",
        system_message="""\
You always see the risks and downsides. Keep to 1-2 sentences.
Do NOT say DONE yourself.""",
    )

    summarizer = AssistantAgent(
        "Summarizer",
        model_client=client,
        description="Gives a final balanced recommendation after debate",
        system_message="""\
Synthesize the debate into 2-3 sentences of balanced advice.
End with DONE.""",
    )

    def selector_func(messages):
        """Custom turn logic: Optimist → Pessimist → ... → Summarizer."""
        if not messages:
            return "Optimist"
        non_user = [m for m in messages if m.source != "user"]
        turns = len(non_user)
        if turns >= 4:
            return "Summarizer"
        last = messages[-1].source
        if last == "Optimist":
            return "Pessimist"
        return "Optimist"

    team = SelectorGroupChat(
        [optimist, pessimist, summarizer],
        model_client=client,
        termination_condition=TextMentionTermination("DONE"),
        max_turns=8,
        selector_func=selector_func,
    )

    async for msg in team.run_stream(
        task="I'm thinking about quitting my job to start a bakery."
    ):
        if isinstance(msg, TextMessage) and msg.source != "user":
            print(f"[{msg.source}] {msg.content}")
            print()


asyncio.run(main())
