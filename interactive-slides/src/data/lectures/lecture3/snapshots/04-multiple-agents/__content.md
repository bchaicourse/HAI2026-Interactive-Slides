## Multiple Agents, Different Perspectives

An agent's behavior is defined by its `system_message`. By creating multiple agents with different system messages, we can get different perspectives on the same question.

```python
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
```

We run each agent separately on the same question:

```python
question = "I'm thinking about quitting my job to start a bakery."

result = await optimist.run(task=question)
print(result.messages[-1].content)

result = await pessimist.run(task=question)
print(result.messages[-1].content)
```

**Expected output (will vary):**
```
--- Optimist ---
- **Pursuing Passion**: Starting a bakery allows you to turn your love for
  baking into a fulfilling career...
- **Creative Freedom**: You'll have the opportunity to express your creativity...

--- Pessimist ---
- **Financial Instability**: Transitioning to a bakery may lead to unpredictable
  income...
- **Market Competition**: The bakery industry can be highly competitive...
```

### The Problem

This works, but each agent runs in isolation. The Pessimist doesn't know what the Optimist said. If we want agents to build on each other's analysis, take turns in a conversation, or coordinate their responses, we need orchestration patterns that define how agents interact.
