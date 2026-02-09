## Step 3: Add Question Input

Now that users can filter data visually, let's add the natural language question interface. Users will type their questions in the left column, and results will appear in the right column.

---

### Update the Left Column

**Display the filtered dataset and add question input:**

```python
with col1:
    st.subheader("Filtered Dataset")
    st.write(filtered_df)

    st.subheader("Ask a Question")
    user_question = st.text_input(
        "What would you like to know about this data?",
        placeholder="e.g., What is the average IMDB rating?"
    )

    analyze_button = st.button("Analyze", type="primary")
```

The `st.text_input()` widget creates a text box for user questions. The `placeholder` parameter shows example text when the input is empty.

The `st.button()` with `type="primary"` creates a prominent button that users click to submit their question.

---

### Update the Right Column

**Add conditional logic to show results:**

```python
with col2:
    st.subheader("Analysis Results")

    if analyze_button and user_question:
        st.info("Analysis pipeline will be implemented in the next step...")
    elif analyze_button and not user_question:
        st.error("Please enter a question.")
    else:
        st.write("Enter a question and click 'Analyze' to see results.")
```

This creates three different states:

1. **Button clicked with a question**: Shows a placeholder message (we'll add the real LLM pipeline in Step 4)
2. **Button clicked without a question**: Shows an error
3. **Initial state**: Shows instructions

---

### How It Works

When a user types a question and clicks "Analyze":

1. The entire script re-runs (remember Streamlit's reactive model!)
2. `user_question` contains the text the user typed
3. `analyze_button` returns `True` because it was just clicked
4. The `if` condition is satisfied, and the placeholder message displays

In the next step, we'll replace the placeholder with the actual LLM-based analysis pipeline (generate → execute → interpret) that we learned in Part 2.
