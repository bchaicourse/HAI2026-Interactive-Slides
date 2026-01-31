from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import pandas as pd

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Code(BaseModel):
    code: str

def get_dataframe_schema(df):
    """Generate a schema description for the LLM."""
    schema = f"Columns: {df.columns.tolist()}\n"
    schema += f"Data types:\n{df.dtypes.to_string()}\n"
    schema += f"Shape: {df.shape}\n"
    schema += f"\nSample data (first 3 rows):\n{df.head(3).to_string()}"
    return schema

def generate_code(task_description, df_schema):
    """Generate Python code to accomplish a task on a dataframe."""
    prompt = f"""
    Your code will be executed in the following environment:

    python
    import pandas as pd
    import numpy as np

    df = pd.read_csv('sample.csv')

    # YOUR CODE GOES HERE

    DataFrame schema:
    {df_schema}

    Task: {task_description}

    Write the code that will replace "# YOUR CODE GOES HERE".
    Make sure to print the result (do not save to variables without printing).

    Provide only executable Python code, no explanations.
    """

    response = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format=Code,
        temperature=0
    )

    return response.choices[0].message.parsed.code

# Usage
df = pd.read_csv('sample.csv')
schema = get_dataframe_schema(df)
task_description = "Calculate the average Score"

generated_code = generate_code(task_description, schema)
print("Generated Code:")
print(generated_code)