# Part 2: Analyzing Data with LLMs

Now let's explore how to use LLMs for data analysis. Traditional data analysis tools require you to write specific queries or code for each question. The advantage of using LLMs is that users can ask questions in natural language, making data exploration more flexible and accessible.

## Naive Approach: Ask the LLM to Calculate

Let's try the simplest approach: ask the LLM to analyze data directly. We'll calculate the average score from a simple CSV dataset.

**sample.csv:**
```
Name,Age,Score
Alice,25,85
Bob,30,92
Charlie,28,78
Diana,35,88
Eve,22,95
```

**Load the data and ask the LLM:**
```python
df = pd.read_csv('sample.csv')
csv_content = df.to_csv(index=False)

prompt = f"""
Here is a dataset:

{csv_content}

Calculate the average Score.
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.0
)

print(response.choices[0].message.content)
```

The LLM analyzes the data and shows step-by-step reasoning:

```
To calculate the average score, you need to sum all the scores and then divide by the number of entries.

Here are the scores from the dataset:
- Alice: 85
- Bob: 92
- Charlie: 78
...

Now, let's sum the scores:
85 + 92 + 78 + 88 + 95 = 438

Next, divide the total score by the number of entries (which is 5):
Average Score = 438 / 5 = 87.6

So, the average score is **87.6**.
```

For this simple example, it works!

### But This Approach Has Serious Limitations

**Problem 1: Token Limits**
- Works for 5 rows, but what about 10,000 rows?
- Large datasets exceed the model's context window (128,000 tokens for gpt-4o-mini)
- You can't paste entire datasets into prompts

**Problem 2: LLMs Can't Do Math Reliably**
- The model uses probabilistic token prediction, not actual computation
- Simple calculations might work, but complex aggregations will fail
- **You cannot trust the LLM to do arithmetic accurately**

We need a better approach that scales and computes reliably.
