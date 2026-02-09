## Rejecting with Feedback

The user can now approve actions, but what if the agent's plan looks wrong? Maybe it's querying the wrong column, or using the wrong aggregation. The user needs a way to say "no" and explain *why*, so the agent can adjust its approach.

We add a **Reject** button alongside Approve. When the user rejects, they can type feedback explaining what the agent should do differently. The agent receives this feedback and tries again.

### A New Phase: `awaiting_feedback`

The state machine from the previous step had one path from `awaiting_approval`:

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

> ```python
> messages.append({
>     "role": "tool",
>     "content": rejection_msg,
>     "tool_call_id": tc.id,
> })
> ```

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

> ```python
> btn_col1, btn_col2 = st.columns(2)
> with btn_col1:
>     approved = st.button("Approve", type="primary", use_container_width=True)
> with btn_col2:
>     rejected = st.button("Reject", use_container_width=True)
> return approved, rejected
> ```

A new `render_pending_feedback()` shows a text input where the user can explain why they're rejecting.

`render_panel()` now returns an `actions` dictionary instead of a single boolean, since there are multiple possible user interactions depending on the phase. In `awaiting_approval`, it collects Approve/Reject. In `awaiting_feedback`, it collects the feedback text and Submit button. In all other phases, `actions` stays as an empty `{}`:

> ```python
> actions = {}
> ...
>     elif phase == "awaiting_approval":
>         ...
>         actions = {"approved": approved, "rejected": rejected}
>     elif phase == "awaiting_feedback":
>         ...
>         actions = {"submitted": submitted, "feedback": feedback}
> ...
> return actions
> ```

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

> ```python
> elif phase == "awaiting_approval":
>     if actions.get("approved"):
>         execute_pending_tools()
>         st.rerun()
>     elif actions.get("rejected"):
>         set_state("agent_phase", "awaiting_feedback")
>         st.rerun()
> ```

A new branch handles the feedback submission. When the user types their feedback and clicks Submit, `reject_pending_tools()` sends the rejection message to the model and the agent resumes from `thinking`:

> ```python
> elif phase == "awaiting_feedback" and actions.get("submitted"):
>     reject_pending_tools(actions.get("feedback", ""))
>     st.rerun()
> ```

Once again, `app.py`, `chart_tool.py`, and `movie_tool.py` are completely unchanged. The entire reject-with-feedback feature lives in `agent_panel.py`: one new logic function, two new render functions, and two new lifecycle branches.
