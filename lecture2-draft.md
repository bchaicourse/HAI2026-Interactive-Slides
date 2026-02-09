This continues from ______________(Part 1). In Part 1, we built a data analysis tool with a **hardcoded 3-step pipeline**:

1. **Generate Code** (LLM writes Python code based on the user's question)
2. **Execute Code** (Python subprocess runs the code)
3. **Interpret Result** (LLM explains the output in natural language)

This worked, but the pipeline was rigid. The user asked a question, and the system always followed the same three steps in the same order. If the generated code failed, it just showed an error. If the question required multiple steps of analysis, the system could not handle it. The LLM had no say in *what* to do; it only filled in the blanks of a predetermined workflow.

Today, we replace that hardcoded pipeline with an **agent** that decides for itself which tools to use, in what order, and how many times. By the end of this session, the same data analysis app will be powered by a ReAct loop where the LLM reasons about the question, picks a tool, observes the result, and repeats until it has an answer. We will also add a human-in-the-loop mechanism so the user can approve or reject each action before it runs.

---

# Part 1: Function Calling

---

## From Hardcoded Pipelines to Tool Selection

In Week 3, our code looked roughly like this:

```python
code = generate_code(question, schema)    # always step 1
result = execute_code(code, filtered_df)  # always step 2
answer = interpret_result(result, question) # always step 3
```

The LLM had no choice. It always generated code, we always executed it, and we always asked for an interpretation. What if the question is "Show me a bar chart of average rating by genre"? The pipeline has no charting step at all. What if the generated code crashes? The pipeline just shows the error and stops.

**Function calling** solves this by letting the LLM choose. Instead of us deciding the workflow, we describe a set of available tools, and the LLM decides which one(s) to call and with what arguments. The LLM does not execute the tools itself. It outputs a structured request ("call `execute_code` with this Python code"), our system executes it, and we feed the result back.

---

## Defining Tools

A tool definition tells the LLM what the tool does and what arguments it expects. The OpenAI API accepts tool definitions as JSON objects with three key fields: `name`, `description`, and `parameters`.

### Tool 1: `execute_code`

This tool runs Python code against the dataset, just like in Week 3. The LLM generates pandas code, and we execute it in a subprocess.

```python
import subprocess
import sys

def execute_code(code, filtered_df):
    try:
        filtered_df.to_csv('temp_data.csv', index=False)

        full_code = f"""import pandas as pd
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

        if result.returncode == 0:
            return result.stdout if result.stdout else "Code executed successfully (no output)."
        else:
            return f"Error:\\n{result.stderr}"

    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (10 second limit)."
    except Exception as e:
        return f"Error: {str(e)}"
```

Tool definition as JSON:

```python
execute_code_tool = {
    "type": "function",
    "function": {
        "name": "execute_code",
        "description": "Execute Python code to analyze the dataset. The code runs in an environment where pandas and numpy are imported and the dataset is loaded as a DataFrame called 'df'. The code MUST use print() to output results. If the code fails, the error message is returned.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute. Must use print() to output results. The DataFrame 'df' is already loaded."
                }
            },
            "required": ["code"],
            "additionalProperties": False
        }
    }
}
```

This is essentially the same execution mechanism as Week 3. The difference is that now the LLM calls it as a tool rather than being forced to use it as the first step of a fixed pipeline.

### Tool 2: `create_chart`

This tool takes a Vega-Lite JSON specification and renders it as a chart. Vega-Lite is a declarative grammar for creating visualizations, and Streamlit has built-in support for rendering it via `st.vega_lite_chart`.

```python
import json

def create_chart(vega_lite_spec):
    try:
        spec = json.loads(vega_lite_spec)
        return json.dumps(spec)
    except Exception as e:
        return f"Error parsing Vega-Lite spec: {str(e)}"
```

```python
create_chart_tool = {
    "type": "function",
    "function": {
        "name": "create_chart",
        "description": "Create a visualization by providing a Vega-Lite JSON specification. The data should be included inline in the spec under the 'data.values' field. Use this when the user asks for a visualization, chart, plot, or graph.",
        "parameters": {
            "type": "object",
            "properties": {
                "vega_lite_spec": {
                    "type": "string",
                    "description": "A complete Vega-Lite JSON specification string, including inline data under 'data.values'."
                }
            },
            "required": ["vega_lite_spec"],
            "additionalProperties": False
        }
    }
}
```

**Why Vega-Lite?** The agent needs to produce a chart that Streamlit can render. Vega-Lite specs are JSON objects, which the LLM can generate reliably as structured text. Streamlit renders them natively with `st.vega_lite_chart(spec)`. You do not need to learn Vega-Lite syntax; the LLM handles that.

### Collecting Tools

```python
tools = [execute_code_tool, create_chart_tool]
```

---

## How Function Calling Works

Function calling follows a 5-step conversation flow:

**Step 1: Send the user's message along with tool definitions.**

```python
messages = [
    {"role": "system", "content": "You are a data analysis assistant."},
    {"role": "user", "content": "What is the average IMDB rating?"}
]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools
)
```

**Step 2: Check if the model wants to call a tool.**

The model's response will either contain regular text (it answered directly) or a `tool_calls` list (it wants to use a tool).

```python
message = response.choices[0].message

if message.tool_calls is None:
    # Model responded directly with text
    print(message.content)
else:
    # Model wants to call one or more tools
    for tool_call in message.tool_calls:
        print(f"Tool: {tool_call.function.name}")
        print(f"Args: {tool_call.function.arguments}")
```

**Step 3: Execute the requested tool.**

```python
tool_call = message.tool_calls[0]
func_name = tool_call.function.name
arguments = json.loads(tool_call.function.arguments)

# Call the actual function
if func_name == "execute_code":
    result = execute_code(arguments["code"], filtered_df)
elif func_name == "create_chart":
    result = create_chart(arguments["vega_lite_spec"])
```

**Step 4: Send the tool result back to the model.**

```python
# Append the assistant's tool call message
messages.append(message)

# Append the tool result
messages.append({
    "role": "tool",
    "content": str(result),
    "tool_call_id": tool_call.id
})
```

The `tool_call_id` links the result back to the specific tool call the model made. This is required by the API.

**Step 5: Get the model's final response.**

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools
)

