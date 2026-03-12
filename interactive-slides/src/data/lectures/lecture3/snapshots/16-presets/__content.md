## Finishing Touches

The configurable pipeline from the previous step is fully functional, but a couple of convenience features make it more practical to use.

### Presets

Setting up agents and pipeline steps from scratch takes time. Presets let you load a ready-made configuration with one click, explore how it works, and then modify it.

The app ships with three preset buttons at the top of the page:

- **Decision Support**: the same Clarifier → Researcher → Debate Team → Advisor pipeline we've been building throughout Part 2.
- **Stakeholder Simulation**: a Swarm where a Coordinator, StakeholderFinder, and Simulator hand off to each other in a cycle, gathering multiple perspectives before synthesizing a recommendation.
- **Blank Canvas**: a single empty agent, so you can build from scratch without deleting the defaults first.

Presets are defined in `defaults.py` as a dictionary of `{name: {agents, pipeline}}` configurations. Clicking a preset button replaces the current session state and triggers a rerun, updating all tabs to reflect the new configuration.

### Transcript Download

After the pipeline finishes, a **Download Transcript** button appears below the conversation. Clicking it saves the full exchange (question and all agent responses) as a `.txt` file. The conversation history is stored in `st.session_state` so it persists across reruns.

### Try It

Load the **Stakeholder Simulation** preset and run it. Watch how the Coordinator, StakeholderFinder, and Simulator hand off to each other in a loop, building up multiple perspectives before the Coordinator synthesizes a recommendation. Then try modifying it: add a Researcher with the Wikipedia tool before the swarm, or change the Simulator's system message to make it more opinionated.
