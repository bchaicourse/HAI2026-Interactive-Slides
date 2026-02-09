# Part 1: Function Calling

## From Hardcoded Pipelines to Tool Selection

Previously, our analysis pipeline was hardcoded into three fixed steps:

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

- The **class docstring** (`"""Add two numbers together."""`) becomes the tool's description
- Each **field** becomes a parameter with its type and description

Calling `pydantic_function_tool(Plus)` converts this Pydantic model into a JSON structure:

```json
{
  "type": "function",
  "function": {
    "name": "Plus",
    "strict": true,
    "parameters": {
      "description": "Add two numbers together.",
      "properties": {
        "a": { "description": "The first number", "title": "A", "type": "number" },
        "b": { "description": "The second number", "title": "B", "type": "number" }
      },
      "required": ["a", "b"],
      "title": "Plus",
      "type": "object",
      "additionalProperties": false
    },
    "description": "Add two numbers together."
  }
}
```

You don't need to memorize this structure. It's a predefined format for communicating tool information between your code and the API. The key fields to understand are:

- **`name`**: The class name, used as the tool identifier.
- **`description`**: From the docstring. The LLM reads this to decide *when* to use the tool.
- **`parameters`**: From the fields. The LLM uses this to construct valid arguments.
