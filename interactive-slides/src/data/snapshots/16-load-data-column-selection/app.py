import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Analysis Tool", layout="wide")

st.title("Interactive Data Analysis Tool")

# Load data
df = pd.read_csv('movies.csv')

# Sidebar placeholder
with st.sidebar:
    st.header("Data Filters")
    st.write("Filters will go here...")

# Two-column layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Filtered Dataset")
    st.write(df)  # Show the full dataset for now

with col2:
    st.subheader("Analysis Results")
    st.write("Results will appear here...")