---
source: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
scraped: 2026-03-23
section: build-with-claude
---

# Prompt caching

Prompt caching optimizes your API usage by allowing resuming from specific prefixes in your prompts. This significantly reduces processing time and costs for repetitive tasks or prompts with consistent elements.

**Important Note on Data Retention:**
Prompt caching stores KV cache representations and cryptographic hashes of cached content, but does not store the raw text of prompts or responses. This may be suitable for customers who require zero-data-retention (ZDR-type) commitments.

## Two Ways to Enable Prompt Caching

1. **Automatic caching**: Add a single `cache_control` field at the top level of your request. The system automatically applies the cache breakpoint to the last cacheable block and moves it forward as conversations grow. Best for multi-turn conversations.

2. **Explicit cache breakpoints**: Place `cache_control` directly on individual content blocks for fine-grained control over exactly what gets cached.

### Quick Start - Automatic Caching

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    cache_control={"type": "ephemeral"},
    system="You are an AI assistant tasked with analyzing literary works.",
    messages=[
        {
            "role": "user",
            "content": "Analyze the major themes in 'Pride and Prejudice'.",
        }
    ],
)
print(response.usage.model_dump_json())
```

## How Prompt Caching Works

1. The system checks if a prompt prefix (up to a specified cache breakpoint) is already cached from a recent query
2. If found, it uses the cached version, reducing processing time and costs
3. Otherwise, it processes the full prompt and caches the prefix once the response begins

**Default cache lifetime:** 5 minutes (refreshed at no additional cost when used)
**Optional 1-hour cache:** Available at 2x the base input token price

## Pricing

| Model | Base Input | 5m Cache Writes | 1h Cache Writes | Cache Hits | Output |
|-------|-----------|-----------------|-----------------|-----------|--------|
| Claude Opus 4.6 | $5/MTok | $6.25/MTok | $10/MTok | $0.50/MTok | $25/MTok |
| Claude Sonnet 4.6 | $3/MTok | $3.75/MTok | $6/MTok | $0.30/MTok | $15/MTok |
| Claude Haiku 4.5 | $1/MTok | $1.25/MTok | $2/MTok | $0.10/MTok | $5/MTok |

**Pricing multipliers:**
- 5-minute cache write tokens: 1.25x base input price
- 1-hour cache write tokens: 2x base input price
- Cache read tokens: 0.1x base input price

## Supported Models

- Claude Opus 4.6, 4.5, 4.1, 4
- Claude Sonnet 4.6, 4.5, 4, 3.7
- Claude Haiku 4.5, 3.5, 3

## Automatic Caching in Multi-Turn Conversations

With automatic caching, the cache point moves forward automatically as conversations grow:

| Request | Cache Behavior |
|---------|---|
| Request 1 | Everything written to cache |
| Request 2 | Previous content read from cache; new content written |
| Request 3 | Previous content read from cache; new content written |

## Explicit Cache Breakpoints

For more control, place `cache_control` directly on individual blocks:

```json
{
  "model": "claude-opus-4-6",
  "max_tokens": 1024,
  "system": [
    {
      "type": "text",
      "text": "You are an AI assistant.",
      "cache_control": { "type": "ephemeral" }
    }
  ],
  "messages": [{ "role": "user", "content": "Hello" }]
}
```

### Important Guidelines for Explicit Breakpoints

**Three Core Principles:**

1. **Cache writes happen only at your breakpoint** - The system writes exactly one cache entry at the block you mark
2. **Cache reads look backward** - The system checks prior requests walking backward one block at a time
3. **Lookback window is 20 blocks** - The system checks at most 20 positions per breakpoint

**Key Takeaway:** Place `cache_control` on the last block whose prefix is identical across requests. If you place it on content that changes every request (timestamps, per-request context), you'll never get a cache hit.

### What Can Be Cached

- Tool definitions
- System messages
- Text messages (user and assistant turns)
- Images & Documents
- Tool use and tool results

### What Cannot Be Cached

- Thinking blocks cannot be explicitly marked with `cache_control` (but ARE cached alongside other content in previous assistant turns)
- Sub-content blocks like citations (though source documents can be cached)
- Empty text blocks

## Cache Invalidation

Changes at each level invalidate that level and all subsequent levels (following the hierarchy: tools → system → messages):

- **Tool definitions changes**: Invalidates entire cache
- **Web search/citations toggle**: Invalidates system and message cache
- **Speed setting changes**: Invalidates system and message cache
- **Tool choice changes**: Invalidates only message cache
- **Images added/removed**: Invalidates only message cache

## Minimum Token Requirements

| Model | Minimum Cacheable Length |
|-------|--------------------------|
| Claude Opus 4.6, 4.5 | 4,096 tokens |
| Claude Sonnet 4.6 | 2,048 tokens |
| Claude Haiku 4.5 | 4,096 tokens |
| Claude Haiku 3.5, 3 | 2,048 tokens |
| Others | 1,024 tokens |

## Tracking Cache Performance

Monitor these usage fields in API responses:

- `cache_creation_input_tokens`: Tokens written to cache
- `cache_read_input_tokens`: Tokens retrieved from cache
- `input_tokens`: Tokens after the last cache breakpoint

**Total input tokens calculation:**
```
total_input_tokens = cache_read_input_tokens + cache_creation_input_tokens + input_tokens
```

## 1-Hour Cache Duration

For extended cache lifetime, specify TTL in cache_control:

```json
{
  "cache_control": {
    "type": "ephemeral",
    "ttl": "1h"
  }
}
```

Use 1-hour cache when:
- Prompts are used less frequently than every 5 minutes but more frequently than every hour
- Latency is critical and follow-ups may be sent beyond 5 minutes
- You want to improve rate limit utilization

## Best Practices

- Start with **automatic caching** for multi-turn conversations
- Use **explicit breakpoints** when caching different sections with different change frequencies
- Cache stable, reusable content (system instructions, large contexts, tool definitions)
- Place cached content at the prompt's beginning
- Place the breakpoint on the last block that stays identical across requests
- Regularly analyze cache hit rates and adjust strategy

## Common Use Cases

- **Conversational agents**: Reduce cost/latency for extended conversations with long instructions or uploaded documents
- **Coding assistants**: Keep relevant codebase sections in prompt
- **Large document processing**: Incorporate complete long-form material without increasing latency
- **Detailed instruction sets**: Share 20+ diverse examples of high-quality answers
- **Agentic tool use**: Improve performance for multiple tool calls and iterative changes
- **Knowledge base chat**: Embed entire documents and let users ask questions

## Important Update

Starting February 5, 2026, prompt caching will use **workspace-level isolation** instead of organization-level isolation on the Claude API and Azure AI Foundry (preview). Caches will be isolated per workspace, ensuring data separation between workspaces within the same organization.
