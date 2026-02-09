from openai import pydantic_function_tool
from pydantic import BaseModel, Field
import json


class Plus(BaseModel):
    """Add two numbers together."""
    a: float = Field(description="The first number")
    b: float = Field(description="The second number")


class Multiply(BaseModel):
    """Multiply two numbers together."""
    a: float = Field(description="The first number")
    b: float = Field(description="The second number")


tools = [pydantic_function_tool(Plus), pydantic_function_tool(Multiply)]

for tool in tools:
    print(json.dumps(tool, indent=2))
    print()
