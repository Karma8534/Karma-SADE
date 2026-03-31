---
source: https://platform.claude.com/docs/en/agent-sdk/streaming-output
scraped: 2026-03-23
section: agent-sdk
---

# Stream responses in real-time

Get real-time responses from the Agent SDK as text and tool calls stream in

---

By default, the Agent SDK yields complete `AssistantMessage` objects after Claude finishes generating each response. To receive incremental updates as text and tool calls are generated, enable partial message streaming by setting `include_partial_messages` (Python) or `includePartialMessages` (TypeScript) to `true` in your options.

## Enable streaming output

Set `include_partial_messages` (Python) or `includePartialMessages` (TypeScript) to `true`. This causes the SDK to yield `StreamEvent` messages containing raw API events as they arrive, in addition to the usual `AssistantMessage` and `ResultMessage`.

```python Python
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import StreamEvent
import asyncio


async def stream_response():
    options = ClaudeAgentOptions(
        include_partial_messages=True,
        allowed_tools=["Bash", "Read"],
    )

    async for message in query(prompt="List the files in my project", options=options):
        if isinstance(message, StreamEvent):
            event = message.event
            if event.get("type") == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    print(delta.get("text", ""), end="", flush=True)


asyncio.run(stream_response())
```

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "List the files in my project",
  options: { includePartialMessages: true, allowedTools: ["Bash", "Read"] }
})) {
  if (message.type === "stream_event") {
    const event = message.event;
    if (event.type === "content_block_delta") {
      if (event.delta.type === "text_delta") {
        process.stdout.write(event.delta.text);
      }
    }
  }
}
```

## StreamEvent reference

When partial messages are enabled, you receive raw Claude API streaming events wrapped in an object:

- **Python**: `StreamEvent` (import from `claude_agent_sdk.types`)
- **TypeScript**: `SDKPartialAssistantMessage` with `type: 'stream_event'`

The `event` field contains the raw streaming event from the Claude API. Common event types:

| Event Type | Description |
|:-----------|:------------|
| `message_start` | Start of a new message |
| `content_block_start` | Start of a new content block (text or tool use) |
| `content_block_delta` | Incremental update to content |
| `content_block_stop` | End of a content block |
| `message_delta` | Message-level updates (stop reason, usage) |
| `message_stop` | End of the message |

## Message flow

With partial messages enabled, you receive messages in this order:

```text
StreamEvent (message_start)
StreamEvent (content_block_start) - text block
StreamEvent (content_block_delta) - text chunks...
StreamEvent (content_block_stop)
StreamEvent (content_block_start) - tool_use block
StreamEvent (content_block_delta) - tool input chunks...
StreamEvent (content_block_stop)
StreamEvent (message_delta)
StreamEvent (message_stop)
AssistantMessage - complete message with all content
... tool executes ...
ResultMessage - final result
```

## Stream text responses

```python Python
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import StreamEvent
import asyncio


async def stream_text():
    options = ClaudeAgentOptions(include_partial_messages=True)

    async for message in query(prompt="Explain how databases work", options=options):
        if isinstance(message, StreamEvent):
            event = message.event
            if event.get("type") == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    print(delta.get("text", ""), end="", flush=True)

    print()


asyncio.run(stream_text())
```

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Explain how databases work",
  options: { includePartialMessages: true }
})) {
  if (message.type === "stream_event") {
    const event = message.event;
    if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
      process.stdout.write(event.delta.text);
    }
  }
}

console.log();
```

## Stream tool calls

Track when tools start, receive their input as it streams, and see when they complete.

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

let currentTool: string | null = null;
let toolInput = "";

for await (const message of query({
  prompt: "Read the README.md file",
  options: { includePartialMessages: true, allowedTools: ["Read", "Bash"] }
})) {
  if (message.type === "stream_event") {
    const event = message.event;

    if (event.type === "content_block_start") {
      if (event.content_block.type === "tool_use") {
        currentTool = event.content_block.name;
        toolInput = "";
        console.log(`Starting tool: ${currentTool}`);
      }
    } else if (event.type === "content_block_delta") {
      if (event.delta.type === "input_json_delta") {
        const chunk = event.delta.partial_json;
        toolInput += chunk;
      }
    } else if (event.type === "content_block_stop") {
      if (currentTool) {
        console.log(`Tool ${currentTool} called with: ${toolInput}`);
        currentTool = null;
      }
    }
  }
}
```

## Known limitations

- **Extended thinking**: when you explicitly set `max_thinking_tokens` / `maxThinkingTokens`, `StreamEvent` messages are not emitted.
- **Structured output**: the JSON result appears only in the final `ResultMessage.structured_output`, not as streaming deltas.
