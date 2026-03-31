---
source: https://code.claude.com/docs/en/common-workflows
scraped: 2026-03-23
section: claude-code
---

# Common workflows

> Step-by-step guides for exploring codebases, fixing bugs, refactoring, testing, and other everyday tasks with Claude Code.

This page covers practical workflows for everyday development: exploring unfamiliar code, debugging, refactoring, writing tests, creating PRs, and managing sessions.

## Understand new codebases

### Get a quick codebase overview

```bash
cd /path/to/project
claude
```

```text
give me an overview of this codebase
```

```text
explain the main architecture patterns used here
```

```text
what are the key data models?
```

```text
how is authentication handled?
```

### Find relevant code

```text
find the files that handle user authentication
```

```text
how do these authentication files work together?
```

```text
trace the login process from front-end to database
```

## Fix bugs efficiently

```text
I'm seeing an error when I run npm test
```

```text
suggest a few ways to fix the @ts-ignore in user.ts
```

```text
update user.ts to add the null check you suggested
```

## Refactor code

```text
find deprecated API usage in our codebase
```

```text
suggest how to refactor utils.js to use modern JavaScript features
```

```text
refactor utils.js to use ES2024 features while maintaining the same behavior
```

```text
run tests for the refactored code
```

## Use specialized subagents

```text
/agents
```

```text
review my recent code changes for security issues
```

```text
run all tests and fix any failures
```

```text
use the code-reviewer subagent to check the auth module
```

To create custom subagents:
```text
/agents
```
Then select "Create New subagent" and follow the prompts to define: a unique identifier, when Claude should use this agent, which tools it can access, and a system prompt.

## Use Plan Mode for safe code analysis

Plan Mode instructs Claude to create a plan by analyzing the codebase with read-only operations, perfect for exploring codebases, planning complex changes, or reviewing code safely.

### When to use Plan Mode

- **Multi-step implementation**: When your feature requires making edits to many files
- **Code exploration**: When you want to research the codebase thoroughly before changing anything
- **Interactive development**: When you want to iterate on the direction with Claude

### How to use Plan Mode

Turn on Plan Mode during a session using **Shift+Tab** to cycle through permission modes.

Start a new session in Plan Mode:
```bash
claude --permission-mode plan
```

Run "headless" queries in Plan Mode:
```bash
claude --permission-mode plan -p "Analyze the authentication system and suggest improvements"
```

### Example: Planning a complex refactor

```bash
claude --permission-mode plan
```

```text
I need to refactor our authentication system to use OAuth2. Create a detailed migration plan.
```

```text
What about backward compatibility?
```

```text
How should we handle database migration?
```

Press `Ctrl+G` to open the plan in your default text editor.

When you accept a plan, Claude automatically names the session from the plan content.

### Configure Plan Mode as default

```json
// .claude/settings.json
{
  "permissions": {
    "defaultMode": "plan"
  }
}
```

## Work with tests

```text
find functions in NotificationsService.swift that are not covered by tests
```

```text
add tests for the notification service
```

```text
add test cases for edge conditions in the notification service
```

```text
run the new tests and fix any failures
```

## Create pull requests

```text
summarize the changes I've made to the authentication module
```

```text
create a pr
```

```text
enhance the PR description with more context about the security improvements
```

When you create a PR using `gh pr create`, the session is automatically linked to that PR. You can resume it later with `claude --from-pr <number>`.

## Handle documentation

```text
find functions without proper JSDoc comments in the auth module
```

```text
add JSDoc comments to the undocumented functions in auth.js
```

```text
improve the generated documentation with more context and examples
```

```text
check if the documentation follows our project standards
```

## Work with images

You can use any of these methods:
1. Drag and drop an image into the Claude Code window
2. Copy an image and paste it into the CLI with ctrl+v
3. Provide an image path to Claude: "Analyze this image: /path/to/your/image.png"

```text
What does this image show?
```

```text
Describe the UI elements in this screenshot
```

```text
Here's a screenshot of the error. What's causing it?
```

```text
Generate CSS to match this design mockup
```

## Reference files and directories

Use @ to quickly include files or directories.

```text
Explain the logic in @src/utils/auth.js
```

