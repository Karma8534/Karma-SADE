---
source: https://platform.claude.com/docs/en/api/models
scraped: 2026-03-23
section: api
---

# Models

## List

**get** `/v1/models`

List available models.

The Models API response can be used to determine which models are available for use in the API. More recently released models are listed first.

### Query Parameters

- `after_id: optional string` — ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately after this object.
- `before_id: optional string` — ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately before this object.
- `limit: optional number` — Number of items to return per page. Defaults to `20`. Ranges from `1` to `1000`.

### Returns

Paginated list of `ModelInfo` objects:

```json
{
  "data": [ ...ModelInfo objects... ],
  "first_id": "string",
  "last_id": "string",
  "has_more": false
}
```

### Example

```bash
curl https://api.anthropic.com/v1/models \
    -H 'anthropic-version: 2023-06-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Retrieve

**get** `/v1/models/{model_id}`

Get a specific model.

The Models API response can be used to determine information about a specific model or resolve a model alias to a model ID.

### Path Parameters

- `model_id: string` — Model identifier or alias.

### Example

```bash
curl https://api.anthropic.com/v1/models/$MODEL_ID \
    -H 'anthropic-version: 2023-06-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## ModelInfo Object

```typescript
{
  id: string,                    // Unique model identifier
  display_name: string,          // Human-readable name
  created_at: string,            // RFC 3339 datetime of model release
  max_input_tokens: number,      // Maximum input context window size
  max_tokens: number,            // Maximum value for max_tokens parameter
  type: "model",                 // Always "model"
  capabilities: ModelCapabilities
}
```

## ModelCapabilities Object

```typescript
{
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
```

## Available Beta Headers

Optional `anthropic-beta` header values for models endpoint:

- `message-batches-2024-09-24`
- `prompt-caching-2024-07-31`
- `computer-use-2024-10-22`
- `computer-use-2025-01-24`
- `pdfs-2024-09-25`
- `token-counting-2024-11-01`
- `token-efficient-tools-2025-02-19`
- `output-128k-2025-02-19`
- `files-api-2025-04-14`
- `mcp-client-2025-04-04`
- `mcp-client-2025-11-20`
- `dev-full-thinking-2025-05-14`
- `interleaved-thinking-2025-05-14`
- `code-execution-2025-05-22`
- `extended-cache-ttl-2025-04-11`
- `context-1m-2025-08-07`
- `context-management-2025-06-27`
- `model-context-window-exceeded-2025-08-26`
- `skills-2025-10-02`
- `fast-mode-2026-02-01`
