## Your First API Call

At its core, interacting with an LLM via the OpenAI API is straightforward. You send a message and receive a response. The `system` message defines the AI's role and behavior, while the `user` message is your actual query.

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is a Large Language Model?"}
    ]
)

print(response.choices[0].message.content)
```
