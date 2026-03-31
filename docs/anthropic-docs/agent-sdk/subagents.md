---
source: https://platform.claude.com/docs/en/agent-sdk/subagents
scraped: 2026-03-23
section: agent-sdk
---

# Subagents in the SDK

Define and invoke subagents to isolate context, run tasks in parallel, and apply specialized instructions in your Claude Agent SDK applications.

---

Subagents are separate agent instances that your main agent can spawn to handle focused subtasks. Use subagents to isolate context for focused subtasks, run multiple analyses in parallel, and apply specialized instructions without bloating the main agent's prompt.

## Overview

You can create subagents in three ways:

- **Programmatically**: use the `agents` parameter in your `query()` options
- **Filesystem-based**: define agents as markdown files in `.claude/agents/` directories
- **Built-in general-purpose**: Claude can invoke the built-in `general-purpose` subagent at any time via the Agent tool without you defining anything

## Benefits of using subagents

### Context isolation

Each subagent runs in its own fresh conversation. Intermediate tool calls and results stay inside the subagent; only its final message returns to the parent.

### Parallelization

Multiple subagents can run concurrently, dramatically speeding up complex workflows.

### Specialized instructions and knowledge

Each subagent can have tailored system prompts with specific expertise, best practices, and constraints.

### Tool restrictions

Subagents can be limited to specific tools, reducing the risk of unintended actions.

## Creating subagents

### Programmatic definition (recommended)

```python Python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


async def main():
    async for message in query(
        prompt="Review the authentication module for security issues",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Grep", "Glob", "Agent"],
            agents={
                "code-reviewer": AgentDefinition(
                    description="Expert code review specialist. Use for quality, security, and maintainability reviews.",
                    prompt="""You are a code review specialist with expertise in security, performance, and best practices.

When reviewing code:
- Identify security vulnerabilities
- Check for performance issues
- Verify adherence to coding standards""",
                    tools=["Read", "Grep", "Glob"],
                    model="sonnet",
                ),
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Review the authentication module for security issues",
  options: {
    allowedTools: ["Read", "Grep", "Glob", "Agent"],
    agents: {
      "code-reviewer": {
        description: "Expert code review specialist. Use for quality, security, and maintainability reviews.",
        prompt: `You are a code review specialist with expertise in security, performance, and best practices.

When reviewing code:
- Identify security vulnerabilities
- Check for performance issues
- Verify adherence to coding standards`,
        tools: ["Read", "Grep", "Glob"],
        model: "sonnet"
      }
    }
  }
})) {
  if ("result" in message) console.log(message.result);
}
```

### AgentDefinition configuration

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `description` | `string` | Yes | Natural language description of when to use this agent |
| `prompt` | `string` | Yes | The agent's system prompt defining its role and behavior |
| `tools` | `string[]` | No | Array of allowed tool names. If omitted, inherits all tools |
| `model` | `'sonnet' \| 'opus' \| 'haiku' \| 'inherit'` | No | Model override for this agent |

> **Note:** Subagents cannot spawn their own subagents. Don't include `Agent` in a subagent's `tools` array.

## What subagents inherit

| The subagent receives | The subagent does not receive |
|:---|:---|
| Its own system prompt and the Agent tool's prompt | The parent's conversation history or tool results |
| Project CLAUDE.md (loaded via `settingSources`) | Skills (unless listed in `AgentDefinition.skills`, TypeScript only) |
| Tool definitions (inherited from parent, or the subset in `tools`) | The parent's system prompt |

## Invoking subagents

### Automatic invocation

Claude automatically decides when to invoke subagents based on the task and each subagent's `description`. Write clear, specific descriptions so Claude can match tasks to the right subagent.

### Explicit invocation

To guarantee Claude uses a specific subagent, mention it by name in your prompt:

```text
"Use the code-reviewer agent to check the authentication module"
```

## Detecting subagent invocation

Subagents are invoked via the Agent tool. Check for `tool_use` blocks where `name` is `"Agent"`.

> **Note:** The tool name was renamed from `"Task"` to `"Agent"` in Claude Code v2.1.63. Check both values for compatibility.

## Resuming subagents

Subagents can be resumed to continue where they left off. When a subagent completes, Claude receives its agent ID in the Agent tool result.

## Tool restrictions

Common tool combinations:

| Use case | Tools | Description |
|:---------|:------|:------------|
| Read-only analysis | `Read`, `Grep`, `Glob` | Can examine code but not modify or execute |
| Test execution | `Bash`, `Read`, `Grep` | Can run commands and analyze output |
| Code modification | `Read`, `Edit`, `Write`, `Grep`, `Glob` | Full read/write access without command execution |
| Full access | All tools | Inherits all tools from parent (omit `tools` field) |

## Troubleshooting

### Claude not delegating to subagents

1. **Include the Agent tool**: subagents are invoked via the Agent tool, so it must be in `allowedTools`
2. **Use explicit prompting**: mention the subagent by name
3. **Write a clear description**: explain exactly when the subagent should be used

## Related documentation

- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents): comprehensive subagent documentation including filesystem-based definitions
- [SDK overview](/docs/en/agent-sdk/overview): getting started with the Claude Agent SDK
