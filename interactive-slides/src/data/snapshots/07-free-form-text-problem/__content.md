## The Problem with Free-Form Text Output

Natural language is great for humans, but terrible for programs. Consider this task: extract specific information from text.

### Attempting Unstructured Extraction

**The prompt:**
```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": """
        Extract the following details from this text:

        Text: 'Alice Smith was born on June 12, 1990.
        She recently bought a car, a red 2020 Toyota Corolla...'

        Details to Extract:
        - Name
        - Date of Birth
        - Car Model
        - Car Year
        ...
        """
    }]
)
```

**The output:**
```
Here are the extracted details:

- **Name**: Alice Smith
- **Date of Birth**: June 12, 1990
- **Car Model**: Toyota Corolla
...
```

### Why This Is Problematic

The output is markdown-formatted text. To use this in a program, you would need to:

1. **Parse the markdown** (what if it uses `*` instead of `-`?)
2. **Handle format variations** (sometimes it might use numbered lists, or no formatting at all)
3. **Extract each field reliably** (regex? string splitting? both fragile)

This is **brittle and error-prone**. Different runs might produce different formats, breaking your parsing logic.

**Solution:** Use structured outputs with Pydantic schemas (next section).