## Configurable Pipeline

In the previous step, the agent editor lets you change what agents say, but the pipeline structure is still hardcoded. If you want to try a different team type or reorder steps, you have to edit Python code.

This final step adds a pipeline builder UI. Each step can be a single agent or a team, and teams support all three collaboration patterns from Part 1: round-robin, LLM orchestration, and swarm. Combined with the agent editor, the entire multi-agent system is now configurable from the browser.

### Pipeline as Data

The same approach from the agent editor applies here. Each pipeline step is a dictionary in `st.session_state.pipeline`:

```python
DEFAULT_PIPELINE = [
    {"type": "agent", "agent_name": "Clarifier"},
    {"type": "agent", "agent_name": "Researcher"},
    {
        "type": "team",
        "team_name": "Debate_Team",
        "team_type": "roundrobin",
        "members": ["Optimist", "Pessimist"],
        "max_turns": 4,
        ...
    },
    {"type": "agent", "agent_name": "Advisor"},
]
```

Agent steps only need a name. Team steps carry additional configuration: team type, member list, max turns, and type-specific settings (termination keyword, routing guidance, or handoff targets).

### The Pipeline Editor

`tab_pipeline.py` renders an expander for each step. A radio button switches between "agent" (select from a dropdown) and "team" (configure the team). For teams, the UI adapts based on team type:

- **Round-robin**: optional termination keyword
- **LLM orchestration**: optional routing guidance that gets appended to the selector prompt
- **Swarm**: a handoff configuration section where you set each member's handoff targets (other members or "user")

The swarm configuration is the most involved. For each member, a multiselect lets you pick which agents it can hand off to. At least one agent must hand off to `"user"` so the swarm can terminate.

### Building AutoGen Objects

The new file `builder.py` translates UI configuration into real AutoGen objects. The main function, `build_pipeline`, loops over the pipeline steps: agent steps become `AssistantAgent` objects, team steps become inner teams wrapped in `SocietyOfMindAgent`. The outer pipeline is a `RoundRobinGroupChat` where each member speaks once.

A few design decisions worth noting:

- **Name sanitization.** AutoGen requires agent names to be valid Python identifiers (no spaces or special characters). The builder runs all names through `_safe_name()`, which replaces invalid characters with underscores. This way users can type "My Agent" in the UI and it becomes `My_Agent` internally.
- **Two clients.** Swarm agents need `parallel_tool_calls=False` (handoffs are tool calls, and parallel calls break them). A separate `swarm_client` is created for this. All other agents use the standard client.
- **`reflect_on_tool_use` is disabled for swarm agents with tools.** `reflect_on_tool_use=True` combined with `parallel_tool_calls=False` causes a crash in AutoGen. Swarm agents with the Wikipedia tool will return raw tool results instead of a natural-language summary, but `SocietyOfMindAgent` summarizes the output anyway.
- **Single-step pipelines** skip the outer `RoundRobinGroupChat` and return the agent or team directly.

### Simplified app.py

With the build logic extracted to `builder.py`, the main file is much simpler. It initializes session state, creates three tabs, and delegates:

```python
t_agents, t_pipeline, t_run = st.tabs(
    ["1. Define Agents", "2. Build Pipeline", "3. Run"]
)

tab_agents.render(t_agents)
tab_pipeline.render(t_pipeline)
```

The Run tab calls `build_pipeline` and passes the result to a new `run_and_display` helper in `display.py`. This helper handles both single agents and teams, using `run_stream` for teams and `run` for individual agents. It also displays `ToolCallSummaryMessage` in addition to `TextMessage`, which is needed for swarm agents: since they use `reflect_on_tool_use=False`, their tool results come back as `ToolCallSummaryMessage` rather than `TextMessage`.

```python
team_or_agent, is_team = build_pipeline(
    st.session_state.agents,
    st.session_state.pipeline,
)
run_and_display(team_or_agent, is_team, question)
```

### What You See in the Browser

The app now has three tabs. **Tab 1** is the agent editor from before. **Tab 2** is the new pipeline builder with expandable steps, each configurable as an agent or a team. **Tab 3** shows the current pipeline as a summary string (e.g., "Clarifier -> Researcher -> Debate_Team -> Advisor"), followed by the question input and run button.

Try changing the Debate Team's type from "roundrobin" to "swarm", setting up handoff targets, and running the pipeline to see how the output changes.
