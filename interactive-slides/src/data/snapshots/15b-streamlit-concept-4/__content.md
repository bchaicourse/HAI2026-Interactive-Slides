## Streamlit Concept 4: Layout Control

By default, Streamlit displays everything **vertically** (top to bottom). We learned that `st.sidebar` lets you place content **horizontally** (sidebar on the left, main area on the right). But what if you want to arrange content **horizontally within the main area** itself?

Use `st.columns()` to create side-by-side layouts. This is perfect for displaying related information in multiple columns.

**Create a two-column layout:**
```python
import streamlit as st

st.title("Hello Streamlit")

# Two-column layout
col1, col2 = st.columns(2)
```

`st.columns(2)` creates two columns of equal width. You can also specify different widths with ratios like `st.columns([1, 2])` for a 1:2 ratio.

**Place content in each column:**
```python
with col1:
    st.subheader("Your Input")
    st.write(f"Name: {name}")
    st.write(f"Color: {color}")

with col2:
    st.subheader("Our Response")
    if name:
        st.write(f"Hello, {name}!")
        st.write(f"Great choice! {color} is awesome.")
    else:
        st.write("Enter your name to see a greeting.")
```

Everything inside a `with col1:` or `with col2:` block appears in that specific column, allowing you to create sophisticated multi-column layouts.