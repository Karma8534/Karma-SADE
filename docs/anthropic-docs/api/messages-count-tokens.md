---
source: https://platform.claude.com/docs/en/api/messages/count_tokens
scraped: 2026-03-23
section: api
---

# Count Tokens

**post** `/v1/messages/count_tokens`

Count the number of tokens in a Message.

The Token Count API can be used to count the number of tokens in a Message, including tools, images, and documents, without creating it.

Learn more about token counting in our [user guide](https://docs.claude.com/en/docs/build-with-claude/token-counting)

## Body Parameters

### `messages` (array of MessageParam, required)

Input messages.

Our models are trained to operate on alternating `user` and `assistant` conversational turns. Each input message must be an object with a `role` and `content`.

Example with a single `user` message:

```json
[{"role": "user", "content": "Hello, Claude"}]
```

Example with multiple conversational turns:

```json
[
  {"role": "user", "content": "Hello there."},
  {"role": "assistant", "content": "Hi, I'm Claude. How can I help you?"},
  {"role": "user", "content": "Can you explain LLMs in plain English?"}
]
```

There is a limit of 100,000 messages in a single request.

Content can be a string or array of content blocks. Supported content block types include:

- **TextBlockParam**: `{ text, type: "text", cache_control?, citations? }`
- **ImageBlockParam**: Images via base64 (`Base64ImageSource`) or URL (`URLImageSource`)
  - Supported media types: `image/jpeg`, `image/png`, `image/gif`, `image/webp`
- **DocumentBlockParam**: PDFs or plain text documents
- **ThinkingBlockParam**: Extended thinking content
- **ToolUseBlockParam**: Tool invocations
- **ToolResultBlockParam**: Results from tool execution

### `model` (Model, required)

The model to use for token counting.

**Available Models:**
- `claude-opus-4-6`
- `claude-sonnet-4-6`
- `claude-haiku-4-5`
- `claude-opus-4-5`
- `claude-sonnet-4-5`
- `claude-opus-4-1`
- `claude-sonnet-4-0`
- `claude-3-haiku-20240307`

### `system` (optional string or array of TextBlockParam)

System prompt. Use the top-level `system` parameter — there is no `"system"` role for input messages.

### `thinking` (optional ThinkingConfigParam)

Configuration for extended thinking.

**Options:**
- `ThinkingConfigEnabled`: Requires budget ≥1,024 tokens
- `ThinkingConfigDisabled`: Disable thinking
- `ThinkingConfigAdaptive`: Model decides when to use thinking

### `tools` (optional array of ToolUnion)

Definitions of tools the model may use, included in the token count.

**Tool Types:**
- Custom Tools (`Tool`): Define custom tools with JSON schema
- Code Execution tools
- Bash (`ToolBash20250124`)
- Text Editor (`ToolTextEditor20250728`)
- Web Search (`WebSearchTool20260209`)
- Web Fetch (`WebFetchTool20260309`)
- Tool Search tools
- Memory (`MemoryTool20250818`)

### `tool_choice` (optional ToolChoice)

How the model should use provided tools.

**Options:**
- `ToolChoiceAuto`: Model decides automatically
- `ToolChoiceAny`: Model must use any available tool
- `ToolChoiceTool`: Model uses specified tool
- `ToolChoiceNone`: Model cannot use tools

## Response

Returns a `TokenCountResponse` object:

```json
{
  "input_tokens": 1234
}
```

- `input_tokens`: The number of input tokens that would be counted for this request

## Cache Control

`CacheControlEphemeral` can be applied to content blocks:

```json
{
  "type": "ephemeral",
  "ttl": "5m"
}
```

TTL options: `"5m"` (default, 5 minutes) or `"1h"` (1 hour)

## Example

```python
import anthropic

client = anthropic.Anthropic()

count = client.messages.count_tokens(
    model="claude-opus-4-6",
    messages=[{"role": "user", "content": "Hello, world"}]
)
print(count.input_tokens)  # 10
```

```typescript
const count = await client.messages.countTokens({
  model: "claude-opus-4-6",
  messages: [{ role: "user", content: "Hello, world" }]
});
console.log(count.input_tokens); // 10
```
