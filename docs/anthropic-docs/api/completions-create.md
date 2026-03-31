---
source: https://platform.claude.com/docs/en/api/completions/create
scraped: 2026-03-23
section: api
---

## Create

**post** `/v1/complete`

[Legacy] Create a Text Completion.

The Text Completions API is a legacy API. We recommend using the Messages API going forward.

Future models and features will not be compatible with Text Completions.

### Header Parameters

- `"anthropic-beta": optional array of AnthropicBeta`

  Optional header to specify the beta version(s) you want to use. Values include:
  - `"message-batches-2024-09-24"`
  - `"prompt-caching-2024-07-31"`
  - `"computer-use-2024-10-22"`
  - `"computer-use-2025-01-24"`
  - `"pdfs-2024-09-25"`
  - `"token-counting-2024-11-01"`
  - `"token-efficient-tools-2025-02-19"`
  - `"output-128k-2025-02-19"`
  - `"files-api-2025-04-14"`
  - `"mcp-client-2025-04-04"`
  - `"mcp-client-2025-11-20"`
  - `"dev-full-thinking-2025-05-14"`
  - `"interleaved-thinking-2025-05-14"`
  - `"code-execution-2025-05-22"`
  - `"extended-cache-ttl-2025-04-11"`
  - `"context-1m-2025-08-07"`
  - `"context-management-2025-06-27"`
  - `"model-context-window-exceeded-2025-08-26"`
  - `"skills-2025-10-02"`
  - `"fast-mode-2026-02-01"`

### Body Parameters

- `max_tokens_to_sample: number`

  The maximum number of tokens to generate before stopping.

- `model: Model`

  The model that will complete your prompt. Available models include:
  - `"claude-opus-4-6"` — Most intelligent model for building agents and coding
  - `"claude-sonnet-4-6"` — Best combination of speed and intelligence
  - `"claude-haiku-4-5"` — Fastest model with near-frontier intelligence
  - `"claude-haiku-4-5-20251001"` — Fastest model with near-frontier intelligence
  - `"claude-opus-4-5"` — Premium model combining maximum intelligence with practical performance
  - `"claude-sonnet-4-5"` — High-performance model for agents and coding
  - `"claude-opus-4-1"` — Exceptional model for specialized complex tasks
  - `"claude-opus-4-0"` — Powerful model for complex tasks
  - `"claude-sonnet-4-0"` — High-performance model with extended thinking
  - `"claude-3-haiku-20240307"` — Fast and cost-effective model

- `prompt: string`

  The prompt that you want Claude to complete. Format using alternating `\n\nHuman:` and `\n\nAssistant:` conversational turns.

- `metadata: optional Metadata`

  - `user_id: optional string` — An external identifier for the user.

- `stop_sequences: optional array of string`

  Sequences that will cause the model to stop generating.

- `stream: optional boolean`

  Whether to incrementally stream the response using server-sent events.

- `temperature: optional number`

  Amount of randomness. Defaults to `1.0`. Ranges from `0.0` to `1.0`.

- `top_k: optional number`

  Only sample from the top K options for each subsequent token.

- `top_p: optional number`

  Use nucleus sampling.

### Returns

- `Completion = object { id, completion, model, stop_reason, type }`

  - `id: string` — Unique object identifier.
  - `completion: string` — The resulting completion up to and excluding the stop sequences.
  - `model: Model` — The model that completed the prompt.
  - `stop_reason: string` — Either `"stop_sequence"` or `"max_tokens"`.
  - `type: "completion"` — Always `"completion"` for Text Completions.

### Example

```bash
curl https://api.anthropic.com/v1/complete \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    --max-time 600 \
    -d '{
          "max_tokens_to_sample": 256,
          "model": "claude-opus-4-6",
          "prompt": "\n\nHuman: Hello, world!\n\nAssistant:"
        }'
```
