from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Setup complete - client is ready to use
print("OpenAI client initialized successfully!")
print(f"Using API key: {os.getenv('OPENAI_API_KEY')[:8]}...")
