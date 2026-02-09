## Sending Tools to the LLM

Now we pass the tool definitions to the API along with a user question:

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is 123789 multiplied by 4564560?"}],
    tools=tools
)
```

When tools are provided, the model can respond in two ways:
- **A `tool_calls` list**: it wants to use a tool
- **Regular text**: it answered directly without using any tool

We check which case it is:

```python
message = response.choices[0].message

if message.tool_calls:
    tool_call = message.tool_calls[0]
    print(tool_call.function.name)       # which tool it chose
    print(tool_call.function.arguments)  # what arguments it wants to pass
else:
    print(message.content)              # direct text response
```

### Three Queries, Three Different Responses

For "What is 123789 multiplied by 4564560?":
```
Tool called: Multiply
Arguments:   {"a":123789,"b":4564560}
```

For "What is 123789 plus 4564560?":
```
Tool called: Plus
Arguments:   {"a":123789,"b":4564560}
```

For "What is the capital of France?":
```
Response: The capital of France is Paris.
```

The model reads the tool descriptions and decides whether any tool is relevant. For arithmetic questions, it selects the matching tool and extracts the numbers as structured arguments. For unrelated questions, it skips the tools entirely and responds with text.

### Key Observation

Notice that **the model did not compute anything**. It only said *what it wants to call* and *with what arguments*. The response is a structured request, not an answer. To get an actual result, our code needs to:

1. Execute the requested tool locally
2. Send the result back to the model
3. Let the model compose a final answer

This execute-and-return flow is what we build next.
