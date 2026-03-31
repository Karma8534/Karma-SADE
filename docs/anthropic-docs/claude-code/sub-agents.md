---
source: https://code.claude.com/docs/en/sub-agents
scraped: 2026-03-23
section: claude-code
---

# Create custom subagents

> Create and use specialized AI subagents in Claude Code for task-specific workflows and improved context management.

Subagents are specialized AI assistants that handle specific types of tasks. Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions. When Claude encounters a task that matches a subagent's description, it delegates to that subagent, which works independently and returns results.

Subagents help you:
- **Preserve context** by keeping exploration and implementation out of your main conversation
- **Enforce constraints** by limiting which tools a subagent can use
- **Reuse configurations** across projects with user-level subagents
- **Specialize behavior** with focused system prompts for specific domains
- **Control costs** by routing tasks to faster, cheaper models like Haiku

## Built-in subagents

| Agent | Model | When Claude uses it |
|---|---|---|
| **Explore** | Haiku (fast, low-latency) | File discovery, code search, codebase exploration. Read-only tools only. |
| **Plan** | Inherits from main conversation | Codebase research for planning. Read-only tools only. |
| **general-purpose** | Inherits from main conversation | Complex research, multi-step operations, code modifications |
| Bash | Inherits | Running terminal commands in a separate context |
| statusline-setup | Sonnet | When you run `/statusline` to configure your status line |
| Claude Code Guide | Haiku | When you ask questions about Claude Code features |

## Quickstart: create your first subagent

Subagents are defined in Markdown files with YAML frontmatter. You can create them manually or use the `/agents` command.

1. Run `/agents`
2. Select **Create new agent**, then choose **Personal**
3. Select **Generate with Claude** and describe the subagent
4. Select tools, model, color, and memory configuration
5. Press `s` or `Enter` to save

## Configure subagents

### Choose the subagent scope

| Location | Scope | Priority |
|---|---|---|
| `--agents` CLI flag | Current session | 1 (highest) |
| `.claude/agents/` | Current project | 2 |
| `~/.claude/agents/` | All your projects | 3 |
| Plugin's `agents/` directory | Where plugin is enabled | 4 (lowest) |

Project subagents (`.claude/agents/`) are ideal for subagents specific to a codebase. Check them into version control.

**CLI-defined subagents:**
```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

### Write subagent files

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

### Supported frontmatter fields

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique identifier using lowercase letters and hyphens |
| `description` | Yes | When Claude should delegate to this subagent |
| `tools` | No | Tools the subagent can use. Inherits all tools if omitted |
| `disallowedTools` | No | Tools to deny, removed from inherited or specified list |
| `model` | No | Model to use: `sonnet`, `opus`, `haiku`, a full model ID, or `inherit` |
| `permissionMode` | No | Permission mode: `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, or `plan` |
| `maxTurns` | No | Maximum number of agentic turns before the subagent stops |
| `skills` | No | Skills to load into the subagent's context at startup |
| `mcpServers` | No | MCP servers available to this subagent |
| `hooks` | No | Lifecycle hooks scoped to this subagent |
| `memory` | No | Persistent memory scope: `user`, `project`, or `local` |
| `background` | No | Set to `true` to always run this subagent as a background task |
| `effort` | No | Effort level when this subagent is active |
| `isolation` | No | Set to `worktree` to run the subagent in a temporary git worktree |

### Choose a model

- **Model alias**: `sonnet`, `opus`, or `haiku`
- **Full model ID**: such as `claude-opus-4-6` or `claude-sonnet-4-6`
- **inherit**: Use the same model as the main conversation (default)

### Control subagent capabilities

#### Available tools

```yaml
---
name: safe-researcher
description: Research agent with restricted capabilities
tools: Read, Grep, Glob, Bash
---
```

```yaml
---
name: no-writes
description: Inherits every tool except file writes
disallowedTools: Write, Edit
---
```

#### Restrict which subagents can be spawned

```yaml
---
name: coordinator
description: Coordinates work across specialized agents
tools: Agent(worker, researcher), Read, Bash
---
```

#### Scope MCP servers to a subagent

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

#### Permission modes

| Mode | Behavior |
|---|---|
| `default` | Standard permission checking with prompts |
| `acceptEdits` | Auto-accept file edits |
| `dontAsk` | Auto-deny permission prompts |
| `bypassPermissions` | Skip permission prompts |
| `plan` | Plan mode (read-only exploration) |

#### Preload skills into subagents

```yaml
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns from the preloaded skills.
```

#### Enable persistent memory

```yaml
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---
```

| Scope | Location | Use when |
|---|---|---|
| `user` | `~/.claude/agent-memory/<name-of-agent>/` | the subagent should remember learnings across all projects |
| `project` | `.claude/agent-memory/<name-of-agent>/` | the subagent's knowledge is project-specific and shareable via version control |
| `local` | `.claude/agent-memory-local/<name-of-agent>/` | the subagent's knowledge is project-specific but should not be checked in |

#### Conditional rules with hooks

```yaml
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```

#### Disable specific subagents

```json
{
  "permissions": {
    "deny": ["Agent(Explore)", "Agent(my-custom-agent)"]
  }
}
```

## Work with subagents

### Invoke subagents explicitly

**Natural language**: name the subagent in your prompt:
```text
Use the test-runner subagent to fix failing tests
Have the code-reviewer subagent look at my recent changes
```

**@-mention**: guarantees the subagent runs for one task:
```text
@"code-reviewer (agent)" look at the auth changes
```

**Session-wide**: pass `--agent <name>` to start a session where the main thread takes on that subagent's system prompt:
```bash
claude --agent code-reviewer
```

To make it the default for every session in a project:
```json
{
  "agent": "code-reviewer"
}
```

### Run subagents in foreground or background

- **Foreground subagents** block the main conversation until complete
- **Background subagents** run concurrently while you continue working

You can press **Ctrl+B** to background a running task.

### Common patterns

#### Isolate high-volume operations

```text
Use a subagent to run the test suite and report only the failing tests with their error messages
```

#### Run parallel research

```text
Research the authentication, database, and API modules in parallel using separate subagents
```

#### Chain subagents

```text
Use the code-reviewer subagent to find performance issues, then use the optimizer subagent to fix them
```

### Choose between subagents and main conversation

**Use the main conversation when:**
- The task needs frequent back-and-forth or iterative refinement
- Multiple phases share significant context
- You're making a quick, targeted change
- Latency matters

**Use subagents when:**
- The task produces verbose output you don't need in your main context
- You want to enforce specific tool restrictions or permissions
- The work is self-contained and can return a summary

## Example subagents

### Code reviewer

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)
```

### Debugger

```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works
```

### Data scientist

```markdown
---
name: data-scientist
description: Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.
tools: Bash, Read, Write
model: sonnet
---

You are a data scientist specializing in SQL and BigQuery analysis.
```

### Database query validator

```markdown
---
name: db-reader
description: Execute read-only database queries. Use when analyzing data or generating reports.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

You are a database analyst with read-only access. Execute SELECT queries to answer questions about the data.
```

Validation script:
```bash
#!/bin/bash
# Blocks SQL write operations, allows SELECT queries

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Block write operations (case-insensitive)
if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|REPLACE|MERGE)\b' > /dev/null; then
  echo "Blocked: Write operations not allowed. Use SELECT queries only." >&2
  exit 2
fi

exit 0
```
