## Executing the Tool Call

In the previous step, the model told us *what* it wants to call. Now we implement the actual functions and execute them.

```python
def plus(a, b):
    return a + b

def multiply(a, b):
    return a * b
```

When a tool call is present, the arguments come as a JSON string. We parse them with `json.loads` and dispatch to the matching function:

```python
args = json.loads(tool_call.function.arguments)

if name == "Multiply":
    result = multiply(args["a"], args["b"])
elif name == "Plus":
    result = plus(args["a"], args["b"])
```

The computation is done by Python, not the LLM. The model chose the right tool and extracted the arguments; our code does the math.