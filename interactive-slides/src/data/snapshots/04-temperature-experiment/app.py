from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Temperature = 0.0 (Deterministic)
print("--- Temperature = 0.0 (Deterministic) ---")
for i in range(3):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Generate three random numbers between 1 and 100."}],
        temperature=0.0
    )
    print(f"Attempt {i+1}: {response.choices[0].message.content}\n")

# Temperature = 2.0 (Highly Creative)
print("\n--- Temperature = 2.0 (Highly Creative) ---")
for i in range(3):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Generate three random numbers between 1 and 100."}],
        temperature=2.0
    )
    print(f"Attempt {i+1}: {response.choices[0].message.content}\n")