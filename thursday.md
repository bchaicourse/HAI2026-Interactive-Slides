# Building an Interactive Data Analysis Tool (Part 2)

This post continues from [Building an Interactive Data Analysis Tool (Part 1)](https://datawithinreach.notion.site/Building-an-Interactive-Data-Analysis-Tool-Part-1-2ee7a47fd21780beb1cbe8ef0387d3be). In that post, we built a Streamlit app where users filter a movie dataset with sidebar controls and ask questions in natural language. The app used a hardcoded 3-step pipeline to answer those questions: generate Python code, execute it, and interpret the result. It worked, but the pipeline was rigid. If the generated code failed, the app showed the error and stopped. If a question needed a different approach, the pipeline could not adapt.

In this post, we turn that static pipeline into an **agentic** system. Instead of following fixed steps, the LLM will choose its own tools, reason about intermediate results, retry when something goes wrong, and pause for human approval before taking action.

**What we will build:** An upgraded version of the Part 1 app where the LLM autonomously selects tools, reasons through multi-step analysis, self-corrects when code fails, and requests human approval before executing actions. The result is a data analysis agent that can recover from mistakes and respond to user feedback in real time.

> **What you will learn:**
> - How to define tools and let the LLM choose which ones to call (function calling)
> - How to build a multi-turn tool calling loop where the LLM observes results and decides next steps
> - How to implement the ReAct (Reasoning + Acting) pattern for transparent, self-correcting agents
> - How to separate state, logic, and rendering for maintainable agentic UIs
> - How to add human-in-the-loop controls: approval gates and rejection with feedback

# Part 1: Function Calling

## From Hardcoded Pipelines to Tool Selection

**Function calling** lets the LLM choose which tools to use and with what arguments, instead of following a fixed pipeline. Before applying this to our data analysis tool, let's understand how it works with a simple example.

## Defining Tools with Pydantic

A tool definition tells the LLM what a tool does and what arguments it expects. The OpenAI SDK provides `pydantic_function_tool` to generate tool definitions from Pydantic models:

```python
from openai import pydantic_function_tool
from pydantic import BaseModel, Field

class Plus(BaseModel):
    """Add two numbers together."""
    a: float = Field(description="The first number")
    b: float = Field(description="The second number")
```

- The **class docstring** (`"""Add two numbers together."""`) becomes the tool's description
- Each **field** becomes a parameter with its type and description

Calling `pydantic_function_tool(Plus)` converts this Pydantic model into a JSON structure:

```json
{
  "type": "function",
  "function": {
    "name": "Plus",
    "strict": true,
    "parameters": {
      "description": "Add two numbers together.",
      "properties": {
        "a": { "description": "The first number", "title": "A", "type": "number" },
        "b": { "description": "The second number", "title": "B", "type": "number" }
      },
      "required": ["a", "b"],
      "title": "Plus",
      "type": "object",
      "additionalProperties": false
    },
    "description": "Add two numbers together."
  }
}
```

You don't need to memorize this structure. It's a predefined format for communicating tool information between your code and the API. The key fields to understand are:

- **`name`**: The class name, used as the tool identifier.
- **`description`**: From the docstring. The LLM reads this to decide *when* to use the tool.
- **`parameters`**: From the fields. The LLM uses this to construct valid arguments.

## Letting the LLM Choose Tools

We've defined what tools are available. Now the question is: how do we let the LLM actually *know about* these tools so it can decide to use them?

The answer is the `tools` parameter. When making an API call, we pass our tool definitions alongside the user's message:

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is 123789 multiplied by 4564560?"}],
    tools=tools   # <-- this is what makes the LLM aware of our tools
)
```

By including `tools=tools`, the LLM can now see the name, description, and parameters of every tool we defined. It will read those descriptions and decide on its own whether any tool is relevant to the user's question.

### Reading the Model's Response

Once the LLM responds, there are two possible outcomes:

1. The model **wants to use a tool** (the response contains `tool_calls`)
2. The model **answers directly** with text (no tools needed)

We can check which case it is:

```python
message = response.choices[0].message

if message.tool_calls:
    tool_call = message.tool_calls[0]
    print(tool_call.function.name)       # which tool it chose
    print(tool_call.function.arguments)  # what arguments it wants to pass
else:
    print(message.content)              # direct text response
```

### Seeing It in Action

Let's try sending three different queries to the same model with the same two tools (`Plus` and `Multiply`), and see how the model decides differently depending on the question.

**Query 1: "What is 123789 multiplied by 4564560?"**
```
Tool called: Multiply
Arguments:   {"a":123789,"b":4564560}
```

The model recognizes this as a multiplication problem, picks the `Multiply` tool, and extracts the two numbers as arguments.

**Query 2: "What is 123789 plus 4564560?"**
```
Tool called: Plus
Arguments:   {"a":123789,"b":4564560}
```

Same idea, different tool. The model picks `Plus` this time.

**Query 3: "What is the capital of France?"**
```
Response: The capital of France is Paris.
```

This question has nothing to do with math. The model decides that neither `Plus` nor `Multiply` is relevant, so it skips the tools entirely and responds with plain text.

### Important: The Model Didn't Compute Anything

Notice that the model only said *what it wants to call* and *with what arguments*. It did not actually perform the calculation. The response is a structured request, not an answer.

## Executing the Tool Call

It's our job to take the model's response and actually execute it. First, we define the actual Python functions that do the work:

```python
def plus(a, b):
    return a + b

