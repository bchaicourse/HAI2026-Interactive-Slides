## Nesting Teams with SocietyOfMindAgent

What if you want to use a whole team as a single step in a larger workflow? `SocietyOfMindAgent` wraps an entire team as a single agent. The outer team sees only the summary, not the raw inner conversation.

### Inner Team

First, we create a `RoundRobinGroupChat` with our Optimist and Pessimist:

```python
from autogen_agentchat.agents import AssistantAgent, SocietyOfMindAgent

debate = RoundRobinGroupChat(
    [optimist, pessimist],
    termination_condition=TextMentionTermination("DONE"),
    max_turns=6,
)
```

Then wrap it as a single agent:

```python
debate_team = SocietyOfMindAgent(
    "Debate_Team",
    team=debate,
    model_client=client,
    description="A team that debates pros and cons",
)
```

`debate_team` now behaves like any other `AssistantAgent`. When it receives a task, it internally runs the full debate, then summarizes the conversation and returns the summary as its response.

### Outer Team

We can put `debate_team` inside another team alongside a Summarizer:

```python
summarizer = AssistantAgent(
    "Summarizer",
    model_client=client,
    system_message="Read the debate summary and give a final 2-3 sentence recommendation.",
)

outer = RoundRobinGroupChat(
    [debate_team, summarizer],
    max_turns=2,
)
```

The flow is:
1. The outer team sends the task to `Debate_Team`
2. `Debate_Team` internally runs the debate (Optimist and Pessimist)
3. `SocietyOfMindAgent` summarizes the inner conversation
4. The summary is passed to the Summarizer in the outer team

The outer team only sees the summary from `Debate_Team`, not the individual Optimist/Pessimist messages.

```python
async for msg in outer.run_stream(
    task="I'm thinking about quitting my job to start a bakery."
):
    if isinstance(msg, TextMessage) and msg.source != "user":
        print(f"[{msg.source}] {msg.content}")
```

**Expected output (will vary):**
```
[Optimist] That sounds like an exciting adventure! Following your passion can
lead to a fulfilling new chapter in your life.

[Pessimist] While pursuing your passion is inspiring, consider the financial
stability and market demand for your bakery before making the leap...

[Optimist] DONE. It's great to be cautious, but preparing a solid plan will
help you navigate the challenges and turn your dream into a successful reality!

[Debate_Team] Pursuing your passion can indeed lead to a fulfilling new chapter
in your life! While it's important to remain cautious and consider factors
like financial stability and market demand, creating a solid business plan
can help you navigate challenges effectively...

[Summarizer] Starting your own bakery could be a fulfilling pursuit, but it's
crucial to approach this transition wisely. Ensure you have a comprehensive
business plan and financial cushion in place to mitigate risks...
```

Note that `run_stream()` yields the inner team's messages too, so you can observe the debate in real time. However, the Summarizer only receives the `Debate_Team` summary, not the individual Optimist/Pessimist messages.
