## Estimating API Costs

OpenAI charges based on tokens used. For **gpt-4o-mini** (as of 2026):

- **Input tokens**: $0.150 per 1M tokens
- **Output tokens**: $0.600 per 1M tokens

Note that output tokens are 4x more expensive than input tokens, as generating text requires more computation than processing it.

### Creating a Cost Estimation Function

**Step 1: Define the function and get token counts**
```python
def estimate_cost(input_text, output_text, model="gpt-4o-mini"):
    encoding = tiktoken.encoding_for_model(model)

    input_tokens = len(encoding.encode(input_text))
    output_tokens = len(encoding.encode(output_text))
```

**Step 2: Set the pricing (per 1 million tokens)**
```python
    input_price_per_million = 0.150
    output_price_per_million = 0.600
```

**Step 3: Calculate costs**
```python
    input_cost = (input_tokens / 1_000_000) * input_price_per_million
    output_cost = (output_tokens / 1_000_000) * output_price_per_million
    total_cost = input_cost + output_cost
```

**Step 4: Return all information**
```python
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost
    }
```

### Using the Function

```python
input_text = "Explain how large language models work in 100 words."
output_text = """Large language models are neural networks..."""

cost_info = estimate_cost(input_text, output_text)
print(f"Total cost: ${cost_info['total_cost']:.6f}")
```

This helps you estimate costs before making API calls, especially important when processing large amounts of text.