def multiply(a, b):
    return a * b
```

Then, when the model returns a tool call, we need to:

1. **Parse the arguments**: They come back as a JSON string, so we use `json.loads` to convert them into a Python dictionary.
2. **Match the tool name**: Check which function the model requested and call it with the parsed arguments.

```python
name = tool_call.function.name
args = json.loads(tool_call.function.arguments)

if name == "Multiply":
    result = multiply(args["a"], args["b"])
elif name == "Plus":
    result = plus(args["a"], args["b"])
```

This is an important distinction to keep in mind: the LLM chose the right tool and extracted the arguments from natural language, but **Python is doing the actual computation**. The model never calculated `123789 * 4564560` itself.

---

Running this with the query "What is 123789 multiplied by 4564560?" produces:

```
Tool called: Multiply
Arguments:   {'a': 123789, 'b': 4564560}
Result:      565042317840
```

---

## The Tool Calling Loop

So far, we've been handling a single tool call: the model picks a tool, we execute it, and we print the result. But the model never saw that result. It was a one-shot interaction.

What if a question requires multiple steps? Consider: **What is ((123789 + 4564569) * 999999) + 333221?**

This needs three operations in sequence, where each step depends on the previous result:
1. `Plus(123789, 4564569)` → 4688358
2. `Multiply(4688358, 999999)` → 4688353311642
3. `Plus(4688353311642, 333221)` → 4688353644863

No single tool call can solve this. The model needs to call a tool, see its result, use that result to decide the next tool call, and repeat until it has the final answer. To make this possible, we need two things: a **loop** and a **message history** that accumulates results.

### How the Loop Works

Here's the full loop:

```python
for i in range(10):  # safety limit to prevent infinite loops
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        parallel_tool_calls=False
    )

    message = response.choices[0].message

    if message.tool_calls:
        messages.append(message)

        for tool_call in message.tool_calls:
            # execute and append result...
            messages.append({
                "role": "tool",
                "content": str(result),
                "tool_call_id": tool_call.id
            })
    else:
        print(message.content)  # final answer
        break
```

Let's walk through what each part does:

**1. Send the full message history to the model.**

```python
response = client.chat.completions.create(
    ...
    messages=messages,
    ...
)
```

Every iteration calls the API with `messages=messages`. This list contains the original user question, every tool call the model has made so far, and every result we've sent back. The model sees the entire conversation history each time.

**2. If the model responds with `tool_calls`, execute and feed the result back.**

```python
if message.tool_calls:
    messages.append(message)

    for tool_call in message.tool_calls:
        # execute and append result...
        messages.append({
            "role": "tool",
            "content": str(result),
            "tool_call_id": tool_call.id
        })
```

We first append the model's own response to the history, then execute the tool and append its result with `"role": "tool"`. Notice `tool_call_id`: each tool call the model makes has a unique ID, and we include it in the result so the API can match each result to the specific call that requested it. This is the key mechanism: by adding the result back to `messages`, the model can see what happened and use it to decide the next step.

**3. If the model responds with text, stop.**

```python
else:
    print(message.content)  # final answer
    break
```

When the model has enough information to answer, it returns plain text instead of a tool call. We print it and `break` out of the loop.

### Why `parallel_tool_calls=False`?

You may have noticed another parameter in the API call:

```python
response = client.chat.completions.create(
    ...
    parallel_tool_calls=False
)
```

By default, the model is allowed to request multiple tool calls in a single turn. For example, if you asked "What is 2+3 and 4*5?", the model could call both `Plus` and `Multiply` at the same time, which would be efficient.

But for our sequential calculation, that would be a problem. The model might try to call both `Plus` and `Multiply` at once, before knowing the result of the first step. Setting `parallel_tool_calls=False` forces the model to request one tool call at a time, ensuring each step completes before the next one begins.

---

Running the loop with the query "What is ((123789 + 4564569) * 999999) + 333221?" produces:

```
Step 1: Plus(123789, 4564569) = 4688358
Step 2: Multiply(4688358, 999999) = 4688353311642
Step 3: Plus(4688353311642, 333221) = 4688353644863

Final answer: The result of ((123789 + 4564569) × 999999) + 333221 is 4,688,353,644,863.
```

The model called three tools in sequence, using each result as input for the next step, then synthesized the final answer in plain text.

---

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

---

The complete terminal output for the example above looks like this:

```
Step 1: QueryMovieDB
  Code:   df.nlargest(5, 'IMDB Rating')[['Title', 'IMDB Rating']]
  Result: No output. Did you forget to use print()?

Step 2: QueryMovieDB
  Code:   print(df.nlargest(5, 'IMDB Rating')[['Title', 'IMDB Rating']])
  Result:                Title  IMDB Rating
  706        Inception          9.1
  639  The Dark Knight          8.9
  183       Fight Club          8.8
  151       The Matrix          8.7
  708         The Town          8.7

