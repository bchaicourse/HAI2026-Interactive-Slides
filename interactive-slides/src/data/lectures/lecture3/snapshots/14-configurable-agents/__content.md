## Configurable Agents

So far, changing an agent means editing Python code and restarting the app. In this step, we add a UI that lets you edit agents directly in the browser: tweak their names, rewrite system messages, toggle tools. The pipeline structure stays fixed (Clarifier → Researcher → Debate Team → Advisor), but the agents feeding into it become fully customizable.

### Overall Structure

The app splits into two tabs and three new files:

- **Tab 1 ("Define Agents")**: an editor where you can modify, add, or remove agents
- **Tab 2 ("Run")**: the same pipeline from before, but now it builds agents from the editor's state instead of hardcoding them

The new files:
- `defaults.py` stores the starting agent configurations as a list of dictionaries
- `tab_agents.py` renders the agent editor UI
- `app.py` ties everything together with tabs and session state

### Representing Agents as Data

Instead of creating `AssistantAgent` objects directly, we represent each agent as a plain dictionary with four fields:

```python
# defaults.py
DEFAULT_AGENTS = [
    {
        "name": "Clarifier",
        "system_message": "You take a vague decision and reframe it into ...",
        "description": "Reframes decisions into clear problem statements",
        "has_wiki_tool": False,
    },
    # ... Researcher (has_wiki_tool=True), Optimist, Pessimist, Advisor
]
```

When the app first loads, these defaults are copied into `st.session_state.agents` with a UUID attached to each one. From that point on, the UI reads from and writes to session state:

```python
if "agents" not in st.session_state:
    st.session_state.agents = [
        {**a, "id": str(uuid.uuid4())} for a in DEFAULT_AGENTS
    ]
```

We'll see why the UUIDs are needed in a moment.

### The Agent Editor

`tab_agents.py` loops over `st.session_state.agents` and renders an expander for each one. The key pattern is two-way binding:

```python
for i, agent in enumerate(st.session_state.agents):
    aid = agent["id"]
    with st.expander(agent["name"]):
        name = st.text_input("Name", agent["name"], key=f"an_{aid}")
        msg = st.text_area("System Message", agent["system_message"], key=f"am_{aid}")
        # ... description, wiki toggle
        st.session_state.agents[i].update(name=name, system_message=msg, ...)
```

Each widget reads its default value from session state, and the user's edit is written back with `.update(...)`. On the next Streamlit rerun, the widget picks up the updated value. This keeps the widgets and data in sync.

Notice that each widget's `key` uses the agent's UUID (`aid`), not the list index `i`. This is why we added UUIDs earlier: Streamlit identifies widgets by their key, so if you used `key=f"name_{i}"` and then removed an agent in the middle of the list, all the indices after it would shift. Streamlit would bind the wrong data to the wrong widget. UUIDs are stable regardless of list order.

### Building Agents from Config

When you click "Run", the app reads session state and constructs real AutoGen agents:

```python
agents = {}
for cfg in st.session_state.agents:
    kwargs = {}
    if cfg.get("has_wiki_tool"):
        kwargs["tools"] = [wiki_tool]
        kwargs["reflect_on_tool_use"] = True
    agents[cfg["name"]] = AssistantAgent(
        cfg["name"],
        model_client=client,
        system_message=cfg.get("system_message", ""),
        **kwargs,
    )
```

The pipeline itself is still hardcoded: it looks up agents by name (`agents["Clarifier"]`, `agents["Researcher"]`, etc.) and wires them into the same `RoundRobinGroupChat` + `SocietyOfMindAgent` structure from the previous step. If you rename or remove a required agent, you'll get a `KeyError`. The next step removes this limitation by making the pipeline configurable too.

### What You See in the Browser

**Tab 1** shows five collapsible sections, one per default agent. Expanding a section reveals fields for name, description, system message, and a Wikipedia tool toggle. You can add new agents or remove existing ones.

**Tab 2** works the same as before: enter a question, click the button, and see the pipeline output. The difference is that the agents now reflect whatever you configured in Tab 1.
