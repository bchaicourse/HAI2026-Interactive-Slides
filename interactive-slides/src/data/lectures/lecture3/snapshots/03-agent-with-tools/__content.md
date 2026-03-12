## Adding Tools to an Agent

So far, our agent can only generate text. To let it perform actual computation, we give it **tools**. With the raw OpenAI API, this requires defining Pydantic models, converting them with `pydantic_function_tool()`, and writing the tool-calling loop yourself. AutoGen simplifies this: you wrap a plain Python function with `FunctionTool` (from `autogen-core`), and the framework handles the rest.

```python
from autogen_core.tools import FunctionTool

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

multiply_tool = FunctionTool(multiply, description="Multiply two numbers")
```

Pass the tool to an agent via the `tools` parameter. We also set `reflect_on_tool_use=True`, which tells the agent to send the tool result back to the LLM so it can interpret it and decide what to do next. Without this, the agent would return the raw tool result and stop.

```python
agent = AssistantAgent(
    "Calculator",
    model_client=client,
    tools=[multiply_tool],
    system_message="Use the provided tools to solve math problems.",
    reflect_on_tool_use=True,
)
```

> **Note:** The default for `reflect_on_tool_use` is `False` because AutoGen is designed primarily for multi-agent teams, where the team orchestrator controls the flow between agents. When using a single agent standalone, set it to `True` so the agent can complete the full task on its own.

Let's test with a multiplication no LLM could do in its head:

```python
result = await agent.run(task="What is 4839281574 * 7291048365?")
for msg in result.messages:
    print(msg)
```

### New Message Types

With tools, `result.messages` now contains new types beyond `TextMessage`:

```
source='user' content='What is 4839281574 * 7291048365?' type='TextMessage'
source='Calculator' content=[FunctionCall(arguments='{"a":4839281574,"b":7291048365}', name='multiply')] type='ToolCallRequestEvent'
source='Calculator' content=[FunctionExecutionResult(content='35283436007887326510', name='multiply')] type='ToolCallExecutionEvent'
source='Calculator' content='The product of 4839281574 and 7291048365 is 35,283,436,007,887,326,510.' type='TextMessage'
```

- **`ToolCallRequestEvent`**: The agent requests a tool call (which function, with what arguments)
- **`ToolCallExecutionEvent`**: The result of executing the tool
- The final **`TextMessage`**: The agent interpreted the tool result and produced a natural language answer. This is because `reflect_on_tool_use=True` sends the result back to the LLM for one more round.
