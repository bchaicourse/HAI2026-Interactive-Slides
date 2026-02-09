## Adding the ReAct Loop to the UI

In the previous step, our Streamlit app made a single tool call: one chance to generate code, and if it failed, the user just saw the error. Now we integrate the ReAct pattern from Part 1, giving the model the ability to reason, retry, and self-correct.

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