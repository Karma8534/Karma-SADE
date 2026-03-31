---
source: https://platform.claude.com/docs/en/api/models/retrieve
scraped: 2026-03-23
section: api
---

# Models - Retrieve

**get** `/v1/models/{model_id}`

Get a specific model.

The Models API response can be used to determine information about a specific model or resolve a model alias to a model ID.

## Path Parameters

- `model_id: string` — Model identifier or alias.

## Header Parameters

- `anthropic-beta: optional array` — Optional header to specify the beta version(s) you want to use.

## Returns

Returns a `ModelInfo` object:

```typescript
{
  id: string,                    // Unique model identifier
  display_name: string,          // Human-readable name
  created_at: string,            // RFC 3339 datetime of model release
  max_input_tokens: number,      // Maximum input context window size in tokens
  max_tokens: number,            // Maximum value for the max_tokens parameter
  type: "model",                 // Always "model"
  capabilities: {
    batch: { supported: boolean },
    citations: { supported: boolean },
    code_execution: { supported: boolean },
    image_input: { supported: boolean },
    pdf_input: { supported: boolean },
    structured_outputs: { supported: boolean },
    thinking: {
      supported: boolean,
      types: {
        adaptive: { supported: boolean },
        enabled: { supported: boolean }
      }
    },
    effort: {
      supported: boolean,
      low: { supported: boolean },
      medium: { supported: boolean },
      high: { supported: boolean },
      max: { supported: boolean }
    },
    context_management: {
      supported: boolean,
      clear_thinking_20251015: { supported: boolean },
      clear_tool_uses_20250919: { supported: boolean },
      compact_20260112: { supported: boolean }
    }
  }
}
```

## Example

```bash
curl https://api.anthropic.com/v1/models/$MODEL_ID \
    -H 'anthropic-version: 2023-06-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```
