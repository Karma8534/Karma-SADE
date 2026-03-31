---
source: https://platform.claude.com/docs/en/agent-sdk/permissions
scraped: 2026-03-23
section: agent-sdk
---

# Configure permissions

Control how your agent uses tools with permission modes, hooks, and declarative allow/deny rules.

---

The Claude Agent SDK provides permission controls to manage how Claude uses tools. Use permission modes and rules to define what's allowed automatically, and the `canUseTool` callback to handle everything else at runtime.

## How permissions are evaluated

When Claude requests a tool, the SDK checks permissions in this order:

1. **Hooks** - Run hooks first, which can allow, deny, or continue to the next step
2. **Deny rules** - Check `deny` rules (from `disallowed_tools` and settings.json). If a deny rule matches, the tool is blocked, even in `bypassPermissions` mode.
3. **Permission mode** - Apply the active permission mode. `bypassPermissions` approves everything that reaches this step.
4. **Allow rules** - Check `allow` rules (from `allowed_tools` and settings.json). If a rule matches, the tool is approved.
5. **canUseTool callback** - If not resolved by any of the above, call your `canUseTool` callback. In `dontAsk` mode, this step is skipped and the tool is denied.

## Allow and deny rules

`allowed_tools` and `disallowed_tools` (TypeScript: `allowedTools` / `disallowedTools`) add entries to the allow and deny rule lists.

| Option | Effect |
| :--- | :--- |
| `allowed_tools=["Read", "Grep"]` | `Read` and `Grep` are auto-approved. Tools not listed here still exist and fall through to the permission mode and `canUseTool`. |
| `disallowed_tools=["Bash"]` | `Bash` is always denied. Deny rules hold in every permission mode, including `bypassPermissions`. |

For a locked-down agent, pair `allowedTools` with `permissionMode: "dontAsk"` (TypeScript only):

```typescript
const options = {
  allowedTools: ["Read", "Glob", "Grep"],
  permissionMode: "dontAsk"
};
```

> **Warning:** `allowed_tools` does not constrain `bypassPermissions`. Setting `allowed_tools=["Read"]` alongside `permission_mode="bypassPermissions"` still approves every tool. If you need `bypassPermissions` but want specific tools blocked, use `disallowed_tools`.

## Permission modes

| Mode | Description | Tool behavior |
| :--- | :---------- | :------------ |
| `default` | Standard permission behavior | No auto-approvals; unmatched tools trigger your `canUseTool` callback |
| `dontAsk` (TypeScript only) | Deny instead of prompting | Anything not pre-approved is denied; `canUseTool` is never called |
| `acceptEdits` | Auto-accept file edits | File edits and filesystem operations are automatically approved |
| `bypassPermissions` | Bypass all permission checks | All tools run without permission prompts (use with caution) |
| `plan` | Planning mode | No tool execution; Claude plans without making changes |

> **Warning - Subagent inheritance:** When using `bypassPermissions`, all subagents inherit this mode and it cannot be overridden.

### Set permission mode

```python Python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Help me refactor this code",
        options=ClaudeAgentOptions(permission_mode="default"),
    ):
        pass


asyncio.run(main())
```

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Help me refactor this code",
  options: { permissionMode: "default" }
})) {
  // ...
}
```

### Change mode during streaming

```python Python
q = query(
    prompt="Help me refactor this code",
    options=ClaudeAgentOptions(permission_mode="default"),
)
await q.set_permission_mode("acceptEdits")
async for message in q:
    pass
```

```typescript TypeScript
const q = query({
  prompt: "Help me refactor this code",
  options: { permissionMode: "default" }
});
await q.setPermissionMode("acceptEdits");
for await (const message of q) {
  // ...
}
```

### Mode details

#### Accept edits mode (`acceptEdits`)

Auto-approves file operations:
- File edits (Edit, Write tools)
- Filesystem commands: `mkdir`, `touch`, `rm`, `mv`, `cp`

#### Don't ask mode (`dontAsk`, TypeScript only)

Converts any permission prompt into a denial. Tools pre-approved by `allowed_tools` or hooks run as normal. Everything else is denied without calling `canUseTool`.

#### Bypass permissions mode (`bypassPermissions`)

Auto-approves all tool uses without prompts. Hooks still execute and can block operations if needed.

> **Warning:** Use with extreme caution. Claude has full system access in this mode.

#### Plan mode (`plan`)

Prevents tool execution entirely. Claude can analyze code and create plans but cannot make changes. Claude may use `AskUserQuestion` to clarify requirements.

## Related resources

- [Handle approvals and user input](/docs/en/agent-sdk/user-input): interactive approval prompts and clarifying questions
- [Hooks guide](/docs/en/agent-sdk/hooks): run custom code at key points in the agent lifecycle
