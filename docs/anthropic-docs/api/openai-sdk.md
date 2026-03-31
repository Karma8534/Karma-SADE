---
source: https://platform.claude.com/docs/en/api/openai-sdk
scraped: 2026-03-23
section: api
---

# OpenAI SDK compatibility

Anthropic provides a compatibility layer that enables you to use the OpenAI SDK to test the Claude API. With a few code changes, you can quickly evaluate Anthropic model capabilities.

Note: This compatibility layer is primarily intended to test and compare model capabilities, and is not considered a long-term or production-ready solution for most use cases. For the best experience and access to Claude API's full feature set (PDF processing, citations, extended thinking, and prompt caching), use the native Claude API.

## Getting started with the OpenAI SDK

To use the OpenAI SDK compatibility feature:

1. Use an official OpenAI SDK
2. Update your base URL to point to the Claude API
3. Replace your API key with a Claude API key
4. Update your model name to use a Claude model

### Quick start example

```python
# Python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),  # Your Claude API key
    base_url="https://api.anthropic.com/v1/",  # the Claude API endpoint
)

response = client.chat.completions.create(
    model="claude-opus-4-6",  # Claude model name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who are you?"},
    ],
)

print(response.choices[0].message.content)
```

```typescript
// TypeScript
import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: "ANTHROPIC_API_KEY", // Your Claude API key
  baseURL: "https://api.anthropic.com/v1/" // Claude API endpoint
});

const response = await openai.chat.completions.create({
  messages: [{ role: "user", content: "Who are you?" }],
  model: "claude-opus-4-6" // Claude model name
});

console.log(response.choices[0].message.content);
```

## Important OpenAI compatibility limitations

### API behavior

* The `strict` parameter for function calling is ignored. For guaranteed schema conformance, use the native Claude API with Structured Outputs.
* Audio input is not supported.
* Prompt caching is not supported in the OpenAI SDK compatibility layer (but is supported in the Anthropic SDK).
* System/developer messages are hoisted and concatenated to the beginning of the conversation, as Anthropic only supports a single initial system message.

Most unsupported fields are silently ignored rather than producing errors.

### System / developer message hoisting

Since Anthropic only supports an initial system message, the API takes all system/developer messages and concatenates them together with a single newline between them. This full string is then supplied as a single system message at the start of the messages.

### Extended thinking support

You can enable extended thinking capabilities by adding the `thinking` parameter:

```python
# Python
response = client.chat.completions.create(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": "Who are you?"}],
    extra_body={"thinking": {"type": "enabled", "budget_tokens": 2000}},
)
```

```typescript
// TypeScript
const response = await openai.chat.completions.create({
  messages: [{ role: "user", content: "Who are you?" }],
  model: "claude-sonnet-4-6",
  // @ts-expect-error
  thinking: { type: "enabled", budget_tokens: 2000 }
});
```

## Rate limits

Rate limits follow Anthropic's standard limits for the `/v1/messages` endpoint.

## Detailed OpenAI compatible API support

### Request fields

| Field | Support status |
|--------|----------------|
| `model` | Use Claude model names |
| `max_tokens` | Fully supported |
| `max_completion_tokens` | Fully supported |
| `stream` | Fully supported |
| `stream_options` | Fully supported |
| `top_p` | Fully supported |
| `parallel_tool_calls` | Fully supported |
| `stop` | All non-whitespace stop sequences work |
| `temperature` | Between 0 and 1 (inclusive). Values greater than 1 are capped at 1. |
| `n` | Must be exactly 1 |
| `logprobs` | Ignored |
| `metadata` | Ignored |
| `response_format` | Ignored |
| `prediction` | Ignored |
| `presence_penalty` | Ignored |
| `frequency_penalty` | Ignored |
| `seed` | Ignored |
| `service_tier` | Ignored |
| `audio` | Ignored |
| `logit_bias` | Ignored |
| `store` | Ignored |
| `user` | Ignored |
| `modalities` | Ignored |
| `top_logprobs` | Ignored |
| `reasoning_effort` | Ignored |

### Tools fields

`tools[n].function` fields:

| Field | Support status |
|-------|----------------|
| `name` | Fully supported |
| `description` | Fully supported |
| `parameters` | Fully supported |
| `strict` | Ignored |

### Messages array fields

**Developer/System role:** Content is fully supported but hoisted to initial system message. `name` is ignored.

**User role:**
- `content` as string — Fully supported
- `content` as array, `type == "text"` — Fully supported
- `content` as array, `type == "image_url"` — `url` supported, `detail` ignored
- `content` as array, `type == "input_audio"` — Ignored
- `content` as array, `type == "file"` — Ignored

**Assistant role:**
- `content` as string or `type == "text"` — Fully supported
- `tool_calls` — Fully supported
- `function_call` — Fully supported
- `audio` — Ignored
- `refusal` — Ignored

**Tool role:**
- `content` as string or `type == "text"` — Fully supported
- `tool_call_id` — Fully supported
- `tool_choice` — Fully supported
- `name` — Ignored

### Response fields

| Field | Support status |
|-------|----------------|
| `id` | Fully supported |
| `choices[]` | Will always have a length of 1 |
| `choices[].finish_reason` | Fully supported |
| `choices[].message.role` | Fully supported |
| `choices[].message.content` | Fully supported |
| `choices[].message.tool_calls` | Fully supported |
| `object` | Fully supported |
| `created` | Fully supported |
| `model` | Fully supported |
| `usage.completion_tokens` | Fully supported |
| `usage.prompt_tokens` | Fully supported |
| `usage.total_tokens` | Fully supported |
| `usage.completion_tokens_details` | Always empty |
| `usage.prompt_tokens_details` | Always empty |
| `choices[].message.refusal` | Always empty |
| `logprobs` | Always empty |
| `service_tier` | Always empty |
| `system_fingerprint` | Always empty |

### Header compatibility

| Header | Support Status |
|---------|----------------|
| `x-ratelimit-limit-requests` | Fully supported |
| `x-ratelimit-limit-tokens` | Fully supported |
| `x-ratelimit-remaining-requests` | Fully supported |
| `x-ratelimit-remaining-tokens` | Fully supported |
| `x-ratelimit-reset-requests` | Fully supported |
| `x-ratelimit-reset-tokens` | Fully supported |
| `retry-after` | Fully supported |
| `request-id` | Fully supported |
| `openai-version` | Always `2020-10-01` |
| `authorization` | Fully supported |
| `openai-processing-ms` | Always empty |
