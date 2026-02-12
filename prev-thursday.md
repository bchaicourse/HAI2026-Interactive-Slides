# HAI2026 Interactive Slides - All Readings

---

# Part 1: API Fundamentals

---

## Setting Up Python + OpenAI Environment

Before we begin, ensure you have Python 3.8+ installed on your system.

### Create a Virtual Environment

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

**Note:** Once the virtual environment is activated, you can use `python` (instead of `python3`) on all platforms.

### Install Required Packages

First, create a `requirements.txt` file with the following content:

```
openai
python-dotenv
```

Then install from requirements.txt:
```bash
pip install -r requirements.txt
```

Alternatively, you can install packages directly by specifying library names:
```bash
pip install openai python-dotenv
```

### Set Up Your OpenAI API Key

Create a `.env` file in your project directory:

```
OPENAI_API_KEY=sk-proj-...
```

Replace `sk-proj-...` with your actual OpenAI API key.

### Import Dependencies in Python

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

---

## Your First API Call

At its core, interacting with an LLM via the OpenAI API is straightforward. You send a message and receive a response. The `system` message defines the AI's role and behavior, while the `user` message is your actual query.

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is a Large Language Model?"}
    ]
)

print(response.choices[0].message.content)
```

---

## Multi-turn Conversations

The chat API supports **multi-turn conversations** by including previous messages in the `messages` array. This allows the model to maintain context across multiple exchanges.

### How It Works

Each message has a `role`:
- `system`: Sets the assistant's behavior
- `user`: User's input
- `assistant`: Model's previous responses

By including the assistant's previous response in the next API call, the model can reference earlier parts of the conversation.

### Example: Building Context

```python
messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is a Large Language Model?"},
    {"role": "assistant", "content": "A Large Language Model (LLM) is..."},
    {"role": "user", "content": "Summarize that in three words."}
]
```

The model can now reference "that" (its previous explanation) to provide a concise summary.

**Key Point:** You must manually include the conversation history in each API call. The API itself is stateless.

---

## Experimenting with Parameters: Temperature

When you call an LLM, you can control how it generates text using parameters. One of the most important is **temperature** (range: 0.0 to 2.0), which controls randomness in the model's outputs.

- **Temperature = 0.0**: Deterministic (always picks the most likely token)
- **Temperature = 2.0**: Highly creative (samples very varied outputs)

Let's see this in action by comparing both extremes.

---

## Counting Tokens

When working with LLM APIs, you pay per token. Understanding token counts helps you estimate costs and avoid exceeding context limits.

**What is a token?** Tokens are chunks of text. Roughly:
- 1 token ≈ 4 characters in English
- 1 token ≈ ¾ words
- 100 tokens ≈ 75 words

The exact tokenization depends on the model. Use the `tiktoken` library to count tokens precisely.

### Installing tiktoken

```bash
pip install tiktoken
```

### Counting Tokens in a Prompt

Use `tiktoken` to get the exact token count for your text before sending it to the API.

**Step 1: Get the tokenizer for your model**
```python
import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4o-mini")
```

**Step 2: Encode your text into tokens**
```python
prompt = "What are the top three use cases of tokens in OpenAI API?"
tokens = encoding.encode(prompt)
```

**Step 3: Examine the results**
```python
print(f"Text: {prompt}")
print(f"Number of tokens: {len(tokens)}")
print(f"Token IDs: {tokens}")
```

**What this shows:**
- **Text**: Your original input string
- **Number of tokens**: How many tokens this text uses (affects your API costs)
- **Token IDs**: The list of integer IDs representing each token in the model's vocabulary. Each ID corresponds to a piece of text (word, subword, or character). This is what the model actually processes internally.

---

## Estimating API Costs

OpenAI charges based on tokens used. For **gpt-4o-mini** (as of 2026):

- **Input tokens**: $0.150 per 1M tokens
- **Output tokens**: $0.600 per 1M tokens

Note that output tokens are 4x more expensive than input tokens, as generating text requires more computation than processing it.

### Creating a Cost Estimation Function

**Step 1: Define the function and get token counts**
```python
def estimate_cost(input_text, output_text, model="gpt-4o-mini"):
    encoding = tiktoken.encoding_for_model(model)

    input_tokens = len(encoding.encode(input_text))
    output_tokens = len(encoding.encode(output_text))
