import streamlit as st
import pandas as pd
import subprocess
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

# --- Setup ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
st.set_page_config(page_title="Agentic Data Analysis", layout="wide")
st.title("Agentic Data Analysis Tool")

# --- Load Data ---
df = pd.read_csv("movies.csv")

# --- Tool Functions ---

def execute_code(code, filtered_df):
    try:
        filtered_df.to_csv("temp_data.csv", index=False)

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
            timeout=10,
        )

        if result.returncode == 0:
            return result.stdout if result.stdout else "Code executed successfully (no output)."
        else:
            return f"Error:\n{result.stderr}"

    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (10 second limit)."
    except Exception as e:
        return f"Error: {str(e)}"


def create_chart(vega_lite_spec):
    try:
        spec = json.loads(vega_lite_spec)
        return json.dumps(spec)
    except Exception as e:
        return f"Error parsing Vega-Lite spec: {str(e)}"


# --- Tool Definitions (JSON for API) ---

tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": (
                "Execute Python code to analyze the dataset. "
                "The code runs in an environment where pandas and numpy are imported "
                "and the dataset is loaded as a DataFrame called 'df'. "
                "The code MUST use print() to output results. "
                "If the code fails, the error message is returned."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute. Must use print() to output results. The DataFrame 'df' is already loaded.",
                    }
                },
                "required": ["code"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_chart",
            "description": (
                "Create a visualization by providing a Vega-Lite JSON specification. "
                "The data should be included inline in the spec under the 'data.values' field. "
                "Use this when the user asks for a visualization, chart, plot, or graph."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "vega_lite_spec": {
                        "type": "string",
                        "description": "A complete Vega-Lite JSON specification string, including inline data under 'data.values'.",
                    }
                },
                "required": ["vega_lite_spec"],
                "additionalProperties": False,
            },
        },
    },
]

# --- Schema Helper and System Prompt ---

def get_dataframe_schema(target_df):
    schema = f"Columns: {target_df.columns.tolist()}\n"
    schema += f"Data types:\n{target_df.dtypes.to_string()}\n"
    schema += f"Shape: {target_df.shape}\n"
    schema += f"\nSample data (first 3 rows):\n{target_df.head(3).to_string()}"
    return schema


def build_system_prompt(filtered_df):
    schema = get_dataframe_schema(filtered_df)
    return f"""You are a data analysis assistant. You help users analyze a movie dataset by using the tools available to you.

You MUST operate in a strict loop of Thought → Action → Observation → Thought → ...

CRITICAL RULES:
1. You MUST always output a Thought (text reasoning) BEFORE making any tool call. Never call a tool without explaining your reasoning first.
2. After receiving a tool result (Observation), you MUST write a Thought analyzing the result BEFORE calling another tool or giving a final answer.
3. When using execute_code, you MUST wrap every result in print(). For example: print(df.describe()), print(df.groupby('Genre')['IMDB Rating'].mean()). NEVER write bare expressions like df.head() without print(). If you get "no output", it means you forgot print().

Dataset schema:
{schema}

Guidelines:
- Use execute_code to run Python code on the DataFrame 'df'. ALWAYS use print() to output results. Never write bare expressions.
- Use create_chart when the user asks for a visualization. You must first use execute_code to compute the data, then pass the computed results as inline data in a Vega-Lite spec.
- If code returns an error, read the error message carefully, explain what went wrong in your Thought, and try a corrected version.
"""


# --- Agent Runner (step-by-step with human-in-the-loop) ---

def agent_reasoning_step(state):
    """Force the agent to reason (no tool calls) about the latest observation."""
    messages = state["messages"]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="none",
    )

    message = response.choices[0].message

    if message.content:
        state["trace"].append({"type": "thought", "content": message.content})
        state["messages"].append({"role": "assistant", "content": message.content})

    return state


def agent_step(state):
    """Run one iteration of the agent. Returns the updated state.

    state keys:
        messages: list  - conversation messages for the API
        trace: list     - UI-friendly trace of thoughts/tool calls
        status: str     - "pending_approval", "running", "done"
        pending_tool_calls: list - tool calls awaiting user approval
        pending_assistant_message: obj - the assistant message that produced the pending tool calls
        answer: str     - final answer (set when status == "done")
    """
    messages = state["messages"]

    # If the last message is a tool result, force a reasoning step first
    if messages and messages[-1].get("role") == "tool":
        state = agent_reasoning_step(state)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=state["messages"],
        tools=tools,
    )

    message = response.choices[0].message

    # Record any text the model produced
    if message.content:
        state["trace"].append({"type": "thought", "content": message.content})

    # If no tool calls, the agent is done
    if message.tool_calls is None:
        state["status"] = "done"
        state["answer"] = message.content
        return state

    # Tool calls exist: pause for human approval
    state["status"] = "pending_approval"
    state["pending_tool_calls"] = message.tool_calls
    state["pending_assistant_message"] = message
    return state


