# Part 2: Decision Support

## A Single Agent in Streamlit

In Part 2, we'll build a **Decision Support** web app that helps users think through decisions using multiple agents. We'll start with a single agent and add complexity one step at a time.

```python
import asyncio
import os

import streamlit as st
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from display import display_message
```

The app creates an Advisor agent and runs it when the button is clicked:

```python
if st.button("Get Advice", type="primary", use_container_width=True):
    client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    advisor = AssistantAgent(
        "Advisor",
        model_client=client,
        system_message=(
            "You help people make decisions. Analyze the situation from multiple angles, "
            "then give a balanced, actionable recommendation in 2-3 short paragraphs."
        ),
    )

    async def run():
        with st.chat_message("user"):
            st.markdown(question)
        result = await advisor.run(task=question)
        for msg in result.messages:
            if hasattr(msg, "source") and msg.source != "user":
                display_message(msg.source, msg.content)

    asyncio.run(run())
```

One thing to note: AutoGen is async, but Streamlit is sync. We bridge the two with `asyncio.run()` inside the button handler.

### display.py

The new file `display.py` provides a `display_message()` helper that renders each agent's response as a colored chat bubble. It assigns a consistent color to each agent name using a hash, so the same agent always gets the same color. We'll reuse this helper throughout Part 2.

```python
def display_message(source, text):
    with st.chat_message("assistant"):
        color = _agent_color(source)
        st.markdown(
            f'<span style="color:{color};font-weight:700">'
            f'{source.replace("_", " ")}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(text)
```

### What you see in the browser

When you click "Get Advice", the Advisor responds with a 2-3 paragraph recommendation analyzing the decision from multiple angles.
