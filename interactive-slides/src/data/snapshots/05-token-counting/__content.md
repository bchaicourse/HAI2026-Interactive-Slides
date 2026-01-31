## Counting Tokens

When working with LLM APIs, you pay per token. Understanding token counts helps you estimate costs and avoid exceeding context limits.

**What is a token?** Tokens are chunks of text. Roughly:
- 1 token ≈ 4 characters in English
- 1 token ≈ ¾ words
- 100 tokens ≈ 75 words

The exact tokenization depends on the model. Use the `tiktoken` library to count tokens precisely.

### Installing tiktoken

```bash
pip install tiktoken
```

### Counting Tokens in a Prompt

Use `tiktoken` to get the exact token count for your text before sending it to the API.

**Step 1: Get the tokenizer for your model**
```python
import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4o-mini")
```

**Step 2: Encode your text into tokens**
```python
prompt = "What are the top three use cases of tokens in OpenAI API?"
tokens = encoding.encode(prompt)
```

**Step 3: Examine the results**
```python
print(f"Text: {prompt}")
print(f"Number of tokens: {len(tokens)}")
print(f"Token IDs: {tokens}")
```

**What this shows:**
- **Text**: Your original input string
- **Number of tokens**: How many tokens this text uses (affects your API costs)
- **Token IDs**: The list of integer IDs representing each token in the model's vocabulary. Each ID corresponds to a piece of text (word, subword, or character). This is what the model actually processes internally.