def execute_approved_tools(state, filtered_df):
    """Execute the pending tool calls after user approval."""
    message = state["pending_assistant_message"]
    state["messages"].append(message)

    for tool_call in state["pending_tool_calls"]:
        func_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if func_name == "execute_code":
            result = execute_code(arguments["code"], filtered_df)
        elif func_name == "create_chart":
            result = create_chart(arguments["vega_lite_spec"])
        else:
            result = f"Unknown tool: {func_name}"

        state["trace"].append({
            "type": "tool_call",
            "tool": func_name,
            "arguments": arguments,
            "result": result,
        })

        state["messages"].append({
            "role": "tool",
            "content": str(result),
            "tool_call_id": tool_call.id,
        })

    # Clear pending state and continue
    state["pending_tool_calls"] = None
    state["pending_assistant_message"] = None
    state["status"] = "running"
    return state


def reject_pending_tools(state, feedback=""):
    """Handle user rejection: tell the agent the action was denied, with optional feedback."""
    message = state["pending_assistant_message"]
    state["messages"].append(message)

    rejection_msg = "User rejected this action."
    if feedback:
        rejection_msg += f" User feedback: {feedback}"
    else:
        rejection_msg += " Try a different approach or ask the user for clarification."

    for tool_call in state["pending_tool_calls"]:
        state["trace"].append({
            "type": "tool_call_rejected",
            "tool": tool_call.function.name,
            "arguments": json.loads(tool_call.function.arguments),
            "feedback": feedback,
        })

        state["messages"].append({
            "role": "tool",
            "content": rejection_msg,
            "tool_call_id": tool_call.id,
        })

    state["pending_tool_calls"] = None
    state["pending_assistant_message"] = None
    state["status"] = "running"
    return state


def init_agent_state(question, filtered_df):
    """Create a fresh agent state."""
    system_prompt = build_system_prompt(filtered_df)
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        "trace": [],
        "status": "running",
        "pending_tool_calls": None,
        "pending_assistant_message": None,
        "answer": None,
        "iteration": 0,
        "max_iterations": 10,
    }


# --- Sidebar Filters ---

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

    if "Genre" in filtered_df.columns:
        genres = filtered_df["Genre"].dropna().unique()
        selected_genres = st.multiselect(
            "Filter by Genre:", genres, default=genres.tolist()
        )
        filtered_df = filtered_df[filtered_df["Genre"].isin(selected_genres)]

    if "Release Year" in filtered_df.columns:
        min_year = int(filtered_df["Release Year"].min())
        max_year = int(filtered_df["Release Year"].max())
        year_range = st.slider(
            "Filter by Release Year:", min_year, max_year, (min_year, max_year)
        )
        filtered_df = filtered_df[
            (filtered_df["Release Year"] >= year_range[0])
            & (filtered_df["Release Year"] <= year_range[1])
        ]

    if "IMDB Rating" in filtered_df.columns:
        min_rating = float(filtered_df["IMDB Rating"].min())
        max_rating = float(filtered_df["IMDB Rating"].max())
        rating_range = st.slider(
            "Filter by IMDB Rating:", min_rating, max_rating, (min_rating, max_rating)
        )
        filtered_df = filtered_df[
            (filtered_df["IMDB Rating"] >= rating_range[0])
            & (filtered_df["IMDB Rating"] <= rating_range[1])
        ]


# --- Session State Initialization ---

if "agent_state" not in st.session_state:
    st.session_state.agent_state = None


# --- Main Layout ---

col1, col2 = st.columns(2)

with col1:
    st.subheader("Filtered Dataset")
    st.write(filtered_df)

    st.subheader("Ask a Question")
    user_question = st.text_input(
        "What would you like to know about this data?",
        placeholder="e.g., What genre has the highest average IMDB rating?",
    )
    analyze_button = st.button("Analyze", type="primary")


# --- Handle Analyze Button ---

if analyze_button and user_question:
    st.session_state.agent_state = init_agent_state(user_question, filtered_df)
    # Run the first step immediately
    st.session_state.agent_state = agent_step(st.session_state.agent_state)
    st.rerun()

elif analyze_button and not user_question:
    with col2:
        st.error("Please enter a question.")


