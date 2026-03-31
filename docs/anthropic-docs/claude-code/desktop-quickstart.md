---
source: https://code.claude.com/docs/en/desktop-quickstart
scraped: 2026-03-23
section: claude-code
---

# Get started with the desktop app

> Install Claude Code on desktop and start your first coding session

The desktop app gives you Claude Code with a graphical interface: visual diff review, live app preview, GitHub PR monitoring with auto-merge, parallel sessions with Git worktree isolation, scheduled tasks, and the ability to run tasks remotely. No terminal required.

The desktop app has three tabs:

- **Chat**: General conversation with no file access, similar to claude.ai.
- **Cowork**: An autonomous background agent that works on tasks in a cloud VM with its own environment.
- **Code**: An interactive coding assistant with direct access to your local files.

Claude Code requires a Pro, Max, Teams, or Enterprise subscription.

## Install

1. **Download the app**:
   - [macOS](https://claude.ai/api/desktop/darwin/universal/dmg/latest/redirect) — Universal build for Intel and Apple Silicon
   - [Windows](https://claude.ai/api/desktop/win32/x64/exe/latest/redirect) — For x64 processors
   - [Windows ARM64](https://claude.ai/api/desktop/win32/arm64/exe/latest/redirect)
   - Linux is not currently supported.

2. **Sign in**: Launch Claude from your Applications folder (macOS) or Start menu (Windows). Sign in with your Anthropic account.

3. **Open the Code tab**: Click the **Code** tab at the top center.

The desktop app includes Claude Code. You don't need to install Node.js or the CLI separately.

## Start your first session

### Choose an environment and folder

Select **Local** to run Claude on your machine using your files directly. Click **Select folder** and choose your project directory.

On Windows, Git must be installed for local sessions to work. Most Macs include Git by default.

You can also select:
- **Remote**: Run sessions on Anthropic's cloud infrastructure that continue even if you close the app.
- **SSH**: Connect to a remote machine over SSH.

### Choose a model

Select a model from the dropdown next to the send button. You cannot change the model after the session starts.

### Tell Claude what to do

Type what you want Claude to do:

- `Find a TODO comment and fix it`
- `Add tests for the main function`
- `Create a CLAUDE.md with instructions for this codebase`

### Review and accept changes

By default, the Code tab starts in **Ask permissions mode**, where Claude proposes changes and waits for your approval before applying them. You'll see:

1. A diff view showing exactly what will change in each file
2. Accept/Reject buttons to approve or decline each change
3. Real-time updates as Claude works through your request

If you reject a change, Claude will ask how you'd like to proceed differently. Your files aren't modified until you accept.

## Now what?

**Interrupt and steer**: You can interrupt Claude at any point. If it's going down the wrong path, click the stop button or type your correction and press **Enter**.

**Give Claude more context**: Type `@filename` in the prompt box to pull a specific file into the conversation, or attach images and PDFs using the attachment button.

**Use skills for repeatable tasks**: Type `/` or click **+** → **Slash commands** to browse built-in commands and custom skills.

**Review changes before committing**: After Claude edits files, a `+12 -1` indicator appears. Click it to open the diff view, review modifications file by file, and comment on specific lines.

**Adjust how much control you have**: Use the permission mode selector to switch between:
- **Ask permissions** (default): requires approval before every edit
- **Auto accept edits**: auto-accepts file edits for faster iteration
- **Plan mode**: maps out an approach without touching any files

**Add plugins**: Click the **+** button next to the prompt box and select **Plugins** to browse and install plugins.

**Preview your app**: Click the **Preview** dropdown to run your dev server directly in the desktop.

**Track your pull request**: After opening a PR, Claude Code monitors CI check results and can automatically fix failures or merge the PR once all checks pass.

**Put Claude on a schedule**: Set up scheduled tasks to run Claude automatically on a recurring basis.

**Scale up when you're ready**: Open parallel sessions from the sidebar to work on multiple tasks at once, each in its own Git worktree.

## Coming from the CLI?

Desktop runs the same engine as the CLI with a graphical interface. You can run both simultaneously on the same project. They share configuration (CLAUDE.md files, MCP servers, hooks, skills, and settings).

## What's next

- Use Claude Code Desktop: permission modes, parallel sessions, diff view, connectors, and enterprise configuration
- Troubleshooting: solutions to common errors and setup issues
- Best practices: tips for writing effective prompts
- Common workflows: tutorials for debugging, refactoring, testing, and more
