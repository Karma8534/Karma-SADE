---
source: https://platform.claude.com/docs/en/build-with-claude/token-counting
scraped: 2026-03-23
section: build-with-claude
---

# Token counting

Token counting enables you to determine the number of tokens in a message before sending it to Claude, helping you make informed decisions about your prompts and usage. With token counting, you can:
- Proactively manage rate limits and costs
- Make smart model routing decisions
- Optimize prompts to be a specific length

This feature is eligible for Zero Data Retention (ZDR).

## How to count message tokens

The token counting endpoint accepts the same structured list of inputs for creating a message, including support for system prompts, tools, images, and PDFs. The response contains the total number of input tokens.

The token count should be considered an **estimate**. In some cases, the actual number of input tokens used when creating a message may differ by a small amount.

### Supported models

All active models support token counting.

### Count tokens in basic messages

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.count_tokens(
    model="claude-opus-4-6",
    system="You are a scientist",
    messages=[{"role": "user", "content": "Hello, Claude"}],
)

print(response.json())
# {"input_tokens": 14}
```

```bash
curl https://api.anthropic.com/v1/messages/count_tokens \
    --header "x-api-key: $ANTHROPIC_API_KEY" \
    --header "content-type: application/json" \
    --header "anthropic-version: 2023-06-01" \
    --data '{
      "model": "claude-opus-4-6",
      "system": "You are a scientist",
      "messages": [{"role": "user", "content": "Hello, Claude"}]
    }'
```

### Count tokens with tools

```python
response = client.messages.count_tokens(
    model="claude-opus-4-6",
    tools=[
        {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"],
            },
        }
    ],
    messages=[{"role": "user", "content": "What is the weather like in San Francisco?"}],
)
# {"input_tokens": 403}
```

## Pricing and rate limits

Token counting is **free to use** but subject to requests per minute rate limits based on your usage tier.

| Usage tier | Requests per minute (RPM) |
|------------|---------------------------|
| 1          | 100                       |
| 2          | 2,000                     |
| 3          | 4,000                     |
| 4          | 8,000                     |

Token counting and message creation have separate and independent rate limits.