print(response.choices[0].message.content)
```

The model now has the tool result in its context and can compose a natural language answer.

---

## Key Observation

Notice that this 5-step flow is just one round of tool use. The model called one tool, got one result, and produced a final answer. But what if the question requires multiple tools? For example: "Show me a bar chart of average IMDB rating by genre." The model would need to:

1. Call `execute_code` to calculate average rating by genre
2. Call `create_chart` to produce the visualization

Or what if the first code attempt fails? The model would need to read the error, fix the code, and try again. A single round of function calling cannot do this. We need a **loop**.

---

# Part 2: The ReAct Loop

---

## From One-Shot to Iterative

The ReAct pattern (Reasoning + Acting) extends function calling into an iterative loop. Instead of calling a tool once and stopping, the agent repeats a cycle:

1. **Think** about the current situation
2. **Act** by calling a tool
3. **Observe** the result
4. Go back to step 1, or produce a final answer

This is the core of what makes an agent autonomous: it decides on its own when to call tools, when to try again after an error, and when it has enough information to answer.

## Implementing the ReAct Loop

The implementation is a `for` loop that keeps calling the model until it stops requesting tools:

```python
def run_agent(question, system_prompt, tools, filtered_df, max_iterations=10):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    for i in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )

        message = response.choices[0].message

        # If no tool calls, the agent is done
        if message.tool_calls is None:
            return message.content, messages

        # Save the assistant's message (with tool call info)
        messages.append(message)

        # Execute each tool call
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if func_name == "execute_code":
                result = execute_code(arguments["code"], filtered_df)
            elif func_name == "create_chart":
                result = create_chart(arguments["vega_lite_spec"])

            messages.append({
                "role": "tool",
                "content": str(result),
                "tool_call_id": tool_call.id
            })

    return "Max iterations reached.", messages
