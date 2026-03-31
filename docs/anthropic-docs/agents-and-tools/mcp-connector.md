---
source: https://platform.claude.com/docs/en/agents-and-tools/mcp-connector
scraped: 2026-03-23
section: agents-and-tools
---

# MCP connector

Claude's Model Context Protocol (MCP) connector feature enables you to connect to remote MCP servers directly from the Messages API without a separate MCP client.

> **Current version**: This feature requires the beta header: `"anthropic-beta": "mcp-client-2025-11-20"`
>
> The previous version (`mcp-client-2025-04-04`) is deprecated.

> This feature is in beta and is **not** eligible for Zero Data Retention (ZDR).

## Key features

- **Direct API integration**: Connect to MCP servers without implementing an MCP client
- **Tool calling support**: Access MCP tools through the Messages API
- **Flexible tool configuration**: Enable all tools, allowlist specific tools, or denylist unwanted tools
- **Per-tool configuration**: Configure individual tools with custom settings
- **OAuth authentication**: Support for OAuth Bearer tokens for authenticated servers
- **Multiple servers**: Connect to multiple MCP servers in a single request

## Limitations

- Only tool calls are currently supported from the MCP specification.
- The server must be publicly exposed through HTTP (supports both Streamable HTTP and SSE transports). Local STDIO servers cannot be connected directly.
- The MCP connector is currently not supported on Amazon Bedrock and Google Vertex.

## Using the MCP connector in the Messages API

The MCP connector uses two components:

1. **MCP Server Definition** (`mcp_servers` array): Defines server connection details (URL, authentication)
2. **MCP Toolset** (`tools` array): Configures which tools to enable and how to configure them

### Basic example

```bash Shell
curl https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: mcp-client-2025-11-20" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1000,
    "messages": [{"role": "user", "content": "What tools do you have available?"}],
    "mcp_servers": [
      {
        "type": "url",
        "url": "https://example-server.modelcontextprotocol.io/sse",
        "name": "example-mcp",
        "authorization_token": "YOUR_TOKEN"
      }
    ],
    "tools": [
      {
        "type": "mcp_toolset",
        "mcp_server_name": "example-mcp"
      }
    ]
  }'
```

```python Python
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=1000,
    messages=[{"role": "user", "content": "What tools do you have available?"}],
    mcp_servers=[
        {
            "type": "url",
            "url": "https://example-server.modelcontextprotocol.io/sse",
            "name": "example-mcp",
            "authorization_token": "YOUR_TOKEN",
        }
    ],
    tools=[{"type": "mcp_toolset", "mcp_server_name": "example-mcp"}],
    betas=["mcp-client-2025-11-20"],
)
```

## MCP server configuration

Each MCP server in the `mcp_servers` array defines the connection details:

```json
{
  "type": "url",
  "url": "https://example-server.modelcontextprotocol.io/sse",
  "name": "example-mcp",
  "authorization_token": "YOUR_TOKEN"
}
```

### Field descriptions

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | string | Yes | Currently only "url" is supported |
| `url` | string | Yes | The URL of the MCP server. Must start with https:// |
| `name` | string | Yes | A unique identifier for this MCP server. Must be referenced by exactly one MCPToolset in the `tools` array. |
| `authorization_token` | string | No | OAuth authorization token if required by the MCP server. |

## MCP toolset configuration

### Basic structure

```json
{
  "type": "mcp_toolset",
  "mcp_server_name": "example-mcp",
  "default_config": {
    "enabled": true,
    "defer_loading": false
  },
  "configs": {
    "specific_tool_name": {
      "enabled": true,
      "defer_loading": true
    }
  }
}
```

### Field descriptions

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | string | Yes | Must be "mcp_toolset" |
| `mcp_server_name` | string | Yes | Must match a server name defined in the `mcp_servers` array |
| `default_config` | object | No | Default configuration applied to all tools in this set |
| `configs` | object | No | Per-tool configuration overrides. Keys are tool names. |
| `cache_control` | object | No | Cache breakpoint configuration for this toolset |

### Tool configuration options

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `enabled` | boolean | `true` | Whether this tool is enabled |
| `defer_loading` | boolean | `false` | If true, tool description is not sent to the model initially. Used with Tool Search Tool. |

## Common configuration patterns

### Enable all tools with default configuration

