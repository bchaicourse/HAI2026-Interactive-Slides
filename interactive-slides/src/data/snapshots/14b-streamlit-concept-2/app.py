import streamlit as st
import pandas as pd

st.write("# User Input Demo")

# Create sample data for the widgets
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 28],
    'Score': [85, 92, 78]
}
df = pd.DataFrame(data)

# Text input
user_question = st.text_input(
    "Ask a question:",
    placeholder="e.g., What is the average score?"
)

# Multiselect
selected_columns = st.multiselect("Select columns:", df.columns.tolist())

# Slider
age_range = st.slider("Select age range:", 20, 40, (25, 35))

# Button
if st.button("Analyze"):
    st.write("Button clicked!")

    # Show what was selected
    if user_question:
        st.write(f"Your question: {user_question}")
    if selected_columns:
        st.write(f"Selected columns: {selected_columns}")
    st.write(f"Age range: {age_range[0]} to {age_range[1]}")