```

**Step 2: Set the pricing (per 1 million tokens)**
```python
    input_price_per_million = 0.150
    output_price_per_million = 0.600
```

**Step 3: Calculate costs**
```python
    input_cost = (input_tokens / 1_000_000) * input_price_per_million
    output_cost = (output_tokens / 1_000_000) * output_price_per_million
    total_cost = input_cost + output_cost
```

**Step 4: Return all information**
```python
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost
    }
```

### Using the Function

```python
input_text = "Explain how large language models work in 100 words."
output_text = """Large language models are neural networks..."""

cost_info = estimate_cost(input_text, output_text)
print(f"Total cost: ${cost_info['total_cost']:.6f}")
```

This helps you estimate costs before making API calls, especially important when processing large amounts of text.

---

## The Problem with Free-Form Text Output

Natural language is great for humans, but terrible for programs. Consider this task: extract specific information from text.

### Attempting Unstructured Extraction

**The prompt:**
```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": """
        Extract the following details from this text:

        Text: 'Alice Smith was born on June 12, 1990.
        She recently bought a car, a red 2020 Toyota Corolla...'

        Details to Extract:
        - Name
        - Date of Birth
        - Car Model
        - Car Year
        ...
        """
    }]
)
```

**The output:**
```
Here are the extracted details:

- **Name**: Alice Smith
- **Date of Birth**: June 12, 1990
- **Car Model**: Toyota Corolla
...
```

### Why This Is Problematic

The output is markdown-formatted text. To use this in a program, you would need to:

1. **Parse the markdown** (what if it uses `*` instead of `-`?)
2. **Handle format variations** (sometimes it might use numbered lists, or no formatting at all)
3. **Extract each field reliably** (regex? string splitting? both fragile)

This is **brittle and error-prone**. Different runs might produce different formats, breaking your parsing logic.

**Solution:** Use structured outputs with Pydantic schemas (next section).

---

## The Solution: Structured Output using Pydantic Models

**Pydantic** is a Python library for data validation. OpenAI's API integrates with Pydantic to support **structured outputs**—you define a schema, and the model returns data matching that exact structure.

**Step 1: Install Pydantic**
```bash
pip install pydantic
```

**Step 2: Define your schema**
```python
from pydantic import BaseModel

class ExtractedData(BaseModel):
    name: str
    date_of_birth: str
    car_model: str
    car_year: str
    car_color: str
    license_plate_number: str
    address: str
    phone_number: str
```

**Step 3: Use `.parse()` with `response_format`**
```python
response = client.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": "Extract the following details..."
    }],
    response_format=ExtractedData
)
```

**Step 4: Access structured data directly**
```python
data = response.choices[0].message.parsed
print(f"Name: {data.name}")
print(f"Car: {data.car_year} {data.car_color} {data.car_model}")
```

No parsing required—just direct attribute access.

---

# Part 2: Analyzing Data with LLMs

---

Now let's explore how to use LLMs for data analysis. Traditional data analysis tools require you to write specific queries or code for each question. The advantage of using LLMs is that users can ask questions in natural language, making data exploration more flexible and accessible.

## Naive Approach: Ask the LLM to Calculate

Let's try the simplest approach: ask the LLM to analyze data directly. We'll calculate the average score from a simple CSV dataset.

**sample.csv:**
```
Name,Age,Score
Alice,25,85
Bob,30,92
Charlie,28,78
Diana,35,88
Eve,22,95
```

**Load the data and ask the LLM:**
```python
df = pd.read_csv('sample.csv')
csv_content = df.to_csv(index=False)

prompt = f"""
Here is a dataset:

{csv_content}

Calculate the average Score.
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.0
)

print(response.choices[0].message.content)
```

The LLM analyzes the data and shows step-by-step reasoning:

```
To calculate the average score, you need to sum all the scores and then divide by the number of entries.

Here are the scores from the dataset:
- Alice: 85
- Bob: 92
- Charlie: 78
...

Now, let's sum the scores:
85 + 92 + 78 + 88 + 95 = 438

Next, divide the total score by the number of entries (which is 5):
Average Score = 438 / 5 = 87.6

