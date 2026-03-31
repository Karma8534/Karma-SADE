---
source: https://platform.claude.com/docs/en/agent-sdk/custom-tools
scraped: 2026-03-23
section: agent-sdk
---

# Custom Tools

Build and integrate custom tools to extend Claude Agent SDK functionality

---

Custom tools allow you to extend Claude Code's capabilities with your own functionality through in-process MCP servers, enabling Claude to interact with external services, APIs, or perform specialized operations.

## Creating Custom Tools

Use the `createSdkMcpServer` and `tool` helper functions to define type-safe custom tools:

```typescript TypeScript
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const customServer = createSdkMcpServer({
  name: "my-custom-tools",
  version: "1.0.0",
  tools: [
    tool(
      "get_weather",
      "Get current temperature for a location using coordinates",
      {
        latitude: z.number().describe("Latitude coordinate"),
        longitude: z.number().describe("Longitude coordinate")
      },
      async (args) => {
        const response = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${args.latitude}&longitude=${args.longitude}&current=temperature_2m&temperature_unit=fahrenheit`
        );
        const data = await response.json();
        return {
          content: [{ type: "text", text: `Temperature: ${data.current.temperature_2m}°F` }]
        };
      }
    )
  ]
});
```

```python Python
from claude_agent_sdk import tool, create_sdk_mcp_server
from typing import Any
import aiohttp


@tool(
    "get_weather",
    "Get current temperature for a location using coordinates",
    {"latitude": float, "longitude": float},
)
async def get_weather(args: dict[str, Any]) -> dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={args['latitude']}&longitude={args['longitude']}&current=temperature_2m&temperature_unit=fahrenheit"
        ) as response:
            data = await response.json()

    return {
        "content": [{"type": "text", "text": f"Temperature: {data['current']['temperature_2m']}°F"}]
    }


custom_server = create_sdk_mcp_server(
    name="my-custom-tools",
    version="1.0.0",
    tools=[get_weather],
)
```

## Using Custom Tools

> **Important:** Custom MCP tools require streaming input mode. You must use an async generator/iterable for the `prompt` parameter.

### Tool Name Format

Tools follow the pattern: `mcp__{server_name}__{tool_name}`

Example: a tool named `get_weather` in server `my-custom-tools` becomes `mcp__my-custom-tools__get_weather`

```typescript TypeScript
async function* generateMessages() {
  yield {
    type: "user" as const,
    message: { role: "user" as const, content: "What's the weather in San Francisco?" }
  };
}

for await (const message of query({
  prompt: generateMessages(),
  options: {
    mcpServers: { "my-custom-tools": customServer },
    allowedTools: ["mcp__my-custom-tools__get_weather"],
    maxTurns: 3
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

```python Python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
import asyncio

options = ClaudeAgentOptions(
    mcp_servers={"my-custom-tools": custom_server},
    allowed_tools=["mcp__my-custom-tools__get_weather"],
)


async def main():
    async with ClaudeSDKClient(options=options) as client:
        await client.query("What's the weather in San Francisco?")
        async for msg in client.receive_response():
            print(msg)


asyncio.run(main())
```

## Error Handling

```typescript TypeScript
tool(
  "fetch_data",
  "Fetch data from an API",
  { endpoint: z.string().url() },
  async (args) => {
    try {
      const response = await fetch(args.endpoint);
      if (!response.ok) {
        return {
          content: [{ type: "text", text: `API error: ${response.status} ${response.statusText}` }]
        };
      }
      const data = await response.json();
      return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
    } catch (error) {
      return { content: [{ type: "text", text: `Failed to fetch data: ${error.message}` }] };
    }
  }
);
```

## Related Documentation

- [TypeScript SDK Reference](/docs/en/agent-sdk/typescript)
- [Python SDK Reference](/docs/en/agent-sdk/python)
- [MCP Documentation](https://modelcontextprotocol.io)
- [SDK Overview](/docs/en/agent-sdk/overview)
