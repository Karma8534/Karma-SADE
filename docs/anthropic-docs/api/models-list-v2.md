---
source: https://platform.claude.com/docs/en/api/models-list
scraped: 2026-03-23
section: api
---

# List Models

**get** `/v1/models`

List available models.

The Models API response can be used to determine which models are available for use in the API. More recently released models are listed first.

## Query Parameters

- `after_id: optional string`

  ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately after this object.

- `before_id: optional string`

  ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately before this object.

- `limit: optional number`

  Number of items to return per page. Defaults to `20`. Ranges from `1` to `1000`.

## Header Parameters

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

## Returns

- `data: array of ModelInfo`

  Each `ModelInfo` object contains:

  - `id: string` — Unique model identifier.

  - `capabilities: ModelCapabilities` — Model capability information.

    - `batch: CapabilitySupport` — Whether the model supports the Batch API. `{ supported: boolean }`
    - `citations: CapabilitySupport` — Whether the model supports citation generation. `{ supported: boolean }`
    - `code_execution: CapabilitySupport` — Whether the model supports code execution tools. `{ supported: boolean }`
    - `context_management: ContextManagementCapability` — Context management support and available strategies.
      - `clear_thinking_20251015: CapabilitySupport`
      - `clear_tool_uses_20250919: CapabilitySupport`
      - `compact_20260112: CapabilitySupport`
      - `supported: boolean`
    - `effort: EffortCapability` — Effort (reasoning_effort) support and available levels.
      - `high: CapabilitySupport`
      - `low: CapabilitySupport`
      - `max: CapabilitySupport`
      - `medium: CapabilitySupport`
      - `supported: boolean`
    - `image_input: CapabilitySupport` — Whether the model accepts image content blocks. `{ supported: boolean }`
    - `pdf_input: CapabilitySupport` — Whether the model accepts PDF content blocks. `{ supported: boolean }`
    - `structured_outputs: CapabilitySupport` — Whether the model supports structured output / JSON mode / strict tool schemas. `{ supported: boolean }`
    - `thinking: ThinkingCapability` — Thinking capability and supported type configurations.
      - `supported: boolean`
      - `types: ThinkingTypes`
        - `adaptive: CapabilitySupport` — Whether the model supports thinking with type 'adaptive' (auto).
        - `enabled: CapabilitySupport` — Whether the model supports thinking with type 'enabled'.

  - `created_at: string` — RFC 3339 datetime string representing the time at which the model was released.

  - `display_name: string` — A human-readable name for the model.

  - `max_input_tokens: number` — Maximum input context window size in tokens for this model.

  - `max_tokens: number` — Maximum value for the `max_tokens` parameter when using this model.

  - `type: "model"` — Object type. For Models, this is always `"model"`.

- `first_id: string` — First ID in the `data` list. Can be used as the `before_id` for the previous page.

- `has_more: boolean` — Indicates if there are more results in the requested page direction.

- `last_id: string` — Last ID in the `data` list. Can be used as the `after_id` for the next page.

## Example

```http
curl https://api.anthropic.com/v1/models \
    -H 'anthropic-version: 2023-06-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```
