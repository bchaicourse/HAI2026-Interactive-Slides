## Executing the Tool Call

We saw that the model responds with *which tool* it wants to call and *what arguments* to pass. But the model doesn't actually run anything. It's our job to take that response and execute it.

First, we define the actual Python functions that do the work:

```python
def plus(a, b):
    return a + b

def multiply(a, b):
    return a * b
```

Then, when the model returns a tool call, we need to:

1. **Parse the arguments**: They come back as a JSON string, so we use `json.loads` to convert them into a Python dictionary.
2. **Match the tool name**: Check which function the model requested and call it with the parsed arguments.

```python
name = tool_call.function.name
args = json.loads(tool_call.function.arguments)

if name == "Multiply":
    result = multiply(args["a"], args["b"])
elif name == "Plus":
    result = plus(args["a"], args["b"])
```

This is an important distinction to keep in mind: the LLM chose the right tool and extracted the arguments from natural language, but **Python is doing the actual computation**. The model never calculated `123789 * 4564560` itself.
