---
source: https://platform.claude.com/docs/en/build-with-claude/streaming
scraped: 2026-03-23
section: build-with-claude
---

# Streaming Messages

---

When creating a Message, you can set `"stream": true` to incrementally stream the response using server-sent events (SSE).

## Streaming with SDKs

The Python and TypeScript SDKs offer multiple ways of streaming. The PHP SDK provides streaming via `createStream()`. The Python SDK allows both sync and async streams.

```python Python
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    model="claude-opus-4-6",
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

```typescript TypeScript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

await client.messages
  .stream({
    messages: [{ role: "user", content: "Hello" }],
    model: "claude-opus-4-6",
    max_tokens: 1024
  })
  .on("text", (text) => {
    console.log(text);
  });
```

## Get the final message without handling events

If you don't need to process text as it arrives, the SDKs provide a way to use streaming under the hood while returning the complete `Message` object, identical to what `.create()` returns. This is especially useful for requests with large `max_tokens` values, where the SDKs require streaming to avoid HTTP timeouts.

```python Python
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    max_tokens=128000,
    messages=[{"role": "user", "content": "Write a detailed analysis..."}],
    model="claude-opus-4-6",
) as stream:
    message = stream.get_final_message()

print(message.content[0].text)
```

## Streaming without SDKs

If you would like to stream responses without using the Anthropic SDKs, you can make a raw HTTP request and parse the events yourself.

```bash Shell
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "stream": true,
    "messages": [
        {"role": "user", "content": "Hello, Claude!"}
    ]
}'
```

The response will be a series of server-sent events (SSE).

## Event types

When streaming, the server sends the following events in order:

### message_start
Contains a `Message` object with empty `content`. The `usage` field will contain the number of input tokens.

```json
event: message_start
data: {"type": "message_start", "message": {"id": "msg_...", "type": "message", "role": "assistant", "content": [], "model": "claude-opus-4-6", "stop_reason": null, "stop_sequence": null, "usage": {"input_tokens": 25, "output_tokens": 1}}}
```

### content_block_start
Indicates the start of a new content block. The index of the block within the content array is provided.

```json
event: content_block_start
data: {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}
```

### ping
A periodic ping to keep the connection alive.

```json
event: ping
data: {"type": "ping"}
```

### content_block_delta
Contains a delta object for a content block. The delta type for text blocks is `text_delta`, and the value is a string.

```json
event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hello"}}
```

### content_block_stop
Indicates the end of a content block.

```json
event: content_block_stop
data: {"type": "content_block_stop", "index": 0}
```

### message_delta
Indicates a top-level change to the final message object. Contains the `stop_reason` and `stop_sequence` fields.

```json
event: message_delta
data: {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": null}, "usage": {"output_tokens": 15}}
```

### message_stop
Indicates the end of the message.

```json
event: message_stop
data: {"type": "message_stop"}
```

## Raw HTTP streaming request and response example

**Request:**
```bash
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "stream": true,
    "messages": [
        {"role": "user", "content": "Hello, Claude!"}
    ]
}'
```

**Response:**
```
event: message_start
data: {"type":"message_start","message":{"id":"msg_...","type":"message","role":"assistant","content":[],"model":"claude-opus-4-6","stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":10,"output_tokens":1}}}

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}

event: ping
data: {"type": "ping"}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Hello"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"!"}}

event: content_block_stop
data: {"type":"content_block_stop","index":0}

event: message_delta
data: {"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":null},"usage":{"output_tokens":3}}

event: message_stop
data: {"type":"message_stop"}
```
