## Building a Real Application

Now let's combine everything we've learned—**LLM-based analysis** (generate → execute → interpret) and **Streamlit UI** (display, inputs, sidebar, layout)—to build a real data analysis tool.

### Our Goal

Build a data analysis tool where:
1. Users **filter data visually** using sidebar controls (columns, genres, ratings, etc.)
2. Users **ask a factual question** about the filtered data (text input)
3. The system **generates Python code, executes it, and interprets the result** to answer the question

---

## Step 1: Setup Layout and Load Data

Let's work with a real movie dataset. Here's a preview of the first few rows:

```
Title,Worldwide Gross,Production Budget,Release Year,Content Rating,Running Time,Genre,Creative Type,Rotten Tomatoes Rating,IMDB Rating
From Dusk Till Dawn,25728961,20000000,1996,R,107,Horror,Fantasy,63,7.1
Broken Arrow,148345997,65000000,1996,R,108,Action,Contemporary Fiction,55,5.8
City Hall,20278055,40000000,1996,R,111,Drama,Contemporary Fiction,55,6.1
Happy Gilmore,38623460,10000000,1996,PG-13,92,Comedy,Contemporary Fiction,58,6.9
Fargo,51204567,7000000,1996,R,87,Thriller,Contemporary Fiction,94,8.3
```

Download the full dataset from the course repository and place it in the same directory as your `app.py`:

**Download:** https://github.com/bchaicourse/HAI2026-Week3-Practice/blob/main/movies.csv

**Configure the page and add a title:**
```python
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Analysis Tool", layout="wide")

st.title("Interactive Data Analysis Tool")
```

A data analysis app needs more horizontal space to display data, filters, and results. The `layout="wide"` parameter uses the full browser width. This must be the **first** Streamlit command.

**Load the dataset:**
```python
# Load data
df = pd.read_csv('movies.csv')
```

**Create the app structure:**

Now let's create a sidebar for filters and a two-column layout for displaying data and results:

```python
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
```

We've created the skeleton of our app:
- **Sidebar (left)**: Will contain our data filters
- **Column 1 (center-left)**: Will show the filtered dataset
- **Column 2 (center-right)**: Will display analysis results