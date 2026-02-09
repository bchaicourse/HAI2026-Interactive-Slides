## The ReAct Pattern

In the tool calling loop we built, the model jumps straight from question to tool call without explaining *why* it's choosing that tool or what it plans to do. It works, but we have no visibility into the model's decision-making process.

The **ReAct** (Reasoning + Acting) pattern addresses this by splitting each iteration into two explicit steps:

1. **Thought**: The model reasons about the current situation and decides what to do next.
2. **Action**: The model calls a tool, or provides the final answer.

### Structured Reasoning with Pydantic

To make the model's reasoning explicit, we define a `Reasoning` model using Pydantic's structured output:

```python
class Reasoning(BaseModel):
    reason: str = Field(
        description="Your reasoning about what you know so far and what to do next"
    )
    use_tool: bool = Field(
        description="True if you need to run code, False if you can give the final answer"
    )
    answer: Optional[str] = Field(
        default=None,
        description="Your final answer. Only provide when use_tool is False."
    )
```

There are three fields here:

- **`reason`**: The model writes out its thinking. This makes each step transparent and debuggable.
- **`use_tool`**: A boolean that explicitly tells us whether the model wants to call a tool or is ready to answer. This replaces the `for i in range(10)` safety limit from before. Instead of guessing when the model is done, we get a clear signal.
- **`answer`**: The final answer, only provided when `use_tool` is `False`.

### The Loop: Two API Calls Per Iteration

The ReAct loop makes two separate API calls each iteration. Here's the full structure:

```python
while True:
    # 1. Reasoning: structured output, no tools
    response = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        response_format=Reasoning,
    )
    reasoning = response.choices[0].message.parsed
    messages.append({"role": "assistant", "content": reasoning.reason})

    if not reasoning.use_tool:
        print(reasoning.answer)
        break

    # 2. Acting: tools available
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=[QueryMovieDBTool],
        parallel_tool_calls=False
    )

    message = response.choices[0].message

    if message.tool_calls:
        messages.append(message)

        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = query_movie_db(args["code"])

            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.id
            })
```

Let's break this down:

**1. The Reasoning call:**

```python
response = client.chat.completions.parse(
    model="gpt-4o-mini",
    messages=messages,
    response_format=Reasoning,
)
reasoning = response.choices[0].message.parsed
```

This uses `response_format=Reasoning` with no `tools` parameter. The model is forced to output structured JSON with its reasoning and decision. We use `client.chat.completions.parse` instead of `.create` so the response is automatically parsed into our `Reasoning` model. If `use_tool` is `False`, we print the answer and stop.

**Appending the reasoning to the message history:**

```python
messages.append({"role": "assistant", "content": reasoning.reason})
```

This is crucial. The model's reasoning is added to the message history *before* the Acting call. This way, the Acting call can see the model's own plan and act on it.

**2. The Acting call:**

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=[QueryMovieDBTool],
    parallel_tool_calls=False
)
```

This uses `tools=[QueryMovieDBTool]` with no `response_format`. Because the model's reasoning is already in the message history, it acts on its own plan and calls the appropriate tool.

**3. Execute and feed results back:**

```python
messages.append(message)

for tool_call in message.tool_calls:
    args = json.loads(tool_call.function.arguments)
    result = query_movie_db(args["code"])

    messages.append({
        "role": "tool",
        "content": result,
        "tool_call_id": tool_call.id
    })
```

Same as the tool calling loop from before: we execute the tool, append the result to the message history, and the loop continues with the next Reasoning call.

### Thought, Action, Observation

Let's see what this looks like in practice with the same question as before:

```
Thought: I need to query the database for top-rated movies...

Action: QueryMovieDB
Code:   df.nlargest(5, 'IMDB Rating')[['Title', 'IMDB Rating']]
Observation: No output. Did you forget to use print()?

Thought: I forgot print(). Let me fix that...

Action: QueryMovieDB
Code:   print(df.nlargest(5, 'IMDB Rating')[['Title', 'IMDB Rating']])
Observation: (actual data)

Thought: I now have the data. → use_tool: false
Answer: 1. Inception - 9.1 ...
```

Each thought explains *why* the model is taking its next action. When something goes wrong (the missing `print()`), the model reasons about the error before retrying. This makes the entire process transparent and easy to follow.
