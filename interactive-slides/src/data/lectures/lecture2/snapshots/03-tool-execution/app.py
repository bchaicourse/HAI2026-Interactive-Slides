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

# ========== Call and Execute ==========

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is 123789 multiplied by 4564560?"}],
    tools=tools
)

message = response.choices[0].message

if message.tool_calls:
    tool_call = message.tool_calls[0]
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    print(f"Tool called: {name}")
    print(f"Arguments:   {args}")

    if name == "Multiply":
        result = multiply(args["a"], args["b"])
    elif name == "Plus":
        result = plus(args["a"], args["b"])

    print(f"Result:      {result}")
else:
    print(f"No tool call. Response: {message.content}")