Final answer:
The top 5 highest-rated movies by IMDB Rating are:
1. Inception - 9.1
2. The Dark Knight - 8.9
3. Fight Club - 8.8
4. The Matrix - 8.7
5. The Town - 8.7
```

The model recovered from its own mistake, produced real results, and summarized them in natural language.

---

## The ReAct Pattern

In the tool calling loop we built, the model jumps straight from question to tool call without explaining *why* it's choosing that tool or what it plans to do. It works, but we have no visibility into the model's decision-making process.

The **ReAct** (Reasoning + Acting) pattern addresses this by splitting each iteration into two explicit steps:

1. **Thought**: The model reasons about the current situation and decides what to do next.
2. **Action**: The model calls a tool, or provides the final answer.

### Structured Reasoning with Pydantic

To make the model's reasoning explicit, we define a `Reasoning` model using Pydantic's structured output:

```python
class Reasoning(BaseModel):
    reason: str = Field(
        description="Your reasoning about what you know so far and what to do next"
    )
    use_tool: bool = Field(
        description="True if you need to run code, False if you can give the final answer"
    )
    answer: Optional[str] = Field(
        default=None,
        description="Your final answer. Only provide when use_tool is False."
    )
```

There are three fields here:

- **`reason`**: The model writes out its thinking. This makes each step transparent and debuggable.
- **`use_tool`**: A boolean that explicitly tells us whether the model wants to call a tool or is ready to answer. This replaces the `for i in range(10)` safety limit from before. Instead of guessing when the model is done, we get a clear signal.
- **`answer`**: The final answer, only provided when `use_tool` is `False`.

### The Loop: Two API Calls Per Iteration

The ReAct loop makes two separate API calls each iteration. Here's the full structure:

```python
while True:
    # 1. Reasoning: structured output, no tools
    response = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        response_format=Reasoning,
    )
    reasoning = response.choices[0].message.parsed
    messages.append({"role": "assistant", "content": reasoning.reason})

    if not reasoning.use_tool:
        print(reasoning.answer)
        break

    # 2. Acting: tools available
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=[QueryMovieDBTool],
        parallel_tool_calls=False
    )

    message = response.choices[0].message

    if message.tool_calls:
        messages.append(message)

        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = query_movie_db(args["code"])

            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.id
            })
```

Let's break this down:

**1. The Reasoning call:**

```python
response = client.chat.completions.parse(
    model="gpt-4o-mini",
    messages=messages,
    response_format=Reasoning,
)
reasoning = response.choices[0].message.parsed
```

This uses `response_format=Reasoning` with no `tools` parameter. The model is forced to output structured JSON with its reasoning and decision. We use `client.chat.completions.parse` instead of `.create` so the response is automatically parsed into our `Reasoning` model. If `use_tool` is `False`, we print the answer and stop.

**Appending the reasoning to the message history:**

```python
messages.append({"role": "assistant", "content": reasoning.reason})
```

This is crucial. The model's reasoning is added to the message history *before* the Acting call. This way, the Acting call can see the model's own plan and act on it.

**2. The Acting call:**

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=[QueryMovieDBTool],
    parallel_tool_calls=False
)
```

This uses `tools=[QueryMovieDBTool]` with no `response_format`. Because the model's reasoning is already in the message history, it acts on its own plan and calls the appropriate tool.

**3. Execute and feed results back:**

```python
messages.append(message)

for tool_call in message.tool_calls:
    args = json.loads(tool_call.function.arguments)
    result = query_movie_db(args["code"])

    messages.append({
        "role": "tool",
        "content": result,
        "tool_call_id": tool_call.id
    })
```

Same as the tool calling loop from before: we execute the tool, append the result to the message history, and the loop continues with the next Reasoning call.

### Thought, Action, Observation

Let's see what this looks like in practice with the same question as before:

```
Thought: I need to query the database for top-rated movies...

Action: QueryMovieDB
Code:   df.nlargest(5, 'IMDB Rating')[['Title', 'IMDB Rating']]
Observation: No output. Did you forget to use print()?

Thought: I forgot print(). Let me fix that...

Action: QueryMovieDB
Code:   print(df.nlargest(5, 'IMDB Rating')[['Title', 'IMDB Rating']])
Observation: (actual data)

Thought: I now have the data. → use_tool: false
Answer: 1. Inception - 9.1 ...
```

Each thought explains *why* the model is taking its next action. When something goes wrong (the missing `print()`), the model reasons about the error before retrying. This makes the entire process transparent and easy to follow.

---

The complete terminal output for the ReAct loop looks like this:

```
Thought: I need to query the movie database to find out which movies have the
         top 5 highest IMDB ratings.

Action: QueryMovieDB
Code:   df.nlargest(5, 'IMDB Rating')
Observation: No output. Did you forget to use print()?

Thought: I forgot to print the results. I need to run the query again
         with print().

Action: QueryMovieDB
Code:   print(df.nlargest(5, 'IMDB Rating'))
Observation:
            Title  Worldwide Gross  ...  IMDB Rating
706        Inception        753830280  ...          9.1
639  The Dark Knight       1022345358  ...          8.9
183       Fight Club        100853753  ...          8.8
151       The Matrix        460279930  ...          8.7
708         The Town         33180607  ...          8.7

Thought: I now have the data. I can provide the final answer.

Answer:
1. Inception - IMDB Rating: 9.1
2. The Dark Knight - IMDB Rating: 8.9
3. Fight Club - IMDB Rating: 8.8
4. The Matrix - IMDB Rating: 8.7
5. The Town - IMDB Rating: 8.7
```

Compared to the tool calling loop output, each step now starts with a Thought that makes the model's reasoning visible. The Thought → Action → Observation cycle repeats until the model has enough information to produce a final Answer.

---

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

---

