## Streamlit Concept 2: User Inputs

Streamlit provides widgets for collecting user input. Each widget returns a value that you can use in your code.

**Text input:**
```python
user_question = st.text_input(
    "Ask a question:",
    placeholder="e.g., What is the average score?"
)
```

The `placeholder` parameter shows hint text when the input is empty.

**Multiselect (choose multiple options):**
```python
selected_columns = st.multiselect("Select columns:", df.columns.tolist())
```

Returns a list of selected values.

**Slider (numeric range):**
```python
age_range = st.slider("Select age range:", 20, 40, (25, 35))
```

The parameters are: `(label, min_value, max_value, default_value)`. Returns a tuple `(start, end)` for range sliders.

**Button:**
```python
if st.button("Analyze"):
    st.write("Button clicked!")
```

Returns `True` when clicked, `False` otherwise.

---

## The Reactive Model

**Key concept:** When a user interacts with any widget, Streamlit **re-runs the entire script** from top to bottom.

Let's see what happens with the button in our code:

```python
if st.button("Analyze"):
    st.write("Button clicked!")

    if user_question:
        st.write(f"Your question: {user_question}")
    if selected_columns:
        st.write(f"Selected columns: {selected_columns}")
    st.write(f"Age range: {age_range[0]} to {age_range[1]}")
```

**Before clicking the button:**
- `st.button("Analyze")` returns `False`
- The `if` block doesn't execute
- You only see the input widgets

**After clicking the button:**
- The entire script re-runs from the beginning
- The screen is cleared and rebuilt from scratch
- `st.button("Analyze")` returns `True` (because it was just clicked)
- The `if` block executes and displays the results
- **Important:** Your input values (`user_question`, `selected_columns`, `age_range`) are preserved!

**Note:** While it's helpful to think of the screen being completely cleared and rebuilt, Streamlit is actually smarter—it only updates the parts that changed.