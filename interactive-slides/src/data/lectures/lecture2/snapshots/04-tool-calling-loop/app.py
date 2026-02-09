from openai import OpenAI, pydantic_function_tool
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()


class Plus(BaseModel):
    """Add two numbers together."""
    a: float = Field(description="The first number")
    b: float = Field(description="The second number")


class Multiply(BaseModel):
    """Multiply two numbers together."""
    a: float = Field(description="The first number")
    b: float = Field(description="The second number")


tools = [pydantic_function_tool(Plus), pydantic_function_tool(Multiply)]

# ========== Tool Functions ==========

def plus(a, b):
    return a + b

def multiply(a, b):
    return a * b

# ========== Tool Calling Loop ==========

messages = [
    {"role": "user", "content": "What is ((123789 + 4564569) * 999999) + 333221?"}
]

for i in range(10):
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
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if name == "Multiply":
                result = multiply(args["a"], args["b"])
            elif name == "Plus":
                result = plus(args["a"], args["b"])

            print(f"Step {i + 1}: {name}({args['a']}, {args['b']}) = {result}")

            messages.append({
                "role": "tool",
                "content": str(result),
                "tool_call_id": tool_call.id
            })
    else:
        print(f"\nFinal answer: {message.content}")
        break