**What you should see:** The app looks identical to the Lecture 1 version: sidebar filters on the left, a question input and "Analyze" button in the middle, and analysis results on the right. The only difference is under the hood, where the hardcoded 3-step pipeline has been replaced with a single round of tool calling.

---

## Adding the ReAct Loop to the UI

Now we integrate the ReAct pattern from Part 1, giving the model the ability to reason, retry, and self-correct.

### Designing the Layout

The ReAct loop produces multiple rounds of Thought, Action, and Observation before reaching a final answer. We need to display all of this in a way that isn't overwhelming. Here's the plan:

1. **`st.container(height=600)`**: The reasoning trace can get long, so we wrap everything in a fixed-height scrollable container to prevent the results panel from growing endlessly.
2. **`st.expander("Agent Reasoning Trace")`**: Inside the container, the step-by-step trace (Thought/Action/Observation) goes into a collapsible section. It stays open during execution so the user can watch the progress, but can be collapsed afterwards.
3. **Final answer outside the expander**: The model's final answer is displayed below the expander, so the user can always see it without scrolling through the trace.

### The Code

The `Reasoning` model and the `while True` loop structure are the same as Part 1. The difference is that each step is now rendered with Streamlit components:

```python
results_container = st.container(height=600)

with results_container:
    with st.expander("Agent Reasoning Trace", expanded=True):
        while True:
            # Reasoning call...
            st.markdown(f"**Thought:** {reasoning.reason}")

            if not reasoning.use_tool:
                break

            # Acting call...
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    ...
                    st.markdown(f"**Action:** `{name}`")
                    st.code(args["code"], language='python')
                    st.markdown("**Observation:**")
                    st.code(result, language="text")
                    st.divider()

    st.write("**Answer:**")
    st.write(reasoning.answer)
```

Each iteration renders three things inside the expander:
- **Thought:** the model's reasoning about what to do next
- **Action:** the tool it called and the code it generated
- **Observation:** the execution result (or error message)

When the loop ends (the model sets `use_tool` to `False`), the final answer appears below the expander, inside the container but outside the collapsible trace.

---

**What you should see:** When you ask a question, the right panel now shows a scrollable "Agent Reasoning Trace" expander. Inside it, each step displays the model's **Thought**, the **Action** it took (with the generated code), and the **Observation** (execution result or error). If the model's code fails, it automatically retries. The final answer appears below the collapsed expander.

---

## Separating State, Logic, and UI

### The Problem

This works, but state updates, API calls, and UI rendering are all interleaved inside a single `while True` loop:

```python
with st.expander("Agent Reasoning Trace", expanded=True):
    while True:
        response = client.chat.completions.parse(...)   # logic
        st.markdown(f"**Thought:** {reasoning.reason}")  # UI
        response = client.chat.completions.create(...)   # logic
        result = query_movie_db(args["code"], ...)       # logic
        st.code(args["code"], language='python')          # UI
        messages.append(...)                              # state
```

This works, but it's fragile. Want to add a new tool? You have to modify the loop. Want to change how results are displayed? You have to touch the same block that handles API calls. Every new feature means rewriting this tightly coupled code.

To be fair, this coupling is by design in Streamlit. It's what makes simple UIs so easy to build. For example, our sidebar filters create UI widgets and filter data in the same block, and that works great. But for agentic AI interactions with multiple phases, retries, and growing complexity, keeping everything in one loop becomes unmanageable. It helps to separate concerns explicitly.

We do this by extracting the entire `col2` block into a new file, `agent_panel.py`, and splitting it into three parts: **state**, **logic**, and **rendering**.

### What Does "Separating State, Logic, and UI" Mean?

Before looking at the code, let's clarify what these three concerns are:

- **State**: The data that describes the current situation. What phase is the agent in? What messages have been exchanged? What events have occurred? State is *stored* and *updated*, but it doesn't do any computation or draw anything on screen.
- **Logic**: The part that *changes* the state. It makes API calls, executes tools, and decides what phase to move to next. It reads the current state, does work, and writes new state. But it never touches the UI.
- **Rendering**: The part that *reads* the state and draws it on screen. It decides what to show based on the current phase and events. But it never makes API calls or changes the state.

The key idea is that each part only does its own job. Logic doesn't render. Rendering doesn't mutate state. This makes each piece simple and independently modifiable.

### State

All agent data lives in `st.session_state`, which persists across reruns. We access it through two simple helpers:

```python
def get_state(key):
    return st.session_state.get(key, DEFAULT_STATE[key])

def set_state(key, value):
    st.session_state[key] = value
```

The agent tracks its current **phase** and four pieces of data:

```python
DEFAULT_STATE = {
    "agent_phase": "idle",
    "agent_events": [],
    "agent_messages": [],
    "agent_tools": [],
    "agent_df": None,
}
```

- **`agent_phase`**: Where the agent is in its lifecycle (`idle`, `thinking`, `acting`, `done`).
- **`agent_events`**: A list of events (thoughts, actions, answers) used for rendering.
- **`agent_messages`**: The message history sent to the API.
- **`agent_tools`**: The tool definitions.
- **`agent_df`**: The filtered DataFrame.

When the user clicks Analyze, `restart_agent()` resets all of these and sets the phase to `"thinking"` to kick off the loop:

```python
def restart_agent(user_question, filtered_df):
    set_state("agent_phase", "thinking")
    set_state("agent_events", [])
    set_state("agent_messages", [
        {"role": "system", "content": "..."},
        {"role": "user", "content": user_question},
    ])
    set_state("agent_tools", get_tools(filtered_df))
    set_state("agent_df", filtered_df)
```

