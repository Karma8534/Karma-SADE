---
source: https://code.claude.com/docs/en/desktop
scrape_date: 2026-03-23
section: claude-code
---

# Use Claude Code Desktop

> Get more out of Claude Code Desktop: parallel sessions with Git isolation, visual diff review, app previews, PR monitoring, permission modes, connectors, and enterprise configuration.

The Code tab within the Claude Desktop app lets you use Claude Code through a graphical interface instead of the terminal.

Desktop adds these capabilities on top of the standard Claude Code experience:
- Visual diff review with inline comments
- Live app preview with dev servers
- GitHub PR monitoring with auto-fix and auto-merge
- Parallel sessions with automatic Git worktree isolation
- Scheduled tasks that run Claude on a recurring schedule
- Connectors for GitHub, Slack, Linear, and more
- Local, SSH, and cloud environments

New to Desktop? Start with [Get started](/en/desktop-quickstart) to install the app and make your first edit.

## Start a session

Before you send your first message, configure:
- **Environment**: Local, Remote, or SSH connection
- **Project folder**: select the folder or repository Claude works in
- **Model**: pick a model from the dropdown (locked once the session starts)
- **Permission mode**: choose how much autonomy Claude has

## Work with code

### Use the prompt box

Type what you want Claude to do and press Enter. You can interrupt Claude at any point by clicking the stop button or typing a correction.

The **+** button gives you access to file attachments, skills, connectors, and plugins.

### Add files and context to prompts

- **@mention files**: type `@` followed by a filename to add a file to the conversation context
- **Attach files**: attach images, PDFs, and other files using the attachment button, or drag and drop

### Choose a permission mode

| Mode | Settings key | Behavior |
| :--- | :--- | :--- |
| **Ask permissions** | `default` | Claude asks before editing files or running commands. Recommended for new users. |
| **Auto accept edits** | `acceptEdits` | Claude auto-accepts file edits but still asks before running terminal commands. |
| **Plan mode** | `plan` | Claude analyzes code and creates a plan without modifying files or running commands. |
| **Bypass permissions** | `bypassPermissions` | Claude runs without permission prompts. Only use in sandboxed containers or VMs. |

Best practice: Start complex tasks in Plan mode, then switch to Auto accept edits or Ask permissions to execute.

### Preview your app

Claude can start a dev server and open an embedded browser to verify changes. From the preview panel you can:
- Interact with your running app directly
- Watch Claude auto-verify changes (screenshots, DOM inspection, form filling)
- Start or stop servers from the **Preview** dropdown
- Persist cookies and local storage across server restarts with **Persist sessions**

### Review changes with diff view

When Claude changes files, a diff stats indicator appears (e.g., `+12 -1`). Click it to open the diff viewer. Click any line to add a comment. Submit all comments with Cmd+Enter (macOS) or Ctrl+Enter (Windows).

### Review your code

Click **Review code** in the diff view toolbar to ask Claude to evaluate the changes. The review focuses on compile errors, definite logic errors, security vulnerabilities, and obvious bugs.

### Monitor pull request status

After opening a pull request, a CI status bar appears with:
- **Auto-fix**: Claude automatically attempts to fix failing CI checks
- **Auto-merge**: Claude merges the PR once all checks pass (requires GitHub repo to have auto-merge enabled)

Note: PR monitoring requires the GitHub CLI (`gh`) to be installed and authenticated.

## Manage sessions

### Work in parallel with sessions

Click **+ New session** in the sidebar. For Git repositories, each session gets its own isolated copy using Git worktrees, stored in `<project-root>/.claude/worktrees/`.

### Run long-running tasks remotely

