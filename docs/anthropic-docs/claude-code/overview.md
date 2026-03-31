---
source: https://code.claude.com/docs/en/overview
scraped: 2026-03-23
section: claude-code
---

# Claude Code overview

> Claude Code is an agentic coding tool that reads your codebase, edits files, runs commands, and integrates with your development tools. Available in your terminal, IDE, desktop app, and browser.

Claude Code is an AI-powered coding assistant that helps you build features, fix bugs, and automate development tasks. It understands your entire codebase and can work across multiple files and tools to get things done.

## Get started

Choose your environment to get started. Most surfaces require a [Claude subscription](https://claude.com/pricing) or [Anthropic Console](https://console.anthropic.com/) account. The Terminal CLI and VS Code also support third-party providers.

### Terminal

The full-featured CLI for working with Claude Code directly in your terminal. Edit files, run commands, and manage your entire project from the command line.

**macOS, Linux, WSL:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell:**
```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows CMD:**
```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

Windows requires [Git for Windows](https://git-scm.com/downloads/win). Install it first if you don't have it.

Native installations automatically update in the background to keep you on the latest version.

**Homebrew:**
```bash
brew install --cask claude-code
```

**WinGet:**
```powershell
winget install Anthropic.ClaudeCode
```

Then start Claude Code in any project:
```bash
cd your-project
claude
```

You'll be prompted to log in on first use.

### VS Code

The VS Code extension provides inline diffs, @-mentions, plan review, and conversation history directly in your editor.

- [Install for VS Code](vscode:extension/anthropic.claude-code)
- [Install for Cursor](cursor:extension/anthropic.claude-code)

Or search for "Claude Code" in the Extensions view. After installing, open the Command Palette and select **Open in New Tab**.

### Desktop app

A standalone app for running Claude Code outside your IDE or terminal. Review diffs visually, run multiple sessions side by side, schedule recurring tasks, and kick off cloud sessions.

Download:
- [macOS](https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect)
- [Windows](https://claude.ai/api/desktop/win32/x64/exe/latest/redirect)
- [Windows ARM64](https://claude.ai/api/desktop/win32/arm64/exe/latest/redirect)

### Web

Run Claude Code in your browser with no local setup. Start coding at [claude.ai/code](https://claude.ai/code).

### JetBrains

A plugin for IntelliJ IDEA, PyCharm, WebStorm, and other JetBrains IDEs. Install the [Claude Code plugin](https://plugins.jetbrains.com/plugin/27310-claude-code-beta-) from the JetBrains Marketplace.

## What you can do

### Automate the work you keep putting off

Claude Code handles tedious tasks: writing tests for untested code, fixing lint errors across a project, resolving merge conflicts, updating dependencies, and writing release notes.

```bash
claude "write tests for the auth module, run them, and fix any failures"
```

### Build features and fix bugs

Describe what you want in plain language. Claude Code plans the approach, writes the code across multiple files, and verifies it works.

### Create commits and pull requests

Claude Code works directly with git. It stages changes, writes commit messages, creates branches, and opens pull requests.

```bash
claude "commit my changes with a descriptive message"
```

In CI, you can automate code review and issue triage with GitHub Actions or GitLab CI/CD.

### Connect your tools with MCP

The Model Context Protocol (MCP) is an open standard for connecting AI tools to external data sources. With MCP, Claude Code can read your design docs in Google Drive, update tickets in Jira, pull data from Slack, or use your own custom tooling.

### Customize with instructions, skills, and hooks

`CLAUDE.md` is a markdown file you add to your project root that Claude Code reads at the start of every session. Use it to set coding standards, architecture decisions, preferred libraries, and review checklists.

Create custom commands to package repeatable workflows your team can share, like `/review-pr` or `/deploy-staging`.

Hooks let you run shell commands before or after Claude Code actions, like auto-formatting after every file edit or running lint before a commit.

### Run agent teams and build custom agents

Spawn multiple Claude Code agents that work on different parts of a task simultaneously. A lead agent coordinates the work, assigns subtasks, and merges results.

### Pipe, script, and automate with the CLI

```bash
# Analyze recent log output
tail -200 app.log | claude -p "Slack me if you see any anomalies"

# Automate translations in CI
claude -p "translate new strings into French and raise a PR for review"

# Bulk operations across files
git diff main --name-only | claude -p "review these changed files for security issues"
```

## Use Claude Code everywhere

| I want to... | Best option |
|---|---|
| Continue a local session from my phone or another device | Remote Control |
| Push events from Telegram, Discord, or my own webhooks into a session | Channels |
| Start a task locally, continue on mobile | Web or Claude iOS app |
| Automate PR reviews and issue triage | GitHub Actions or GitLab CI/CD |
| Get automatic code review on every PR | GitHub Code Review |
| Route bug reports from Slack to pull requests | Slack |
| Debug live web applications | Chrome |
| Build custom agents for your own workflows | Agent SDK |

## Next steps

- **Quickstart**: walk through your first real task, from exploring a codebase to committing a fix
- **Store instructions and memories**: give Claude persistent instructions with CLAUDE.md files and auto memory
- **Common workflows and best practices**: patterns for getting the most out of Claude Code
- **Settings**: customize Claude Code for your workflow
- **Troubleshooting**: solutions for common issues