```json
{
  "type": "mcp_toolset",
  "mcp_server_name": "google-calendar-mcp"
}
```

### Allowlist - Enable only specific tools

```json
{
  "type": "mcp_toolset",
  "mcp_server_name": "google-calendar-mcp",
  "default_config": {
    "enabled": false
  },
  "configs": {
    "search_events": {
      "enabled": true
    },
    "create_event": {
      "enabled": true
    }
  }
}
```

### Denylist - Disable specific tools

```json
{
  "type": "mcp_toolset",
  "mcp_server_name": "google-calendar-mcp",
  "configs": {
    "delete_all_events": {
      "enabled": false
    },
    "share_calendar_publicly": {
      "enabled": false
    }
  }
}
```

## Validation rules

- **Server must exist**: The `mcp_server_name` in an MCPToolset must match a server defined in the `mcp_servers` array
- **Server must be used**: Every MCP server defined in `mcp_servers` must be referenced by exactly one MCPToolset
- **Unique toolset per server**: Each MCP server can only be referenced by one MCPToolset
- **Unknown tool names**: If a tool name in `configs` doesn't exist on the MCP server, a backend warning is logged but no error is returned

## Response content types

### MCP Tool Use Block

```json
{
  "type": "mcp_tool_use",
  "id": "mcptoolu_014Q35RayjACSWkSj4X2yov1",
  "name": "echo",
  "server_name": "example-mcp",
  "input": { "param1": "value1", "param2": "value2" }
}
```

### MCP Tool Result Block

```json
{
  "type": "mcp_tool_result",
  "tool_use_id": "mcptoolu_014Q35RayjACSWkSj4X2yov1",
  "is_error": false,
  "content": [
    {
      "type": "text",
      "text": "Hello"
    }
  ]
}
```

## Multiple MCP servers

You can connect to multiple MCP servers by including multiple server definitions in `mcp_servers` and a corresponding MCPToolset for each in the `tools` array.

## Authentication

For MCP servers that require OAuth authentication, obtain an access token and pass it as the `authorization_token` parameter. API consumers are expected to handle the OAuth flow and obtain the access token prior to making the API call.

### Obtaining an access token for testing

The MCP inspector can guide you through the process:

1. Run: `npx @modelcontextprotocol/inspector`
2. Select "SSE" or "Streamable HTTP" as transport type
3. Enter the URL of the MCP server
4. Click "Open Auth Settings" and then "Quick OAuth Flow"
5. Follow the OAuth Flow Progress steps
6. Copy the `access_token` value

## Migration guide

If you're using the deprecated `mcp-client-2025-04-04` beta header, follow this guide to migrate to the new version.

### Key changes

1. **New beta header**: Change from `mcp-client-2025-04-04` to `mcp-client-2025-11-20`
2. **Tool configuration moved**: Tool configuration now lives in the `tools` array as MCPToolset objects, not in the MCP server definition
3. **More flexible configuration**: New pattern supports allowlisting, denylisting, and per-tool configuration

### Migration steps

**Before (deprecated):**

```json
{
  "mcp_servers": [
    {
      "type": "url",
      "url": "https://mcp.example.com/sse",
      "name": "example-mcp",
      "authorization_token": "YOUR_TOKEN",
      "tool_configuration": {
        "enabled": true,
        "allowed_tools": ["tool1", "tool2"]
      }
    }
  ]
}
```

**After (current):**

```json
{
  "mcp_servers": [
    {
      "type": "url",
      "url": "https://mcp.example.com/sse",
      "name": "example-mcp",
      "authorization_token": "YOUR_TOKEN"
    }
  ],
  "tools": [
    {
      "type": "mcp_toolset",
      "mcp_server_name": "example-mcp",
      "default_config": {
        "enabled": false
      },
      "configs": {
        "tool1": {"enabled": true},
        "tool2": {"enabled": true}
      }
    }
  ]
}
```

### Common migration patterns

| Old pattern | New pattern |
|-------------|-------------|
| No `tool_configuration` (all tools enabled) | MCPToolset with no `default_config` or `configs` |
| `tool_configuration.enabled: false` | MCPToolset with `default_config.enabled: false` |
| `tool_configuration.allowed_tools: [...]` | MCPToolset with `default_config.enabled: false` and specific tools enabled in `configs` |
