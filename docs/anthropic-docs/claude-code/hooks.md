---
source: https://code.claude.com/docs/en/hooks
scraped: 2026-03-23
section: claude-code
---

# Hooks reference

## Overview

Hooks are user-defined shell commands, HTTP endpoints, or LLM prompts that execute automatically at specific points in Claude Code's lifecycle. This reference covers event schemas, configuration options, JSON input/output formats, and advanced features.

## Hook lifecycle

Hooks fire at specific points during a Claude Code session:

| Event | When it fires |
|---|---|
| `SessionStart` | When a session begins or resumes |
| `UserPromptSubmit` | When you submit a prompt, before Claude processes it |
| `PreToolUse` | Before a tool call executes. Can block it |
| `PermissionRequest` | When a permission dialog appears |
| `PostToolUse` | After a tool call succeeds |
| `PostToolUseFailure` | After a tool call fails |
| `Notification` | When Claude Code sends a notification |
| `SubagentStart` | When a subagent is spawned |
| `SubagentStop` | When a subagent finishes |
| `Stop` | When Claude finishes responding |
| `StopFailure` | When the turn ends due to an API error |
| `TeammateIdle` | When an agent team teammate is about to go idle |
| `TaskCompleted` | When a task is being marked as completed |
| `InstructionsLoaded` | When CLAUDE.md or .claude/rules/*.md files are loaded |
| `ConfigChange` | When a configuration file changes during a session |
| `WorktreeCreate` | When a worktree is being created |
| `WorktreeRemove` | When a worktree is being removed |
| `PreCompact` | Before context compaction |
| `PostCompact` | After context compaction completes |
| `Elicitation` | When an MCP server requests user input |
| `ElicitationResult` | After a user responds to an MCP elicitation |
| `SessionEnd` | When a session terminates |

## Configuration

Hooks are defined in JSON settings files with three levels of nesting:

1. **Hook event** (e.g., `PreToolUse`, `Stop`)
2. **Matcher group** (filter condition, e.g., "only for Bash tool")
3. **Hook handler** (command, HTTP endpoint, prompt, or agent)

### Hook locations and scope

| Location | Scope | Shareable |
|---|---|---|
| `~/.claude/settings.json` | All projects | No |
| `.claude/settings.json` | Single project | Yes |
| `.claude/settings.local.json` | Single project | No |
| Managed policy settings | Organization-wide | Yes |
| Plugin `hooks/hooks.json` | When plugin enabled | Yes |
| Skill/agent frontmatter | While component active | Yes |

### Matcher patterns

The `matcher` field is a regex string filtering when hooks fire. Use `"*"`, `""`, or omit to match all occurrences.

| Event | Matches on | Example values |
|---|---|---|
| `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest` | tool name | `Bash`, `Edit\|Write`, `mcp__.*` |
| `SessionStart` | how session started | `startup`, `resume`, `clear`, `compact` |
| `SessionEnd` | why session ended | `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other` |
| `Notification` | notification type | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog` |
| `SubagentStart`, `SubagentStop` | agent type | `Bash`, `Explore`, `Plan`, custom agent names |
| `PreCompact`, `PostCompact` | compaction trigger | `manual`, `auto` |
| `ConfigChange` | config source | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` |
| `StopFailure` | error type | `rate_limit`, `authentication_failed`, `billing_error`, `invalid_request`, `server_error`, `max_output_tokens`, `unknown` |
| `InstructionsLoaded` | load reason | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` |
| `Elicitation`, `ElicitationResult` | MCP server name | your configured MCP server names |

### Hook handler types

#### Command hook fields

```json
{
  "type": "command",
  "command": "path/to/script.sh",
  "timeout": 600,
  "async": false,
  "statusMessage": "Custom message"
}
```

| Field | Required | Description |
|---|---|---|
| `type` | yes | `"command"` |
| `command` | yes | Shell command to execute |
| `timeout` | no | Seconds before canceling (default: 600) |
| `async` | no | Run in background without blocking |
| `statusMessage` | no | Custom spinner message |

#### HTTP hook fields

```json
{
  "type": "http",
  "url": "http://localhost:8080/hooks",
  "headers": {
    "Authorization": "Bearer $MY_TOKEN"
  },
  "allowedEnvVars": ["MY_TOKEN"],
  "timeout": 30
}
```

#### Prompt and agent hook fields

```json
{
  "type": "prompt",
  "prompt": "Should this action proceed? $ARGUMENTS",
  "model": "fast-model",
  "timeout": 30
}
```

### Reference scripts by path

```json
{
  "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-style.sh"
}
```

### Disable hooks

```json
{
  "disableAllHooks": true
}
```

## Hook input and output

### Common input fields

All hooks receive these JSON fields via stdin (command) or POST body (HTTP):

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "agent_id": "optional-agent-id",
  "agent_type": "optional-agent-type"
}
```

### Exit codes

- **Exit 0**: Success. Parse stdout for JSON output
- **Exit 2**: Blocking error. stderr text fed back to Claude
- **Any other code**: Non-blocking error. stderr shown in verbose mode

#### Exit code 2 behavior

| Hook event | Blocks? | Effect |
|---|---|---|
| `PreToolUse`, `PermissionRequest`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `TeammateIdle`, `TaskCompleted`, `ConfigChange`, `Elicitation`, `ElicitationResult`, `WorktreeCreate` | Yes | Action prevented |
| `PostToolUse`, `PostToolUseFailure`, `Notification`, `SubagentStart`, `SessionStart`, `SessionEnd`, `PreCompact`, `PostCompact`, `WorktreeRemove`, `InstructionsLoaded`, `StopFailure` | No | stderr shown to user/Claude |

### JSON output

Exit with code 0 and print JSON for structured control:

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Warning message",
  "decision": "block",
  "reason": "Why action was blocked",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny"
  }
}
```

| Field | Default | Description |
|---|---|---|
| `continue` | `true` | If `false`, stops Claude entirely |
| `stopReason` | none | Message shown when `continue` is `false` |
| `suppressOutput` | `false` | Hide stdout from verbose mode |
| `systemMessage` | none | Warning shown to user |

### Decision control patterns

| Events | Pattern | Key fields |
|---|---|---|
| `UserPromptSubmit`, `PostToolUse`, `PostToolUseFailure`, `Stop`, `SubagentStop`, `ConfigChange` | Top-level `decision` | `decision: "block"`, `reason` |
| `TeammateIdle`, `TaskCompleted` | Exit code or `continue` | Exit 2 or `{"continue": false}` |
| `PreToolUse` | `hookSpecificOutput` | `permissionDecision` (allow/deny/ask), `permissionDecisionReason` |
| `PermissionRequest` | `hookSpecificOutput` | `decision.behavior` (allow/deny) |
| `WorktreeCreate` | stdout path | Hook prints absolute worktree path |
| `Elicitation`, `ElicitationResult` | `hookSpecificOutput` | `action` (accept/decline/cancel), `content` |

## Key hook events

### SessionStart

Fires when session begins or resumes. Keep these fast. Only `type: "command"` supported.

**Input fields:**
- `source`: `startup`, `resume`, `clear`, or `compact`
- `model`: model identifier
- `agent_type`: optional, if using `--agent`

**Output:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Additional context for Claude"
  }
}
```

**Persist environment variables:**
```bash
#!/bin/bash
if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
fi
exit 0
```

### PreToolUse

Before tool execution. Can allow, deny, or ask for permission.

**Input fields:**
- `tool_name`: Bash, Edit, Write, Read, Glob, Grep, Agent, WebFetch, WebSearch, MCP tools
- `tool_input`: tool-specific parameters
- `tool_use_id`: unique identifier

**Output:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "Reason shown to user",
    "updatedInput": {"field": "new_value"},
    "additionalContext": "Context for Claude"
  }
}
```

### PostToolUse

After successful tool execution.

**Input fields:**
- `tool_name`, `tool_input`, `tool_response`, `tool_use_id`

**Output:**
```json
{
  "decision": "block",
  "reason": "Reason for blocking",
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Additional context",
    "updatedMCPToolOutput": "For MCP tools only"
  }
}
```

### PermissionRequest

When permission dialog appears.

**Output:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow|deny",
      "updatedInput": {"command": "new_command"},
      "updatedPermissions": [
        {
          "type": "addRules",
          "rules": [{"toolName": "Bash", "ruleContent": "command"}],
          "behavior": "allow",
          "destination": "localSettings|projectSettings|userSettings|session"
        }
      ],
      "message": "For deny only"
    }
  }
}
```

### Stop

When Claude finishes responding. Can block to continue.

**Input fields:**
- `stop_hook_active`: `true` if already continuing from another stop hook
- `last_assistant_message`: text of Claude's final response

**Output:**
```json
{
  "decision": "block",
  "reason": "Why Claude should continue"
}
```

### ConfigChange

When configuration files change.

**Output:**
```json
{
  "decision": "block",
  "reason": "Why change should be blocked"
}
```

### TaskCompleted

When a task is marked complete.

**Output:**
```json
{
  "continue": false,
  "stopReason": "Why task cannot be completed"
}
```

## Example: Bash command validator

```bash
#!/bin/bash
# Block destructive rm commands

COMMAND=$(jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Destructive command blocked by hook"
    }
  }'
else
  exit 0  # allow the command
fi
```

Configuration:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/block-rm.sh"
          }
        ]
      }
    ]
  }
}
```
