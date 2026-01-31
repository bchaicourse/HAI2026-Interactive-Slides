# Part 3: Building a Web Interface with Streamlit

So far, we explored the 3-step chain through isolated examples—generating code, executing it, and interpreting results. Now we'll integrate these techniques into a complete web application with a structured user interface.

## Why Not Just a Chatbot?

Chatbots are the dominant interface for generative AI, but they're not always the best choice. For data analysis tasks, consider what a user must articulate:

> *"Show me the average rating for action movies released between 2010 and 2020, but only include movies with more than 1000 reviews"*

This requires precise language, knowledge of available columns, and careful specification of constraints. Users must translate their analytical intent into prose, which is error-prone and tedious.

**A structured UI solves this:**

- Filters for columns, genres, and date ranges are **visual controls** (checkboxes, sliders)
- The user asks a simpler question: "What is the average rating?"
- The system already knows the filtered context

This hybrid approach—structured input + natural language—reduces the articulation barrier while preserving the flexibility of prompting.

## Why Streamlit?

**Streamlit** turns Python scripts into interactive web apps with minimal code. You write normal Python, and Streamlit handles the HTML, CSS, and JavaScript.

### Installation

```bash
pip install streamlit
```

### Your First Streamlit App

```python
import streamlit as st

st.title("Hello Streamlit!")
st.write("Welcome to Streamlit")
```

Run it:
```bash
streamlit run app.py
```

This opens a browser window with your app. The terminal will display the URL (usually `http://localhost:8501` or a different port if 8501 is in use).
