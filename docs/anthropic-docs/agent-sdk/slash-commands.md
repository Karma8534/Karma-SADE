---
source: https://platform.claude.com/docs/en/agent-sdk/slash-commands
scraped: 2026-03-23
section: agent-sdk
---

# Slash Commands in the SDK

Learn how to use slash commands to control Claude Code sessions through the SDK

---

Slash commands provide a way to control Claude Code sessions with special commands that start with `/`.

## Discovering Available Slash Commands

Available slash commands are listed in the system initialization message:

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({ prompt: "Hello Claude", options: { maxTurns: 1 } })) {
  if (message.type === "system" && message.subtype === "init") {
    console.log("Available slash commands:", message.slash_commands);
  }
}
```

```python Python
import asyncio
from claude_agent_sdk import query


async def main():
    async for message in query(prompt="Hello Claude", options={"max_turns": 1}):
        if message.type == "system" and message.subtype == "init":
            print("Available slash commands:", message.slash_commands)


asyncio.run(main())
```

## Sending Slash Commands

Send slash commands by including them in your prompt string:

```typescript TypeScript
for await (const message of query({ prompt: "/compact", options: { maxTurns: 1 } })) {
  if (message.type === "result") {
    console.log("Command executed:", message.result);
  }
}
```

## Common Slash Commands

### `/compact` - Compact Conversation History

Reduces the size of your conversation history by summarizing older messages while preserving important context.

### `/clear` - Clear Conversation

Starts a fresh conversation by clearing all previous history.

## Creating Custom Slash Commands

> **Note:** The `.claude/commands/` directory is the legacy format. The recommended format is `.claude/skills/<name>/SKILL.md`, which supports the same slash-command invocation plus autonomous invocation by Claude. See [Skills](/docs/en/agent-sdk/skills) for the current format.

### File Locations

- **Project commands**: `.claude/commands/` - Available only in the current project (legacy; prefer `.claude/skills/`)
- **Personal commands**: `~/.claude/commands/` - Available across all your projects (legacy; prefer `~/.claude/skills/`)

### File Format

Create `.claude/commands/refactor.md`:

```markdown
Refactor the selected code to improve readability and maintainability.
Focus on clean code principles and best practices.
```

This creates the `/refactor` command.

### With Frontmatter

```markdown
---
allowed-tools: Read, Grep, Glob
description: Run security vulnerability scan
---

Analyze the codebase for security vulnerabilities including:
- SQL injection risks
- XSS vulnerabilities
- Exposed credentials
```

### Advanced Features

#### Arguments and Placeholders

Create `.claude/commands/fix-issue.md`:

```markdown
---
argument-hint: [issue-number] [priority]
description: Fix a GitHub issue
---

Fix issue #$1 with priority $2.
```

#### Bash Command Execution

Include dynamic content with `!` prefix:

```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
description: Create a git commit
---

## Context

- Current status: !`git status`
- Current diff: !`git diff HEAD`

## Task

Create a git commit with appropriate message based on the changes.
```

#### File References

Include file contents using the `@` prefix:

```markdown
Review the following configuration files:
- Package config: @package.json
- TypeScript config: @tsconfig.json
```

## Using Custom Commands in the SDK

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "/refactor src/auth/login.ts",
  options: { maxTurns: 3 }
})) {
  if (message.type === "assistant") {
    console.log("Refactoring suggestions:", message.message);
  }
}
```

## See Also

- [Slash Commands](https://code.claude.com/docs/en/slash-commands) - Complete slash command documentation
- [Subagents in the SDK](/docs/en/agent-sdk/subagents) - Similar filesystem-based configuration for subagents
- [TypeScript SDK reference](/docs/en/agent-sdk/typescript) - Complete API documentation
