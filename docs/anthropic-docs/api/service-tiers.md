---
source: https://platform.claude.com/docs/en/api/service-tiers
scraped: 2026-03-23
section: api
---

# Service tiers

Different tiers of service allow you to balance availability, performance, and predictable costs based on your application's needs.

Anthropic offers three service tiers:
- **Priority Tier:** Best for workflows deployed in production where time, availability, and predictable pricing are important
- **Standard:** Default tier for both piloting and scaling everyday use cases
- **Batch:** Best for asynchronous workflows which can wait or benefit from being outside your normal capacity

## Standard Tier

The standard tier is the default service tier for all API requests. The API prioritizes these requests alongside all other requests with best-effort availability.

## Priority Tier

The API prioritizes requests in this tier over all other requests. This prioritization helps minimize "server overloaded" errors, even during peak times.

## How requests get assigned tiers

When handling a request, Anthropic decides to assign a request to Priority Tier when your organization has sufficient priority tier capacity for both input and output tokens per minute.

Anthropic counts usage against Priority Tier capacity as follows:

**Input Tokens**
- Cache reads as 0.1 tokens per token read from the cache
- Cache writes as 1.25 tokens per token written with a 5 minute TTL
- Cache writes as 2.00 tokens per token written with a 1 hour TTL
- Long-context (>200k input tokens) requests on Claude Sonnet 4.5 and Sonnet 4: 2 tokens per token
- US-only inference (`inference_geo: "us"`) on Claude Opus 4.6 and newer: 1.1 tokens per token
- All other input tokens: 1 token per token

**Output Tokens**
- Long-context (>200k input tokens) requests on Claude Sonnet 4.5 and Sonnet 4: 1.5 tokens per token
- US-only inference (`inference_geo: "us"`) on Claude Opus 4.6 and newer: 1.1 tokens per token
- All other output tokens: 1 token per token

Note: Requests assigned Priority Tier pull from both the Priority Tier capacity and the regular rate limits. If servicing the request would exceed the rate limits, the request is declined.

## Using service tiers

You can control which service tiers can be used for a request by setting the `service_tier` parameter:

```python
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude!"}],
    service_tier="auto",  # Automatically use Priority Tier when available, fallback to standard
)
```

The `service_tier` parameter accepts the following values:

- `"auto"` (default) - Uses the Priority Tier capacity if available, falling back to your other capacity if not
- `"standard_only"` - Only use standard tier capacity

The response `usage` object also includes the service tier assigned to the request:

```json
{
  "usage": {
    "input_tokens": 410,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0,
    "output_tokens": 585,
    "service_tier": "priority"
  }
}
```

When requesting `service_tier="auto"` with a model with a Priority Tier commitment, these response headers provide insights:
```text
anthropic-priority-input-tokens-limit: 10000
anthropic-priority-input-tokens-remaining: 9618
anthropic-priority-input-tokens-reset: 2025-01-12T23:11:59Z
anthropic-priority-output-tokens-limit: 10000
anthropic-priority-output-tokens-remaining: 6000
anthropic-priority-output-tokens-reset: 2025-01-12T23:12:21Z
```

## Get started with Priority Tier

Benefits of committing to Priority Tier capacity:
- **Higher availability**: Target 99.5% uptime with prioritized computational resources
- **Cost Control**: Predictable spend and discounts for longer commitments
- **Flexible overflow**: Automatically falls back to standard tier when you exceed your committed capacity

Commitment decisions:
- A number of input tokens per minute
- A number of output tokens per minute
- A commitment duration (1, 3, 6, or 12 months)
- A specific model version

### Supported models

Priority Tier is supported by: Claude Opus 4.6, Claude Opus 4.5, Claude Opus 4.1, Claude Opus 4, Claude Sonnet 4.6, Claude Sonnet 4.5, Claude Sonnet 4, Claude Sonnet 3.7 (deprecated), Claude Haiku 4.5, Claude Haiku 3.5 (deprecated).

### How to access Priority Tier

1. Contact sales to complete provisioning
2. (Optional) Update your API requests to set the `service_tier` parameter to `auto`
3. Monitor your usage through response headers and the Claude Console
