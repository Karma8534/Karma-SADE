---
source: https://code.claude.com/docs/en/how-claude-code-works
scraped: 2026-03-23
section: claude-code
---

# How Claude Code works

> Understand the agentic loop, built-in tools, and how Claude Code interacts with your project.

Claude Code is an agentic assistant that runs in your terminal. While it excels at coding, it can help with anything you can do from the command line: writing docs, running builds, searching files, researching topics, and more.

## The agentic loop

When you give Claude a task, it works through three phases: **gather context**, **take action**, and **verify results**. These phases blend together. Claude uses tools throughout, whether searching files to understand your code, editing to make changes, or running tests to check its work.

The loop adapts to what you ask. A question about your codebase might only need context gathering. A bug fix cycles through all three phases repeatedly. A refactor might involve extensive verification. Claude decides what each step requires based on what it learned from the previous step, chaining dozens of actions together and course-correcting along the way.

You're part of this loop too. You can interrupt at any point to steer Claude in a different direction, provide additional context, or ask it to try a different approach.

The agentic loop is powered by two components: **models** that reason and **tools** that act.

### Models

Claude Code uses Claude models to understand your code and reason about tasks. Claude can read code in any language, understand how components connect, and figure out what needs to change to accomplish your goal. For complex tasks, it breaks work into steps, executes them, and adjusts based on what it learns.

Multiple models are available with different tradeoffs. Sonnet handles most coding tasks well. Opus provides stronger reasoning for complex architectural decisions. Switch with `/model` during a session or start with `claude --model <name>`.

### Tools

Tools are what make Claude Code agentic. Without tools, Claude can only respond with text. With tools, Claude can act: read your code, edit files, run commands, search the web, and interact with external services.

| Category | What Claude can do |
|---|---|
| **File operations** | Read files, edit code, create new files, rename and reorganize |
| **Search** | Find files by pattern, search content with regex, explore codebases |
| **Execution** | Run shell commands, start servers, run tests, use git |
| **Web** | Search the web, fetch documentation, look up error messages |
| **Code intelligence** | See type errors and warnings after edits, jump to definitions, find references |

Claude chooses which tools to use based on your prompt and what it learns along the way. When you say "fix the failing tests," Claude might:

1. Run the test suite to see what's failing
2. Read the error output
3. Search for the relevant source files
4. Read those files to understand the code
5. Edit the files to fix the issue
6. Run the tests again to verify

**Extending the base capabilities:** The built-in tools are the foundation. You can extend what Claude knows with skills, connect to external services with MCP, automate workflows with hooks, and offload tasks to subagents.

## What Claude can access

When you run `claude` in a directory, Claude Code gains access to:

- **Your project.** Files in your directory and subdirectories, plus files elsewhere with your permission.
- **Your terminal.** Any command you could run: build tools, git, package managers, system utilities, scripts.
- **Your git state.** Current branch, uncommitted changes, and recent commit history.
- **Your CLAUDE.md.** A markdown file where you store project-specific instructions, conventions, and context.
- **Auto memory.** Learnings Claude saves automatically as you work. The first 200 lines of MEMORY.md are loaded at the start of each session.
- **Extensions you configure.** MCP servers for external services, skills for workflows, subagents for delegated work, and Claude in Chrome for browser interaction.

Because Claude sees your whole project, it can work across it — searching for relevant files, reading multiple files to understand context, making coordinated edits across them, running tests to verify the fix, and committing the changes if you ask.

## Environments and interfaces

### Execution environments

Claude Code runs in three environments, each with different tradeoffs:

| Environment | Where code runs | Use case |
|---|---|---|
| **Local** | Your machine | Default. Full access to your files, tools, and environment |
| **Cloud** | Anthropic-managed VMs | Offload tasks, work on repos you don't have locally |
| **Remote Control** | Your machine, controlled from a browser | Use the web UI while keeping everything local |

### Interfaces

You can access Claude Code through the terminal, the desktop app, IDE extensions, claude.ai/code, Remote Control, Slack, and CI/CD pipelines. The interface determines how you see and interact with Claude, but the underlying agentic loop is identical.

## Work with sessions

Claude Code saves your conversation locally as you work. Each message, tool use, and result is stored, which enables rewinding, resuming, and forking sessions. Before Claude makes code changes, it also snapshots the affected files so you can revert if needed.

