from openai import OpenAI, pydantic_function_tool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

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

# ========== Query 1 ==========

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is 123789 multiplied by 4564560?"}],
    tools=tools
)

message = response.choices[0].message
print("Query: What is 123789 multiplied by 4564560?")
if message.tool_calls:
    tool_call = message.tool_calls[0]
    print(f"  Tool called: {tool_call.function.name}")
    print(f"  Arguments:   {tool_call.function.arguments}")
else:
    print(f"  Response: {message.content}")
print()

# ========== Query 2 ==========

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is 123789 plus 4564560?"}],
    tools=tools
)

message = response.choices[0].message
print("Query: What is 123789 plus 4564560?")
if message.tool_calls:
    tool_call = message.tool_calls[0]
    print(f"  Tool called: {tool_call.function.name}")
    print(f"  Arguments:   {tool_call.function.arguments}")
else:
    print(f"  Response: {message.content}")
print()

# ========== Query 3 ==========

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    tools=tools
)

message = response.choices[0].message
print("Query: What is the capital of France?")
if message.tool_calls:
    tool_call = message.tool_calls[0]
    print(f"  Tool called: {tool_call.function.name}")
    print(f"  Arguments:   {tool_call.function.arguments}")
else:
    print(f"  Response: {message.content}")
