## Adding a Chart Tool

In the previous step, we separated state, logic, and UI so that new features could be added without rewriting existing code. Let's put that to the test by adding a second tool: one that lets the agent create chart visualizations.

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

Because we separated concerns in the previous step, each layer gets a small, focused addition.

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

This is the payoff of the separation we did in the previous step. Adding a completely new tool required small, isolated changes to each layer, without rewriting any existing logic.
