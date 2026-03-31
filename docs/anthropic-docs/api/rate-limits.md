---
source: https://platform.claude.com/docs/en/api/rate-limits
scraped: 2026-03-23
section: api
---

# Rate limits

To mitigate misuse and manage capacity on the API, limits are in place on how much an organization can use the Claude API.

There are two types of limits:

1. **Spend limits** set a maximum monthly cost an organization can incur for API usage.
2. **Rate limits** set the maximum number of API requests an organization can make over a defined period of time.

## About rate limits

* Limits are defined by **usage tier**, where each tier is associated with a different set of spend and rate limits.
* Your organization will increase tiers automatically as you reach certain thresholds.
* Limits are set at the organization level.
* The API uses the token bucket algorithm to do rate limiting.
* All limits represent maximum allowed usage, not guaranteed minimums.

## Spend limits

### Requirements to advance tier

| Usage Tier | Credit Purchase | Max Credit Purchase | Monthly Spend Limit |
|------------|-----------------|---------------------|---------------------|
| Tier 1     | $5              | $100                | $100                |
| Tier 2     | $40             | $500                | $500                |
| Tier 3     | $200            | $1,000              | $1,000              |
| Tier 4     | $400            | $200,000            | $200,000            |
| Monthly Invoicing | N/A      | N/A                 | No limit            |

## Rate limits

The rate limits for the Messages API are measured in requests per minute (RPM), input tokens per minute (ITPM), and output tokens per minute (OTPM). If you exceed any rate limit you will get a 429 error, along with a `retry-after` header.

### Cache-aware ITPM

For most Claude models, only uncached input tokens count towards your ITPM rate limits:
- `input_tokens` (tokens after the last cache breakpoint) — **Count towards ITPM**
- `cache_creation_input_tokens` (tokens being written to cache) — **Count towards ITPM**
- `cache_read_input_tokens` (tokens read from cache) — **Do NOT count towards ITPM** for most models

Some older models (marked with †) also count `cache_read_input_tokens` towards ITPM rate limits.

### Tier 1 Rate Limits

| Model | RPM | ITPM | OTPM |
|-------|-----|------|------|
| Claude Sonnet 4.x | 50 | 30,000 | 8,000 |
| Claude Sonnet 3.7 (deprecated) | 50 | 20,000 | 8,000 |
| Claude Haiku 4.5 | 50 | 50,000 | 10,000 |
| Claude Haiku 3.5 (deprecated) | 50 | 50,000† | 10,000 |
| Claude Haiku 3 | 50 | 50,000† | 10,000 |
| Claude Opus 4.x | 50 | 30,000 | 8,000 |

### Tier 2 Rate Limits

| Model | RPM | ITPM | OTPM |
|-------|-----|------|------|
| Claude Sonnet 4.x | 1,000 | 450,000 | 90,000 |
| Claude Sonnet 3.7 (deprecated) | 1,000 | 40,000 | 16,000 |
| Claude Haiku 4.5 | 1,000 | 450,000 | 90,000 |
| Claude Haiku 3.5 (deprecated) | 1,000 | 100,000† | 20,000 |
| Claude Haiku 3 | 1,000 | 100,000† | 20,000 |
| Claude Opus 4.x | 1,000 | 450,000 | 90,000 |

### Tier 3 Rate Limits

| Model | RPM | ITPM | OTPM |
|-------|-----|------|------|
| Claude Sonnet 4.x | 2,000 | 800,000 | 160,000 |
| Claude Sonnet 3.7 (deprecated) | 2,000 | 80,000 | 32,000 |
| Claude Haiku 4.5 | 2,000 | 1,000,000 | 200,000 |
| Claude Haiku 3.5 (deprecated) | 2,000 | 200,000† | 40,000 |
| Claude Haiku 3 | 2,000 | 200,000† | 40,000 |
| Claude Opus 4.x | 2,000 | 800,000 | 160,000 |

### Tier 4 Rate Limits

