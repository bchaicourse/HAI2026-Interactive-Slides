## RoundRobinGroupChat

AutoGen provides **teams**, predefined orchestration patterns that manage how multiple agents interact. There are several team types, each with a different communication strategy. We'll start with the simplest: `RoundRobinGroupChat`, where agents take turns in a fixed rotation.

```python
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

team = RoundRobinGroupChat(
    [optimist, pessimist],
    termination_condition=TextMentionTermination("DONE"),
    max_turns=10,
)
```

The first argument is the list of agents. The order determines the turn order: Optimist speaks first, then Pessimist, then Optimist again, and so on.

### Termination Conditions

A team needs to know when to stop. `TextMentionTermination("DONE")` ends the conversation when any agent says "DONE". `max_turns=10` is a safety limit that prevents infinite loops if no agent ever says "DONE".

To make this work, we tell the Optimist in its `system_message` to say "DONE" after a few rounds:

```python
optimist = AssistantAgent(
    "Optimist",
    model_client=client,
    system_message="""\
You are part of a two-agent debate. You always see the bright side.
Keep each response to 1-2 sentences. Be concise and direct.
After hearing Pessimist at least twice, say DONE to end the conversation.""",
)
```

### Streaming with `run_stream()`

Instead of `run()` which waits for the entire conversation to finish, `run_stream()` yields messages as they're produced. We filter for `TextMessage` to skip internal orchestration messages:

```python
from autogen_agentchat.messages import TextMessage

async for msg in team.run_stream(
    task="I'm thinking about quitting my job to start a bakery."
):
    if isinstance(msg, TextMessage) and msg.source != "user":
        print(f"[{msg.source}] {msg.content}")
```

**Expected output (will vary):**
```
[Optimist] That's an exciting decision! Starting a bakery can be a wonderful
way to pursue your passion and share your creations with others.

[Pessimist] Quitting your job to start a bakery comes with significant
financial risks; without a stable income, you could face challenges...

[Optimist] While financial risks are real, many successful bakers start small
and grow their businesses over time...

[Pessimist] Even with a slow start, the baking industry is highly competitive
and saturated...

[Optimist] True, there is competition, but having a unique selling point can
help you stand out... DONE
```

The agents take turns in order, each responding to everything said so far. When the Optimist decides the debate has gone long enough, it says "DONE" and the team stops.
