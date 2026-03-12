## Preset Configurations

The configurable pipeline from the previous step is powerful, but setting up agents and pipeline steps from scratch takes time. Presets give students a few ready-made configurations to load with one click, explore how they work, and then modify.

### Three Presets

The app ships with three preset buttons at the top of the page:

**Decision Support** is the same configuration we've been building throughout Part 2: Clarifier → Researcher → Debate Team (round-robin) → Advisor.

**Stakeholder Simulation** demonstrates a Swarm with a cyclical handoff pattern. Three agents work together:
- **Coordinator** receives the decision and hands off to StakeholderFinder. After each stakeholder perspective comes back, the Coordinator decides whether to request more or synthesize a final recommendation.
- **StakeholderFinder** identifies one relevant stakeholder (e.g., "your family", "a local chef") and hands off to Simulator.
- **Simulator** role-plays as that stakeholder, giving their perspective in character, then hands back to Coordinator.

The handoff cycle (Coordinator → StakeholderFinder → Simulator → Coordinator → ...) repeats until the Coordinator has enough perspectives, at which point it hands off to `user` and the swarm terminates.

**Blank Canvas** loads a single empty agent with no system message, so you can build a configuration from scratch without having to delete the defaults first.

### How It Works

Presets are defined in `defaults.py` as a dictionary of `{name: {agents, pipeline}}` configurations. The preset buttons in `app.py` replace `st.session_state.agents` and `st.session_state.pipeline` with the selected preset's data and trigger a rerun:

```python
preset_names = list(PRESETS.keys())
cols = st.columns(len(preset_names))
for i, name in enumerate(preset_names):
    with cols[i]:
        if st.button(name, use_container_width=True):
            st.session_state.agents = [
                {**a, "id": str(uuid.uuid4())} for a in PRESETS[name]["agents"]
            ]
            st.session_state.pipeline = [
                {**s, "id": str(uuid.uuid4())} for s in PRESETS[name]["pipeline"]
            ]
            st.rerun()
```

After loading a preset, all the tabs update to reflect the new configuration. You can freely modify the agents and pipeline from there.

### Try It

Load the **Stakeholder Simulation** preset and run it. Watch how the Coordinator, StakeholderFinder, and Simulator hand off to each other in a loop, building up multiple perspectives before the Coordinator synthesizes a recommendation. Then try modifying it: add a Researcher with the Wikipedia tool before the swarm, or change the Simulator's system message to make it more opinionated.