```

This is exactly the 5-step function calling flow from Part 1, wrapped in a loop. Each iteration:

1. Calls the model with the full message history.
2. Checks if the model wants to call a tool.
3. If yes, executes the tool, appends the result, and loops back.
4. If no, the model's text response is the final answer. The loop ends.

The `max_iterations` parameter is a safety net to prevent infinite loops.

---

## The System Prompt

The system prompt guides how the agent reasons. We embed the dataset schema directly, so the agent knows what columns and types are available without needing a separate tool.

```python
def get_dataframe_schema(df):
    schema = f"Columns: {df.columns.tolist()}\\n"
    schema += f"Data types:\\n{df.dtypes.to_string()}\\n"
    schema += f"Shape: {df.shape}\\n"
    schema += f"\\nSample data (first 3 rows):\\n{df.head(3).to_string()}"
    return schema

def build_system_prompt(filtered_df):
    schema = get_dataframe_schema(filtered_df)
    return f"""You are a data analysis assistant. You help users analyze a movie dataset by using the tools available to you.

You operate in a loop of Thought, Action, and Observation:

Thought: Reason about what you need to do next.
Action: Call one of the available tools.
Observation: Review the result of the tool call.

Repeat this cycle until you have enough information to answer the user's question. When you are ready, provide a clear final answer.

Dataset schema:
{schema}

Guidelines:
- Use execute_code to run Python code on the DataFrame 'df'. Always use print() to output results.
- Use create_chart when the user asks for a visualization. You must first use execute_code to compute the data, then pass the computed results as inline data in a Vega-Lite spec.
- If code returns an error, read the error message carefully and try a corrected version.
"""
```

---

## Seeing It in Action

Let's trace through a concrete example. The user asks: "What genre has the highest average IMDB rating?"

**Iteration 1:**

```
Thought: I need to calculate the average IMDB rating per genre.
Action: execute_code("print(df.groupby('Genre')['IMDB Rating'].mean().sort_values(ascending=False).head())")
Observation:
Genre
Musical     6.88
Horror      6.22
Adventure   6.19
...
```

**Iteration 2 (Final Answer):**

```
The genre with the highest average IMDB rating is Musical, with an average rating of 6.88.
```

Now consider what happens when the agent makes an error:

**Iteration 1 (with error):**

```
Thought: I'll calculate the average rating by genre.
Action: execute_code("print(df.groupby('genre')['imdb_rating'].mean())")
Observation: Error: KeyError: 'genre'
```

**Iteration 2 (self-correction):**

```
Thought: The column names are case-sensitive. Let me check them.
Action: execute_code("print(df.columns.tolist())")
Observation: ['Title', 'Worldwide Gross', ..., 'Genre', ..., 'IMDB Rating']
```

**Iteration 3 (corrected query):**

```
Action: execute_code("print(df.groupby('Genre')['IMDB Rating'].mean().sort_values(ascending=False))")
Observation: [results]
```

This self-correction is what makes the ReAct loop qualitatively different from the Week 3 pipeline. In Week 3, the error would have been shown to the user and that was it.

---

# Part 3: Human-in-the-Loop

---

## Why Not Just Let the Agent Run?

The `run_agent` function from Part 2 executes all tool calls automatically. The agent decides, acts, and moves on without asking the user. This is efficient, but recall Tuesday's discussion about agent autonomy: an agent that never asks permission is a liability. Our agent runs arbitrary Python code. Even with a subprocess sandbox, the user should have the opportunity to review what the agent wants to execute before it actually runs.

The goal is to **pause the agent when it wants to call a tool**, show the user what action is planned, and let them approve or reject it. If rejected, the agent receives feedback that the action was denied and tries a different approach.

## The Challenge with Streamlit

Streamlit's reactive model reruns the entire script from top to bottom on every user interaction. This means we cannot simply pause a Python loop mid-execution and wait for a button click. Instead, we need to save the agent's state to `st.session_state` so it survives across reruns.

## Step-by-Step Agent with Session State

Instead of a single `run_agent` function that loops to completion, we split the logic into smaller functions:

**`agent_step`**: Run one iteration of the agent. If the model wants to call a tool, return the pending tool calls without executing them.

```python
def agent_step(state):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=state["messages"],
        tools=tools
    )

    message = response.choices[0].message

    if message.content:
        state["trace"].append({"type": "thought", "content": message.content})

    if message.tool_calls is None:
        state["status"] = "done"
        state["answer"] = message.content
        return state

    # Pause: tool calls need approval
    state["status"] = "pending_approval"
    state["pending_tool_calls"] = message.tool_calls
    state["pending_assistant_message"] = message
    return state
