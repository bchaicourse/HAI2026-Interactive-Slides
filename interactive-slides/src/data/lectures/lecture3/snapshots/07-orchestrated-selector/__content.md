## LLM-Based Orchestration

In the previous section, `selector_func` used Python code to decide who speaks next. But `SelectorGroupChat` can also let an LLM make that decision. If you don't provide a `selector_func`, the team uses its `model_client` to read the conversation and pick the next speaker based on each agent's `description`.

This is useful when the routing logic is hard to express in code, like "pick whichever expert is most relevant to what's being discussed right now."

### Example: Expert Panel

Let's create four agents with distinct expertise. Instead of coding the turn order, we let the LLM decide who should speak:

```python
financial_advisor = AssistantAgent(
    "FinancialAdvisor",
    model_client=client,
    description="Expert in budgeting, savings, startup costs, and financial planning",
    system_message="You are a financial advisor. Give practical money-related advice in 1-2 sentences. ...",
)

lifestyle_coach = AssistantAgent(
    "LifestyleCoach",
    model_client=client,
    description="Expert in work-life balance, personal fulfillment, and well-being",
    system_message="You are a lifestyle coach. Give advice on personal fulfillment ... ",
)

business_strategist = AssistantAgent(
    "BusinessStrategist",
    model_client=client,
    description="Expert in market analysis, competition, and business growth strategies",
    system_message="You are a business strategist. Give advice on market positioning ... ",
)

summarizer = AssistantAgent(
    "Summarizer",
    model_client=client,
    description="Wraps up by synthesizing all expert advice into a final recommendation",
    system_message="Synthesize all the expert advice into 2-3 sentences ... End with DONE.",
)
```

Notice that `description` is what the LLM reads to decide routing. The more specific the description, the better the routing decisions.

### Creating the Team

The team is created without `selector_func`. The LLM picks the next speaker each turn:

```python
team = SelectorGroupChat(
    [financial_advisor, lifestyle_coach, business_strategist, summarizer],
    model_client=client,
    termination_condition=TextMentionTermination("DONE"),
    max_turns=6,
)

async for msg in team.run_stream(
    task="I'm thinking about quitting my job to start a bakery."
):
    if isinstance(msg, TextMessage) and msg.source != "user":
        print(f"[{msg.source}] {msg.content}")
```

**Expected output (will vary):**
```
[FinancialAdvisor] Before making the leap, ensure you have a solid business
plan and at least 3 to 6 months of living expenses saved...

[LifestyleCoach] Pursuing your passion for baking can bring tremendous
fulfillment, but be sure to assess your motivations...

[BusinessStrategist] Focus on identifying a unique selling proposition that
distinguishes your offerings from competitors...

[Summarizer] Before quitting your job, develop a solid business plan, save
at least 3 to 6 months of living expenses, and consider starting your bakery
as a side hustle... DONE
```

The LLM routed the question to each expert based on their `description`, then called the Summarizer to wrap up. No Python routing logic needed.

### Customizing the Selector Prompt

Behind the scenes, the LLM receives this default prompt each turn:

```
You are in a role play game. The following roles are available:
{roles}.
Read the following conversation. Then select the next role from {participants} to play.
Only return the role.

{history}

Read the above conversation. Then select the next role from {participants} to play.
Only return the role.
```

`{roles}`, `{participants}`, and `{history}` are template variables that get replaced with agent descriptions, agent names, and the conversation so far. You can override this with the `selector_prompt` parameter if you need to add specific routing instructions.

> **Note:** The quality of LLM-based routing depends on the model. Smaller models like `gpt-4o-mini` may not always follow complex routing instructions reliably. For deterministic control, use `selector_func` instead.
