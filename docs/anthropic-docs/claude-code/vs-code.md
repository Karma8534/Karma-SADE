---
source: https://code.claude.com/docs/en/vs-code
scraped: 2026-03-23
section: claude-code
---

# Use Claude Code in VS Code

> Install and configure the Claude Code extension for VS Code. Get AI coding assistance with inline diffs, @-mentions, plan review, and keyboard shortcuts.

The VS Code extension provides a native graphical interface for Claude Code, integrated directly into your IDE. With the extension, you can review and edit Claude's plans before accepting them, auto-accept edits as they're made, @-mention files with specific line ranges, access conversation history, and open multiple conversations in separate tabs.

## Prerequisites

- VS Code 1.98.0 or higher
- An Anthropic account

## Install the extension

Click the link for your IDE to install directly:
- [Install for VS Code](vscode:extension/anthropic.claude-code)
- [Install for Cursor](cursor:extension/anthropic.claude-code)

Or in VS Code, press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows/Linux) to open the Extensions view, search for "Claude Code", and click **Install**.

## Get started

**Open the Claude Code panel**: Click the Spark icon in the **Editor Toolbar** (top-right corner of the editor). The icon only appears when you have a file open.

Other ways to open Claude Code:
- **Activity Bar**: click the Spark icon in the left sidebar
- **Command Palette**: `Cmd+Shift+P`, type "Claude Code", select "Open in New Tab"
- **Status Bar**: click **✱ Claude Code** in the bottom-right corner

**Send a prompt**: Ask Claude to help with your code. Claude automatically sees your selected text. Press `Option+K` (Mac) / `Alt+K` (Windows/Linux) to also insert an @-mention reference.

**Review changes**: When Claude wants to edit a file, it shows a side-by-side comparison of the original and proposed changes, then asks for permission.

## Use the prompt box

- **Permission modes**: click the mode indicator at the bottom of the prompt box to switch modes: normal, Plan, or auto-accept
- **Command menu**: click `/` or type `/` to open the command menu
- **Context indicator**: shows how much of Claude's context window you're using
- **Extended thinking**: toggle via the command menu (`/`)
- **Multi-line input**: press `Shift+Enter` to add a new line

### Reference files and folders

Use @-mentions to give Claude context:
```text
> Explain the logic in @auth (fuzzy matches auth.js, AuthService.ts, etc.)
> What's in @src/components/ (include a trailing slash for folders)
```

Press `Option+K` (Mac) / `Alt+K` (Windows/Linux) to insert an @-mention with the file path and line numbers.

### Resume past conversations

Click the dropdown at the top of the Claude Code panel to access your conversation history. You can search by keyword or browse by time.

### Resume remote sessions from Claude.ai

1. Open **Past Conversations**
2. Select the **Remote** tab
3. Browse or search your remote sessions and click to resume

## Customize your workflow

### Choose where Claude lives

Drag the Claude panel to:
- **Secondary sidebar** (right side): keeps Claude visible while you code
- **Primary sidebar** (left sidebar)
- **Editor area**: opens Claude as a tab alongside your files

### Run multiple conversations

Use **Open in New Tab** or **Open in New Window** from the Command Palette to start additional conversations.

### Switch to terminal mode