```

**`execute_approved_tools`**: Called when the user clicks "Approve". Executes the pending tool calls and continues.

```python
def execute_approved_tools(state, filtered_df):
    message = state["pending_assistant_message"]
    state["messages"].append(message)

    for tool_call in state["pending_tool_calls"]:
        func_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if func_name == "execute_code":
            result = execute_code(arguments["code"], filtered_df)
        elif func_name == "create_chart":
            result = create_chart(arguments["vega_lite_spec"])

        state["trace"].append({
            "type": "tool_call",
            "tool": func_name,
            "arguments": arguments,
            "result": result
        })

        state["messages"].append({
            "role": "tool",
            "content": str(result),
            "tool_call_id": tool_call.id
        })

    state["pending_tool_calls"] = None
    state["pending_assistant_message"] = None
    state["status"] = "running"
    return state
```

**`reject_pending_tools`**: Called when the user clicks "Reject". Feeds a rejection message back to the agent so it can try a different approach.

```python
def reject_pending_tools(state):
    message = state["pending_assistant_message"]
    state["messages"].append(message)

    for tool_call in state["pending_tool_calls"]:
        state["trace"].append({
            "type": "tool_call_rejected",
            "tool": tool_call.function.name,
            "arguments": json.loads(tool_call.function.arguments)
        })

        state["messages"].append({
            "role": "tool",
            "content": "User rejected this action. Try a different approach or ask the user for clarification.",
            "tool_call_id": tool_call.id
        })

    state["pending_tool_calls"] = None
    state["pending_assistant_message"] = None
    state["status"] = "running"
    return state
```

**`init_agent_state`**: Creates the initial state when the user clicks "Analyze".

```python
def init_agent_state(question, filtered_df):
    system_prompt = build_system_prompt(filtered_df)
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "trace": [],
        "status": "running",
        "pending_tool_calls": None,
        "pending_assistant_message": None,
        "answer": None,
        "iteration": 0,
        "max_iterations": 10
    }
