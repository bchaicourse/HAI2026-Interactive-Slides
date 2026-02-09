## Step 3: Interpret Result

Finally, ask the LLM to explain the execution result in natural language. This completes the 3-step chain.

**Create an interpretation function:**
```python
def interpret_result(result, question):
    prompt = f"""
    Question: {question}

    Execution result:
    {result}

    Provide a clear, concise interpretation in 2-3 sentences.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    return response.choices[0].message.content
```

**Use it:**
```python
interpretation = interpret_result(execution_result, question)
print("Interpretation:")
print(interpretation)
```

Running the complete 3-step pipeline:

```
Step 1: Generating code...
Generated Code:
import pandas as pd

df = pd.read_csv('sample.csv')
average_score = df['Score'].mean()
print(average_score)

Step 2: Executing code...
Execution Result:
87.6


Step 3: Interpreting result...
Interpretation:
The average score across all individuals in the dataset is 87.6, indicating generally strong performance.
```

**Complete 3-step chain:**
1. **Generate Code** (LLM) - Writes Python code based on the schema
2. **Execute Code** (Python) - Reliably computes the result
3. **Interpret Result** (LLM) - Explains the result in natural language

This approach scales to large datasets and provides computational reliability while maintaining the flexibility of natural language interaction.
