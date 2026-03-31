---
source: https://platform.claude.com/docs/en/agent-sdk/cost-tracking
scraped: 2026-03-23
section: agent-sdk
---

# Track cost and usage

Learn how to track token usage, deduplicate parallel tool calls, and calculate costs with the Claude Agent SDK.

---

The Claude Agent SDK provides detailed token usage information for each interaction with Claude.

## Understand token usage

The TypeScript and Python SDKs expose usage data at different levels of detail:

- **TypeScript** provides per-step token breakdowns on each assistant message, per-model cost via `modelUsage`, and a cumulative total on the result message.
- **Python** provides the accumulated total on the result message (`total_cost_usd` and `usage` dict). Per-step breakdowns are not available on individual assistant messages.

Key scoping concepts:

- **`query()` call:** one invocation of the SDK's `query()` function. Each call produces one `result` message at the end.
- **Step:** a single request/response cycle within a `query()` call.
- **Session:** a series of `query()` calls linked by a session ID. Each `query()` call within a session reports its own cost independently.

## Get the total cost of a query

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({ prompt: "Summarize this project" })) {
  if (message.type === "result") {
    console.log(`Total cost: $${message.total_cost_usd}`);
  }
}
```

```python Python
from claude_agent_sdk import query, ResultMessage
import asyncio


async def main():
    async for message in query(prompt="Summarize this project"):
        if isinstance(message, ResultMessage):
            print(f"Total cost: ${message.total_cost_usd or 0}")


asyncio.run(main())
```

## Track detailed usage in TypeScript

### Track per-step usage

When Claude uses multiple tools in one turn, all messages in that turn share the same `id` with identical usage data. Always deduplicate by ID to avoid double-counting.

> **Warning:** Parallel tool calls produce multiple assistant messages whose nested `BetaMessage` shares the same `id` and identical usage. Always deduplicate by ID to get accurate per-step token counts.

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const seenIds = new Set<string>();
let totalInputTokens = 0;
let totalOutputTokens = 0;

for await (const message of query({ prompt: "Summarize this project" })) {
  if (message.type === "assistant") {
    const msgId = message.message.id;

    if (!seenIds.has(msgId)) {
      seenIds.add(msgId);
      totalInputTokens += message.message.usage.input_tokens;
      totalOutputTokens += message.message.usage.output_tokens;
    }
  }
}

console.log(`Steps: ${seenIds.size}`);
console.log(`Input tokens: ${totalInputTokens}`);
console.log(`Output tokens: ${totalOutputTokens}`);
```

### Break down usage per model

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({ prompt: "Summarize this project" })) {
  if (message.type !== "result") continue;

  for (const [modelName, usage] of Object.entries(message.modelUsage)) {
    console.log(`${modelName}: $${usage.costUSD.toFixed(4)}`);
    console.log(`  Input tokens: ${usage.inputTokens}`);
    console.log(`  Output tokens: ${usage.outputTokens}`);
    console.log(`  Cache read: ${usage.cacheReadInputTokens}`);
    console.log(`  Cache creation: ${usage.cacheCreationInputTokens}`);
  }
}
```

## Accumulate costs across multiple calls

Each `query()` call returns its own `total_cost_usd`. The SDK does not provide a session-level total, so accumulate the totals yourself.

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

let totalSpend = 0;

const prompts = [
  "Read the files in src/ and summarize the architecture",
  "List all exported functions in src/auth.ts"
];

for (const prompt of prompts) {
  for await (const message of query({ prompt })) {
    if (message.type === "result") {
      totalSpend += message.total_cost_usd ?? 0;
      console.log(`This call: $${message.total_cost_usd}`);
    }
  }
}

console.log(`Total spend: $${totalSpend.toFixed(4)}`);
```

```python Python
from claude_agent_sdk import query, ResultMessage
import asyncio


async def main():
    total_spend = 0.0

    prompts = [
        "Read the files in src/ and summarize the architecture",
        "List all exported functions in src/auth.ts",
    ]

    for prompt in prompts:
        async for message in query(prompt=prompt):
            if isinstance(message, ResultMessage):
                cost = message.total_cost_usd or 0
                total_spend += cost
                print(f"This call: ${cost}")

    print(f"Total spend: ${total_spend:.4f}")


asyncio.run(main())
```

## Handle errors, caching, and token discrepancies

- **Failed conversations**: Both success and error result messages include `usage` and `total_cost_usd`. Always read cost data from the result message regardless of its `subtype`.
- **Cache tokens**: The SDK automatically uses prompt caching. Usage includes `cache_creation_input_tokens` and `cache_read_input_tokens` for tracking caching savings.

## Related documentation

- [TypeScript SDK Reference](/docs/en/agent-sdk/typescript) - Complete API documentation
- [SDK Overview](/docs/en/agent-sdk/overview) - Getting started with the SDK
