---
source: https://platform.claude.com/docs/en/api/messages
scraped: 2026-03-23
section: api
---

# Messages

## Create

**post** `/v1/messages`

Send a structured list of input messages with text and/or image content, and the model will generate the next message in the conversation.

The Messages API can be used for either single queries or stateless multi-turn conversations.

Learn more about the Messages API in our [user guide](https://docs.claude.com/en/docs/initial-setup)

### Body Parameters

#### `max_tokens: number` (Required)

The maximum number of tokens to generate before stopping.

Note that our models may stop _before_ reaching this maximum. This parameter only specifies the absolute maximum number of tokens to generate.

Different models have different maximum values for this parameter. See [models](https://docs.claude.com/en/docs/models-overview) for details.

#### `messages: array of MessageParam` (Required)

Input messages.

Our models are trained to operate on alternating `user` and `assistant` conversational turns. When creating a new `Message`, you specify the prior conversational turns with the `messages` parameter, and the model then generates the next `Message` in the conversation. Consecutive `user` or `assistant` turns in your request will be combined into a single turn.

Each input message must be an object with a `role` and `content`. You can specify a single `user`-role message, or you can include multiple `user` and `assistant` messages.

If the final message uses the `assistant` role, the response content will continue immediately from the content in that message. This can be used to constrain part of the model's response.

**Example with a single `user` message:**

```json
[{"role": "user", "content": "Hello, Claude"}]
```

**Example with multiple conversational turns:**

```json
[
  {"role": "user", "content": "Hello there."},
  {"role": "assistant", "content": "Hi, I'm Claude. How can I help you?"},
  {"role": "user", "content": "Can you explain LLMs in plain English?"}
]
```

**Example with a partially-filled response from Claude:**

```json
[
  {"role": "user", "content": "What's the Greek name for Sun? (A) Sol (B) Helios (C) Sun"},
  {"role": "assistant", "content": "The best answer is ("}
]
```

Each input message `content` may be either a single `string` or an array of content blocks, where each block has a specific `type`. Using a `string` for `content` is shorthand for an array of one content block of type `"text"`. The following input messages are equivalent:

```json
{"role": "user", "content": "Hello, Claude"}
```

```json
{"role": "user", "content": [{"type": "text", "text": "Hello, Claude"}]}
```

Note that if you want to include a system prompt, you can use the top-level `system` parameter — there is no `"system"` role for input messages in the Messages API.

There is a limit of 100,000 messages in a single request.

#### `model: Model` (Required)

The model that will complete your prompt.

See [models](https://docs.anthropic.com/en/docs/models-overview) for additional details and options.

**Available Models:**
- `claude-opus-4-6` - Most intelligent model for building agents and coding
- `claude-sonnet-4-6` - Best combination of speed and intelligence
- `claude-haiku-4-5` - Fastest model with near-frontier intelligence
- `claude-opus-4-5` - Premium model combining maximum intelligence with practical performance
- `claude-sonnet-4-5` - High-performance model for agents and coding
- `claude-opus-4-1` - Exceptional model for specialized complex tasks
- `claude-sonnet-4-0` - High-performance model with extended thinking
- `claude-3-haiku-20240307` - Fast and cost-effective model

#### `cache_control: optional CacheControlEphemeral`

Top-level cache control automatically applies a cache_control marker to the last cacheable block in the request.

- `type: "ephemeral"` (required)
- `ttl: optional "5m" or "1h"` - Defaults to `5m`

#### `container: optional string`

Container identifier for reuse across requests.

#### `inference_geo: optional string`

Specifies the geographic region for inference processing. If not specified, the workspace's `default_inference_geo` is used.

#### `metadata: optional Metadata`

An object describing metadata about the request.

- `user_id: optional string` - An external identifier for the user who is associated with the request. This should be a uuid, hash value, or other opaque identifier. Do not include any identifying information such as name, email address, or phone number.

#### `output_config: optional OutputConfig`

Configuration options for the model's output, such as the output format.

- `effort: optional "low" | "medium" | "high" | "max"`
- `format: optional JSONOutputFormat` - A schema to specify Claude's output format in responses.

#### `service_tier: optional "auto" | "standard_only"`

Determines whether to use priority capacity (if available) or standard capacity for this request.

#### `stop_sequences: optional array of string`

Custom text sequences that will cause the model to stop generating.

#### `stream: optional boolean`

Whether to incrementally stream the response using server-sent events.

#### `system: optional string | array of TextBlockParam`

System prompt.

A system prompt is a way of providing context and instructions to Claude, such as specifying a particular goal or role.

#### `temperature: optional number`

Amount of randomness injected into the response.

Defaults to `1.0`. Ranges from `0.0` to `1.0`. Use `temperature` closer to `0.0` for analytical / multiple choice, and closer to `1.0` for creative and generative tasks.

Note that even with `temperature` of `0.0`, the results will not be fully deterministic.

#### `thinking: optional ThinkingConfigParam`

Configuration for enabling Claude's extended thinking.

When enabled, responses include `thinking` content blocks showing Claude's thinking process before the final answer. Requires a minimum budget of 1,024 tokens and counts towards your `max_tokens` limit.

#### `tool_choice: optional ToolChoice`

How the model should use the provided tools. The model can use a specific tool, any available tool, decide by itself, or not use tools at all.

#### `tools: optional array of ToolUnion`

Definitions of tools that the model may use.

If you include `tools` in your API request, the model may return `tool_use` content blocks that represent the model's use of those tools.

#### `top_k: optional number`

Only sample from the top K options for each subsequent token.

#### `top_p: optional number`

Use nucleus sampling.

### Returns

#### `Message`

```typescript
{
  id: string,                    // Unique object identifier
  container: Container,          // Information about the container used
  content: ContentBlock[],       // Content generated by the model
  model: string,                 // The model used
  role: "assistant",             // Role of the message
  stop_reason: string,           // Reason the model stopped
  stop_sequence: string | null,  // The stop sequence that was matched
  usage: {
    input_tokens: number,        // Number of input tokens used
    output_tokens: number        // Number of output tokens generated
  }
}
```
