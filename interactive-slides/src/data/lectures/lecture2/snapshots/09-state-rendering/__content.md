## Separating State, Logic, and UI

### The Problem

In the previous step, state updates, API calls, and UI rendering are all interleaved inside a single `while True` loop:

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

This might seem like extra complexity, but you'll see in the next steps how this separation makes it easy to add new features like additional tools and user approval flows. Each rerun follows the same simple sequence: reset if needed, render, step, rerun.
