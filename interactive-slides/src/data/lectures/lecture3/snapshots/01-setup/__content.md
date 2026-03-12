# Part 1: Multi-Agent Systems

## Setup: Install AutoGen

Building an agent from the raw OpenAI API means writing a lot of plumbing: checking for `tool_calls`, executing functions, appending results to `messages`, and looping until the model is done. This works, but every piece is yours to manage.

**AutoGen** is an open-source multi-agent framework developed by Microsoft Research. It wraps the LLM API, manages conversation history, executes tools, and provides building blocks for connecting multiple agents together.

> **Note:** Microsoft's active development has moved to a newer project called **Agent Framework**. AutoGen still receives minimal bug fixes but is no longer the primary focus. We use AutoGen in this course because Agent Framework is still in its early stages.

### AutoGen's Package Structure

AutoGen is split into three packages, each with a different role:

- **`autogen-agentchat`**: High-level building blocks for creating agents and orchestrating multi-agent teams
- **`autogen-core`**: Lower-level primitives shared across the framework (e.g., tool definitions)
- **`autogen-ext`**: Integrations with external services (e.g., OpenAI, Azure)

You'll import from all three throughout this lecture. When you see an import like `from autogen_agentchat.agents import AssistantAgent`, the first part (`autogen_agentchat`) tells you which package it comes from.

### Install Dependencies

```bash
pip install autogen-agentchat autogen-ext[openai] python-dotenv
```

`autogen-core` is installed automatically as a dependency of `autogen-agentchat`.

### Set Up Your API Key

Create a `.env` file:

```
OPENAI_API_KEY=sk-proj-...
```

### Verify the Installation

```python
from dotenv import load_dotenv
import os

from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()
client = OpenAIChatCompletionClient(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
)
```

**Expected output:**
```
AutoGen installed successfully!
Model: gpt-4o-mini
```
