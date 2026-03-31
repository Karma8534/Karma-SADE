---
source: https://platform.claude.com/docs/en/agent-sdk/plugins
scraped: 2026-03-23
section: agent-sdk
---

# Plugins in the SDK

Load custom plugins to extend Claude Code with commands, agents, skills, and hooks through the Agent SDK

---

Plugins allow you to extend Claude Code with custom functionality that can be shared across projects. Through the Agent SDK, you can programmatically load plugins from local directories to add custom slash commands, agents, skills, hooks, and MCP servers to your agent sessions.

## What are plugins?

Plugins are packages of Claude Code extensions that can include:
- **Skills**: Model-invoked capabilities that Claude uses autonomously (can also be invoked with `/skill-name`)
- **Agents**: Specialized subagents for specific tasks
- **Hooks**: Event handlers that respond to tool use and other events
- **MCP servers**: External tool integrations via Model Context Protocol

> **Note:** The `commands/` directory is a legacy format. Use `skills/` for new plugins.

## Loading plugins

Load plugins by providing their local file system paths in your options configuration.

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Hello",
  options: {
    plugins: [
      { type: "local", path: "./my-plugin" },
      { type: "local", path: "/absolute/path/to/another-plugin" }
    ]
  }
})) {
  // Plugin commands, agents, and other features are now available
}
```

```python Python
import asyncio
from claude_agent_sdk import query


async def main():
    async for message in query(
        prompt="Hello",
        options={
            "plugins": [
                {"type": "local", "path": "./my-plugin"},
                {"type": "local", "path": "/absolute/path/to/another-plugin"},
            ]
        },
    ):
        pass


asyncio.run(main())
```

> **Note:** The path should point to the plugin's root directory (the directory containing `.claude-plugin/plugin.json`).

## Verifying plugin installation

When plugins load successfully, they appear in the system initialization message:

```typescript TypeScript
for await (const message of query({
  prompt: "Hello",
  options: { plugins: [{ type: "local", path: "./my-plugin" }] }
})) {
  if (message.type === "system" && message.subtype === "init") {
    console.log("Plugins:", message.plugins);
    console.log("Commands:", message.slash_commands);
  }
}
```

## Using plugin skills

Skills from plugins are automatically namespaced with the plugin name to avoid conflicts. When invoked as slash commands, the format is `plugin-name:skill-name`.

```typescript TypeScript
for await (const message of query({
  prompt: "/my-plugin:greet",
  options: { plugins: [{ type: "local", path: "./my-plugin" }] }
})) {
  if (message.type === "assistant") {
    console.log(message.content);
  }
}
```

## Plugin structure reference

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Required: plugin manifest
├── skills/                   # Agent Skills
│   └── my-skill/
│       └── SKILL.md
├── commands/                 # Legacy: use skills/ instead
│   └── custom-cmd.md
├── agents/                   # Custom agents
│   └── specialist.md
├── hooks/                    # Event handlers
│   └── hooks.json
└── .mcp.json                # MCP server definitions
```

## Common use cases

### Development and testing

```typescript
plugins: [{ type: "local", path: "./dev-plugins/my-plugin" }];
```

### Multiple plugin sources

```typescript
plugins: [
  { type: "local", path: "./local-plugin" },
  { type: "local", path: "~/.claude/custom-plugins/shared-plugin" }
];
```

## Troubleshooting

### Plugin not loading

1. **Check the path**: Ensure the path points to the plugin root directory (containing `.claude-plugin/`)
2. **Validate plugin.json**: Ensure your manifest file has valid JSON syntax
3. **Check file permissions**: Ensure the plugin directory is readable

### Skills not appearing

1. **Use the namespace**: Plugin skills require the `plugin-name:skill-name` format when invoked as slash commands
2. **Check init message**: Verify the skill appears in `slash_commands` with the correct namespace
3. **Validate skill files**: Ensure each skill has a `SKILL.md` file in its own subdirectory under `skills/`

## See also

- [Plugins](https://code.claude.com/docs/en/plugins) - Complete plugin development guide
- [Slash Commands](/docs/en/agent-sdk/slash-commands) - Using slash commands in the SDK
- [Subagents](/docs/en/agent-sdk/subagents) - Working with specialized agents
- [Skills](/docs/en/agent-sdk/skills) - Using Agent Skills
