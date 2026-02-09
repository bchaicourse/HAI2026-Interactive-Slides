import streamlit as st

st.title("Hello Streamlit")

# Simple inputs (not in sidebar for this example)
name = st.text_input("What's your name?")
color = st.selectbox("Favorite color?", ["Red", "Blue", "Green"])

# Two-column layout
col1, col2 = st.columns(2)

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