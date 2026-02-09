## The Tool Calling Loop

In the previous step, we executed one tool call and printed the raw result. But the model never saw that result, so it could not use it for further reasoning. And some questions require multiple steps.

Consider: **What is ((123789 + 4564569) * 999999) + 333221?**

This requires three operations in sequence:
1. `Plus(123789, 4564569)` → 4688358
2. `Multiply(4688358, 999999)` → 4688353311642
3. `Plus(4688353311642, 333221)` → 4688353644863

No single tool call can solve this. The model needs to call a tool, see the result, call another tool with that result, and repeat until it has the final answer.

### The Loop

We wrap the API call in a loop. Each iteration:

1. Call the model with the full message history
2. If the model returns `tool_calls`: execute them, append the results to the message history, and loop back
3. If the model returns text: that's the final answer. Stop.

```python
for i in range(10):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )

    message = response.choices[0].message

    if message.tool_calls:
        messages.append(message)

        for tool_call in message.tool_calls:
            # execute and append result...
            messages.append({
                "role": "tool",
                "content": str(result),
                "tool_call_id": tool_call.id
            })
    else:
        print(message.content)  # final answer
        break
```

The `range(10)` is a safety limit to prevent infinite loops. The model decides on its own when it has enough information to stop calling tools and produce a final text answer.

### Note: `finish_reason`

Instead of checking `message.tool_calls`, you can also use `response.choices[0].finish_reason`:
- `"tool_calls"`: the model wants to call a tool
- `"stop"`: the model is done and produced a final text response

```python
if response.choices[0].finish_reason == "tool_calls":
    # execute tools...
else:
    # final answer
```

Both approaches work. We use `message.tool_calls` in this tutorial because it gives direct access to the tool call data we need to execute.
