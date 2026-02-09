from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
import json
from movie_tool import QueryMovieDBTool, query_movie_db

load_dotenv()
client = OpenAI()


class Reasoning(BaseModel):
    reason: str = Field(description="Your reasoning about what you know so far and what to do next")
    use_tool: bool = Field(description="True if you need to run code, False if you can give the final answer")
    answer: Optional[str] = Field(default=None, description="Your final answer. Only provide when use_tool is False.")


# ========== ReAct Loop ==========

messages = [
    {"role": "system", "content": "You are a data analyst with access to a tool that executes Python code on a movie database."},
    {"role": "user", "content": "What are the top 5 highest-rated movies by IMDB Rating?"}
]

while True:
    # Reasoning: structured output, no tools
    response = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        response_format=Reasoning,
    )
    reasoning = response.choices[0].message.parsed
    messages.append({"role": "assistant", "content": reasoning.reason})
    print(f"Thought: {reasoning.reason}\n")

    if not reasoning.use_tool:
        print(f"Answer: {reasoning.answer}")
        break

    # Acting: tools available
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=[QueryMovieDBTool],
        parallel_tool_calls=False
    )

    message = response.choices[0].message

    if message.tool_calls:
        messages.append(message)

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if name == QueryMovieDBTool["function"]["name"]:
                result = query_movie_db(args["code"])

            print(f"Action: {name}")
            print(f"Code: {args['code']}")
            print(f"Observation: {result}")

            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.id
            })
    else:
        print(f"Answer: {message.content}")
        break
