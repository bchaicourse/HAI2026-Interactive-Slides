from openai import OpenAI
from dotenv import load_dotenv
import os
import tiktoken

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get the tokenizer for gpt-4o-mini
encoding = tiktoken.encoding_for_model("gpt-4o-mini")

prompt = "What are the top three use cases of tokens in OpenAI API?"
tokens = encoding.encode(prompt)

print(f"Text: {prompt}")
print(f"Number of tokens: {len(tokens)}")
print(f"Token IDs: {tokens}")