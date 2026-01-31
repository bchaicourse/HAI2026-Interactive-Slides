## Step 4: Complete Integration

Now let's integrate the LLM pipeline (generate → execute → interpret) from Part 2 into our Streamlit app. This is where everything comes together!

---

### Add the LLM Pipeline Code

Now we'll add the LLM pipeline functions from Part 2. The code will look long, but don't worry—it's almost identical to what we built before, with just small adaptations to work with the filtered data from the UI.

**At the top of `app.py`, add the OpenAI setup:**

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

**Add the code generation function:**

First, add the helper function to create a dataframe schema:

```python
def get_dataframe_schema(df):
    """Generate a schema description for the LLM."""
    schema = f"Columns: {df.columns.tolist()}\n"
    schema += f"Data types:\n{df.dtypes.to_string()}\n"
    schema += f"Shape: {df.shape}\n"
    schema += f"\nSample data (first 3 rows):\n{df.head(3).to_string()}"
    return schema
```

Then add the Pydantic model and generation function:

```python
from pydantic import BaseModel

class Code(BaseModel):
    code: str

def generate_code(task_description, df_schema):
    """Generate Python code to accomplish a task on a dataframe."""
    prompt = f"""
    Your code will be executed in the following environment:

    python
    import pandas as pd
    import numpy as np

    df = pd.read_csv('temp_data.csv')

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
```

**Add the code execution function:**

```python
import subprocess
import sys

def execute_code(code, df):
    """Execute generated code on a dataframe."""
    try:
        df.to_csv('temp_data.csv', index=False)

        full_code = f"""
import pandas as pd
import numpy as np

df = pd.read_csv('temp_data.csv')

{code}
"""

        with open("generated_code.py", "w") as f:
            f.write(full_code)

        result = subprocess.run(
            [sys.executable, "generated_code.py"],
            capture_output=True,
            text=True,
            timeout=10
        )

        return result.stdout if result.returncode == 0 else result.stderr

    except Exception as e:
        return f"Error during execution: {str(e)}"
```

**Key differences from Part 2:** This function now takes `df` as a parameter (the filtered dataframe from the UI) and saves it to `temp_data.csv` before executing the code. This is necessary because:
- In Part 2, we had a static `sample.csv` file on disk
- Here, we have a dynamic `filtered_df` that changes based on user's filter selections
- The generated code runs in a subprocess, so it can't access `filtered_df` directly
- Solution: save `filtered_df` to `temp_data.csv` so the subprocess can read it

Both `generate_code()` and `execute_code()` now use `temp_data.csv` instead of `sample.csv`.

**Add the interpretation function:**

```python
def interpret_result(result, question):
    """Interpret code execution result in natural language."""
    prompt = f"""
    Question: {question}

    Execution result:
    {result}

    Provide a clear, concise interpretation in 2-3 sentences.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content
```

---

### Connect the Pipeline to the UI

**Replace the placeholder in the right column with the actual pipeline:**

```python
with col2:
    st.subheader("Analysis Results")

    if analyze_button and user_question:
        # Generate schema
        schema = get_dataframe_schema(filtered_df)

        # Step 1: Generate code
        generated_code = generate_code(user_question, schema)

        # Step 2: Execute code
        result = execute_code(generated_code, filtered_df)

        # Step 3: Interpret result
        interpretation = interpret_result(result, user_question)

        # Display results
        st.write("**Generated Code:**")
        st.code(generated_code, language='python')

        st.write("**Execution Output:**")
        st.code(result, language="text")

        st.write("**Interpretation:**")
        st.write(interpretation)

    elif analyze_button and not user_question:
        st.error("Please enter a question.")
```

When the button is clicked, the script re-runs, the three pipeline functions execute sequentially, and each result is immediately displayed with `st.write()` and `st.code()`.

---

### Done!

You've now built a complete data analysis application. Users can filter data visually, ask questions in natural language, and get reliable computational results with explanations—all in one app.

The complete implementation is available at: https://github.com/bchaicourse/HAI2026-Week3-Practice
