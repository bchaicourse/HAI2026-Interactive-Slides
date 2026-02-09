import streamlit as st

st.title("Hello Streamlit")

# Sidebar: Get user's name
with st.sidebar:
    name = st.text_input("What's your name?")
    color = st.selectbox("Favorite color?", ["Red", "Blue", "Green"])

# Main area displays the sidebar inputs
st.write(f"Name: {name}")
st.write(f"Color: {color}")

if name:
    st.write(f"Hello, {name}!")
    st.write(f"Great choice! {color} is awesome.")
else:
    st.write("Enter your name to see a greeting.")