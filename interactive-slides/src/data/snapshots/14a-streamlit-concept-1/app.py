import streamlit as st
import pandas as pd

# Headers using markdown in st.write()
st.write("# Data Analysis Tool")
st.write("This is regular text.")

# Create sample data
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 28],
    'Score': [85, 92, 78]
}
df = pd.DataFrame(data)

# Display interactive table using st.write()
st.write(df)