```

The state dictionary persists in `st.session_state` across Streamlit reruns. Each button click triggers a rerun, but the agent picks up exactly where it left off.

---

# Part 4: Building the Streamlit App

---

## Step 1: Setup and Dependencies

```python
import streamlit as st
import pandas as pd
import subprocess
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Agentic Data Analysis", layout="wide")
st.title("Agentic Data Analysis Tool")
```

Your `requirements.txt`:

```
openai
python-dotenv
streamlit
```

No new dependencies compared to Week 3.

---

## Step 2: Load Data, Tools, and Agent Functions

This section contains everything from Parts 1-3: tool functions, tool JSON definitions, schema helper, system prompt builder, and the four agent state functions (`init_agent_state`, `agent_step`, `execute_approved_tools`, `reject_pending_tools`).

---

## Step 3: Sidebar Filters

The sidebar filters are identical to Week 3.

```python
with st.sidebar:
    st.header("Data Filters")

    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to include:", all_columns, default=all_columns
    )

    if not selected_columns:
        st.error("Please select at least one column.")
        st.stop()

    filtered_df = df[selected_columns]

    st.subheader("Row Filters")

    if 'Genre' in filtered_df.columns:
        genres = filtered_df['Genre'].dropna().unique()
        selected_genres = st.multiselect("Filter by Genre:", genres, default=genres.tolist())
        filtered_df = filtered_df[filtered_df['Genre'].isin(selected_genres)]

    if 'Release Year' in filtered_df.columns:
        min_year = int(filtered_df['Release Year'].min())
        max_year = int(filtered_df['Release Year'].max())
        year_range = st.slider("Filter by Release Year:", min_year, max_year, (min_year, max_year))
        filtered_df = filtered_df[
            (filtered_df['Release Year'] >= year_range[0]) &
            (filtered_df['Release Year'] <= year_range[1])
        ]

    if 'IMDB Rating' in filtered_df.columns:
        min_rating = float(filtered_df['IMDB Rating'].min())
        max_rating = float(filtered_df['IMDB Rating'].max())
        rating_range = st.slider("Filter by IMDB Rating:", min_rating, max_rating, (min_rating, max_rating))
        filtered_df = filtered_df[
            (filtered_df['IMDB Rating'] >= rating_range[0]) &
            (filtered_df['IMDB Rating'] <= rating_range[1])
        ]
```

---

## Step 4: Session State and Main Layout

Initialize session state and create the two-column layout:

```python
if "agent_state" not in st.session_state:
    st.session_state.agent_state = None

col1, col2 = st.columns(2)

with col1:
    st.subheader("Filtered Dataset")
    st.write(filtered_df)

    st.subheader("Ask a Question")
    user_question = st.text_input(
        "What would you like to know about this data?",
        placeholder="e.g., What genre has the highest average IMDB rating?"
    )
    analyze_button = st.button("Analyze", type="primary")
```

When the user clicks "Analyze", we create a fresh agent state and run the first step:

```python
if analyze_button and user_question:
    st.session_state.agent_state = init_agent_state(user_question, filtered_df)
    st.session_state.agent_state = agent_step(st.session_state.agent_state)
    st.rerun()
```

---

## Step 5: Rendering the Agent State

The right column renders differently depending on the agent's status:

**When `status == "done"`**: Show the reasoning trace in a collapsible expander, the final answer, and any charts.

**When `status == "pending_approval"`**: Show the trace so far, then display the pending action with "Approve" and "Reject" buttons.

```python
with col2:
    st.subheader("Analysis Results")
    state = st.session_state.agent_state

    if state is None:
        st.write("Enter a question and click 'Analyze' to see results.")

    elif state["status"] == "done":
        with st.expander("Agent Reasoning Trace", expanded=False):
            for step in state["trace"]:
                if step["type"] == "thought":
                    st.markdown(f"**Thought:** {step['content']}")
                elif step["type"] == "tool_call":
                    st.markdown(f"**Tool:** `{step['tool']}`")
                    if step["tool"] == "execute_code":
                        st.code(step["arguments"]["code"], language="python")
                    else:
                        st.code(json.dumps(step["arguments"], indent=2), language="json")
                    st.text(f"Result: {step['result'][:500]}")
                elif step["type"] == "tool_call_rejected":
                    st.markdown(f"**Rejected:** `{step['tool']}`")
                st.divider()

        st.markdown("**Answer:**")
        st.write(state["answer"])

        for step in state["trace"]:
            if step["type"] == "tool_call" and step["tool"] == "create_chart":
                try:
                    spec = json.loads(step["result"])
                    st.vega_lite_chart(spec, use_container_width=True)
                except:
                    pass

    elif state["status"] == "pending_approval":
        # Show trace so far
        if state["trace"]:
            with st.expander("Agent Reasoning Trace (so far)", expanded=True):
                # ... render trace steps ...

        # Show the pending action
        st.warning("The agent wants to perform the following action:")
        for tool_call in state["pending_tool_calls"]:
            func_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            st.markdown(f"**Tool:** `{func_name}`")
            if func_name == "execute_code":
                st.code(arguments["code"], language="python")
            elif func_name == "create_chart":
                st.code(arguments["vega_lite_spec"], language="json")

        # Approve / Reject buttons
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("Approve", type="primary", use_container_width=True):
                state = execute_approved_tools(state, filtered_df)
                # Continue running until next approval or done
                while state["status"] == "running" and state["iteration"] < state["max_iterations"]:
                    state = agent_step(state)
                    state["iteration"] += 1
                    if state["status"] != "running":
                        break
                st.session_state.agent_state = state
                st.rerun()

        with btn_col2:
            if st.button("Reject", use_container_width=True):
                state = reject_pending_tools(state)
                # Agent tries a different approach
                while state["status"] == "running" and state["iteration"] < state["max_iterations"]:
                    state = agent_step(state)
                    state["iteration"] += 1
                    if state["status"] != "running":
                        break
                st.session_state.agent_state = state
                st.rerun()
