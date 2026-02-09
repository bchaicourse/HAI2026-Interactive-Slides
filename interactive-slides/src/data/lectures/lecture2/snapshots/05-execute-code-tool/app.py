from openai import OpenAI
from dotenv import load_dotenv
import json
from movie_tool import QueryMovieDBTool, query_movie_db

load_dotenv()
client = OpenAI()

# ========== Tool Calling Loop ==========

messages = [
    {"role": "system", "content": "You are a data analyst with access to a tool that executes Python code on a movie database."},
    {"role": "user", "content": "What are the top 5 highest-rated movies by IMDB Rating?"}
]

for i in range(10):
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

            print(f"Step {i + 1}: {name}")
            print(f"Code: {args['code']}")
            print(f"Result: {result}")

            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.id
            })
    else:
        print(f"\nFinal answer:\n{message.content}")
        break
