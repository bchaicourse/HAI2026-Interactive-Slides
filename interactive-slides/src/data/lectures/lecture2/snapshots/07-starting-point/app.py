import streamlit as st
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import json
from movie_tool import get_tools, query_movie_db

load_dotenv()
client = OpenAI()

st.set_page_config(page_title="Data Analysis Tool", layout="wide")
st.title("Interactive Data Analysis Tool")

df = pd.read_csv('movies.csv')

with st.sidebar:
    st.header("Data Filters")

    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to include:",
        all_columns,
        default=all_columns
    )

    if not selected_columns:
        st.error("Please select at least one column.")
        st.stop()

    filtered_df = df[selected_columns]

    st.subheader("Row Filters")

    if 'Genre' in filtered_df.columns:
        genres = filtered_df['Genre'].dropna().unique()
        selected_genres = st.multiselect(
            "Filter by Genre:",
            genres,
            default=genres.tolist()
        )
        filtered_df = filtered_df[filtered_df['Genre'].isin(selected_genres)]

    if 'Release Year' in filtered_df.columns:
        min_year = int(filtered_df['Release Year'].min())
        max_year = int(filtered_df['Release Year'].max())
        year_range = st.slider(
            "Filter by Release Year:",
            min_year,
            max_year,
            (min_year, max_year)
        )
        filtered_df = filtered_df[
            (filtered_df['Release Year'] >= year_range[0]) &
            (filtered_df['Release Year'] <= year_range[1])
        ]

    if 'IMDB Rating' in filtered_df.columns:
        min_rating = float(filtered_df['IMDB Rating'].min())
        max_rating = float(filtered_df['IMDB Rating'].max())
        rating_range = st.slider(
            "Filter by IMDB Rating:",
            min_rating,
            max_rating,
            (min_rating, max_rating)
        )
        filtered_df = filtered_df[
            (filtered_df['IMDB Rating'] >= rating_range[0]) &
            (filtered_df['IMDB Rating'] <= rating_range[1])
        ]

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Filtered Dataset")
    st.write(filtered_df)

    st.subheader("Ask a Question")
    user_question = st.text_input(
        "What would you like to know about this data?",
        placeholder="e.g., What is the average IMDB rating?"
    )
    analyze_button = st.button("Analyze", type="primary")

with col2:
    st.subheader("Analysis Results")

    if analyze_button and user_question:
        tools = get_tools(filtered_df)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a data analyst with access to a tool that executes Python code on a movie database."},
                {"role": "user", "content": user_question}
            ],
            tools=tools
        )

        message = response.choices[0].message

        if message.tool_calls:
            tool_call = message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            result = query_movie_db(args["code"], filtered_df)

            st.write("**Generated Code:**")
            st.code(args["code"], language='python')

            st.write("**Result:**")
            st.code(result, language="text")
        else:
            st.write(message.content)

    elif analyze_button and not user_question:
        st.error("Please enter a question.")
