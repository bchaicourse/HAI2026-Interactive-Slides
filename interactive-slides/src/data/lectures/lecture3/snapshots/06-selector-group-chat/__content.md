## SelectorGroupChat

`RoundRobinGroupChat` always follows a fixed rotation. But what if you want more control, like routing to a specific agent based on a condition? `SelectorGroupChat` lets you define a `selector_func` that decides who speaks next.

### Adding a Third Agent

Let's add a Summarizer that wraps up the debate. Each agent now includes a `description` parameter, which the team can use to understand each agent's role:

```python
from autogen_agentchat.teams import SelectorGroupChat

optimist = AssistantAgent(
    "Optimist",
    model_client=client,
    description="Sees the bright side and highlights opportunities",
    system_message="""\
You always see the bright side. Keep to 1-2 sentences.
Do NOT say DONE yourself.""",
)

pessimist = AssistantAgent(
    "Pessimist",
    model_client=client,
    description="Plays devil's advocate and identifies risks",
    system_message="""\
You always see the risks and downsides. Keep to 1-2 sentences.
Do NOT say DONE yourself.""",
)

summarizer = AssistantAgent(
    "Summarizer",
    model_client=client,
    description="Gives a final balanced recommendation after debate",
    system_message="""\
Synthesize the debate into 2-3 sentences of balanced advice.
End with DONE.""",
)
```

### selector_func

The `selector_func` receives the full message history and returns the name of the next agent. Here we implement: Optimist and Pessimist alternate, then after 4 turns the Summarizer takes over:

```python
def selector_func(messages):
    if not messages:
        return "Optimist"
    non_user = [m for m in messages if m.source != "user"]
    turns = len(non_user)
    if turns >= 4:
        return "Summarizer"
    last = messages[-1].source
    if last == "Optimist":
        return "Pessimist"
    return "Optimist"
```

You can write any logic here: fixed rotation, conditional routing, content-based decisions, etc. If `selector_func` returns `None`, the team falls back to using an LLM to pick the next speaker based on agent descriptions.

### Creating the Team

```python
team = SelectorGroupChat(
    [optimist, pessimist, summarizer],
    model_client=client,
    termination_condition=TextMentionTermination("DONE"),
    max_turns=8,
    selector_func=selector_func,
)
```

> **Note:** `SelectorGroupChat` requires a `model_client` because it also supports LLM-based routing, where the LLM reads agent descriptions to pick the next speaker (we'll see this in the next section). When you provide a `selector_func`, the LLM router is not used, but `model_client` is still required.

**Expected output (will vary):**
```
[Optimist] That's an exciting venture! Starting a bakery could be a wonderful
way to turn your passion for baking into a fulfilling career.

[Pessimist] However, consider the financial instability and long hours often
associated with starting a business...

[Optimist] Those challenges can definitely seem daunting, but every successful
business has faced them! ...

[Pessimist] While determination is key, keep in mind that many startups fail
within the first few years...

[Summarizer] Consider your passion and dedication against the realities of
financial risks and market competition... DONE
```
