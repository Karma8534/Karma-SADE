---
source: https://code.claude.com/docs/en/settings
scraped: 2026-03-23
section: claude-code
---

# Claude Code settings

> Configure Claude Code with global and project-level settings, and environment variables.

Claude Code offers a variety of settings to configure its behavior to meet your needs. You can configure Claude Code by running the `/config` command when using the interactive REPL, which opens a tabbed Settings interface where you can view status information and modify configuration options.

## Configuration scopes

Claude Code uses a **scope system** to determine where configurations apply and who they're shared with.

### Available scopes

| Scope | Location | Who it affects | Shared with team? |
|---|---|---|---|
| **Managed** | Server-managed settings, plist / registry, or system-level `managed-settings.json` | All users on the machine | Yes (deployed by IT) |
| **User** | `~/.claude/` directory | You, across all projects | No |
| **Project** | `.claude/` in repository | All collaborators on this repository | Yes (committed to git) |
| **Local** | `.claude/settings.local.json` | You, in this repository only | No (gitignored) |

### When to use each scope

**Managed scope** is for:
- Security policies that must be enforced organization-wide
- Configurations that should apply to all users on the machine
- Settings deployed by IT using MDM (Mobile Device Management) tools

**User scope** is for:
- Personal preferences that apply across all your projects
- Your preferred model, theme, or default permission mode
- Tools you always trust (like your preferred test runner)

**Project scope** is for:
- Shared team settings that benefit all project contributors
- Project-specific permissions, hooks, and MCP servers
- Settings that should be version-controlled with the project

**Local scope** is for:
- Personal overrides for a specific project
- Settings you don't want to share with teammates
- Temporary configuration changes

### Priority order

When settings exist at multiple scopes, Claude Code applies them in this priority order (highest to lowest):

1. Managed (highest — cannot be overridden)
2. Local
3. Project
4. User (lowest)

## Settings files

| File | Scope | Description |
|---|---|---|
| `~/.claude/settings.json` | User | Personal settings across all projects |
| `.claude/settings.json` | Project | Shared project settings (commit to git) |
| `.claude/settings.local.json` | Local | Personal project overrides (gitignore this) |
| `managed-settings.json` | Managed | Organization-wide policies |

### Settings file format

```json
{
  "model": "claude-opus-4-6",
  "theme": "dark",
  "permissions": {
    "allow": ["Bash(npm run *)", "Read"],
    "deny": ["Bash(rm *)"]
  },
  "env": {
    "MY_VAR": "value"
  }
}
```

## Available settings

### Model settings

| Setting | Type | Description |
|---|---|---|
| `model` | string | Model to use. Options: `sonnet`, `opus`, `haiku`, or a full model ID |
| `smallFastModel` | string | Model for lightweight tasks (used by the Explore subagent) |

### Display settings

| Setting | Type | Description |
|---|---|---|
| `theme` | string | Color theme: `light`, `dark`, `light-daltonized`, `dark-daltonized` |
| `preferredLanguage` | string | Language for Claude's responses |
| `verbose` | boolean | Show full turn-by-turn output |
| `streamingEnabled` | boolean | Enable/disable response streaming |

### Behavior settings

| Setting | Type | Description |
|---|---|---|
| `autoUpdaterStatus` | string | Auto-update preference: `enabled` or `disabled` |
| `defaultPermissionMode` | string | Default permission mode: `default`, `acceptEdits`, `bypassPermissions`, or `plan` |
| `includeGitInstructions` | boolean | Include git status in system prompt |
| `enableTelemetry` | boolean | Enable/disable usage telemetry |

### Permissions

```json
{
  "permissions": {
    "allow": ["Bash(git *)", "Read", "Edit"],
    "deny": ["Bash(rm -rf *)", "Write(/etc/*)"],
    "defaultMode": "default"
  }
}
```

### Permission rule syntax

Permission rules support glob-style pattern matching:

