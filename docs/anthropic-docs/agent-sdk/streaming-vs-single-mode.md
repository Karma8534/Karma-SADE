---
source: https://platform.claude.com/docs/en/agent-sdk/streaming-vs-single-mode
scraped: 2026-03-23
section: agent-sdk
---

# Streaming Input

Understanding the two input modes for Claude Agent SDK and when to use each

---

## Overview

The Claude Agent SDK supports two distinct input modes for interacting with agents:

- **Streaming Input Mode** (Default & Recommended) - A persistent, interactive session
- **Single Message Input** - One-shot queries that use session state and resuming

## Streaming Input Mode (Recommended)

Streaming input mode is the **preferred** way to use the Claude Agent SDK. It provides full access to the agent's capabilities and enables rich, interactive experiences.

It allows the agent to operate as a long lived process that takes in user input, handles interruptions, surfaces permission requests, and handles session management.

### Benefits

- Image Uploads: Attach images directly to messages for visual analysis
- Queued Messages: Send multiple messages that process sequentially, with ability to interrupt
- Tool Integration: Full access to all tools and custom MCP servers during the session
- Hooks Support: Use lifecycle hooks to customize behavior at various points
- Real-time Feedback: See responses as they're generated, not just final results
- Context Persistence: Maintain conversation context across multiple turns naturally

### Implementation Example

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";
import { readFile } from "fs/promises";

async function* generateMessages() {
  yield {
    type: "user" as const,
    message: {
      role: "user" as const,
      content: "Analyze this codebase for security issues"
    }
  };

  await new Promise((resolve) => setTimeout(resolve, 2000));

  yield {
    type: "user" as const,
    message: {
      role: "user" as const,
      content: [
        { type: "text", text: "Review this architecture diagram" },
        {
          type: "image",
          source: {
            type: "base64",
            media_type: "image/png",
            data: await readFile("diagram.png", "base64")
          }
        }
      ]
    }
  };
}

for await (const message of query({
  prompt: generateMessages(),
  options: { maxTurns: 10, allowedTools: ["Read", "Grep"] }
})) {
  if (message.type === "result") {
    console.log(message.result);
  }
}
```

```python Python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
import asyncio
import base64


async def streaming_analysis():
    async def message_generator():
        yield {
            "type": "user",
            "message": {"role": "user", "content": "Analyze this codebase for security issues"},
        }
        await asyncio.sleep(2)

        with open("diagram.png", "rb") as f:
            image_data = base64.b64encode(f.read()).decode()

        yield {
            "type": "user",
            "message": {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Review this architecture diagram"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}},
                ],
            },
        }

    options = ClaudeAgentOptions(max_turns=10, allowed_tools=["Read", "Grep"])

    async with ClaudeSDKClient(options) as client:
        await client.query(message_generator())
        async for message in client.receive_response():
            pass


asyncio.run(streaming_analysis())
```

## Single Message Input

Single message input is simpler but more limited.

### When to Use Single Message Input

Use single message input when:

- You need a one-shot response
- You do not need image attachments, hooks, etc.
- You need to operate in a stateless environment, such as a lambda function

### Limitations

> **Warning:** Single message input mode does **not** support:
> - Direct image attachments in messages
> - Dynamic message queueing
> - Real-time interruption
> - Hook integration
> - Natural multi-turn conversations

### Implementation Example

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Explain the authentication flow",
  options: { maxTurns: 1, allowedTools: ["Read", "Grep"] }
})) {
  if (message.type === "result") {
    console.log(message.result);
  }
}

for await (const message of query({
  prompt: "Now explain the authorization process",
  options: { continue: true, maxTurns: 1 }
})) {
  if (message.type === "result") {
    console.log(message.result);
  }
}
```

```python Python
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
import asyncio


async def single_message_example():
    async for message in query(
        prompt="Explain the authentication flow",
        options=ClaudeAgentOptions(max_turns=1, allowed_tools=["Read", "Grep"]),
    ):
        if isinstance(message, ResultMessage):
            print(message.result)

    async for message in query(
        prompt="Now explain the authorization process",
        options=ClaudeAgentOptions(continue_conversation=True, max_turns=1),
    ):
        if isinstance(message, ResultMessage):
            print(message.result)


asyncio.run(single_message_example())
```
