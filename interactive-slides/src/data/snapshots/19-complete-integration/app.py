import streamlit as st
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import subprocess
import sys

# ====================
# LLM Pipeline Codes
# ====================

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def execute_code(code, df):
    """Execute generated code on a dataframe.

    WARNING: This is unsafe for production. Use sandboxing in real applications.
    """
    try:
        # Save dataframe to temp CSV
        df.to_csv('temp_data.csv', index=False)

        # Prepend imports and dataframe loading to the code
        full_code = f"""
import pandas as pd
import numpy as np

df = pd.read_csv('temp_data.csv')

{code}
"""

        # Write to file
        with open("generated_code.py", "w") as f:
            f.write(full_code)

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


def get_dataframe_schema(df):
    """Generate a schema description for the LLM."""
    schema = f"Columns: {df.columns.tolist()}\n"
    schema += f"Data types:\n{df.dtypes.to_string()}\n"
    schema += f"Shape: {df.shape}\n"
    schema += f"\nSample data (first 3 rows):\n{df.head(3).to_string()}"
    return schema


# ====================
# Streamlit UI Codes
# ====================

st.set_page_config(page_title="Data Analysis Tool", layout="wide")

st.title("Interactive Data Analysis Tool")

df = pd.read_csv('movies.csv')

with st.sidebar:
    st.header("Data Filters")

    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to include:",
        all_columns,
        default=all_columns
    )

    if not selected_columns:
        st.error("Please select at least one column.")
        st.stop()

    filtered_df = df[selected_columns]

    st.subheader("Row Filters")

    if 'Genre' in filtered_df.columns:
        genres = filtered_df['Genre'].dropna().unique()
        selected_genres = st.multiselect(
            "Filter by Genre:",
            genres,
            default=genres.tolist()
        )
        filtered_df = filtered_df[filtered_df['Genre'].isin(selected_genres)]

    if 'Release Year' in filtered_df.columns:
        min_year = int(filtered_df['Release Year'].min())
        max_year = int(filtered_df['Release Year'].max())
        year_range = st.slider(
            "Filter by Release Year:",
            min_year,
            max_year,
            (min_year, max_year)
        )
        filtered_df = filtered_df[
            (filtered_df['Release Year'] >= year_range[0]) &
            (filtered_df['Release Year'] <= year_range[1])
        ]

    if 'IMDB Rating' in filtered_df.columns:
        min_rating = float(filtered_df['IMDB Rating'].min())
        max_rating = float(filtered_df['IMDB Rating'].max())
        rating_range = st.slider(
            "Filter by IMDB Rating:",
            min_rating,
            max_rating,
            (min_rating, max_rating)
        )
        filtered_df = filtered_df[
            (filtered_df['IMDB Rating'] >= rating_range[0]) &
            (filtered_df['IMDB Rating'] <= rating_range[1])
        ]

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Filtered Dataset")
    st.write(filtered_df)

    st.subheader("Ask a Question")
    user_question = st.text_input(
        "What would you like to know about this data?",
        placeholder="e.g., What is the average IMDB rating?"
    )

    analyze_button = st.button("Analyze", type="primary")

with col2:
    st.subheader("Analysis Results")

    if analyze_button and user_question:
        schema = get_dataframe_schema(filtered_df)
        generated_code = generate_code(user_question, schema)
        result = execute_code(generated_code, filtered_df)
        interpretation = interpret_result(result, user_question)

        st.write("**Generated Code:**")
        st.code(generated_code, language='python')

        st.write("**Execution Output:**")
        st.code(result, language="text")

        st.write("**Interpretation:**")
        st.write(interpretation)

    elif analyze_button and not user_question:
        st.error("Please enter a question.")