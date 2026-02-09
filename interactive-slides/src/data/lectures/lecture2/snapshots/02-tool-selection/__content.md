## Letting the LLM Choose Tools

We've defined what tools are available. Now the question is: how do we let the LLM actually *know about* these tools so it can decide to use them?

The answer is the `tools` parameter. When making an API call, we pass our tool definitions alongside the user's message:

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is 123789 multiplied by 4564560?"}],
    tools=tools   # <-- this is what makes the LLM aware of our tools
)
```

By including `tools=tools`, the LLM can now see the name, description, and parameters of every tool we defined. It will read those descriptions and decide on its own whether any tool is relevant to the user's question.

### Reading the Model's Response

Once the LLM responds, there are two possible outcomes:

1. The model **wants to use a tool** (the response contains `tool_calls`)
2. The model **answers directly** with text (no tools needed)

We can check which case it is:

```python
message = response.choices[0].message

if message.tool_calls:
    tool_call = message.tool_calls[0]
    print(tool_call.function.name)       # which tool it chose
    print(tool_call.function.arguments)  # what arguments it wants to pass
else:
    print(message.content)              # direct text response
```

### Seeing It in Action

Let's try sending three different queries to the same model with the same two tools (`Plus` and `Multiply`), and see how the model decides differently depending on the question.

**Query 1: "What is 123789 multiplied by 4564560?"**
```
Tool called: Multiply
Arguments:   {"a":123789,"b":4564560}
```

The model recognizes this as a multiplication problem, picks the `Multiply` tool, and extracts the two numbers as arguments.

**Query 2: "What is 123789 plus 4564560?"**
```
Tool called: Plus
Arguments:   {"a":123789,"b":4564560}
```

Same idea, different tool. The model picks `Plus` this time.

**Query 3: "What is the capital of France?"**
```
Response: The capital of France is Paris.
```

This question has nothing to do with math. The model decides that neither `Plus` nor `Multiply` is relevant, so it skips the tools entirely and responds with plain text.

### Important: The Model Didn't Compute Anything

Notice that the model only said *what it wants to call* and *with what arguments*. It did not actually perform the calculation. The response is a structured request, not an answer.