**Sessions are independent.** Each new session starts with a fresh context window, without the conversation history from previous sessions. Claude can persist learnings across sessions using auto memory, and you can add your own persistent instructions in CLAUDE.md.

### Work across branches

Each Claude Code conversation is a session tied to your current directory. Claude sees your current branch's files. When you switch branches, Claude sees the new branch's files, but your conversation history stays the same.

Since sessions are tied to directories, you can run parallel Claude sessions by using git worktrees, which create separate directories for individual branches.

### Resume or fork sessions

When you resume a session with `claude --continue` or `claude --resume`, you pick up where you left off using the same session ID. Your full conversation history is restored, but session-scoped permissions are not.

To branch off and try a different approach without affecting the original session:
```bash
claude --continue --fork-session
```

This creates a new session ID while preserving the conversation history up to that point.

### The context window

Claude's context window holds your conversation history, file contents, command outputs, CLAUDE.md, auto memory, loaded skills, and system instructions. As you work, context fills up.

#### When context fills up

Claude Code manages context automatically as you approach the limit. It clears older tool outputs first, then summarizes the conversation if needed. Put persistent rules in CLAUDE.md rather than relying on conversation history.

To control what's preserved during compaction, add a "Compact Instructions" section to CLAUDE.md or run `/compact` with a focus (like `/compact focus on the API changes`).

Run `/context` to see what's using space.

#### Manage context with skills and subagents

- **Skills** load on demand. Claude sees skill descriptions at session start, but the full content only loads when a skill is used.
- **Subagents** get their own fresh context, completely separate from your main conversation. When done, they return a summary.

## Stay safe with checkpoints and permissions

### Undo changes with checkpoints

**Every file edit is reversible.** Before Claude edits any file, it snapshots the current contents. If something goes wrong, press `Esc` twice to rewind to a previous state, or ask Claude to undo.

Checkpoints are local to your session, separate from git. They only cover file changes.

### Control what Claude can do

Press `Shift+Tab` to cycle through permission modes:

- **Default**: Claude asks before file edits and shell commands
- **Auto-accept edits**: Claude edits files without asking, still asks for commands
- **Plan mode**: Claude uses read-only tools only, creating a plan you can approve before execution

You can also allow specific commands in `.claude/settings.json` so Claude doesn't ask each time.

---

## Work effectively with Claude Code

### Ask Claude Code for help

Claude Code can teach you how to use it. Ask questions like "how do I set up hooks?" or "what's the best way to structure my CLAUDE.md?" and Claude will explain.

Built-in commands guide you through setup:
- `/init` walks you through creating a CLAUDE.md for your project
- `/agents` helps you configure custom subagents
- `/doctor` diagnoses common issues with your installation

### It's a conversation

Claude Code is conversational. You don't need perfect prompts. Start with what you want, then refine:

```text
Fix the login bug
```

[Claude investigates, tries something]

```text
That's not quite right. The issue is in the session handling.
```

[Claude adjusts approach]

### Be specific upfront

The more precise your initial prompt, the fewer corrections you'll need. Reference specific files, mention constraints, and point to example patterns.

```text
The checkout flow is broken for users with expired cards.
Check src/payments/ for the issue, especially token refresh.
Write a failing test first, then fix it.
```

### Give Claude something to verify against

Claude performs better when it can check its own work. Include test cases, paste screenshots of expected UI, or define the output you want.

```text
Implement validateEmail. Test cases: 'user@example.com' → true,
'invalid' → false, 'user@.com' → false. Run the tests after.
```

### Explore before implementing

For complex problems, separate research from coding. Use plan mode (`Shift+Tab` twice) to analyze the codebase first:

```text
Read src/auth/ and understand how we handle sessions.
Then create a plan for adding OAuth support.
```

### Delegate, don't dictate

Think of delegating to a capable colleague. Give context and direction, then trust Claude to figure out the details:

```text
The checkout flow is broken for users with expired cards.
The relevant code is in src/payments/. Can you investigate and fix it?
```

## What's next

- **Extend with features**: Add Skills, MCP connections, and custom commands
- **Common workflows**: Step-by-step guides for typical tasks
