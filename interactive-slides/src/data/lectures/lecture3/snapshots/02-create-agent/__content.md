## Creating Your First Agent

Let's create a single agent and give it a task. In AutoGen, `AssistantAgent` (from `autogen-agentchat`) is the basic building block for this. It wraps an LLM client with a name and a system prompt.

```python
from autogen_agentchat.agents import AssistantAgent

agent = AssistantAgent(
    "TechExplainer",
    model_client=client,
    system_message="You are an expert at explaining technical concepts in simple terms. Keep answers to 2-3 sentences.",
)
```

The setup is similar to a raw OpenAI API call:

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is a multi-agent system?"}
    ]
)
```

The difference is what happens when you call `run()`. Instead of making a single API call, `run()` handles the full interaction, including multiple rounds if tools are involved:

```python
result = await agent.run(task="What is a multi-agent system?")
```

### Async by Default

Notice the `await` keyword. AutoGen is async-first: all `run()` calls use `await`, and your entry point uses `asyncio.run()`. This is because multi-agent workflows naturally involve waiting (for API responses, tool execution, etc.), and async makes it easy to run agents concurrently.

```python
import asyncio

async def main():
    # ... agent creation and run() calls go here

asyncio.run(main())
```

### Reading the Result

`run()` returns a `TaskResult` containing a `.messages` list of everything that happened during the run. Let's print all messages to see the full picture:

Let's print all messages to see what's inside:

```python
result = await agent.run(task="What is a multi-agent system?")

for msg in result.messages:
    print(msg)
```

```
source='user' content='What is a multi-agent system?' type='TextMessage' ...
source='TechExplainer' content='A multi-agent system is a network of ...' type='TextMessage' ...
```

The `.messages` list contains the full conversation. The first message (`source='user'`) is the task we passed in, and the second (`source='TechExplainer'`) is the agent's response. For a simple call like this there are only two, but when tools or multiple agents are involved, this list grows with each interaction.

To extract just the final answer:

```python
final_answer = result.messages[-1].content
print(final_answer)
```

**Expected output (will vary):**
```
A multi-agent system is a network of multiple autonomous entities, called
agents, that work together to achieve specific goals or solve problems. ...
```
