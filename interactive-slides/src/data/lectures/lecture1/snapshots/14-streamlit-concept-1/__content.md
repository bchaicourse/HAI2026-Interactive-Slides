## Streamlit Concept 1: Displaying Content with `st.write()`

Streamlit's most versatile function is `st.write()`—it automatically handles different data types and renders them appropriately.

**Use `st.write()` for everything:**
```python
import streamlit as st
import pandas as pd

# Headers using markdown
st.write("# Data Analysis Tool")
st.write("This is regular text.")
```

You can create headers by passing markdown strings to `st.write()`. The `#` creates a large heading (equivalent to `<h1>` in HTML).

**`st.write()` also renders dataframes:**
```python
# Create sample data
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 28],
    'Score': [85, 92, 78]
}
df = pd.DataFrame(data)

# Display interactive table using st.write()
st.write(df)
```

When you pass a pandas DataFrame to `st.write()`, it automatically renders an interactive table with sorting and scrolling.

**Other specialized functions:**

Of course, Streamlit provides dedicated functions for specific use cases. For example, `st.title()` and `st.dataframe()` do the same jobs as the code above:

```python
st.title("Data Analysis Tool")  # Same as st.write("# Data Analysis Tool")
st.dataframe(df)                # Same as st.write(df)
```

You can find many more functions in the [Streamlit API Reference](https://docs.streamlit.io/develop/api-reference).