```text
What's the structure of @src/components?
```

```text
Show me the data from @github:repos/owner/repo/issues
```

## Use extended thinking (thinking mode)

Extended thinking is enabled by default. Toggle verbose mode with `Ctrl+O` to see the internal reasoning.

| Scope | How to configure |
|---|---|
| **Effort level** | Run `/effort`, adjust in `/model`, or set `CLAUDE_CODE_EFFORT_LEVEL` |
| **`ultrathink` keyword** | Include "ultrathink" anywhere in your prompt for high effort on that turn |
| **Toggle shortcut** | Press `Option+T` (macOS) or `Alt+T` (Windows/Linux) |
| **Global default** | Use `/config` to toggle thinking mode |
| **Limit token budget** | Set `MAX_THINKING_TOKENS` environment variable |

> **Warning**: You're charged for all thinking tokens used.

## Resume previous conversations

- `claude --continue` continues the most recent conversation in the current directory
- `claude --resume` opens a conversation picker or resumes by name
- `claude --from-pr 123` resumes sessions linked to a specific pull request

From inside an active session, use `/resume` to switch to a different conversation.

### Name your sessions

```bash
claude -n auth-refactor
```

Or use `/rename` during a session. Resume by name later:

```bash
claude --resume auth-refactor
```

### Use the session picker

Keyboard shortcuts in the picker:

| Shortcut | Action |
|---|---|
| `↑` / `↓` | Navigate between sessions |
| `→` / `←` | Expand or collapse grouped sessions |
| `Enter` | Select and resume the highlighted session |
| `P` | Preview the session content |
| `R` | Rename the highlighted session |
| `/` | Search to filter sessions |
| `A` | Toggle between current directory and all projects |
| `B` | Filter to sessions from your current git branch |
| `Esc` | Exit the picker or search mode |

## Run parallel Claude Code sessions with Git worktrees

Use the `--worktree` (`-w`) flag to create an isolated worktree and start Claude in it:

```bash
# Start Claude in a worktree named "feature-auth"
claude --worktree feature-auth

# Start another session in a separate worktree
claude --worktree bugfix-123

# Auto-generates a name
claude --worktree
```

Worktrees are created at `<repo>/.claude/worktrees/<name>` and branch from the default remote branch.

### Worktree cleanup

When you exit a worktree session, Claude handles cleanup based on whether you made changes:
- **No changes**: the worktree and its branch are removed automatically
- **Changes or commits exist**: Claude prompts you to keep or remove the worktree

### Manage worktrees manually

```bash
# Create a worktree with a new branch
git worktree add ../project-feature-a -b feature-a

# Create a worktree with an existing branch
git worktree add ../project-bugfix bugfix-123

# Start Claude in the worktree
cd ../project-feature-a && claude

# Clean up when done
git worktree remove ../project-feature-a
```

## Get notified when Claude needs your attention

Add a `Notification` hook to get desktop notifications:

**macOS:**
```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

**Linux:**
```json
{
  "hooks": {
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Claude Code needs your attention'"
          }
        ]
      }
    ]
  }
}
```

Matcher values for specific events:
| Matcher | Fires when |
|---|---|
| `permission_prompt` | Claude needs you to approve a tool use |
| `idle_prompt` | Claude is done and waiting for your next prompt |
| `auth_success` | Authentication completes |
| `elicitation_dialog` | Claude is asking you a question |

## Use Claude as a unix-style utility

### Add Claude to your verification process

```json
// package.json
{
    "scripts": {
        "lint:claude": "claude -p 'you are a linter. please look at the changes vs. main and report any issues related to typos. report the filename and line number on one line, and a description of the issue on the second line. do not return any other text.'"
    }
}
```

### Pipe in, pipe out

```bash
cat build-error.txt | claude -p 'concisely explain the root cause of this build error' > output.txt
```

### Control output format

```bash
# Text format (default)
cat data.txt | claude -p 'summarize this data' --output-format text > summary.txt

# JSON format
cat code.py | claude -p 'analyze this code for bugs' --output-format json > analysis.json

# Streaming JSON format
cat log.txt | claude -p 'parse this log file for errors' --output-format stream-json
```
