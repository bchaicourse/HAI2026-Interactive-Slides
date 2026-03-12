## Swarm & Handoff

In the team types we've seen so far, a central mechanism decides who speaks next (fixed rotation in `RoundRobinGroupChat`, a function or LLM in `SelectorGroupChat`). `Swarm` takes a different approach: each agent decides for itself who to hand off to next.

### Defining Handoffs

Each agent declares which agents it can hand off to via the `handoffs` parameter. A `Handoff` specifies the target agent and a description that helps the LLM decide when to use it:

```python
from autogen_agentchat.base import Handoff
from autogen_agentchat.teams import Swarm

researcher = AssistantAgent(
    "Researcher",
    model_client=client,
    handoffs=[
        Handoff(target="Writer",
                description="After researching, hand off to Writer"),
    ],
    system_message="""\
You are a Researcher. Gather 3 key facts about the topic in bullet points.
Then hand off to Writer.""",
)

writer = AssistantAgent(
    "Writer",
    model_client=client,
    handoffs=[
        Handoff(target="user",
                description="After writing, return to user"),
    ],
    system_message="""\
You are a Writer. Take the Researcher's facts and write a short paragraph.
Then hand off to user.""",
)
```

Behind the scenes, AutoGen converts each `Handoff` into a tool call that the LLM can invoke. When the agent calls a handoff tool, control passes to the target agent, which receives the full conversation history.

### HandoffTermination

`HandoffTermination(target="user")` stops the swarm when an agent hands off to `"user"`. This is the standard way to end a swarm workflow:

```python
from autogen_agentchat.conditions import HandoffTermination

team = Swarm(
    [researcher, writer],
    termination_condition=HandoffTermination(target="user"),
    max_turns=10,
)
```

The first agent in the list (`researcher`) receives the initial task. From there, routing is entirely driven by handoffs.

### parallel_tool_calls=False

Since handoffs are implemented as tool calls, you need to set `parallel_tool_calls=False` on the client. Otherwise the model might try to call multiple handoff tools at once, which AutoGen would reject:

```python
client = OpenAIChatCompletionClient(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    parallel_tool_calls=False,
)
```

### Running the Swarm

We use `run_stream()` and also print `HandoffMessage` to see the transitions:

```python
from autogen_agentchat.messages import TextMessage, HandoffMessage

async for msg in team.run_stream(task="Tell me about the history of coffee."):
    if isinstance(msg, TextMessage) and msg.source != "user":
        print(f"[{msg.source}] {msg.content}")
    elif isinstance(msg, HandoffMessage) and msg.target != "user":
        print(f"[{msg.source}] *Handing off to {msg.target}...*")
```

**Expected output (will vary):**
```
[Researcher] *Handing off to Writer...*

[Writer] The history of coffee is rich and fascinating, tracing back to its
origins in the ancient coffee forests of Ethiopia, where legend suggests that
a goat herder named Kaldi first discovered the stimulating effects of the beans
in the 9th century. From Ethiopia, coffee made its way to the Arabian Peninsula,
where it became a significant part of social life... Over the centuries, coffee
has woven itself into the cultural fabric of societies worldwide.
```

The Researcher gathers facts and hands off to the Writer, who composes a paragraph and hands off to the user, ending the swarm.