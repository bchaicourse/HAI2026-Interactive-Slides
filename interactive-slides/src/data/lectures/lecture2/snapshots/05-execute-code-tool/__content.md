## Applying Tool Calling to Data Analysis

So far, our tools have been simple arithmetic functions like `Plus` and `Multiply`. Now let's apply the same tool calling pattern to something more useful: letting the LLM write and execute Python code to analyze a real dataset.

In this step, we introduce a new file, `movie_tool.py`, which contains the tool definition and the code execution logic. The main `app.py` imports from it and runs the same tool calling loop as before.

### Defining the Tool

In `movie_tool.py`, we define a single tool called `QueryMovieDB`. Its only parameter is `code`, a string of Python code that will be executed against a movie dataset:

```python
class QueryMovieDB(BaseModel):
    """Query the movie database using Python code."""
    code: str = Field(description="Python code to execute")
```

But there's a problem. The LLM needs to know *what data is available* in order to write meaningful code. What columns does the dataset have? What are their types? We solve this by embedding the dataset's schema directly into the tool description:

```python
QueryMovieDBTool = pydantic_function_tool(
    QueryMovieDB,
    description=f"Execute Python code to query the movie database. "
                f"The DataFrame `df` is pre-loaded. "
                f"Always use print() to output results.\n\n"
                f"Schema:\n{_schema}"
)
```

The `description` parameter here overrides the class docstring (`"""Query the movie database using Python code."""`) in the generated JSON. By embedding the schema, the LLM sees column names, data types, and sample rows as part of the tool definition itself, giving it everything it needs to write correct code.

### Executing the Code

The `query_movie_db()` function works almost identically to the `execute_code()` function from Lecture 1: it wraps the LLM-generated code with imports, writes it to a file, and runs it as a subprocess. The one difference is what we return to the LLM:

- **Error** (`returncode != 0`): return `stderr`, so the LLM can see what went wrong and fix it
- **Empty output**: return `"No output. Did you forget to use print()?"` as a hint
- **Success**: return `stdout` with the actual data

We're not just returning success or failure. We're giving the LLM *detailed feedback* that it can use to improve its next attempt.

### Self-Correction in Action

This feedback mechanism enables something powerful. Let's say we ask: "What are the top 5 highest-rated movies by IMDB Rating?"

```
Step 1: QueryMovieDB
  Code:   df.nlargest(5, 'IMDB Rating')[['Title', 'IMDB Rating']]
  Result: No output. Did you forget to use print()?

Step 2: QueryMovieDB
  Code:   print(df.nlargest(5, 'IMDB Rating')[['Title', 'IMDB Rating']])
  Result: (actual data showing top 5 movies)
```

The model's first attempt generates code without `print()`, producing no output. Our tool returns a helpful hint, and the model sees this as the tool result in its message history. On its second attempt, it corrects itself by adding `print()` and successfully retrieves the data.

This self-correcting behavior is the key advantage over the hardcoded pipeline we built previously, which would have simply shown the empty result and stopped. The tool calling loop lets the model observe its mistakes, adjust, and try again automatically.
