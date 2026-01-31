from openai import OpenAI
from dotenv import load_dotenv
import os
import tiktoken

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def estimate_cost(input_text, output_text, model="gpt-4o-mini"):
    """Estimate the cost of an API call."""
    encoding = tiktoken.encoding_for_model(model)

    input_tokens = len(encoding.encode(input_text))
    output_tokens = len(encoding.encode(output_text))

    # Pricing for gpt-4o-mini (per 1M tokens)
    input_price_per_million = 0.150
    output_price_per_million = 0.600

    input_cost = (input_tokens / 1_000_000) * input_price_per_million
    output_cost = (output_tokens / 1_000_000) * output_price_per_million
    total_cost = input_cost + output_cost

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost
    }

# Example usage
input_text = "Explain how large language models work in 100 words."
output_text = """Large language models are neural networks trained on vast amounts of text data.
They learn patterns in language by predicting the next word in a sequence. During training,
the model adjusts billions of parameters to minimize prediction errors. When you give it a prompt,
it generates text by repeatedly predicting the most likely next token based on the context.
These models use a Transformer architecture, which allows them to process long sequences efficiently
and capture complex relationships between words. The "large" refers to the number of parameters,
often reaching hundreds of billions."""

cost_info = estimate_cost(input_text, output_text)

print(f"Input tokens: {cost_info['input_tokens']}")
print(f"Output tokens: {cost_info['output_tokens']}")
print(f"Total tokens: {cost_info['total_tokens']}")
print(f"\nInput cost: ${cost_info['input_cost']:.6f}")
print(f"Output cost: ${cost_info['output_cost']:.6f}")
print(f"Total cost: ${cost_info['total_cost']:.6f}")