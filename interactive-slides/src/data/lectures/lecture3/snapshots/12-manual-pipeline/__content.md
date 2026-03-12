## From One Agent to a Pipeline

A single agent that handles everything (clarifying the question, researching facts, and giving advice) tends to produce generic output. A pipeline lets each agent specialize in one job, and each step builds on the work of the previous ones.

### Three Specialized Agents

We split the single Advisor into three agents:

- **Clarifier** reframes the vague question into a structured problem statement. It is told not to suggest solutions.
- **Researcher** takes over the Wikipedia tool from the previous step's Advisor. Its only job is to look up facts and report bullet points.
- **Advisor** no longer researches. It reads everything that came before and gives a concise recommendation.

```python
clarifier = AssistantAgent(
    "Clarifier",
    model_client=client,
    system_message=(
        "You take a vague decision and reframe it into a clear problem statement.\n\n"
        "1. Identify the core dilemma.\n"
        "2. List 2-3 key constraints (time, money, relationships, etc.).\n\n"
        "Keep it brief. Do NOT suggest solutions."
    ),
)

researcher = AssistantAgent(
    "Researcher",
    model_client=client,
    tools=[wiki_tool],
    system_message=(
        "You research relevant facts to inform the decision. "
        "Use the search_wikipedia tool to look up topics. "
        "Only report what you learned from the tool, nothing else. "
        "Keep it to 3-5 short bullet points."
    ),
    reflect_on_tool_use=True,
)

advisor = AssistantAgent(
    "Advisor",
    model_client=client,
    system_message=(
        "Read all previous context and give a final 2-3 sentence recommendation. "
        "Be decisive and actionable."
    ),
)
```

### Running the Pipeline

We wire the three agents into a `RoundRobinGroupChat` with `max_turns=3` so each speaks once in order:

```python
team = RoundRobinGroupChat(
    [clarifier, researcher, advisor],
    max_turns=3,
)

async for msg in team.run_stream(task=question):
    if isinstance(msg, TextMessage) and msg.source != "user":
        display_message(msg.source, msg.content)
```

Each agent sees all prior messages, so the Researcher can read the Clarifier's output and the Advisor can read both.

### Expected Output

When you click "Get Advice", three colored chat bubbles appear:

1. **Clarifier** identifies the core dilemma (adventure vs. skill-building) and lists constraints like time and budget.
2. **Researcher** shows bullet points of facts from Wikipedia.
3. **Advisor** synthesizes everything into a 2-3 sentence recommendation.
