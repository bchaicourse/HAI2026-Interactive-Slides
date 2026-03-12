from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

client = OpenAIChatCompletionClient(model="gpt-4o-mini")
print("AutoGen installed successfully!")
print(f"Model: gpt-4o-mini")
