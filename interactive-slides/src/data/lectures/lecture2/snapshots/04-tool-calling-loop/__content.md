## The Tool Calling Loop

So far, we've been handling a single tool call: the model picks a tool, we execute it, and we print the result. But the model never saw that result. It was a one-shot interaction.

What if a question requires multiple steps? Consider: **What is ((123789 + 4564569) * 999999) + 333221?**

This needs three operations in sequence, where each step depends on the previous result:
1. `Plus(123789, 4564569)` → 4688358
2. `Multiply(4688358, 999999)` → 4688353311642
3. `Plus(4688353311642, 333221)` → 4688353644863

No single tool call can solve this. The model needs to call a tool, see its result, use that result to decide the next tool call, and repeat until it has the final answer. To make this possible, we need two things: a **loop** and a **message history** that accumulates results.

### How the Loop Works

Here's the full loop:

```python
for i in range(10):  # safety limit to prevent infinite loops
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        parallel_tool_calls=False
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

Let's walk through what each part does:

**1. Send the full message history to the model.**

```python
response = client.chat.completions.create(
    ...
    messages=messages,
    ...
)
```

Every iteration calls the API with `messages=messages`. This list contains the original user question, every tool call the model has made so far, and every result we've sent back. The model sees the entire conversation history each time.

**2. If the model responds with `tool_calls`, execute and feed the result back.**

```python
if message.tool_calls:
    messages.append(message)

    for tool_call in message.tool_calls:
        # execute and append result...
        messages.append({
            "role": "tool",
            "content": str(result),
            "tool_call_id": tool_call.id
        })
```

We first append the model's own response to the history, then execute the tool and append its result with `"role": "tool"`. Notice `tool_call_id`: each tool call the model makes has a unique ID, and we include it in the result so the API can match each result to the specific call that requested it. This is the key mechanism: by adding the result back to `messages`, the model can see what happened and use it to decide the next step.

**3. If the model responds with text, stop.**

```python
else:
    print(message.content)  # final answer
    break
```

When the model has enough information to answer, it returns plain text instead of a tool call. We print it and `break` out of the loop.

### Why `parallel_tool_calls=False`?

You may have noticed another parameter in the API call:

```python
response = client.chat.completions.create(
    ...
    parallel_tool_calls=False
)
```

By default, the model is allowed to request multiple tool calls in a single turn. For example, if you asked "What is 2+3 and 4*5?", the model could call both `Plus` and `Multiply` at the same time, which would be efficient.

But for our sequential calculation, that would be a problem. The model might try to call both `Plus` and `Multiply` at once, before knowing the result of the first step. Setting `parallel_tool_calls=False` forces the model to request one tool call at a time, ensuring each step completes before the next one begins.
