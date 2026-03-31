---
source: https://code.claude.com/docs/en/quickstart
scraped: 2026-03-23
section: claude-code
---

# Quickstart

> Welcome to Claude Code!

This quickstart guide will have you using AI-powered coding assistance in a few minutes.

## Before you begin

Make sure you have:
- A terminal or command prompt open
- A code project to work with
- A Claude subscription (Pro, Max, Teams, or Enterprise), Claude Console account, or access through a supported cloud provider

## Step 1: Install Claude Code

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

**Homebrew:**
```bash
brew install --cask claude-code
```

**WinGet:**
```powershell
winget install Anthropic.ClaudeCode
```

## Step 2: Log in to your account

Claude Code requires an account to use. When you start an interactive session with the `claude` command, you'll need to log in:

```bash
claude
# You'll be prompted to log in on first use
```

```bash
/login
# Follow the prompts to log in with your account
```

You can log in using any of these account types:
- Claude Pro, Max, Teams, or Enterprise (recommended)
- Claude Console (API access with pre-paid credits)
- Amazon Bedrock, Google Vertex AI, or Microsoft Foundry (enterprise cloud providers)

## Step 3: Start your first session

Open your terminal in any project directory and start Claude Code:

```bash
cd /path/to/your/project
claude
```

You'll see the Claude Code welcome screen with your session information, recent conversations, and latest updates. Type `/help` for available commands or `/resume` to continue a previous conversation.

## Step 4: Ask your first question

Let's start with understanding your codebase. Try one of these commands:

```text
what does this project do?
```

```text
what technologies does this project use?
```

```text
where is the main entry point?
```

```text
explain the folder structure
```

You can also ask Claude about its own capabilities:

```text
what can Claude Code do?
```

```text
how do I create custom skills in Claude Code?
```

Claude Code reads your project files as needed. You don't have to manually add context.

## Step 5: Make your first code change

Now let's make Claude Code do some actual coding. Try a simple task:

```text
add a hello world function to the main file
```

Claude Code will:
1. Find the appropriate file
2. Show you the proposed changes
3. Ask for your approval
4. Make the edit

Claude Code always asks for permission before modifying files. You can approve individual changes or enable "Accept all" mode for a session.

## Step 6: Use Git with Claude Code

Claude Code makes Git operations conversational:

```text
what files have I changed?
```

```text
commit my changes with a descriptive message
```

```text
create a new branch called feature/quickstart
```

```text
show me the last 5 commits
```

```text
help me resolve merge conflicts
```

## Step 7: Fix a bug or add a feature

Describe what you want in natural language:

```text
add input validation to the user registration form
```

Or fix existing issues:

```text
there's a bug where users can submit empty forms - fix it
```

Claude Code will:
- Locate the relevant code
- Understand the context
- Implement a solution
- Run tests if available

## Step 8: Test out other common workflows

**Refactor code:**
```text
refactor the authentication module to use async/await instead of callbacks
```

**Write tests:**
```text
write unit tests for the calculator functions
```

**Update documentation:**
```text
update the README with installation instructions
```

**Code review:**
```text
review my changes and suggest improvements
```

## Essential commands

| Command | What it does | Example |
|---|---|---|
| `claude` | Start interactive mode | `claude` |
| `claude "task"` | Run a one-time task | `claude "fix the build error"` |
| `claude -p "query"` | Run one-off query, then exit | `claude -p "explain this function"` |
| `claude -c` | Continue most recent conversation | `claude -c` |
| `claude -r` | Resume a previous conversation | `claude -r` |
| `claude commit` | Create a Git commit | `claude commit` |
| `/clear` | Clear conversation history | `/clear` |
| `/help` | Show available commands | `/help` |
| `exit` or Ctrl+C | Exit Claude Code | `exit` |

## Pro tips for beginners

**Be specific with your requests:**
- Instead of: "fix the bug"
- Try: "fix the login bug where users see a blank screen after entering wrong credentials"

**Use step-by-step instructions:**
```text
1. create a new database table for user profiles
2. create an API endpoint to get and update user profiles
3. build a webpage that allows users to see and edit their information
```

**Let Claude explore first:**
```text
analyze the database schema
```

**Save time with shortcuts:**
- Press `?` to see all available keyboard shortcuts
- Use Tab for command completion
- Press ↑ for command history
- Type `/` to see all commands and skills

## What's next?

- **How Claude Code works**: Understand the agentic loop, built-in tools, and how Claude Code interacts with your project
- **Best practices**: Get better results with effective prompting and project setup
- **Common workflows**: Step-by-step guides for common tasks
- **Extend Claude Code**: Customize with CLAUDE.md, skills, hooks, MCP, and more

## Getting help

- **In Claude Code**: Type `/help` or ask "how do I..."
- **Documentation**: Browse other guides
- **Community**: Join our [Discord](https://www.anthropic.com/discord) for tips and support