| Pattern | Matches |
|---|---|
| `Bash` | Any bash command |
| `Bash(git *)` | Any git command |
| `Bash(npm run *)` | Any npm run command |
| `Read` | Any file read |
| `Read(/src/*)` | Files under /src/ |
| `Write(*.json)` | JSON files |
| `Edit` | Any file edit |
| `mcp__server__tool` | Specific MCP tool |
| `Agent(subagent-name)` | Specific subagent |
| `Skill(skill-name)` | Specific skill |

### Hooks

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'About to run bash'"
          }
        ]
      }
    ],
    "PostToolUse": [...],
    "Stop": [...],
    "SessionStart": [...],
    "SessionEnd": [...]
  }
}
```

### MCP servers

```json
{
  "mcpServers": {
    "my-server": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@my-org/my-mcp-server"]
    },
    "remote-server": {
      "type": "http",
      "url": "https://my-server.example.com/mcp"
    }
  }
}
```

### Environment variables

Set environment variables that apply to all Claude Code sessions:

```json
{
  "env": {
    "NODE_ENV": "development",
    "DEBUG": "true"
  }
}
```

## Environment variables reference

Claude Code respects these environment variables:

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key for authentication |
| `ANTHROPIC_BASE_URL` | Override the Anthropic API base URL |
| `CLAUDE_CODE_USE_BEDROCK` | Set to `1` to use Amazon Bedrock |
| `CLAUDE_CODE_USE_VERTEX` | Set to `1` to use Google Vertex AI |
| `CLAUDE_CODE_USE_FOUNDRY` | Set to `1` to use Microsoft Foundry |
| `AWS_REGION` | AWS region for Bedrock |
| `CLOUD_ML_REGION` | GCP region for Vertex AI |
| `ANTHROPIC_VERTEX_PROJECT_ID` | GCP project ID for Vertex AI |
| `ANTHROPIC_BEDROCK_BASE_URL` | Override Bedrock endpoint |
| `ANTHROPIC_VERTEX_BASE_URL` | Override Vertex AI endpoint |
| `ANTHROPIC_FOUNDRY_BASE_URL` | Override Foundry endpoint |
| `HTTPS_PROXY` / `HTTP_PROXY` | Corporate proxy URL |
| `NODE_EXTRA_CA_CERTS` | Path to additional CA certificates |
| `DISABLE_TELEMETRY` | Set to `1` to disable telemetry |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Disable non-essential network requests |
| `USE_BUILTIN_RIPGREP` | Set to `0` to use system ripgrep |
| `CLAUDE_CODE_GIT_BASH_PATH` | Path to Git Bash on Windows |
| `CLAUDE_CODE_SIMPLE` | Set when `--bare` flag is used |
| `BASH_DEFAULT_TIMEOUT_MS` | Timeout for Bash tool commands |
| `BASH_MAX_TIMEOUT_MS` | Maximum timeout for Bash tool commands |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Pin specific Opus model version |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Pin specific Sonnet model version |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Pin specific Haiku model version |
| `SLASH_COMMAND_TOOL_CHAR_BUDGET` | Override skill description character budget |

## Managed settings

Enterprise administrators can enforce settings via managed configuration. Managed settings take the highest priority and cannot be overridden by users.

### Deployment methods

**File-based (all platforms):**
Place `managed-settings.json` in a system directory.

**macOS MDM (plist):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>permissions</key>
  <dict>
    <key>defaultMode</key>
    <string>plan</string>
  </dict>
</dict>
</plist>
```

**Windows Group Policy (registry):**
Set values under `HKLM\Software\Anthropic\ClaudeCode`.

### Managed settings reference

| Setting | Type | Description |
|---|---|---|
| `channelsEnabled` | boolean | Enable/disable channels feature for Team/Enterprise |
| `remoteControlEnabled` | boolean | Enable/disable Remote Control for Team/Enterprise |
| `permissions.defaultMode` | string | Force a default permission mode |
| `permissions.allow` | array | Global allow rules |
| `permissions.deny` | array | Global deny rules |
| `enabledPlugins` | array | Allowlist of permitted plugins |
| `env` | object | Environment variables applied to all sessions |

## See also

- Permissions — permission modes and rule syntax
- Hooks — automate actions around tool events
- MCP — connect to external tools
- Memory — CLAUDE.md and auto memory
