## Step 2: Add Visual Filters

Now let's add filters to the sidebar so users can narrow down the data before analysis. We'll add two types of filters:
1. **Column filter**: Choose which columns to include
2. **Row filters**: Filter data by Genre, Release Year, and IMDB Rating

---

### Column Selection Filter

**Add column selection to the sidebar:**

```python
# Sidebar: Column selection
with st.sidebar:
    st.header("Data Filters")

    # Column selection
    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to include:",
        all_columns,
        default=all_columns
    )

    if not selected_columns:
        st.error("Please select at least one column.")
        st.stop()

    # Apply column filter
    filtered_df = df[selected_columns]
```

**Understanding the dual nature of this code:**

Notice how this code does two things simultaneously:

1. **UI Generation**: When `st.multiselect()` is called, Streamlit immediately renders a multiselect widget in the sidebar
2. **Data Filtering**: The function also returns the user's current selection, which is then used to filter the dataframe

Here's the flow:
- **First run** (when the page loads): `st.multiselect()` creates the widget AND returns the `default` value (all columns), so `filtered_df` starts with all columns
- **Subsequent runs** (when user changes selection): The script re-runs, `st.multiselect()` recreates the widget with the user's new selection, and `filtered_df` updates accordingly

`st.stop()` prevents errors if no columns are selected by halting script execution.

---

### Row Filters

**Add a subheader for row filters:**

```python
    # Row Filters
    st.subheader("Row Filters")
```

**Genre filter (multiselect):**

```python
    # Genre filter
    if 'Genre' in filtered_df.columns:
        genres = filtered_df['Genre'].dropna().unique()
        selected_genres = st.multiselect(
            "Filter by Genre:",
            genres,
            default=genres.tolist()
        )
        filtered_df = filtered_df[filtered_df['Genre'].isin(selected_genres)]
```

We check if the Genre column exists (in case user deselected it in the column filter above). Then we extract unique genres from `filtered_df`—the dataframe after column selection has been applied. After the user selects genres, we update `filtered_df` again by filtering rows. Notice how `filtered_df` gets progressively filtered: first by columns, then by genre.

**Release Year filter (slider):**

```python
    # Release Year filter
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
```

We calculate `min_year` and `max_year` from the current `filtered_df` (after column and genre filters). The slider returns a tuple `(start, end)`, which we use to further filter `filtered_df`.

**IMDB Rating filter (slider):**

```python
    # IMDB Rating filter
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
```

Same pattern: we compute `min_rating` and `max_rating` from `filtered_df` so the slider adapts to the current data.

---

### Maintain the Two-Column Layout

**Keep the same layout structure from Step 1:**

```python
# Two-column layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Filtered Dataset")
    st.write(filtered_df)

with col2:
    st.subheader("Analysis Results")
    st.write("Results will appear here...")
```

Now users have full control over their data—they can filter by columns, genres, years, and ratings. The filtered dataset displays in the left column, while the right column remains ready for analysis results in the next step.