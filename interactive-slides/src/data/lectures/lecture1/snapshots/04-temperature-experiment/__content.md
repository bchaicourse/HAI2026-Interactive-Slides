## Experimenting with Parameters: Temperature

When you call an LLM, you can control how it generates text using parameters. One of the most important is **temperature** (range: 0.0 to 2.0), which controls randomness in the model's outputs.

- **Temperature = 0.0**: Deterministic (always picks the most likely token)
- **Temperature = 2.0**: Highly creative (samples very varied outputs)

Let's see this in action by comparing both extremes.