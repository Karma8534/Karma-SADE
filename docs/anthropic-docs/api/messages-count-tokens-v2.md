---
source: https://platform.claude.com/docs/en/api/messages-count-tokens
scraped: 2026-03-23
section: api
---

# Count Tokens

**post** `/v1/messages/count_tokens`

Count the number of tokens in a Message.

The Token Count API can be used to count the number of tokens in a Message, including tools, images, and documents, without creating it.

Learn more about token counting in the [user guide](https://docs.anthropic.com/en/docs/build-with-claude/token-counting).

## Body Parameters

- `messages: array of MessageParam`

  Input messages.

  Our models are trained to operate on alternating `user` and `assistant` conversational turns. When creating a new `Message`, you specify the prior conversational turns with the `messages` parameter, and the model then generates the next `Message` in the conversation. Consecutive `user` or `assistant` turns in your request will be combined into a single turn.

  Each input message must be an object with a `role` and `content`. You can specify a single `user`-role message, or you can include multiple `user` and `assistant` messages.

  If the final message uses the `assistant` role, the response content will continue immediately from the content in that message. This can be used to constrain part of the model's response.

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

  Example with a partially-filled response from Claude:
  ```json
  [
    {"role": "user", "content": "What's the Greek name for Sun? (A) Sol (B) Helios (C) Sun"},
    {"role": "assistant", "content": "The best answer is ("}
  ]
  ```

  Each input message `content` may be either a single `string` or an array of content blocks. Using a `string` for `content` is shorthand for an array of one content block of type `"text"`.

  Note that if you want to include a system prompt, you can use the top-level `system` parameter — there is no `"system"` role for input messages in the Messages API.

  There is a limit of 100,000 messages in a single request.

- `model: Model`

  The model that will complete your prompt. See [models](https://docs.anthropic.com/en/docs/models-overview) for additional details and options.

- `system: optional string or array of TextBlockParam`

  System prompt. See our guide to system prompts for context.

- `tool_choice: optional ToolChoice`

  How the model should use the provided tools.

- `tools: optional array of ToolUnion`

  Definitions of tools that the model may use.

- `thinking: optional ThinkingConfigParam`

  Configuration for enabling Claude's extended thinking.

## Content Block Types

### TextBlockParam
- `text: string`
- `type: "text"`
- `cache_control: optional CacheControlEphemeral`
  - `type: "ephemeral"`
  - `ttl: optional "5m" or "1h"` (defaults to `"5m"`)
- `citations: optional array of TextCitationParam`
  - `CitationCharLocationParam` — `cited_text`, `document_index`, `document_title`, `end_char_index`, `start_char_index`, `type: "char_location"`
  - `CitationPageLocationParam` — `cited_text`, `document_index`, `document_title`, `end_page_number`, `start_page_number`, `type: "page_location"`
  - `CitationContentBlockLocationParam` — `cited_text`, `document_index`, `document_title`, `end_block_index`, `start_block_index`, `type: "content_block_location"`
  - `CitationWebSearchResultLocationParam` — `cited_text`, `encrypted_index`, `title`, `type: "web_search_result_location"`, `url`
  - `CitationSearchResultLocationParam` — `cited_text`, `end_block_index`, `search_result_index`, `source`, `start_block_index`, `title`, `type: "search_result_location"`

### ImageBlockParam
- `source: Base64ImageSource or URLImageSource`
  - `Base64ImageSource`: `data`, `media_type` (image/jpeg, image/png, image/gif, image/webp), `type: "base64"`
  - `URLImageSource`: `type: "url"`, `url`
- `type: "image"`
- `cache_control: optional CacheControlEphemeral`

### DocumentBlockParam
- `source: Base64PDFSource or PlainTextSource or URLPDFSource or ContentBlockSource`
  - `Base64PDFSource`: `data`, `media_type: "application/pdf"`, `type: "base64"`
  - `PlainTextSource`: `data`, `media_type: "text/plain"`, `type: "text"`
  - `URLPDFSource`: `type: "url"`, `url`
  - `ContentBlockSource`: `content` (string or array), `type: "content"`
- `type: "document"`
- `cache_control: optional CacheControlEphemeral`
- `citations: optional CitationsConfig` — `enabled: boolean`
- `context: optional string`
- `title: optional string`

### ToolUseBlockParam
- `id: string`
- `input: object`
- `name: string`
- `type: "tool_use"`
- `cache_control: optional CacheControlEphemeral`
- `caller: optional ToolCaller`

### ToolResultBlockParam
- `tool_use_id: string`
- `type: "tool_result"`
- `cache_control: optional CacheControlEphemeral`
- `content: optional string or array of TextBlockParam or ImageBlockParam`
- `is_error: optional boolean`

### ThinkingBlockParam
- `signature: string`
- `thinking: string`
- `type: "thinking"`

### RedactedThinkingBlockParam
- `data: string`
- `type: "redacted_thinking"`

## Returns

- `input_tokens: number`

  The total number of tokens across the provided list of messages, system prompt, and tools.
