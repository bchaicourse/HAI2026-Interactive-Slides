# Part 2: Building the UI

## Starting Point: Lecture 1 App with Tool Calling

This is the Streamlit app from Lecture 1, with one key change: the hardcoded 3-step pipeline (`generate_code` → `execute_code` → `interpret_result`) has been replaced with the tool calling pattern we learned in Part 1.

The Streamlit UI itself (sidebar filters, two-column layout, question input) is identical to Lecture 1. The difference is entirely in how the analysis is performed.

### What Changed in `movie_tool.py`

The tool definition uses the same `QueryMovieDB` model and `pydantic_function_tool` pattern from Part 1, with two adaptations for the Streamlit context:

**1. Dynamic tool definition.** In Part 1, the schema was computed once at module load time, because the data never changed. In Streamlit, the user can change sidebar filters on every interaction, so the tool definition needs to reflect the current filtered data. `get_tools(filtered_df)` rebuilds the tool definition each time:

```python
def get_tools(filtered_df):
    schema = get_dataframe_schema(filtered_df)
    return [pydantic_function_tool(
        QueryMovieDB,
        description=f"...Schema:\n{schema}"
    )]
```

**2. Filtered data parameter.** `query_movie_db(code, filtered_df)` now takes the filtered DataFrame as a parameter and saves it to a temporary CSV, instead of reading `movies.csv` directly:

```python
def query_movie_db(code, filtered_df):
    filtered_df.to_csv('temp_data.csv', index=False)
    ...
```

### What Changed in `app.py`

The only change is in `col2`, where the 3-step pipeline becomes a single tool call:

```python
tools = get_tools(filtered_df)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "..."},
        {"role": "user", "content": user_question}
    ],
    tools=tools
)
```

If the model returns `tool_calls`, we execute `query_movie_db` and display the generated code and result. If not, we show the model's direct text response.

Note that this is still a single round of tool calling. If the generated code fails, the user sees the error. The model cannot retry or self-correct yet.
