---
source: https://platform.claude.com/docs/en/api/messages/create
scraped: 2026-03-23
section: api
---

# Messages API - Create

## Overview

**Endpoint:** `POST /v1/messages`

Send a structured list of input messages with text and/or image content, and the model will generate the next message in the conversation.

The Messages API can be used for either single queries or stateless multi-turn conversations.

## Request Body Parameters

### Core Parameters

#### `max_tokens` (number, required)
The maximum number of tokens to generate before stopping.

- The model may stop before reaching this maximum
- Different models have different maximum values
- See [models overview](https://docs.claude.com/en/docs/models-overview) for details

#### `messages` (array of MessageParam, required)
Input messages for the conversation.

**Structure:**
- Models operate on alternating `user` and `assistant` conversational turns
- Each message must have a `role` and `content`
- Consecutive messages with the same role are combined into a single turn
- Maximum of 100,000 messages per request

**Single user message example:**
```json
[{"role": "user", "content": "Hello, Claude"}]
```

**Multi-turn conversation example:**
```json
[
  {"role": "user", "content": "Hello there."},
  {"role": "assistant", "content": "Hi, I'm Claude. How can I help you?"},
  {"role": "user", "content": "Can you explain LLMs in plain English?"}
]
```

**Constraining response example:**
```json
[
  {"role": "user", "content": "What's the Greek name for Sun? (A) Sol (B) Helios (C) Sun"},
  {"role": "assistant", "content": "The best answer is ("}
]
```

**Content Format:**
Content can be a string or array of content blocks:
```json
{"role": "user", "content": "Hello, Claude"}
```
is equivalent to:
```json
{"role": "user", "content": [{"type": "text", "text": "Hello, Claude"}]}
```

**Content Block Types:**

- **TextBlockParam**: Text content with optional caching and citations
- **ImageBlockParam**: Images (JPEG, PNG, GIF, WebP) via base64 or URL
- **DocumentBlockParam**: PDFs or plain text documents
- **SearchResultBlockParam**: Search results with citations
- **ThinkingBlockParam**: Extended thinking content
- **ToolUseBlockParam**: Tool invocations
- **ToolResultBlockParam**: Results from tool execution
- **ServerToolUseBlockParam**: Server-side tool invocations
- **WebSearchToolResultBlockParam**: Web search results
- **WebFetchToolResultBlockParam**: Fetched web content
- **CodeExecutionToolResultBlockParam**: Code execution results
- **BashCodeExecutionToolResultBlockParam**: Bash execution results
- **TextEditorCodeExecutionToolResultBlockParam**: Text editor operations
- **ToolSearchToolResultBlockParam**: Tool search results
- **ContainerUploadBlockParam**: Files for container upload

#### `model` (Model, required)
The model that will complete the prompt.

**Available Models:**
- `claude-opus-4-6` - Most intelligent model for agents and coding
- `claude-sonnet-4-6` - Best balance of speed and intelligence
- `claude-haiku-4-5` - Fastest model with near-frontier intelligence
- `claude-opus-4-5` - Premium model with maximum intelligence
- `claude-sonnet-4-5` - High-performance model for agents
- `claude-opus-4-1` - Exceptional model for complex tasks
- `claude-sonnet-4-0` - High-performance with extended thinking
- `claude-3-haiku-20240307` - Fast and cost-effective

### Optional Parameters

#### `system` (string or array of TextBlockParam)
System prompt providing context and instructions.

#### `temperature` (number)
Amount of randomness injected into the response.

- Default: `1.0`
- Range: `0.0` to `1.0`
- Closer to `0.0`: analytical/multiple choice tasks
- Closer to `1.0`: creative/generative tasks

#### `top_p` (number)
Nucleus sampling parameter. Use either `temperature` OR `top_p`, not both.

#### `top_k` (number)
Only sample from the top K options for each token.

#### `stop_sequences` (array of string)
Custom text sequences that stop generation.

#### `stream` (boolean)
Enable incremental streaming via server-sent events.

#### `thinking` (ThinkingConfigParam)
Enable extended thinking capability.

**Options:**
- `ThinkingConfigEnabled`: Requires budget ≥1,024 tokens
- `ThinkingConfigDisabled`: Disable thinking
- `ThinkingConfigAdaptive`: Model decides when to use thinking

#### `tools` (array of ToolUnion)
Definitions of tools the model can use.

**Tool Types:**
- **Custom Tools** (`Tool`): Define custom tools with JSON schema
- **Code Execution** (`CodeExecutionTool20250825`, `CodeExecutionTool20260120`)
- **Bash** (`ToolBash20250124`)
- **Text Editor** (`ToolTextEditor20250728`)
- **Web Search** (`WebSearchTool20260209`)
- **Web Fetch** (`WebFetchTool20260309`)
- **Tool Search** (`ToolSearchToolBm25_20251119`, `ToolSearchToolRegex20251119`)
- **Memory** (`MemoryTool20250818`)

#### `tool_choice` (ToolChoice)
How the model should use provided tools.

**Options:**
- `ToolChoiceAuto`: Model decides automatically
- `ToolChoiceAny`: Model must use any available tool
- `ToolChoiceTool`: Model uses specified tool
- `ToolChoiceNone`: Model cannot use tools
- `disable_parallel_tool_use`: Set to `true` for single tool use

#### `metadata` (Metadata)
Request metadata including user identification.

- `user_id`: External identifier (uuid, hash, or opaque ID)
- Do not include PII like names, emails, or phone numbers

#### `cache_control` (CacheControlEphemeral)
Top-level cache control for prompt caching.

**TTL Options:**
- `"5m"`: 5 minutes (default)
- `"1h"`: 1 hour

#### `output_config` (OutputConfig)
Configuration for model output format.

**Options:**
- `format`: JSON schema for structured outputs
- `effort`: Effort level (`"low"`, `"medium"`, `"high"`, `"max"`)

#### `service_tier` (string)
Service tier for the request.

- `"auto"`: Use priority capacity if available
- `"standard_only"`: Use standard capacity only

#### `container` (string)
Container identifier for code execution reuse across requests.

#### `inference_geo` (string)
Geographic region for inference processing.

If not specified, uses workspace's `default_inference_geo`.

## Response

Returns a `Message` object containing:

- `id`: Unique message identifier
- `container`: Container information (if used)
- `content`: Array of `ContentBlock` objects generated by the model
- `type`: Always `"message"`
- `role`: Always `"assistant"`
- `model`: The model that handled the request
- `stop_reason`: Why the model stopped generating (`"end_turn"`, `"max_tokens"`, `"stop_sequence"`, `"tool_use"`)
- `stop_sequence`: The stop sequence matched (if applicable)
- `usage`: Token usage statistics (`input_tokens`, `output_tokens`)
