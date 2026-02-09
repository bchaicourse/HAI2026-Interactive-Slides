# Part 1: Function Calling

## From Hardcoded Pipelines to Tool Selection

In Lecture 1, our analysis pipeline was hardcoded:

```python
code = generate_code(question, schema)      # always step 1
result = execute_code(code, filtered_df)    # always step 2
answer = interpret_result(result, question)  # always step 3
```

The LLM had no choice in what to do. It always followed the same three steps in the same order. If the generated code failed, the pipeline just showed the error and stopped. If a question needed a different approach, the pipeline could not adapt.

**Function calling** changes this by letting the LLM choose which tools to use and with what arguments. Before applying this to our data analysis tool, let's understand how it works with a simple example.

## Defining Tools with Pydantic

A tool definition tells the LLM what a tool does and what arguments it expects. The OpenAI SDK provides `pydantic_function_tool` to generate tool definitions from Pydantic models:

```python
from openai import pydantic_function_tool
from pydantic import BaseModel, Field

class Plus(BaseModel):
    """Add two numbers together."""
    a: float = Field(description="The first number")
    b: float = Field(description="The second number")
```

- The **class docstring** becomes the tool's description
- Each **field** becomes a parameter with its type and description

```python
tools = [pydantic_function_tool(Plus), pydantic_function_tool(Multiply)]
```

`pydantic_function_tool()` converts each Pydantic model into the JSON schema format the API expects. For example, `pydantic_function_tool(Plus)` generates:

```json
{
  "type": "function",
  "function": {
    "name": "Plus",
    "description": "Add two numbers together.",
    "parameters": {
      "properties": {
        "a": { "type": "number", "description": "The first number" },
        "b": { "type": "number", "description": "The second number" }
      },
      "required": ["a", "b"],
      "type": "object"
    }
  }
}
```

- **`name`**: the class name, used as the tool identifier
- **`description`**: from the docstring. The LLM reads this to decide when to use the tool.
- **`parameters`**: from the fields. The LLM uses this to construct valid arguments.

The LLM receives these definitions and uses them to decide which tool to call and with what arguments.
