## Multi-turn Conversations

The chat API supports **multi-turn conversations** by including previous messages in the `messages` array. This allows the model to maintain context across multiple exchanges.

### How It Works

Each message has a `role`:
- `system`: Sets the assistant's behavior
- `user`: User's input
- `assistant`: Model's previous responses

By including the assistant's previous response in the next API call, the model can reference earlier parts of the conversation.

### Example: Building Context

```python
messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is a Large Language Model?"},
    {"role": "assistant", "content": "A Large Language Model (LLM) is..."},
    {"role": "user", "content": "Summarize that in three words."}
]
```

The model can now reference "that" (its previous explanation) to provide a concise summary.

**Key Point:** You must manually include the conversation history in each API call. The API itself is stateless.
