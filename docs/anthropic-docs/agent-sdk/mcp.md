---
source: https://platform.claude.com/docs/en/agent-sdk/mcp
scraped: 2026-03-23
section: agent-sdk
---

# Connect to external tools with MCP

Configure MCP servers to extend your agent with external tools. Covers transport types, tool search for large tool sets, authentication, and error handling.

---

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro) is an open standard for connecting AI agents to external tools and data sources.

## Quickstart

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Use the docs MCP server to explain what hooks are in Claude Code",
  options: {
    mcpServers: {
      "claude-code-docs": {
        type: "http",
        url: "https://code.claude.com/docs/mcp"
      }
    },
    allowedTools: ["mcp__claude-code-docs__*"]
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

```python Python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={
            "claude-code-docs": {
                "type": "http",
                "url": "https://code.claude.com/docs/mcp",
            }
        },
        allowed_tools=["mcp__claude-code-docs__*"],
    )

    async for message in query(
        prompt="Use the docs MCP server to explain what hooks are in Claude Code",
        options=options,
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


asyncio.run(main())
```

## Add an MCP server

### In code

Pass MCP servers directly in the `mcpServers` option.

### From a config file

Create a `.mcp.json` file at your project root:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"]
    }
  }
}
```

## Allow MCP tools

MCP tools follow the naming pattern `mcp__<server-name>__<tool-name>`. Use `allowedTools` to specify which MCP tools Claude can use:

```typescript
allowedTools: [
  "mcp__github__*",         // All tools from the github server
  "mcp__db__query",         // Only the query tool from db server
]
```

Wildcards (`*`) let you allow all tools from a server without listing each one individually.

## Transport types

### stdio servers

Local processes that communicate via stdin/stdout:

```typescript TypeScript
{
  mcpServers: {
    github: {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-github"],
      env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN }
    }
  }
}
```

### HTTP/SSE servers

For cloud-hosted MCP servers and remote APIs:

```typescript TypeScript
{
  mcpServers: {
    "remote-api": {
      type: "sse",
      url: "https://api.example.com/mcp/sse",
      headers: { Authorization: `Bearer ${process.env.API_TOKEN}` }
    }
  }
}
```

For HTTP (non-streaming), use `"type": "http"` instead.

### SDK MCP servers

Define custom tools directly in your application code. See [custom tools guide](/docs/en/agent-sdk/custom-tools).

## MCP tool search

When you have many MCP tools configured, tool definitions can consume a significant portion of your context window. Tool search is auto-enabled when MCP tool descriptions would consume more than 10% of the context window.

Configure with `ENABLE_TOOL_SEARCH` environment variable:

| Value | Behavior |
|:------|:---------|
| `auto` | Activates when MCP tools exceed 10% of context (default) |
| `auto:5` | Activates at 5% threshold |
| `true` | Always enabled |
| `false` | Disabled |

## Authentication

### Pass credentials via environment variables

```typescript TypeScript
{
  mcpServers: {
    github: {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-github"],
      env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN }
    }
  }
}
```

### HTTP headers for remote servers

```typescript TypeScript
{
  mcpServers: {
    "secure-api": {
      type: "http",
      url: "https://api.example.com/mcp",
      headers: { Authorization: `Bearer ${process.env.API_TOKEN}` }
    }
  }
}
```

## Error handling

The SDK emits a `system` message with subtype `init` at the start of each query with connection status for each MCP server.

```typescript TypeScript
for await (const message of query({ prompt: "Process data", options: { mcpServers: { "data-processor": dataServer } } })) {
  if (message.type === "system" && message.subtype === "init") {
    const failedServers = message.mcp_servers.filter((s) => s.status !== "connected");
    if (failedServers.length > 0) {
      console.warn("Failed to connect:", failedServers);
    }
  }
}
```

## Related resources

- **[Custom tools guide](/docs/en/agent-sdk/custom-tools)**: Build your own MCP server that runs in-process
- **[Permissions](/docs/en/agent-sdk/permissions)**: Control which MCP tools your agent can use
- **[MCP server directory](https://github.com/modelcontextprotocol/servers)**: Browse available MCP servers
