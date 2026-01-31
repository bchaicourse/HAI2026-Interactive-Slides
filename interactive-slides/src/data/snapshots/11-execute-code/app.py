from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import subprocess
import sys
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

def execute_code(code):
    """Execute generated code.

    WARNING: This is unsafe for production. Use sandboxing in real applications.
    """
    try:
        # Write code to file
        with open("generated_code.py", "w") as f:
            f.write(code)

        # Execute
        result = subprocess.run(
            [sys.executable, "generated_code.py"],
            capture_output=True,
            text=True,
            timeout=10
        )

        return result.stdout if result.returncode == 0 else result.stderr

    except Exception as e:
        return f"Error during execution: {str(e)}"

# Usage
df = pd.read_csv('sample.csv')
schema = get_dataframe_schema(df)
task_description = "Calculate the average Score"

generated_code = generate_code(task_description, schema)
print("Generated Code:")
print(generated_code)

execution_result = execute_code(generated_code)
print("\nExecution Result:")
print(execution_result)