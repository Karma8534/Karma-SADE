---
source: https://platform.claude.com/docs/en/api/models/list
scraped: 2026-03-23
section: api
---

# Models - List

**get** `/v1/models`

List available models.

The Models API response can be used to determine which models are available for use in the API. More recently released models are listed first.

## Query Parameters

- `after_id: optional string` — ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately after this object.
- `before_id: optional string` — ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately before this object.
- `limit: optional number` — Number of items to return per page. Defaults to `20`. Ranges from `1` to `1000`.

## Header Parameters

- `anthropic-beta: optional array` — Optional header to specify the beta version(s) you want to use.

Available beta values include: `message-batches-2024-09-24`, `prompt-caching-2024-07-31`, `computer-use-2024-10-22`, `files-api-2025-04-14`, `code-execution-2025-05-22`, `context-1m-2025-08-07`, `skills-2025-10-02`, `fast-mode-2026-02-01`, and others.

## Returns

```typescript
{
  data: ModelInfo[],   // Array of model objects
  first_id: string,   // First ID in the data list (use as before_id for previous page)
  last_id: string,    // Last ID in the data list (use as after_id for next page)
  has_more: boolean   // Indicates if there are more results
}
```

### ModelInfo Object

Each model in `data` has:

```typescript
{
  id: string,                    // Unique model identifier
  display_name: string,          // Human-readable name
  created_at: string,            // RFC 3339 datetime of model release
  max_input_tokens: number,      // Maximum input context window size in tokens
  max_tokens: number,            // Maximum value for the max_tokens parameter
  type: "model",                 // Always "model"
  capabilities: ModelCapabilities
}
```

### ModelCapabilities

```typescript
{
  batch: { supported: boolean },             // Supports Batch API
  citations: { supported: boolean },         // Supports citation generation
  code_execution: { supported: boolean },    // Supports code execution tools
  image_input: { supported: boolean },       // Accepts image content blocks
  pdf_input: { supported: boolean },         // Accepts PDF content blocks
  structured_outputs: { supported: boolean },// Supports structured output/JSON mode
  thinking: {
    supported: boolean,
    types: {
      adaptive: { supported: boolean },  // Supports adaptive thinking (auto)
      enabled: { supported: boolean }    // Supports enabled thinking
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
```

## Example

```bash
curl https://api.anthropic.com/v1/models \
    -H 'anthropic-version: 2023-06-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```