| Model | RPM | ITPM | OTPM |
|-------|-----|------|------|
| Claude Sonnet 4.x | 4,000 | 2,000,000 | 400,000 |
| Claude Sonnet 3.7 (deprecated) | 4,000 | 200,000 | 80,000 |
| Claude Haiku 4.5 | 4,000 | 4,000,000 | 800,000 |
| Claude Haiku 3.5 (deprecated) | 4,000 | 400,000† | 80,000 |
| Claude Haiku 3 | 4,000 | 400,000† | 80,000 |
| Claude Opus 4.x | 4,000 | 2,000,000 | 400,000 |

* Opus 4.x rate limit applies to combined traffic across Opus 4.6, Opus 4.5, Opus 4.1, and Opus 4.
** Sonnet 4.x rate limit applies to combined traffic across Sonnet 4.6, Sonnet 4.5, and Sonnet 4.
† Limit counts `cache_read_input_tokens` towards ITPM usage.

### Message Batches API Rate Limits

| Tier | RPM | Max batch requests in queue | Max batch requests per batch |
|------|-----|----------------------------|------------------------------|
| Tier 1 | 50 | 100,000 | 100,000 |
| Tier 2 | 1,000 | 200,000 | 100,000 |
| Tier 3 | 2,000 | 300,000 | 100,000 |
| Tier 4 | 4,000 | 500,000 | 100,000 |

### Fast mode rate limits

When using fast mode (beta: research preview) with `speed: "fast"` on Opus 4.6, dedicated rate limits apply that are separate from standard Opus rate limits. When fast mode rate limits are exceeded, the API returns a `429` error with a `retry-after` header.

## Setting lower limits for Workspaces

You can set custom spend and rate limits per Workspace:
- You cannot set limits on the default Workspace.
- If not set, Workspace limits match the Organization's limit.
- Organization-wide limits always apply.

## Response headers

| Header | Description |
|--------|-------------|
| `retry-after` | The number of seconds to wait until you can retry the request. |
| `anthropic-ratelimit-requests-limit` | The maximum number of requests allowed within any rate limit period. |
| `anthropic-ratelimit-requests-remaining` | The number of requests remaining before being rate limited. |
| `anthropic-ratelimit-requests-reset` | The time when the request rate limit will be fully replenished (RFC 3339). |
| `anthropic-ratelimit-tokens-limit` | The maximum number of tokens allowed within any rate limit period. |
| `anthropic-ratelimit-tokens-remaining` | The number of tokens remaining before being rate limited. |
| `anthropic-ratelimit-tokens-reset` | The time when the token rate limit will be fully replenished (RFC 3339). |
| `anthropic-ratelimit-input-tokens-limit` | The maximum number of input tokens allowed within any rate limit period. |
| `anthropic-ratelimit-input-tokens-remaining` | The number of input tokens remaining before being rate limited. |
| `anthropic-ratelimit-input-tokens-reset` | The time when the input token rate limit will be fully replenished (RFC 3339). |
| `anthropic-ratelimit-output-tokens-limit` | The maximum number of output tokens allowed within any rate limit period. |
| `anthropic-ratelimit-output-tokens-remaining` | The number of output tokens remaining before being rate limited. |
| `anthropic-ratelimit-output-tokens-reset` | The time when the output token rate limit will be fully replenished (RFC 3339). |
| `anthropic-priority-input-tokens-limit` | Priority Tier input tokens limit. (Priority Tier only) |
| `anthropic-priority-input-tokens-remaining` | Priority Tier input tokens remaining. (Priority Tier only) |
| `anthropic-priority-input-tokens-reset` | When Priority Tier input token rate limit will be replenished. (Priority Tier only) |
| `anthropic-priority-output-tokens-limit` | Priority Tier output tokens limit. (Priority Tier only) |
| `anthropic-priority-output-tokens-remaining` | Priority Tier output tokens remaining. (Priority Tier only) |
| `anthropic-priority-output-tokens-reset` | When Priority Tier output token rate limit will be replenished. (Priority Tier only) |
