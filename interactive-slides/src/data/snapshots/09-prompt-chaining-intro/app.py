from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load the data
df = pd.read_csv('sample.csv')
csv_content = df.to_csv(index=False)

prompt = f"""
Here is a dataset:

{csv_content}

Calculate the average Score.
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": prompt}
    ],
    temperature=0.0
)

print(response.choices[0].message.content)