### Logic

`run_step()` checks the current phase and does exactly one thing per call:

**When `phase == "thinking"`:**

```python
response = client.chat.completions.parse(
    model="gpt-4o-mini", messages=messages, response_format=Reasoning,
)
reasoning = response.choices[0].message.parsed

if reasoning.use_tool:
    get_state("agent_events").append({"type": "thought", ...})
    set_state("agent_phase", "acting")
else:
    get_state("agent_events").append({"type": "answer", ...})
    set_state("agent_phase", "done")
```

Call the reasoning API. If the model wants a tool, record the thought as an event and move to `"acting"`. If not, record the answer and move to `"done"`.

**When `phase == "acting"`:**

```python
response = client.chat.completions.create(
    model="gpt-4o-mini", messages=messages, tools=tools, ...
)
for tc in msg.tool_calls:
    result = query_movie_db(args["code"], df)
    get_state("agent_events").append({"type": "action", ...})

set_state("agent_phase", "thinking")
```

Call the tool API, execute the code, record the action as an event, and move back to `"thinking"`. The phase transitions form a simple cycle: `thinking → acting → thinking → ... → done`.

### Rendering

`render_panel()` reads `agent_phase` and renders accordingly. It never makes API calls or mutates state:

```python
def render_panel():
    st.subheader("Analysis Results")
    container = st.container(height=600)
    with container:
        phase = get_state("agent_phase")

        if phase == "idle":
            st.info("Enter a question and click 'Analyze' to see results.")

        elif phase in ("thinking", "acting"):
            with st.expander("Agent Reasoning Trace", expanded=True):
                render_events()
            st.spinner("Agent is thinking...")

        elif phase == "done":
            with st.expander("Agent Reasoning Trace", expanded=False):
                render_events()
            events = get_state("agent_events")
            if events and events[-1].get("answer"):
                st.write("**Answer:**")
                st.write(events[-1]["answer"])
```

- **`idle`**: A placeholder message.
- **`thinking` / `acting`**: The event trace so far (expanded) with a spinner.
- **`done`**: The event trace (collapsed by default) and the final answer below it.

`render_events()` iterates over the `agent_events` list and draws each one based on its type:

```python
def render_events():
    for event in get_state("agent_events"):
        if event["type"] == "thought":
            st.markdown(f"**Thought:** {event['thought']}")
        elif event["type"] == "action":
            st.markdown(f"**Action:** `{event['name']}`")
            st.code(event["code"], language="python")
            st.markdown("**Observation:**")
            st.code(event["result"], language="text")
            st.divider()
        elif event["type"] == "answer":
            st.markdown(f"**Thought:** {event['thought']}")
```

Notice the pattern here: `render_panel()` handles the overall layout, and delegates the event rendering to `render_events()`. This is a useful pattern. You can break UI code into small functions that each render one piece, then compose them together in a parent function. It keeps each function focused and easy to modify independently.

### Putting It All Together: `agent_panel()`

Now that we've seen each piece, here's how they're orchestrated. In `app.py`, the right column becomes a single function call. We pass in everything the agent panel needs to know about the current context: the API client, whether the user clicked Analyze, what question they asked, and the current filtered data:

```python
with col2:
    agent_panel(client, analyze_button, user_question, filtered_df)
```

Inside `agent_panel()`, the three concerns run in order:

```python
def agent_panel(client, analyze_button, user_question, filtered_df):
    if analyze_button and user_question:
        restart_agent(user_question, filtered_df)   # 1. state

    render_panel()                                   # 2. rendering

    if get_state("agent_phase") in ("thinking", "acting"):
        run_step(client)                             # 3. logic
        st.rerun()
```

1. **`restart_agent()`** (State): If the user clicked Analyze, reset all state and set the phase to `"thinking"`. If the user hasn't clicked yet, the state remains at its default, which is `"idle"`.
2. **`render_panel()`** (Rendering): Look at the current state and draw the appropriate UI.
3. **`run_step()`** (Logic): If the agent is still working, advance it by one step and update the state.

### Why `st.rerun()`?

Notice the `st.rerun()` after `run_step()`. This is how we replace the `while True` loop.

In the previous step, the loop ran inside a single script execution: call API, render, call API, render, repeat. Now, each iteration is a *separate run of the entire script*. Here's the flow:

1. Script runs → `render_panel()` draws the current state → `run_step()` advances one step → `st.rerun()`
2. Script runs again from the top → `render_panel()` draws the updated state → `run_step()` advances another step → `st.rerun()`
3. This continues until the agent reaches the `"done"` phase, at which point `run_step()` is not called and the script stops rerunning.

This might seem like extra complexity, but each rerun follows the same simple sequence: reset if needed, render, step, rerun. And as we'll see next, this separation makes it easy to add new features without rewriting existing code.

---

**What you should see:** The app behaves identically to the previous step. The refactoring is purely internal: the code is now split into `app.py` (layout and sidebar) and `agent_panel.py` (state, logic, rendering). No visible changes for the user.

---

## Adding a Chart Tool

Let's put that to the test by adding a second tool: one that lets the agent create chart visualizations.

### New File: `chart_tool.py`