```

---

## What Changed from Week 3

| Aspect | Week 3 | Week 6 |
| --- | --- | --- |
| **Analysis engine** | Hardcoded 3-step pipeline (generate, execute, interpret) | ReAct agent loop (think, act, observe, repeat) |
| **Tool selection** | Always generates Python code, always interprets | Agent chooses between `execute_code` and `create_chart` |
| **Error handling** | Shows error to user | Agent reads error, corrects code, retries automatically |
| **Visualization** | None | Vega-Lite charts via `create_chart` tool |
| **Transparency** | Shows generated code and raw output | Shows full reasoning trace (thoughts + tool calls + results) |
| **User control** | None (pipeline runs automatically) | Approve/Reject buttons before each tool execution |
| **Interpretation** | Separate LLM call to interpret results | Agent interprets results as part of its natural reasoning |

---

# Comparing Approaches: ReAct Prompt vs. Default Prompt

It is worth understanding the effect of the system prompt on agent behavior. Try replacing the detailed ReAct system prompt with a minimal one:

```python
def build_system_prompt(filtered_df):
    schema = get_dataframe_schema(filtered_df)
    return f"""You are a helpful data analysis assistant. Use the supplied tools to assist the user.

Dataset schema:
{schema}
"""
```

For simple questions like "What is the average IMDB rating?", both prompts produce similar results. The model calls `execute_code` and returns an answer.

For complex questions that require multiple steps or error recovery, the ReAct prompt tends to produce more deliberate, step-by-step reasoning. The minimal prompt may be less systematic in its approach.

In practice, modern models handle tool calling loops well even without explicit ReAct instructions. The detailed prompt is most useful as a teaching tool to make the reasoning process visible.

---

# Summary: From Prompting to Agents

| Concept | Tuesday (Theory) | Thursday (Implementation) |
| --- | --- | --- |
| **Tools** | Function calling as the mechanism for LLMs to act on the world | Defined 2 tools (`execute_code`, `create_chart`) with JSON schemas |
| **Autonomy (ReAct)** | Think-Act-Observe loop for multi-step reasoning | `for` loop that repeats until no more tool calls |
| **Transparency** | Design challenge of how much to show the user | Reasoning trace displayed in `st.expander` |
| **Error recovery** | Self-correction as a key capability of autonomous agents | Agent reads Python errors and retries with corrected code |
| **Human-in-the-loop** | Tension between autonomy and safety; choosing the right level of control | Approve/Reject buttons pause the agent before each tool execution |

**What we did not implement today:**

- **Memory (RAG)**: Tuesday covered how agents can retrieve from external documents via embeddings and vector stores. This is a viable extension for the Discussion Assignment.
- **Memory (Conversation History)**: Our agent currently handles one question at a time. Maintaining conversation history across questions is another extension opportunity.

The complete implementation is available at: [repository link]