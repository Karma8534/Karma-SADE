---
source: https://platform.claude.com/docs/en/api/creating-message-batches
scraped: 2026-03-23
section: api
---

# Message Batches API - Create

**Endpoint:** `POST /v1/messages/batches`

Send a batch of Message creation requests.

The Message Batches API can be used to process multiple Messages API requests at once. Once a Message Batch is created, it begins processing immediately. Batches can take up to 24 hours to complete.

## Body Parameters

### `requests` (array of objects, required)

List of requests for prompt completion. Each is an individual request to create a Message.

#### `custom_id` (string, required)

Developer-provided ID created for each request in a Message Batch. Must be unique for each request within the Message Batch.

#### `params` (object, required)

Messages API creation parameters for the individual request.

##### Core Parameters

**`max_tokens`** (number, required)

The maximum number of tokens to generate before stopping.

**`messages`** (array of MessageParam, required)

Input messages. Each must be an object with `role` (either `"user"` or `"assistant"`) and `content` (string or array of content blocks).

Examples:

Single user message:
```json
[{"role": "user", "content": "Hello, Claude"}]
```

Multiple conversational turns:
```json
[
  {"role": "user", "content": "Hello there."},
  {"role": "assistant", "content": "Hi, I'm Claude. How can I help you?"},
  {"role": "user", "content": "Can you explain LLMs in plain English?"}
]
```

**`model`** (Model, required)

The model that will complete your prompt. Available models:
- `claude-opus-4-6` — Most intelligent model for building agents and coding
- `claude-sonnet-4-6` — Best combination of speed and intelligence
- `claude-haiku-4-5` — Fastest model with near-frontier intelligence
- `claude-opus-4-5` — Premium model combining maximum intelligence with practical performance
- `claude-sonnet-4-5` — High-performance model for agents and coding
- `claude-opus-4-1` — Exceptional model for specialized complex tasks
- `claude-opus-4-0` — Powerful model for complex tasks
- `claude-sonnet-4-0` — High-performance model with extended thinking
- `claude-3-haiku-20240307` — Fast and cost-effective model

##### Optional Parameters

**`cache_control`** (optional, CacheControlEphemeral)

- `type`: `"ephemeral"`
- `ttl`: Optional duration (`"5m"` or `"1h"`, defaults to `"5m"`)

**`container`** (optional, string)

Container identifier for reuse across requests.

**`inference_geo`** (optional, string)

Specifies the geographic region for inference processing.

**`metadata`** (optional, Metadata)

- `user_id`: An external identifier for the user (uuid, hash, or opaque identifier).

**`output_config`** (optional, OutputConfig)

- `effort`: Optional effort level (`"low"`, `"medium"`, `"high"`, `"max"`)
- `format`: Optional JSONOutputFormat with schema specification

**`service_tier`** (optional, `"auto"` or `"standard_only"`)

Default: `"auto"`.

**`stop_sequences`** (optional, array of strings)

Custom text sequences that will cause the model to stop generating.

**`stream`** (optional, boolean)

Whether to incrementally stream the response using server-sent events.

**`system`** (optional, string or array of TextBlockParam)

System prompt for context and instructions.

**`temperature`** (optional, number)

Amount of randomness. Default: `1.0`. Range: `0.0` to `1.0`.

**`thinking`** (optional, ThinkingConfigParam)

Configuration for enabling Claude's extended thinking.
- `ThinkingConfigEnabled`: `type: "enabled"`, `budget_tokens` (>=1024, <max_tokens)
- `ThinkingConfigDisabled`: `type: "disabled"`
- `ThinkingConfigAdaptive`: `type: "adaptive"`

**`tool_choice`** (optional, ToolChoice)

How the model should use provided tools.
- `ToolChoiceAuto`: `type: "auto"`
- `ToolChoiceAny`: `type: "any"`
- `ToolChoiceTool`: `type: "tool"`, `name`
- `ToolChoiceNone`: `type: "none"`

**`tools`** (optional, array of ToolUnion)

Definitions of tools the model may use. Each tool includes `name`, `description`, and `input_schema`.

Example:
```json
[
  {
    "name": "get_stock_price",
    "description": "Get the current stock price for a given ticker symbol.",
    "input_schema": {
      "type": "object",
      "properties": {
        "ticker": {
          "type": "string",
          "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
        }
      },
      "required": ["ticker"]
    }
  }
]
```

## Content Block Types

- **TextBlockParam**: `text`, `type: "text"`, optional `cache_control`, optional `citations`
- **ImageBlockParam**: `source` (Base64 or URL), `type: "image"`, optional `cache_control`
- **DocumentBlockParam**: `source` (Base64 PDF, plain text, content block, or URL), `type: "document"`, optional metadata
- **ToolUseBlockParam**: `id`, `input`, `name`, `type: "tool_use"`, optional `cache_control`
- **ToolResultBlockParam**: `tool_use_id`, `type: "tool_result"`, optional `cache_control`, `content`, `is_error`
- **ThinkingBlockParam**: `signature`, `thinking`, `type: "thinking"`
- **RedactedThinkingBlockParam**: `data`, `type: "redacted_thinking"`