Vega-Lite is a widely used standard for describing charts as JSON. You don't need to know the details of how it works. The important thing is: if the LLM generates a valid JSON spec, Streamlit can turn it directly into a chart. Just like our code execution tool, an invalid spec will produce an error, but a correct one renders a visualization.

We implement this as a new tool following the same pattern as `movie_tool.py`:

```python
class CreateChart(BaseModel):
    """Create a chart visualization using a Vega-Lite specification."""
    vega_lite_spec: str = Field(
        description="A complete Vega-Lite JSON specification string, "
                    "including inline data under 'data.values'."
    )
```

The tool takes one parameter: a JSON string. We validate it using `altair`, a Python library that ships with Streamlit, and return a result string to the agent:

```python
def validate_chart(vega_lite_spec):
    try:
        spec = json.loads(vega_lite_spec)
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"

    try:
        alt.Chart.from_dict(spec)
        return spec, "Valid Vega-Lite specification."
    except Exception as e:
        return None, f"Invalid Vega-Lite specification: {e}"
```

If the spec is valid, we return it for rendering. If not, the error message goes back to the agent as its observation, giving it a chance to fix the spec and retry.

### Changes to `app.py`

We add a checkbox that lets the user opt into chart generation. The `show_chart` value is passed to `agent_panel()`:

```python
show_chart = st.checkbox("Show chart")
...
agent_panel(client, analyze_button, user_question, filtered_df, show_chart)
```

### Changes to `agent_panel.py`

Because we separated concerns above, each layer gets a small, focused addition.

**State**: One new key to store validated chart specs. When `show_chart` is `True`, `restart_agent()` adds the chart tool to the tool list and nudges the system prompt to tell the model to create a visualization. Without this prompt nudge, the model often computes the data but doesn't think to visualize it:

```python
DEFAULT_STATE = {
    ...
    "agent_chart_specs": [],
}

def restart_agent(user_question, filtered_df, show_chart=False):
    ...
    if show_chart:
        tools.append(get_chart_tool())
        system_content += " After computing the data, create a chart..."
```

**Logic**: The `acting` phase now needs to handle two different tools. Recall from Part 1 that the tool's name comes from the Pydantic class name. We use `tc.function.name` to dispatch to the right handler:

```python
for tc in msg.tool_calls:
    args = json.loads(tc.function.arguments)

    if tc.function.name == "QueryMovieDB":
        result = query_movie_db(args["code"], df)
        get_state("agent_events").append({"type": "action", ...})
    elif tc.function.name == "CreateChart":
        spec, result = validate_chart(args["vega_lite_spec"])
        if spec:
            get_state("agent_chart_specs").append(spec)
        get_state("agent_events").append({"type": "chart", ...})
```

Valid specs are stored in `agent_chart_specs` for rendering later. Invalid specs produce an error message that goes back to the model so it can fix the spec on its next turn.

**Rendering**: `render_events()` handles the new `"chart"` event type by displaying the spec as JSON:

```python
elif event["type"] == "chart":
    st.markdown(f"**Action:** `{event['name']}`")
    st.code(event["spec_str"], language="json")
    st.markdown("**Observation:**")
    st.code(event["result"], language="text")
```

And `render_panel()` displays the collected charts below the answer when the agent is done:

```python
elif phase == "done":
    ...
    for spec in get_state("agent_chart_specs"):
        st.vega_lite_chart(spec, use_container_width=True)
```

This is the payoff of the separation we did above. Adding a completely new tool required small, isolated changes to each layer, without rewriting any existing logic.

---

**What you should see:** A new "Show chart" checkbox appears in the sidebar. When enabled, the agent creates a Vega-Lite chart visualization after computing the data. The chart renders below the final answer in the results panel. If the chart spec is invalid, the error appears in the reasoning trace and the model retries with a corrected spec.

---

# Part 3: Human-in-the-Loop

## Adding an Approval Step

Up until now, the agent executes tools automatically. It decides to run code and runs it immediately. But in real-world applications, you often want a human to review what the agent is about to do *before* it happens, especially when the tool has side effects like writing to a database, sending an email, or spending money.

We add an approval step: before each tool execution, the agent pauses and shows the user what it wants to do. The user clicks **Approve** to let it proceed.

### A New Phase: `awaiting_approval`

The state machine so far has been:

```
idle → thinking ↔ acting → done
```

We insert a new phase between `acting` and the actual tool execution:

```
idle → thinking → acting → awaiting_approval → thinking → ... → done
```

The key change is that the `acting` phase no longer executes the tool. Instead, it stores the proposed tool calls in state and moves to `awaiting_approval`. The tool only runs when the user clicks Approve.

### Changes to `agent_panel.py`

Again, each layer gets a focused change.

**State**: One new key to hold the pending message while waiting for approval:

```python
DEFAULT_STATE = {
    ...
    "agent_pending_message": None,
}
```

**Logic**: Here is the full logic layer. `run_step()` changes its `acting` branch, and a new `execute_pending_tools()` function is added:

