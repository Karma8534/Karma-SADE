---
source: https://platform.claude.com/docs/en/about-claude/pricing
scraped: 2026-03-23
---

# Pricing

Learn about Anthropic's pricing structure for models and features

---

This page provides detailed pricing information for Anthropic's models and features. All prices are in USD.

For the most current pricing information, please visit [claude.com/pricing](https://claude.com/pricing).

## Model pricing

| Model | Base Input Tokens | 5m Cache Writes | 1h Cache Writes | Cache Hits & Refreshes | Output Tokens |
|---|---|---|---|---|---|
| Claude Opus 4.6 | $5 / MTok | $6.25 / MTok | $10 / MTok | $0.50 / MTok | $25 / MTok |
| Claude Opus 4.5 | $5 / MTok | $6.25 / MTok | $10 / MTok | $0.50 / MTok | $25 / MTok |
| Claude Opus 4.1 | $15 / MTok | $18.75 / MTok | $30 / MTok | $1.50 / MTok | $75 / MTok |
| Claude Opus 4 | $15 / MTok | $18.75 / MTok | $30 / MTok | $1.50 / MTok | $75 / MTok |
| Claude Sonnet 4.6 | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Sonnet 4.5 | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Sonnet 4 | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Sonnet 3.7 (deprecated) | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Haiku 4.5 | $1 / MTok | $1.25 / MTok | $2 / MTok | $0.10 / MTok | $5 / MTok |
| Claude Haiku 3.5 | $0.80 / MTok | $1 / MTok | $1.6 / MTok | $0.08 / MTok | $4 / MTok |
| Claude Opus 3 (deprecated) | $15 / MTok | $18.75 / MTok | $30 / MTok | $1.50 / MTok | $75 / MTok |
| Claude Haiku 3 | $0.25 / MTok | $0.30 / MTok | $0.50 / MTok | $0.03 / MTok | $1.25 / MTok |

> MTok = Million tokens. The "Base Input Tokens" column shows standard input pricing, "Cache Writes" and "Cache Hits" are specific to prompt caching, and "Output Tokens" shows output pricing.

## Third-party platform pricing

Claude models are available on AWS Bedrock, Google Vertex AI, and Microsoft Foundry. For official pricing, visit:
- [AWS Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)
- [Google Vertex AI pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing)
- [Microsoft Foundry pricing](https://azure.microsoft.com/en-us/pricing/details/ai-foundry/#pricing)

> **Regional endpoint pricing for Claude 4.5 models and beyond**
>
> Starting with Claude Sonnet 4.5 and Haiku 4.5, AWS Bedrock and Google Vertex AI offer two endpoint types:
> - **Global endpoints**: Dynamic routing across regions for maximum availability
> - **Regional endpoints**: Data routing guaranteed within specific geographic regions
>
> Regional endpoints include a 10% premium over global endpoints. The Claude API (1P) is global by default and unaffected by this change.

## Feature-specific pricing

### Prompt caching

Prompt caching uses the following pricing multipliers relative to base input token rates:

| Cache operation | Multiplier | Duration |
|:---|:---|:---|
| 5-minute cache write | 1.25x base input price | Cache valid for 5 minutes |
| 1-hour cache write | 2x base input price | Cache valid for 1 hour |
| Cache read (hit) | 0.1x base input price | Same duration as the preceding write |

Cache write tokens are charged when content is first stored. Cache read tokens are charged when a subsequent request retrieves the cached content. A cache hit costs 10% of the standard input price, which means caching pays off after just one cache read for the 5-minute duration (1.25x write), or after two cache reads for the 1-hour duration (2x write).

### Data residency pricing

For Claude Opus 4.6 and newer models, specifying US-only inference via the `inference_geo` parameter incurs a 1.1x multiplier on all token pricing categories. Global routing (the default) uses standard pricing.

### Fast mode pricing

Fast mode (beta: research preview) for Claude Opus 4.6 provides significantly faster output at premium pricing (6x standard rates).

| Input | Output |
|:---|:---|
| $30 / MTok | $150 / MTok |

Fast mode is not available with the Batch API.

### Batch processing

The Batch API allows asynchronous processing of large volumes of requests with a 50% discount on both input and output tokens.

| Model | Batch input | Batch output |
|---|---|---|
| Claude Opus 4.6 | $2.50 / MTok | $12.50 / MTok |
| Claude Opus 4.5 | $2.50 / MTok | $12.50 / MTok |
| Claude Opus 4.1 | $7.50 / MTok | $37.50 / MTok |
| Claude Opus 4 | $7.50 / MTok | $37.50 / MTok |
| Claude Sonnet 4.6 | $1.50 / MTok | $7.50 / MTok |
| Claude Sonnet 4.5 | $1.50 / MTok | $7.50 / MTok |
| Claude Sonnet 4 | $1.50 / MTok | $7.50 / MTok |
| Claude Haiku 4.5 | $0.50 / MTok | $2.50 / MTok |
| Claude Haiku 3.5 | $0.40 / MTok | $2 / MTok |
| Claude Haiku 3 | $0.125 / MTok | $0.625 / MTok |

### Long context pricing

Claude Opus 4.6 and Sonnet 4.6 include the full 1M token context window at standard pricing. For Claude Sonnet 4.5 and Sonnet 4, requests exceeding 200k input tokens are charged at premium long context rates:

| Model | ≤200k input | ≤200k output | >200k input | >200k output |
|---|---|---|---|---|
| Claude Sonnet 4.5 / 4 | $3 / MTok | $15 / MTok | $6 / MTok | $22.50 / MTok |

### Tool use pricing

Tool use requests are priced based on:
1. The total number of input tokens sent to the model (including in the `tools` parameter)
2. The number of output tokens generated
3. For server-side tools, additional usage-based pricing (e.g., web search charges per search performed)

Tool use system prompt token counts by model:

| Model | Tool choice | Tool use system prompt token count |
|---|---|---|
| Claude Opus 4.6 | `auto`, `none` / `any`, `tool` | 346 tokens / 313 tokens |
| Claude Sonnet 4.6 | `auto`, `none` / `any`, `tool` | 346 tokens / 313 tokens |
| Claude Haiku 4.5 | `auto`, `none` / `any`, `tool` | 346 tokens / 313 tokens |
| Claude Haiku 3.5 | `auto`, `none` / `any`, `tool` | 264 tokens / 340 tokens |
| Claude Haiku 3 | `auto`, `none` / `any`, `tool` | 264 tokens / 340 tokens |

### Specific tool pricing

#### Code execution tool

**Code execution is free when used with web search or web fetch.** When `web_search_20260209` or `web_fetch_20260209` is included, there are no additional charges for code execution beyond standard token costs.

When used without these tools:
- Execution time has a minimum of 5 minutes
- Each organization receives **1,550 free hours** of usage per month
- Additional usage beyond 1,550 hours is billed at **$0.05 per hour, per container**

#### Web search tool

Web search is available on the Claude API for **$10 per 1,000 searches**, plus standard token costs.

#### Web fetch tool

Web fetch has **no additional charges** beyond standard token costs.

#### Computer use tool

| Model | Input tokens per tool definition |
|---|---|
| Claude 4.x models | 735 tokens |
| Claude Sonnet 3.7 (deprecated) | 735 tokens |

Computer use beta adds 466-499 tokens to the system prompt.

## Agent use case pricing examples

### Customer support agent example

Example calculation for processing 10,000 support tickets:
- Average ~3,700 tokens per conversation
- Using Claude Opus 4.6 at $5/MTok input, $25/MTok output
- Total cost: ~$37.00 per 10,000 tickets

### Cost optimization strategies

1. **Use appropriate models**: Choose Haiku for simple tasks, Sonnet for complex reasoning
2. **Implement prompt caching**: Reduce costs for repeated context
3. **Batch operations**: Use the Batch API for non-time-sensitive tasks
4. **Monitor usage patterns**: Track token consumption to identify optimization opportunities

## Additional pricing considerations

### Rate limits

Rate limits vary by usage tier: Tier 1 (entry-level), Tier 2 (growing), Tier 3 (established), Tier 4 (maximum standard), Enterprise (custom). For detailed information, see the [rate limits documentation](/docs/en/api/rate-limits).

### Enterprise pricing

For enterprise customers with specific needs:
- Custom rate limits
- Volume discounts
- Dedicated support
- Custom terms

Contact [sales@anthropic.com](mailto:sales@anthropic.com) or through the Claude Console to discuss enterprise pricing options.

## Billing and payment

- Billing is calculated monthly based on actual usage
- Payments are processed in USD
- Credit card and invoicing options available
- Usage tracking available in the Claude Console

## Frequently asked questions

**How is token usage calculated?**
Tokens are pieces of text that models process. As a rough estimate, 1 token is approximately 4 characters or 0.75 words in English.

**Are there free tiers or trials?**
New users receive a small amount of free credits to test the API.

**How do discounts stack?**
Batch API and prompt caching discounts can be combined.

For additional questions about pricing, contact [support@anthropic.com](mailto:support@anthropic.com).
