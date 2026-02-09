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

> ```python
> set_state("agent_pending_message", msg)
> set_state("agent_phase", "awaiting_approval")
> ```

The actual execution moves into `execute_pending_tools()`. We don't need to store tool calls separately since they're accessible as `pending_msg.tool_calls`:

> ```python
> pending_msg = get_state("agent_pending_message")
>
> messages.append(pending_msg)
> for tc in pending_msg.tool_calls:
> ```

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

> ```python
> elif phase == "awaiting_approval":
>     ...
>     approved = st.button("Approve", type="primary", use_container_width=True)
> ```

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

> ```python
> elif phase == "awaiting_approval" and approved:
>     execute_pending_tools()
>     st.rerun()
> ```

Notice how naturally this fits into the existing structure. We added one new phase, split the acting logic into "propose" and "execute", added one render function, and added one lifecycle branch. Everything else remains unchanged, including `app.py`, `chart_tool.py`, and `movie_tool.py`.