```python
def run_step(client):
    phase = get_state("agent_phase")
    messages = get_state("agent_messages")

    if phase == "thinking":
        ...                         # unchanged from before

    elif phase == "acting":
        tools = get_state("agent_tools")
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages,
            tools=tools, parallel_tool_calls=False,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            set_state("agent_phase", "done")
            return

        set_state("agent_pending_message", msg)
        set_state("agent_phase", "awaiting_approval")

def execute_pending_tools():
    messages = get_state("agent_messages")
    df = get_state("agent_df")
    pending_msg = get_state("agent_pending_message")

    messages.append(pending_msg)
    for tc in pending_msg.tool_calls:
        args = json.loads(tc.function.arguments)
        if tc.function.name == "QueryMovieDB":
            result = query_movie_db(args["code"], df)
            ...
        elif tc.function.name == "CreateChart":
            spec, result = validate_chart(args["vega_lite_spec"])
            ...
        messages.append({"role": "tool", "content": result, "tool_call_id": tc.id})

    set_state("agent_pending_message", None)
    set_state("agent_phase", "thinking")
```

Previously, the `acting` branch executed tools immediately and looped back to `thinking`. Now it just stores the message and pauses:

```python
set_state("agent_pending_message", msg)
set_state("agent_phase", "awaiting_approval")
```

The actual execution moves into `execute_pending_tools()`. We don't need to store tool calls separately since they're accessible as `pending_msg.tool_calls`:

```python
pending_msg = get_state("agent_pending_message")

messages.append(pending_msg)
for tc in pending_msg.tool_calls:
```

This is the same execution code as before, just moved into its own function that only runs after the user approves.

**Rendering**: Here is the full rendering layer:

```python
def render_pending_approval():
    st.warning("The agent wants to perform the following action:")
    for tc in get_state("agent_pending_message").tool_calls:
        args = json.loads(tc.function.arguments)
        st.markdown(f"**Tool:** `{tc.function.name}`")
        if tc.function.name == "QueryMovieDB":
            st.code(args["code"], language="python")
        elif tc.function.name == "CreateChart":
            st.code(args["vega_lite_spec"], language="json")

def render_panel():
    st.subheader("Analysis Results")
    container = st.container(height=600)
    approved = False
    with container:
        phase = get_state("agent_phase")

        if phase == "idle":
            ...                     # unchanged
        elif phase in ("thinking", "acting"):
            ...                     # unchanged
        elif phase == "awaiting_approval":
            with st.expander("Agent Reasoning Trace", expanded=True):
                render_events()
            render_pending_approval()
            approved = st.button("Approve", type="primary", use_container_width=True)
        elif phase == "done":
            ...                     # unchanged

    return approved
```

A new helper `render_pending_approval()` displays a warning with the proposed tool call and its arguments, so the user can see exactly what code the agent wants to run before approving.

`render_panel()` now initializes `approved = False` at the top and returns it at the end. The Approve button only exists inside the `awaiting_approval` branch:

```python
elif phase == "awaiting_approval":
    ...
    approved = st.button("Approve", type="primary", use_container_width=True)
```

So in all other phases, `approved` stays `False`. It only becomes `True` when the user actually clicks the button.

**Lifecycle**: Here is the full lifecycle:

```python
def agent_panel(client, analyze_button, user_question, filtered_df, show_chart=False):
    if analyze_button and user_question:
        restart_agent(user_question, filtered_df, show_chart)

    approved = render_panel()

    phase = get_state("agent_phase")
    if phase in ("thinking", "acting"):
        run_step(client)
        st.rerun()
    elif phase == "awaiting_approval" and approved:
        execute_pending_tools()
        st.rerun()
```

`render_panel()` runs every time the page renders, regardless of the current phase. As we saw above, `approved` is only `True` when the user clicks the Approve button during `awaiting_approval`. One new `elif` branch handles this:

```python
elif phase == "awaiting_approval" and approved:
    execute_pending_tools()
    st.rerun()
```

Notice how naturally this fits into the existing structure. We added one new phase, split the acting logic into "propose" and "execute", added one render function, and added one lifecycle branch. Everything else remains unchanged, including `app.py`, `chart_tool.py`, and `movie_tool.py`.

---

**What you should see:** Before each tool execution, the agent pauses and displays the proposed action in a warning box: the code it wants to run or the chart spec it wants to create. An "Approve" button appears below. The agent only proceeds after the user clicks Approve.

---

## Rejecting with Feedback

The user can now approve actions, but what if the agent's plan looks wrong? Maybe it's querying the wrong column, or using the wrong aggregation. The user needs a way to say "no" and explain *why*, so the agent can adjust its approach.

We add a **Reject** button alongside Approve. When the user rejects, they can type feedback explaining what the agent should do differently. The agent receives this feedback and tries again.

### A New Phase: `awaiting_feedback`

The state machine so far has one path from `awaiting_approval`:

```
... → awaiting_approval → (Approve) → thinking → ...
```

We add a second path:

```
... → awaiting_approval → (Approve) → thinking → ...
                        → (Reject)  → awaiting_feedback → (Submit) → thinking → ...
```

Both paths return to `thinking`. The difference is what the agent sees as its tool result: either the actual execution output (Approve), or a rejection message with the user's feedback (Reject).

### Changes to `agent_panel.py`

**Logic**: Here is the full logic layer. `execute_pending_tools()` is unchanged, and a new `reject_pending_tools()` function is added:

```python
def execute_pending_tools():
    ...                             # unchanged from before

def reject_pending_tools(feedback):
    messages = get_state("agent_messages")
    pending_msg = get_state("agent_pending_message")

    rejection_msg = "User rejected this action."
    if feedback:
        rejection_msg += f" User feedback: {feedback}"
    else:
        rejection_msg += " Try a different approach."

    messages.append(pending_msg)
    for tc in pending_msg.tool_calls:
        get_state("agent_events").append({
            "type": "rejected", "name": tc.function.name,
            "feedback": feedback,
        })
        messages.append({
            "role": "tool",
            "content": rejection_msg,
            "tool_call_id": tc.id,
        })

    set_state("agent_pending_message", None)
    set_state("agent_phase", "thinking")
```

