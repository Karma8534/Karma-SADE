---
source: https://platform.claude.com/docs/en/agent-sdk/hooks
scraped: 2026-03-23
section: agent-sdk
---

# Intercept and control agent behavior with hooks

Intercept and customize agent behavior at key execution points with hooks

Hooks are callback functions that run your code in response to agent events, like a tool being called, a session starting, or execution stopping. With hooks, you can:

- **Block dangerous operations** before they execute, like destructive shell commands or unauthorized file access
- **Log and audit** every tool call for compliance, debugging, or analytics
- **Transform inputs and outputs** to sanitize data, inject credentials, or redirect file paths
- **Require human approval** for sensitive actions like database writes or API calls
- **Track session lifecycle** to manage state, clean up resources, or send notifications

## Available hooks

| Hook Event | Python SDK | TypeScript SDK | What triggers it | Example use case |
|------------|------------|----------------|------------------|------------------|
| `PreToolUse` | Yes | Yes | Tool call request (can block or modify) | Block dangerous shell commands |
| `PostToolUse` | Yes | Yes | Tool execution result | Log all file changes to audit trail |
| `PostToolUseFailure` | Yes | Yes | Tool execution failure | Handle or log tool errors |
| `UserPromptSubmit` | Yes | Yes | User prompt submission | Inject additional context into prompts |
| `Stop` | Yes | Yes | Agent execution stop | Save session state before exit |
| `SubagentStart` | Yes | Yes | Subagent initialization | Track parallel task spawning |
| `SubagentStop` | Yes | Yes | Subagent completion | Aggregate results from parallel tasks |
| `PreCompact` | Yes | Yes | Conversation compaction request | Archive full transcript before summarizing |
| `PermissionRequest` | Yes | Yes | Permission dialog would be displayed | Custom permission handling |
| `SessionStart` | No | Yes | Session initialization | Initialize logging and telemetry |
| `SessionEnd` | No | Yes | Session termination | Clean up temporary resources |
| `Notification` | Yes | Yes | Agent status messages | Send agent status updates to Slack or PagerDuty |
| `Setup` | No | Yes | Session setup/maintenance | Run initialization tasks |
| `TeammateIdle` | No | Yes | Teammate becomes idle | Reassign work or notify |
| `TaskCompleted` | No | Yes | Background task completes | Aggregate results from parallel tasks |
| `ConfigChange` | No | Yes | Configuration file changes | Reload settings dynamically |
| `WorktreeCreate` | No | Yes | Git worktree created | Track isolated workspaces |
| `WorktreeRemove` | No | Yes | Git worktree removed | Clean up workspace resources |

## Configure hooks

```python
options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[my_callback])]}
)
```

```typescript
for await (const message of query({
  prompt: "Your prompt",
  options: {
    hooks: {
      PreToolUse: [{ matcher: "Bash", hooks: [myCallback] }]
    }
  }
})) {
  console.log(message);
}
```

### Matchers

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `matcher` | `string` | `undefined` | Regex pattern matched against tool name. MCP tools: `mcp__<server>__<action>`. |
| `hooks` | `HookCallback[]` | - | Required. Array of callback functions |
| `timeout` | `number` | `60` | Timeout in seconds |

### Callback Outputs

- **Top-level**: `systemMessage` (inject into conversation), `continue`/`continue_`
- **`hookSpecificOutput`**: `permissionDecision` ("allow"/"deny"/"ask"), `permissionDecisionReason`, `updatedInput`, `additionalContext`
- Return `{}` to allow without changes
- **deny > ask > allow** when multiple hooks apply

### Async output

```python
return {"async_": True, "asyncTimeout": 30000}
```
```typescript
return { async: true, asyncTimeout: 30000 };
```

## Example: Block .env writes

```python
async def protect_env_files(input_data, tool_use_id, context):
    file_path = input_data["tool_input"].get("file_path", "")
    if file_path.split("/")[-1] == ".env":
        return {"hookSpecificOutput": {"hookEventName": input_data["hook_event_name"], "permissionDecision": "deny", "permissionDecisionReason": "Cannot modify .env files"}}
    return {}
```

## Example: Regex matchers

```python
options = ClaudeAgentOptions(hooks={"PreToolUse": [
    HookMatcher(matcher="Write|Edit|Delete", hooks=[file_security_hook]),
    HookMatcher(matcher="^mcp__", hooks=[mcp_audit_hook]),
    HookMatcher(hooks=[global_logger]),
]})
```

## Common Issues

- Hook not firing: verify event name case-sensitivity, matcher pattern, correct event type
- Matcher only filters by tool name, not file paths — check `tool_input.file_path` inside callback
- `SessionStart`/`SessionEnd` not available in Python SDK callbacks — use settings file shell hooks
- Subagent permission prompts: use `PreToolUse` hooks to auto-approve or configure permission rules
