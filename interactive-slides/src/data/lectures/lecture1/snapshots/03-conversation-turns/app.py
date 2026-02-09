from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Multi-turn Conversation
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is a Large Language Model?"},
        {"role": "assistant", "content": "A Large Language Model (LLM) is a type of artificial intelligence model designed to understand and generate human language. These models are typically based on deep learning techniques, particularly neural networks, and are trained on vast amounts of text data."},
        {"role": "user", "content": "Summarize that in three words."}
    ]
)

print(response.choices[0].message.content)