Open the [Use Terminal setting](vscode://settings/claudeCode.useTerminal) and check the box, or open VS Code settings and go to Extensions → Claude Code → check **Use Terminal**.

## VS Code commands and shortcuts

| Command | Shortcut | Description |
|---|---|---|
| Focus Input | `Cmd+Esc` (Mac) / `Ctrl+Esc` (Windows/Linux) | Toggle focus between editor and Claude |
| Open in Side Bar | - | Open Claude in the left sidebar |
| Open in New Tab | `Cmd+Shift+Esc` (Mac) / `Ctrl+Shift+Esc` (Windows/Linux) | Open a new conversation as an editor tab |
| Open in New Window | - | Open a new conversation in a separate window |
| New Conversation | `Cmd+N` (Mac) / `Ctrl+N` (Windows/Linux) | Start a new conversation |
| Insert @-Mention Reference | `Option+K` (Mac) / `Alt+K` (Windows/Linux) | Insert a reference to the current file and selection |
| Show Logs | - | View extension debug logs |
| Logout | - | Sign out of your Anthropic account |

## Configure settings

### Extension settings

| Setting | Default | Description |
|---|---|---|
| `selectedModel` | `default` | Model for new conversations |
| `useTerminal` | `false` | Launch Claude in terminal mode instead of graphical panel |
| `initialPermissionMode` | `default` | Controls approval prompts: `default`, `plan`, `acceptEdits`, or `bypassPermissions` |
| `preferredLocation` | `panel` | Where Claude opens: `sidebar` or `panel` |
| `autosave` | `true` | Auto-save files before Claude reads or writes them |
| `useCtrlEnterToSend` | `false` | Use Ctrl/Cmd+Enter instead of Enter to send prompts |
| `enableNewConversationShortcut` | `true` | Enable Cmd/Ctrl+N to start a new conversation |
| `hideOnboarding` | `false` | Hide the onboarding checklist |
| `respectGitIgnore` | `true` | Exclude .gitignore patterns from file searches |
| `disableLoginPrompt` | `false` | Skip authentication prompts (for third-party provider setups) |
| `allowDangerouslySkipPermissions` | `false` | Bypass permission prompts. Use with extreme caution. |

## VS Code extension vs. Claude Code CLI

| Feature | CLI | VS Code Extension |
|---|---|---|
| Commands and skills | All | Subset (type `/` to see available) |
| MCP server config | Yes | Partial |
| Checkpoints | Yes | Yes |
| `!` bash shortcut | Yes | No |
| Tab completion | Yes | No |

### Rewind with checkpoints

The VS Code extension supports checkpoints. Hover over any message to reveal the rewind button, then choose from three options:
- **Fork conversation from here**: start a new conversation branch from this message
- **Rewind code to here**: revert file changes back to this point
- **Fork conversation and rewind code**: start a new conversation branch and revert file changes

### Run CLI in VS Code

Open the integrated terminal (`` Ctrl+` `` on Windows/Linux or `` Cmd+` `` on Mac) and run `claude`. The CLI automatically integrates with your IDE.

### Include terminal output in prompts

Reference terminal output using `@terminal:name` where `name` is the terminal's title.

## Connect to external tools with MCP

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

Once configured, ask Claude to use the tools. To manage MCP servers without leaving VS Code, type `/mcp` in the chat panel.

## Work with git

### Use git worktrees for parallel tasks

```bash
claude --worktree feature-auth
```

## Use third-party providers

1. Open the [Disable Login Prompt setting](vscode://settings/claudeCode.disableLoginPrompt) and check the box
2. Follow the setup guide for your provider:
   - Claude Code on Amazon Bedrock
   - Claude Code on Google Vertex AI
   - Claude Code on Microsoft Foundry

## Fix common issues

### Extension won't install

- Ensure you have a compatible version of VS Code (1.98.0 or later)
- Try installing directly from the VS Code Marketplace

### Spark icon not visible

The Spark icon appears in the **Editor Toolbar** when you have a file open. If you don't see it:
1. **Open a file**: The icon requires a file to be open
2. **Check VS Code version**: Requires 1.98.0 or higher
3. **Restart VS Code**: Run "Developer: Reload Window" from the Command Palette
4. **Disable conflicting extensions**: Temporarily disable other AI extensions

Alternatively, click "✱ Claude Code" in the **Status Bar** (bottom-right corner).

### Claude Code never responds

1. Check your internet connection
2. Start a new conversation
3. Try the CLI: run `claude` from the terminal to see more detailed error messages

## Uninstall the extension

1. Open the Extensions view
2. Search for "Claude Code"
3. Click **Uninstall**

To also remove extension data:
```bash
rm -rf ~/.vscode/globalStorage/anthropic.claude-code
```