Select **Remote** when starting a session for tasks that continue even if you close the app. You can monitor them from [claude.ai/code](https://claude.ai/code) or the Claude iOS app. Remote sessions also support multiple repositories.

### Continue in another surface

The **Continue in** menu lets you move your session to:
- **Claude Code on the Web**: sends your local session to continue running remotely
- **Your IDE**: opens your project in a supported IDE

## Extend Claude Code

### Connect external tools

Click the **+** button and select **Connectors** to add integrations like Google Calendar, Slack, GitHub, Linear, Notion, and more. Connectors are MCP servers with a graphical setup flow.

### Use skills

Type `/` in the prompt box or click **+** → **Slash commands** to browse skills including built-in commands, custom skills, project skills, and plugin skills.

### Install plugins

Click **+** → **Plugins** to browse and install plugins from configured marketplaces. Click **Manage plugins** to enable, disable, or uninstall.

### Configure preview servers

Claude stores configuration in `.claude/launch.json`:

```json
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "my-app",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "port": 3000
    }
  ]
}
```

Configuration fields:
| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | string | Unique identifier for this server |
| `runtimeExecutable` | string | Command to run (npm, yarn, node) |
| `runtimeArgs` | string[] | Arguments passed to runtimeExecutable |
| `port` | number | Port your server listens on (default: 3000) |
| `cwd` | string | Working directory relative to project root |
| `env` | object | Additional environment variables |
| `autoPort` | boolean | How to handle port conflicts |
| `program` | string | A script to run with node directly |
| `args` | string[] | Arguments passed to program |

#### Auto-verify changes

When `autoVerify` is enabled (default), Claude automatically verifies code changes after editing. Disable per-project:

```json
{
  "version": "0.0.1",
  "autoVerify": false,
  "configurations": [...]
}
```

## Schedule recurring tasks

Scheduled tasks start a new local session automatically. Create from the **Schedule** sidebar, then configure:
- **Name**: unique identifier
- **Description**: short summary
- **Prompt**: instructions sent to Claude
- **Frequency**: Manual, Hourly, Daily, Weekdays, or Weekly

The desktop app must be open for tasks to fire. Enable **Keep computer awake** in Settings to prevent missed runs.

### How scheduled tasks run

Each task gets a fixed delay of up to 10 minutes after the scheduled time to stagger API traffic. If your computer was asleep, one catch-up run fires on wake for the most recently missed time.

## Environment configuration

### Local sessions

Inherit environment variables from your shell. Set additional variables in `~/.zshrc` or `~/.bashrc` and restart the app.

Extended thinking is enabled by default. Disable with `MAX_THINKING_TOKENS=0`.

### Remote sessions

Continue in the background even if you close the app. Create custom cloud environments with different network access levels from the environment dropdown.

### SSH sessions

Run Claude Code on a remote machine. Add via the environment dropdown → **+ Add SSH connection**. Requires Claude Code installed on the remote machine.

## Enterprise configuration

### Admin console controls

Configure at [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code):
- Code in the desktop
- Code in the web
- Remote Control
- Disable Bypass permissions mode

### Managed settings

| Key | Description |
| :--- | :--- |
| `disableBypassPermissionsMode` | Set to `"disable"` to prevent bypass permissions mode |

### Authentication and SSO

Enterprise organizations can require SSO. See [Setting up SSO](https://support.claude.com/en/articles/13132885-setting-up-single-sign-on-sso).

### Deployment

- **macOS**: distribute via MDM using the `.dmg` installer
- **Windows**: deploy via MSIX package or `.exe` installer

## Coming from the CLI?

Desktop runs the same underlying engine. To move a CLI session into Desktop, run `/desktop` in the terminal (macOS and Windows only).

### Shared configuration

- **CLAUDE.md** files used by both
- **MCP servers** configured in `~/.claude.json` or `.mcp.json` work in both
- **Hooks** and **skills** defined in settings apply to both
- **Settings** in `~/.claude/settings.json` are shared

### What's not available in Desktop

- **Third-party providers**: use the CLI for Bedrock, Vertex, or Foundry
- **Linux**: Desktop is macOS and Windows only
- **Inline code suggestions**
- **Agent teams**: use CLI or Agent SDK
- **Scripting and automation**: use `--print`, Agent SDK

## Troubleshooting

### Check your version

- macOS: Claude menu → About Claude
- Windows: Help → About

### 403 or authentication errors in the Code tab

1. Sign out and back in
2. Verify active paid subscription (Pro, Max, Teams, or Enterprise)
3. Quit and reopen the app completely

### Session not finding installed tools

Verify tools work in your regular terminal, check PATH setup in shell profile, and restart the desktop app.

### Git errors on Windows

Install [Git for Windows](https://git-scm.com/downloads/win) and restart the app.

### "Branch doesn't exist yet"

```bash
git fetch origin <branch-name>
git checkout <branch-name>
```
