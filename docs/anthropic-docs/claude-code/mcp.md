---
source: https://code.claude.com/docs/en/mcp
scraped: 2026-03-23
section: claude-code
---

# Connect Claude Code to tools via MCP

> Learn how to connect Claude Code to your tools with the Model Context Protocol.

The Model Context Protocol (MCP) is an open standard that lets Claude Code connect to external tools, data sources, and services. With MCP, you can give Claude access to databases, APIs, file systems, development tools, and more.

## How MCP works in Claude Code

MCP servers expose tools that Claude can call during a session. When you add an MCP server, its tools become available alongside Claude's built-in tools (Bash, Read, Write, etc.).

Claude Code supports two MCP transport types:
- **stdio**: Runs a local process and communicates over stdin/stdout
- **http**: Connects to a remote server over HTTP/SSE

## Add MCP servers

### Via the CLI

```bash
# Add a stdio server
claude mcp add my-server -- npx -y @my-org/my-mcp-server

# Add with environment variables
claude mcp add my-server -e API_KEY=value -- npx -y @my-org/my-mcp-server

# Add an HTTP server
claude mcp add --transport http my-remote-server https://my-server.example.com/mcp

# Add a GitHub Copilot server
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

### Via settings files

Add to your `~/.claude/settings.json` (user scope) or `.claude/settings.json` (project scope):

```json
{
  "mcpServers": {
    "my-server": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@my-org/my-mcp-server"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

For an HTTP server:

```json
{
  "mcpServers": {
    "remote-server": {
      "type": "http",
      "url": "https://my-server.example.com/mcp",
      "headers": {
        "Authorization": "Bearer your-token"
      }
    }
  }
}
```

### Via `.mcp.json` (project-level)

Create a `.mcp.json` file in your repository root to share MCP configuration with your team:

```json
{
  "mcpServers": {
    "postgres": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

Commit `.mcp.json` to version control so all team members get the same MCP tools automatically.

## Manage MCP servers

```bash
# List configured servers
claude mcp list

# Get details about a server
claude mcp get my-server

# Remove a server
claude mcp remove my-server

# Reset to defaults (remove all user-level servers)
claude mcp reset-project-choice
```

Use `/mcp` inside an interactive Claude Code session to manage MCP servers without leaving the chat panel.

## MCP server scopes

MCP servers can be configured at different scopes:

| Scope | Location | Applies to |
|---|---|---|
| User | `~/.claude/settings.json` | All your projects |
| Project | `.claude/settings.json` or `.mcp.json` | All project collaborators |
| Local | `.claude/settings.local.json` | You in this project only |
| Managed | `managed-mcp.json` | All users in your organization |

## Managed MCP configuration

Enterprise administrators can deploy MCP servers to all users via `managed-mcp.json`. Users cannot remove managed MCP servers.

```json
{
  "mcpServers": {
    "internal-api": {
      "type": "http",
      "url": "https://internal-tools.company.com/mcp"
    }
  }
}
```

## MCP with OAuth authentication

Some MCP servers use OAuth for authentication. When you first connect to such a server, Claude Code opens a browser window for authentication.

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

After authenticating, the token is stored and reused for future sessions.

## Use MCP tools

Once configured, MCP tools are available automatically. You can:

- Reference them directly: "Use the database tool to query users"
- Ask Claude to list available tools: "What MCP tools do you have?"
- Use `/mcp` to see the status of configured servers

### Permissions for MCP tools

MCP tool calls require permission by default. You can allow specific tools in your settings:

```json
{
  "permissions": {
    "allow": ["mcp__github__*", "mcp__postgres__read_*"]
  }
}
```

Or deny specific tools:

```json
{
  "permissions": {
    "deny": ["mcp__filesystem__write_file"]
  }
}
```

## Scope MCP servers to subagents

You can give specific MCP servers to specific subagents:

```yaml
---
name: browser-tester
description: Tests features in a real browser using Playwright
mcpServers:
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  - github
---

Use the Playwright tools to navigate, screenshot, and interact with pages.
```

## Popular MCP servers

The MCP ecosystem includes servers for many tools and services. Check the [MCP registry](https://api.anthropic.com/mcp-registry/docs) for the full list.

Examples include:
- `@modelcontextprotocol/server-filesystem` — Local file system access
- `@modelcontextprotocol/server-github` — GitHub API integration
- `@modelcontextprotocol/server-postgres` — PostgreSQL database queries
- `@modelcontextprotocol/server-sqlite` — SQLite database queries
- `@modelcontextprotocol/server-slack` — Slack messaging
- `@modelcontextprotocol/server-brave-search` — Web search via Brave
- `@modelcontextprotocol/server-puppeteer` — Browser automation

## Troubleshooting MCP

### Server fails to start

Check the server logs with `--debug`:
```bash
claude --debug "api,mcp" "query"
```

Common causes:
- Missing dependencies (run `npm install` or `pip install` first)
- Wrong command path
- Missing required environment variables

### Tools not appearing

1. Run `/mcp` to check server status
2. Verify the server started successfully
3. Check if the tool is blocked by a deny rule in permissions

### Permission errors

If Claude can see a tool but can't call it:
1. Check `permissions.deny` rules in your settings
2. Add an allow rule: `"allow": ["mcp__servername__toolname"]`

## See also

- Settings — full settings reference including mcpServers configuration
- Permissions — control which MCP tools Claude can use
- Subagents — scope MCP servers to specific subagents
- Plugins — package MCP servers with other Claude Code extensions
