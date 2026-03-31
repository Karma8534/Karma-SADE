---
source: https://platform.claude.com/docs/en/api/completions
scraped: 2026-03-23
section: api
---

# Completions

## Create

**post** `/v1/complete`

[Legacy] Create a Text Completion.

The Text Completions API is a legacy API. We recommend using the [Messages API](https://docs.claude.com/en/api/messages) going forward.

Future models and features will not be compatible with Text Completions. See our [migration guide](https://docs.claude.com/en/api/migrating-from-text-completions-to-messages) for guidance in migrating from Text Completions to Messages.

## Body Parameters

### `max_tokens_to_sample` (number, required)

The maximum number of tokens to generate before stopping.

Note that our models may stop _before_ reaching this maximum.

### `model` (Model, required)

The model that will complete your prompt. Available models:

- `claude-opus-4-6` — Most intelligent model for building agents and coding
- `claude-sonnet-4-6` — Best combination of speed and intelligence
- `claude-haiku-4-5` — Fastest model with near-frontier intelligence
- `claude-haiku-4-5-20251001`
- `claude-opus-4-5`
- `claude-opus-4-5-20251101`
- `claude-sonnet-4-5`
- `claude-sonnet-4-5-20250929`
- `claude-opus-4-1`
- `claude-opus-4-1-20250805`
- `claude-opus-4-0`
- `claude-opus-4-20250514`
- `claude-sonnet-4-0`
- `claude-sonnet-4-20250514`
- `claude-3-haiku-20240307` — Fast and cost-effective model

### `prompt` (string, required)

The prompt that you want Claude to complete.

For proper response generation you will need to format your prompt using alternating `\n\nHuman:` and `\n\nAssistant:` conversational turns. For example:

```
"\n\nHuman: {userQuestion}\n\nAssistant:"
```

### `metadata` (optional Metadata)

An object describing metadata about the request.

- `user_id: optional string` — An external identifier for the user. This should be a uuid, hash value, or other opaque identifier. Do not include any identifying information such as name, email address, or phone number.

### `stop_sequences` (optional array of string)

Sequences that will cause the model to stop generating.

Our models stop on `"\n\nHuman:"`, and may include additional built-in stop sequences in the future.

### `stream` (optional boolean)

Whether to incrementally stream the response using server-sent events.

### `temperature` (optional number)

Amount of randomness injected into the response.

Defaults to `1.0`. Ranges from `0.0` to `1.0`. Use `temperature` closer to `0.0` for analytical / multiple choice, and closer to `1.0` for creative and generative tasks.

### `top_k` (optional number)

Only sample from the top K options for each subsequent token.

Used to remove "long tail" low probability responses. Recommended for advanced use cases only.

### `top_p` (optional number)

Use nucleus sampling.

You should either alter `temperature` or `top_p`, but not both. Recommended for advanced use cases only.

## Returns

`Completion` object:

```typescript
{
  id: string,           // Unique object identifier
  completion: string,   // The resulting completion up to and excluding the stop sequences
  model: string,        // The model used
  stop_reason: string,  // "stop_sequence" or "max_tokens"
  type: "completion"    // Always "completion"
}
```

### `stop_reason` values

- `"stop_sequence"` — We reached a stop sequence, either provided via `stop_sequences` parameter or a built-in stop sequence
- `"max_tokens"` — We exceeded `max_tokens_to_sample` or the model's maximum

## Example

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