So, the average score is **87.6**.
```

For this simple example, it works!

### But This Approach Has Serious Limitations

**Problem 1: Token Limits**
- Works for 5 rows, but what about 10,000 rows?
- Large datasets exceed the model's context window (128,000 tokens for gpt-4o-mini)
- You can't paste entire datasets into prompts

**Problem 2: LLMs Can't Do Math Reliably**
- The model uses probabilistic token prediction, not actual computation
- Simple calculations might work, but complex aggregations will fail
- **You cannot trust the LLM to do arithmetic accurately**

We need a better approach that scales and computes reliably.

---

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

---

## Step 2: Execute Code

Now we execute the generated code using Python's subprocess module to get a reliable computational result.

**Create an execution function:**
```python
import subprocess
import sys

def execute_code(code):
    try:
        # Write code to a temporary file
        with open("generated_code.py", "w") as f:
            f.write(code)

        # Execute
        result = subprocess.run(
            [sys.executable, "generated_code.py"],
            capture_output=True,  # Capture stdout and stderr
            text=True,            # Return output as string (not bytes)
            timeout=10
        )

        return result.stdout if result.returncode == 0 else result.stderr

    except Exception as e:
        return f"Error during execution: {str(e)}"
```

**Execute the generated code:**
```python
execution_result = execute_code(generated_code)
print("\nExecution Result:")
print(execution_result)
```

Output:

```
Execution Result:
87.6
```

Now we have a **reliable result computed by Python**, not guessed by the LLM.

**Security Warning:** Executing arbitrary LLM-generated code is dangerous in production. Use sandboxed environments (Docker containers, isolated VMs) in real applications.

---

## Step 3: Interpret Result

Finally, ask the LLM to explain the execution result in natural language. This completes the 3-step chain.

**Create an interpretation function:**
```python
def interpret_result(result, question):
    prompt = f"""
    Question: {question}

    Execution result:
    {result}

    Provide a clear, concise interpretation in 2-3 sentences.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    return response.choices[0].message.content
```

**Use it:**
```python
interpretation = interpret_result(execution_result, question)
print("Interpretation:")
print(interpretation)
```

Running the complete 3-step pipeline:

```
Step 1: Generating code...
Generated Code:
import pandas as pd

df = pd.read_csv('sample.csv')
average_score = df['Score'].mean()
print(average_score)

Step 2: Executing code...
Execution Result:
87.6


Step 3: Interpreting result...
Interpretation:
The average score across all individuals in the dataset is 87.6, indicating generally strong performance.
```

**Complete 3-step chain:**
1. **Generate Code** (LLM) - Writes Python code based on the schema
2. **Execute Code** (Python) - Reliably computes the result
3. **Interpret Result** (LLM) - Explains the result in natural language

This approach scales to large datasets and provides computational reliability while maintaining the flexibility of natural language interaction.

---

# Part 3: Building the UI

---

So far, we explored the 3-step chain through isolated examples—generating code, executing it, and interpreting results. Now we'll integrate these techniques into a complete web application with a structured user interface.

## Why Not Just a Chatbot?

Chatbots are the dominant interface for generative AI, but they're not always the best choice. For data analysis tasks, consider what a user must articulate:

> *"Show me the average rating for action movies released between 2010 and 2020, but only include movies with more than 1000 reviews"*

This requires precise language, knowledge of available columns, and careful specification of constraints. Users must translate their analytical intent into prose, which is error-prone and tedious.

**A structured UI solves this:**

- Filters for columns, genres, and date ranges are **visual controls** (checkboxes, sliders)
- The user asks a simpler question: "What is the average rating?"
- The system already knows the filtered context

This hybrid approach—structured input + natural language—reduces the articulation barrier while preserving the flexibility of prompting.

## Why Streamlit?

**Streamlit** turns Python scripts into interactive web apps with minimal code. You write normal Python, and Streamlit handles the HTML, CSS, and JavaScript.

### Installation

```bash
pip install streamlit
```

### Your First Streamlit App

```python
import streamlit as st

st.title("Hello Streamlit!")
st.write("Welcome to Streamlit")
```

Run it:
```bash
streamlit run app.py
```

This opens a browser window with your app. The terminal will display the URL (usually `http://localhost:8501` or a different port if 8501 is in use).

---

## Streamlit Concept 1: Displaying Content with `st.write()`

Streamlit's most versatile function is `st.write()`—it automatically handles different data types and renders them appropriately.

**Use `st.write()` for everything:**
```python
import streamlit as st
import pandas as pd

# Headers using markdown
st.write("# Data Analysis Tool")
st.write("This is regular text.")
```

You can create headers by passing markdown strings to `st.write()`. The `#` creates a large heading (equivalent to `<h1>` in HTML).

**`st.write()` also renders dataframes:**
```python
# Create sample data
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 28],
    'Score': [85, 92, 78]
}
df = pd.DataFrame(data)

# Display interactive table using st.write()
st.write(df)
```

When you pass a pandas DataFrame to `st.write()`, it automatically renders an interactive table with sorting and scrolling.

**Other specialized functions:**

Of course, Streamlit provides dedicated functions for specific use cases. For example, `st.title()` and `st.dataframe()` do the same jobs as the code above:

```python
st.title("Data Analysis Tool")  # Same as st.write("# Data Analysis Tool")
st.dataframe(df)                # Same as st.write(df)
```

You can find many more functions in the [Streamlit API Reference](https://docs.streamlit.io/develop/api-reference).

---

## Streamlit Concept 2: User Inputs

Streamlit provides widgets for collecting user input. Each widget returns a value that you can use in your code.

**Text input:**
```python
user_question = st.text_input(
    "Ask a question:",
    placeholder="e.g., What is the average score?"
)
```

The `placeholder` parameter shows hint text when the input is empty.

**Multiselect (choose multiple options):**
```python
selected_columns = st.multiselect("Select columns:", df.columns.tolist())
```

Returns a list of selected values.

**Slider (numeric range):**
```python
age_range = st.slider("Select age range:", 20, 40, (25, 35))
```

The parameters are: `(label, min_value, max_value, default_value)`. Returns a tuple `(start, end)` for range sliders.

**Button:**
```python
if st.button("Analyze"):
    st.write("Button clicked!")
```

Returns `True` when clicked, `False` otherwise.

---

## The Reactive Model

**Key concept:** When a user interacts with any widget, Streamlit **re-runs the entire script** from top to bottom.

Let's see what happens with the button in our code:

```python
if st.button("Analyze"):
    st.write("Button clicked!")

    if user_question:
        st.write(f"Your question: {user_question}")
    if selected_columns:
        st.write(f"Selected columns: {selected_columns}")
    st.write(f"Age range: {age_range[0]} to {age_range[1]}")
```

**Before clicking the button:**
- `st.button("Analyze")` returns `False`
- The `if` block doesn't execute
- You only see the input widgets

**After clicking the button:**
- The entire script re-runs from the beginning
- The screen is cleared and rebuilt from scratch
- `st.button("Analyze")` returns `True` (because it was just clicked)
- The `if` block executes and displays the results
- **Important:** Your input values (`user_question`, `selected_columns`, `age_range`) are preserved!

**Note:** While it's helpful to think of the screen being completely cleared and rebuilt, Streamlit is actually smarter—it only updates the parts that changed.

---

## Streamlit Concept 3: Sidebar

To organize controls and keep your main area clean, use `st.sidebar`. This creates a collapsible left panel where you can place input widgets.

**Create a sidebar with input controls:**
```python
import streamlit as st

st.title("Hello Streamlit")  # This is in the main area

# Sidebar: Get user's name
with st.sidebar:
    name = st.text_input("What's your name?")
    color = st.selectbox("Favorite color?", ["Red", "Blue", "Green"])
```

**Key point:** The `with st.sidebar:` block determines where widgets appear:
- **Inside the block** (indented): Appears in the sidebar on the left
- **Outside the block** (not indented): Appears in the main area on the right

In the code above:
- `st.title("Hello Streamlit")` is **outside** → appears in the main area
- `st.text_input()` and `st.selectbox()` are **inside** → appear in the sidebar

**Use sidebar values in the main area:**
```python
# Main area displays the sidebar inputs
st.write(f"Name: {name}")
st.write(f"Color: {color}")

if name:
    st.write(f"Hello, {name}!")
    st.write(f"Great choice! {color} is awesome.")
else:
    st.write("Enter your name to see a greeting.")
```

Notice that all these `st.write()` calls are **outside** the `with st.sidebar:` block, so they appear in the **main area**. The variables `name` and `color` were defined inside the sidebar block, but you can use them anywhere in your script.

The sidebar is perfect for filters, settings, and configuration options—keeping them separate from your main content display.

---

## Streamlit Concept 4: Layout Control

By default, Streamlit displays everything **vertically** (top to bottom). We learned that `st.sidebar` lets you place content **horizontally** (sidebar on the left, main area on the right). But what if you want to arrange content **horizontally within the main area** itself?

Use `st.columns()` to create side-by-side layouts. This is perfect for displaying related information in multiple columns.

**Create a two-column layout:**
```python
import streamlit as st

st.title("Hello Streamlit")

# Two-column layout
col1, col2 = st.columns(2)
```

`st.columns(2)` creates two columns of equal width. You can also specify different widths with ratios like `st.columns([1, 2])` for a 1:2 ratio.

**Place content in each column:**
```python
with col1:
    st.subheader("Your Input")
    st.write(f"Name: {name}")
    st.write(f"Color: {color}")

with col2:
    st.subheader("Our Response")
    if name:
        st.write(f"Hello, {name}!")
        st.write(f"Great choice! {color} is awesome.")
    else:
        st.write("Enter your name to see a greeting.")
```

Everything inside a `with col1:` or `with col2:` block appears in that specific column, allowing you to create sophisticated multi-column layouts.

---

## Building a Real Application

Now let's combine everything we've learned—**LLM-based analysis** (generate → execute → interpret) and **Streamlit UI** (display, inputs, sidebar, layout)—to build a real data analysis tool.

### Our Goal

Build a data analysis tool where:
1. Users **filter data visually** using sidebar controls (columns, genres, ratings, etc.)
2. Users **ask a factual question** about the filtered data (text input)
3. The system **generates Python code, executes it, and interprets the result** to answer the question

---

## Step 1: Setup Layout and Load Data

Let's work with a real movie dataset. Here's a preview of the first few rows:

```
Title,Worldwide Gross,Production Budget,Release Year,Content Rating,Running Time,Genre,Creative Type,Rotten Tomatoes Rating,IMDB Rating
From Dusk Till Dawn,25728961,20000000,1996,R,107,Horror,Fantasy,63,7.1
Broken Arrow,148345997,65000000,1996,R,108,Action,Contemporary Fiction,55,5.8
City Hall,20278055,40000000,1996,R,111,Drama,Contemporary Fiction,55,6.1
Happy Gilmore,38623460,10000000,1996,PG-13,92,Comedy,Contemporary Fiction,58,6.9
Fargo,51204567,7000000,1996,R,87,Thriller,Contemporary Fiction,94,8.3
```

Download the full dataset from the course repository and place it in the same directory as your `app.py`:

**Download:** https://github.com/bchaicourse/HAI2026-Week3-Practice/blob/main/movies.csv

**Configure the page and add a title:**
```python
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Analysis Tool", layout="wide")

st.title("Interactive Data Analysis Tool")
```

A data analysis app needs more horizontal space to display data, filters, and results. The `layout="wide"` parameter uses the full browser width. This must be the **first** Streamlit command.

**Load the dataset:**
```python
# Load data
df = pd.read_csv('movies.csv')
```

**Create the app structure:**

Now let's create a sidebar for filters and a two-column layout for displaying data and results:

```python
# Sidebar placeholder
with st.sidebar:
    st.header("Data Filters")
    st.write("Filters will go here...")

# Two-column layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Filtered Dataset")
    st.write(df)  # Show the full dataset for now

with col2:
    st.subheader("Analysis Results")
    st.write("Results will appear here...")
```

We've created the skeleton of our app:
- **Sidebar (left)**: Will contain our data filters
- **Column 1 (center-left)**: Will show the filtered dataset
- **Column 2 (center-right)**: Will display analysis results

---

## Step 2: Add Visual Filters

Now let's add filters to the sidebar so users can narrow down the data before analysis. We'll add two types of filters:
1. **Column filter**: Choose which columns to include
2. **Row filters**: Filter data by Genre, Release Year, and IMDB Rating

---

### Column Selection Filter

**Add column selection to the sidebar:**

```python
# Sidebar: Column selection
with st.sidebar:
    st.header("Data Filters")

    # Column selection
    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to include:",
        all_columns,
        default=all_columns
    )

    if not selected_columns:
        st.error("Please select at least one column.")
        st.stop()

    # Apply column filter
    filtered_df = df[selected_columns]
```

**Understanding the dual nature of this code:**

Notice how this code does two things simultaneously:

1. **UI Generation**: When `st.multiselect()` is called, Streamlit immediately renders a multiselect widget in the sidebar
2. **Data Filtering**: The function also returns the user's current selection, which is then used to filter the dataframe

Here's the flow:
- **First run** (when the page loads): `st.multiselect()` creates the widget AND returns the `default` value (all columns), so `filtered_df` starts with all columns
- **Subsequent runs** (when user changes selection): The script re-runs, `st.multiselect()` recreates the widget with the user's new selection, and `filtered_df` updates accordingly

`st.stop()` prevents errors if no columns are selected by halting script execution.

---

### Row Filters

**Add a subheader for row filters:**

```python
    # Row Filters
    st.subheader("Row Filters")
```

**Genre filter (multiselect):**

```python
    # Genre filter
    if 'Genre' in filtered_df.columns:
        genres = filtered_df['Genre'].dropna().unique()
        selected_genres = st.multiselect(
            "Filter by Genre:",
            genres,
            default=genres.tolist()
        )
        filtered_df = filtered_df[filtered_df['Genre'].isin(selected_genres)]
```

We check if the Genre column exists (in case user deselected it in the column filter above). Then we extract unique genres from `filtered_df`—the dataframe after column selection has been applied. After the user selects genres, we update `filtered_df` again by filtering rows. Notice how `filtered_df` gets progressively filtered: first by columns, then by genre.

**Release Year filter (slider):**

```python
    # Release Year filter
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
```

We calculate `min_year` and `max_year` from the current `filtered_df` (after column and genre filters). The slider returns a tuple `(start, end)`, which we use to further filter `filtered_df`.

**IMDB Rating filter (slider):**

```python
    # IMDB Rating filter
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
```

Same pattern: we compute `min_rating` and `max_rating` from `filtered_df` so the slider adapts to the current data.

---

### Maintain the Two-Column Layout

**Keep the same layout structure from Step 1:**

```python
# Two-column layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Filtered Dataset")
    st.write(filtered_df)

with col2:
    st.subheader("Analysis Results")
    st.write("Results will appear here...")
```

Now users have full control over their data—they can filter by columns, genres, years, and ratings. The filtered dataset displays in the left column, while the right column remains ready for analysis results in the next step.

---

## Step 3: Add Question Input

Now that users can filter data visually, let's add the natural language question interface. Users will type their questions in the left column, and results will appear in the right column.

---

### Update the Left Column

**Display the filtered dataset and add question input:**

```python
with col1:
    st.subheader("Filtered Dataset")
    st.write(filtered_df)

    st.subheader("Ask a Question")
    user_question = st.text_input(
        "What would you like to know about this data?",
        placeholder="e.g., What is the average IMDB rating?"
    )

    analyze_button = st.button("Analyze", type="primary")
```

The `st.text_input()` widget creates a text box for user questions. The `placeholder` parameter shows example text when the input is empty.

The `st.button()` with `type="primary"` creates a prominent button that users click to submit their question.

---

### Update the Right Column

**Add conditional logic to show results:**

```python
with col2:
    st.subheader("Analysis Results")

    if analyze_button and user_question:
        st.info("Analysis pipeline will be implemented in the next step...")
    elif analyze_button and not user_question:
        st.error("Please enter a question.")
    else:
        st.write("Enter a question and click 'Analyze' to see results.")
```

This creates three different states:

1. **Button clicked with a question**: Shows a placeholder message (we'll add the real LLM pipeline in Step 4)
2. **Button clicked without a question**: Shows an error
3. **Initial state**: Shows instructions

---

### How It Works

When a user types a question and clicks "Analyze":

1. The entire script re-runs (remember Streamlit's reactive model!)
2. `user_question` contains the text the user typed
3. `analyze_button` returns `True` because it was just clicked
4. The `if` condition is satisfied, and the placeholder message displays

In the next step, we'll replace the placeholder with the actual LLM-based analysis pipeline (generate → execute → interpret) that we learned in Part 2.

---

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
