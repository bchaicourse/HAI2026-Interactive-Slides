## Streamlit Concept 3: Sidebar

To organize controls and keep your main area clean, use `st.sidebar`. This creates a collapsible left panel where you can place input widgets.

**Create a sidebar with input controls:**
```python
import streamlit as st

st.title("Hello Streamlit")  # This is in the main area

# Sidebar: Get user's name
with st.sidebar:
    name = st.text_input("What's your name?")
    color = st.selectbox("Favorite color?", ["Red", "Blue", "Green"])
```

**Key point:** The `with st.sidebar:` block determines where widgets appear:
- **Inside the block** (indented): Appears in the sidebar on the left
- **Outside the block** (not indented): Appears in the main area on the right

In the code above:
- `st.title("Hello Streamlit")` is **outside** → appears in the main area
- `st.text_input()` and `st.selectbox()` are **inside** → appear in the sidebar

**Use sidebar values in the main area:**
```python
# Main area displays the sidebar inputs
st.write(f"Name: {name}")
st.write(f"Color: {color}")

if name:
    st.write(f"Hello, {name}!")
    st.write(f"Great choice! {color} is awesome.")
else:
    st.write("Enter your name to see a greeting.")
```

Notice that all these `st.write()` calls are **outside** the `with st.sidebar:` block, so they appear in the **main area**. The variables `name` and `color` were defined inside the sidebar block, but you can use them anywhere in your script.

The sidebar is perfect for filters, settings, and configuration options—keeping them separate from your main content display.