The OpenAI API requires every tool call to have a corresponding tool result message. Instead of the actual execution result, we send the rejection as the tool result:

```python
messages.append({
    "role": "tool",
    "content": rejection_msg,
    "tool_call_id": tc.id,
})
```

The agent receives this rejection as its "observation" and reasons about it in the next Thought step. For example, if the user rejects a query and says "use IMDB Rating, not Rating", the agent sees that feedback and retries with the corrected column name.

**Rendering**: Here is the full rendering layer:

```python
def render_pending_approval():
    st.warning("The agent wants to perform the following action:")
    for tc in get_state("agent_pending_message").tool_calls:
        args = json.loads(tc.function.arguments)
        st.markdown(f"**Tool:** `{tc.function.name}`")
        if tc.function.name == "QueryMovieDB":
            st.code(args["code"], language="python")
        elif tc.function.name == "CreateChart":
            st.code(args["vega_lite_spec"], language="json")

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        approved = st.button("Approve", type="primary", use_container_width=True)
    with btn_col2:
        rejected = st.button("Reject", use_container_width=True)
    return approved, rejected

def render_pending_feedback():
    feedback = st.text_input(
        "Why are you rejecting? Tell the agent what to do instead:",
        key="reject_feedback",
    )
    submitted = st.button("Submit Rejection", use_container_width=True)
    return submitted, feedback

def render_panel():
    st.subheader("Analysis Results")
    container = st.container(height=600)
    actions = {}
    with container:
        phase = get_state("agent_phase")

        if phase == "idle":
            ...                     # unchanged
        elif phase in ("thinking", "acting"):
            ...                     # unchanged
        elif phase == "awaiting_approval":
            with st.expander("Agent Reasoning Trace", expanded=True):
                render_events()
            approved, rejected = render_pending_approval()
            actions = {"approved": approved, "rejected": rejected}
        elif phase == "awaiting_feedback":
            with st.expander("Agent Reasoning Trace", expanded=True):
                render_events()
            submitted, feedback = render_pending_feedback()
            actions = {"submitted": submitted, "feedback": feedback}
        elif phase == "done":
            ...                     # unchanged

    return actions
```

`render_pending_approval()` now shows two buttons side by side and returns both values:

```python
btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    approved = st.button("Approve", type="primary", use_container_width=True)
with btn_col2:
    rejected = st.button("Reject", use_container_width=True)
return approved, rejected
```

A new `render_pending_feedback()` shows a text input where the user can explain why they're rejecting.

`render_panel()` now returns an `actions` dictionary instead of a single boolean, since there are multiple possible user interactions depending on the phase. In `awaiting_approval`, it collects Approve/Reject. In `awaiting_feedback`, it collects the feedback text and Submit button. In all other phases, `actions` stays as an empty `{}`:

```python
actions = {}
...
    elif phase == "awaiting_approval":
        ...
        actions = {"approved": approved, "rejected": rejected}
    elif phase == "awaiting_feedback":
        ...
        actions = {"submitted": submitted, "feedback": feedback}
...
return actions
```

`render_events()` also handles the new `"rejected"` event type, displaying the rejection and the user's feedback in the trace.

**Lifecycle**: Here is the full lifecycle:

```python
def agent_panel(client, analyze_button, user_question, filtered_df, show_chart=False):
    if analyze_button and user_question:
        restart_agent(user_question, filtered_df, show_chart)

    actions = render_panel()

    phase = get_state("agent_phase")
    if phase in ("thinking", "acting"):
        run_step(client)
        st.rerun()
    elif phase == "awaiting_approval":
        if actions.get("approved"):
            execute_pending_tools()
            st.rerun()
        elif actions.get("rejected"):
            set_state("agent_phase", "awaiting_feedback")
            st.rerun()
    elif phase == "awaiting_feedback" and actions.get("submitted"):
        reject_pending_tools(actions.get("feedback", ""))
        st.rerun()
```

The `awaiting_approval` branch now splits into two sub-branches. If the user clicks Approve, tools execute as before. If they click Reject, the phase moves to `awaiting_feedback`:

```python
elif phase == "awaiting_approval":
    if actions.get("approved"):
        execute_pending_tools()
        st.rerun()
    elif actions.get("rejected"):
        set_state("agent_phase", "awaiting_feedback")
        st.rerun()
```

A new branch handles the feedback submission. When the user types their feedback and clicks Submit, `reject_pending_tools()` sends the rejection message to the model and the agent resumes from `thinking`:

```python
elif phase == "awaiting_feedback" and actions.get("submitted"):
    reject_pending_tools(actions.get("feedback", ""))
    st.rerun()
```

Once again, `app.py`, `chart_tool.py`, and `movie_tool.py` are completely unchanged. The entire reject-with-feedback feature lives in `agent_panel.py`: one new logic function, two new render functions, and two new lifecycle branches.

---

**What you should see:** The "Approve" button is now joined by a "Reject" button. Clicking Reject reveals a text input where the user can explain what the agent should do differently. After submitting the feedback, the agent reads it, reasons about it in its next Thought step, and tries a different approach.