# --- Render Agent State in col2 ---

with col2:
    st.subheader("Analysis Results")

    state = st.session_state.agent_state

    if state is None:
        st.write("Enter a question and click 'Analyze' to see results.")

    elif state["status"] == "done":
        # Show reasoning trace
        with st.expander("Agent Reasoning Trace", expanded=False):
            for step in state["trace"]:
                if step["type"] == "thought":
                    st.markdown(f"**Thought:** {step['content']}")
                elif step["type"] == "tool_call":
                    st.markdown(f"**Tool:** `{step['tool']}`")
                    if step["tool"] == "execute_code":
                        st.code(step["arguments"]["code"], language="python")
                    else:
                        st.code(
                            json.dumps(step["arguments"], indent=2), language="json"
                        )
                    st.text(f"Result: {step['result'][:500]}")
                elif step["type"] == "tool_call_rejected":
                    st.markdown(f"**Rejected:** `{step['tool']}`")
                    if step["tool"] == "execute_code":
                        st.code(step["arguments"].get("code", ""), language="python")
                st.divider()

        # Show final answer
        st.markdown("**Answer:**")
        st.write(state["answer"])

        # Render any charts
        for step in state["trace"]:
            if step["type"] == "tool_call" and step["tool"] == "create_chart":
                try:
                    spec = json.loads(step["result"])
                    st.vega_lite_chart(spec, use_container_width=True)
                except Exception:
                    pass

    elif state["status"] in ("pending_approval", "pending_rejection"):
        # Show trace so far
        if state["trace"]:
            with st.expander("Agent Reasoning Trace (so far)", expanded=True):
                for step in state["trace"]:
                    if step["type"] == "thought":
                        st.markdown(f"**Thought:** {step['content']}")
                    elif step["type"] == "tool_call":
                        st.markdown(f"**Tool:** `{step['tool']}`")
                        if step["tool"] == "execute_code":
                            st.code(step["arguments"]["code"], language="python")
                        else:
                            st.code(
                                json.dumps(step["arguments"], indent=2),
                                language="json",
                            )
                        st.text(f"Result: {step['result'][:500]}")
                    elif step["type"] == "tool_call_rejected":
                        st.markdown(f"**Rejected:** `{step['tool']}`")
                        if step.get("feedback"):
                            st.text(f"Feedback: {step['feedback']}")
                    st.divider()

        # Show pending tool calls
        st.warning("The agent wants to perform the following action:")

        for tool_call in state["pending_tool_calls"]:
            func_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            st.markdown(f"**Tool:** `{func_name}`")
            if func_name == "execute_code":
                st.code(arguments["code"], language="python")
            elif func_name == "create_chart":
                st.code(arguments["vega_lite_spec"], language="json")

        if state["status"] == "pending_rejection":
            # Show feedback input
            feedback = st.text_input(
                "Why are you rejecting? Tell the agent what to do instead:",
                key="reject_feedback",
            )
            if st.button("Submit Rejection", use_container_width=True):
                state = reject_pending_tools(state, feedback=feedback)
                state["iteration"] += 1

                while (
                    state["status"] == "running"
                    and state["iteration"] < state["max_iterations"]
                ):
                    state = agent_step(state)
                    if state["status"] == "pending_approval":
                        break
                    if state["status"] == "done":
                        break
                    state["iteration"] += 1

                st.session_state.agent_state = state
                st.rerun()
        else:
            # Approve / Reject buttons
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Approve", type="primary", use_container_width=True):
                    state = execute_approved_tools(state, filtered_df)
                    state["iteration"] += 1

                    while (
                        state["status"] == "running"
                        and state["iteration"] < state["max_iterations"]
                    ):
                        state = agent_step(state)
                        if state["status"] == "pending_approval":
                            break
                        if state["status"] == "done":
                            break
                        state["iteration"] += 1

                    st.session_state.agent_state = state
                    st.rerun()

            with btn_col2:
                if st.button("Reject", use_container_width=True):
                    state["status"] = "pending_rejection"
                    st.session_state.agent_state = state
                    st.rerun()

    elif state["status"] == "running":
        # This shouldn't normally be visible, but handle gracefully
        with st.spinner("Agent is thinking..."):
            while (
                state["status"] == "running"
                and state["iteration"] < state["max_iterations"]
            ):
                state = agent_step(state)
                if state["status"] == "pending_approval":
                    break
                if state["status"] == "done":
                    break
                state["iteration"] += 1

            st.session_state.agent_state = state
            st.rerun()
