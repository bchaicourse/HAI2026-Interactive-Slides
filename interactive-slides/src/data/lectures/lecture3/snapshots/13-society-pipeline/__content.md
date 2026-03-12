## Adding a Debate Step

Before the Advisor makes a recommendation, it would help to have a structured debate exploring both sides. Adding an Optimist and Pessimist directly into the outer team wouldn't work well, since each would speak once without seeing the other's argument. We want a back-and-forth, summarized into a single response for the rest of the pipeline.

This is a good fit for `SocietyOfMindAgent`: an Optimist and Pessimist debate internally, and the outer team only sees the summary.

### The Debate Team

```python
optimist = AssistantAgent(
    "Optimist",
    model_client=client,
    system_message=(
        "You see the bright side. Highlight opportunities and upsides. "
        "Be specific. Keep to 1-2 sentences."
    ),
)

pessimist = AssistantAgent(
    "Pessimist",
    model_client=client,
    system_message=(
        "You identify risks and potential downsides. Be constructive. "
        "Keep to 1-2 sentences."
    ),
)

debate = RoundRobinGroupChat(
    [optimist, pessimist],
    max_turns=4,
)

debate_team = SocietyOfMindAgent(
    "Debate_Team",
    team=debate,
    model_client=client,
    description="Debates pros and cons of the decision",
)
```

With `max_turns=4`, the Optimist and Pessimist each speak twice. The `SocietyOfMindAgent` then summarizes the debate into a single response.

### Updating the Pipeline

We add `debate_team` to the outer team and bump `max_turns` to 4:

```python
team = RoundRobinGroupChat(
    [clarifier, researcher, debate_team, advisor],
    max_turns=4,
)
```

The `run_stream` code stays the same. Because `SocietyOfMindAgent` exposes the same interface as any individual agent, the outer team doesn't need to know it's an entire team internally.

### Expected Output

Four chat bubbles appear:

1. **Clarifier** reframes the question into a problem statement with constraints.
2. **Researcher** presents bullet points from Wikipedia.
3. **Debate Team** shows a summary weighing both sides (not the individual Optimist/Pessimist messages).
4. **Advisor** delivers a recommendation drawing on the problem statement, research, and debate summary.
