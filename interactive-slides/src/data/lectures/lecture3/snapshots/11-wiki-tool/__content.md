## Adding a Wikipedia Tool

The Advisor from the previous step gives general advice based on what the LLM already knows. To make better decisions, we want it to look up real information first. In this step, we give the same Advisor agent a **Wikipedia tool** so it can research facts before advising.

> **Note:** For production use, a search API like Google or Bing would give better results. However, those require API keys and rate limit configuration. Wikipedia's API is free and requires no setup, so we'll use it here.

### wiki_tool.py

The new file `wiki_tool.py` contains a `search_wikipedia` function that calls the MediaWiki API in two steps: search for the most relevant article, then extract its introductory text.

```python
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for a topic and return a brief summary."""
    # Step 1: search for articles matching the query
    # Step 2: extract the intro text of the top result
    # Returns: "{title}: {summary}" (truncated to 1000 chars)
    ...
```

The function uses `urllib` (Python's built-in HTTP library) so no extra dependencies are needed.

### Changes to app.py

We import `FunctionTool` and the search function, then wrap it as a tool:

```python
from autogen_core.tools import FunctionTool
from wiki_tool import search_wikipedia
```

```python
wiki_tool = FunctionTool(
    search_wikipedia,
    description="Search Wikipedia for factual information about any topic.",
)
```

The Advisor gets two additions: `tools=[wiki_tool]` so it can call the function, and `reflect_on_tool_use=True` so it summarizes the raw Wikipedia text instead of dumping it directly. The system message is also updated to tell the agent to research first, then advise:

```python
advisor = AssistantAgent(
    "Advisor",
    model_client=client,
    tools=[wiki_tool],
    system_message=(
        "You help people make decisions. First, use the search_wikipedia tool "
        "to research relevant facts. Then give a balanced, actionable "
        "recommendation in 2-3 short paragraphs grounded in what you found."
    ),
    reflect_on_tool_use=True,
)
```

Everything else (the Streamlit UI, the `display_message` helper, the `asyncio.run()` bridge) stays exactly the same.

### What you see in the browser

The output looks similar to before, but the Advisor's response now references specific facts from Wikipedia instead of relying solely on general knowledge.
