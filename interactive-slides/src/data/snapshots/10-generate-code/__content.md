## Better Approach: Generate Code Instead

Instead of asking the LLM to calculate, ask it to **generate Python code** that we can execute.

This solves both problems:
- **Token limits:** We only send the task description and schema, not the entire dataset
- **Computational reliability:** Python does the math, not the LLM

**3-step process:**
1. Generate Code (LLM)
2. Execute Code (Python)
3. Interpret Result (LLM)

## Step 1: Generate Code

**Define a schema for code output:**
```python
class Code(BaseModel):
    code: str
```

**Create a helper to describe the dataframe:**
```python
def get_dataframe_schema(df):
    schema = f"Columns: {df.columns.tolist()}\n"
    schema += f"Data types:\n{df.dtypes.to_string()}\n"
    schema += f"Shape: {df.shape}\n"
    schema += f"\nSample data (first 3 rows):\n{df.head(3).to_string()}"
    return schema
```

This function creates a compact summary of the dataframe:
```
Columns: ['Name', 'Age', 'Score']
Data types:
Name     object
Age       int64
Score     int64
Shape: (5, 3)

Sample data (first 3 rows):
      Name  Age  Score
0    Alice   25     85
1      Bob   30     92
2  Charlie   28     78
```

**Key insight:** Instead of sending the entire dataset (which could be 10,000+ rows), we send only:
- Column names and types
- Dataset shape
- A few sample rows

This gives the LLM enough context to write correct code without exceeding token limits.

**Generate code with context:**
```python
def generate_code(task_description, df_schema):
    prompt = f"""
    Your code will be executed in the following environment:

    import pandas as pd
    import numpy as np
    df = pd.read_csv('sample.csv')
    # YOUR CODE GOES HERE

    DataFrame schema:
    {df_schema}

    Task: {task_description}

    Write the code that will replace "# YOUR CODE GOES HERE".
    Make sure to print the result.
    Provide only executable Python code, no explanations.
    """

    response = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format=Code,
        temperature=0.0
    )

    return response.choices[0].message.parsed.code
```

**Use it:**
```python
df = pd.read_csv('sample.csv')
schema = get_dataframe_schema(df)
task = "Calculate the average Score"

generated_code = generate_code(task, schema)
print("Generated Code:")
print(generated_code)
```

The LLM generates executable Python code:

```
Generated Code:
import pandas as pd

df = pd.read_csv('sample.csv')
average_score = df['Score'].mean()
print(average_score)
```

The LLM wrote code based on the schema, not the raw data. This code can now be executed reliably.
