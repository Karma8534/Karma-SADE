---
source: https://code.claude.com/docs/en/slack
scrape_date: 2026-03-23
section: claude-code
---

# Claude Code in Slack

> Delegate coding tasks directly from your Slack workspace

Claude Code in Slack brings the power of Claude Code directly into your Slack workspace. When you mention `@Claude` with a coding task, Claude automatically detects the intent and creates a Claude Code session on the web.

This integration is built on the existing Claude for Slack app but adds intelligent routing to Claude Code on the web for coding-related requests.

## Use cases

* **Bug investigation and fixes**: Ask Claude to investigate and fix bugs as soon as they're reported in Slack channels.
* **Quick code reviews and modifications**: Have Claude implement small features or refactor code based on team feedback.
* **Collaborative debugging**: When team discussions provide crucial context, Claude can use that information to inform its debugging approach.
* **Parallel task execution**: Kick off coding tasks in Slack while you continue other work, receiving notifications when complete.

## Prerequisites

| Requirement | Details |
| :--- | :--- |
| Claude Plan | Pro, Max, Teams, or Enterprise with Claude Code access (premium seats) |
| Claude Code on the web | Access to Claude Code on the web must be enabled |
| GitHub Account | Connected to Claude Code on the web with at least one repository authenticated |
| Slack Authentication | Your Slack account linked to your Claude account via the Claude app |

## Setting up Claude Code in Slack

**Step 1: Install the Claude App in Slack**

A workspace administrator must install the Claude app from the Slack App Marketplace. Visit the [Slack App Marketplace](https://slack.com/marketplace/A08SF47R6P4) and click "Add to Slack".

**Step 2: Connect your Claude account**

1. Open the Claude app in Slack
2. Navigate to the App Home tab
3. Click "Connect" to link your Slack account with your Claude account
4. Complete the authentication flow in your browser

**Step 3: Configure Claude Code on the web**

Visit [claude.ai/code](https://claude.ai/code), sign in with the same account, and connect your GitHub account.

**Step 4: Choose your routing mode**

| Mode | Behavior |
| :--- | :--- |
| **Code only** | Routes all @mentions to Claude Code sessions |
| **Code + Chat** | Intelligently routes between Claude Code and Claude Chat |

**Step 5: Add Claude to channels**

Type `/invite @Claude` in any channel where you want to use it. Claude only responds to @mentions in channels where it has been added.

## How it works

### Automatic detection

When you mention @Claude, it analyzes your message to determine if it's a coding task and routes accordingly.

Note: Claude Code in Slack only works in channels (public or private). It does not work in direct messages (DMs).

### Context gathering

**From threads**: Gathers context from all messages in the thread.

**From channels**: Looks at recent channel messages for relevant context.

### Session flow

1. You @mention Claude with a coding request
2. Claude analyzes and detects coding intent
3. A new Claude Code session is created on claude.ai/code
4. Claude posts status updates to your Slack thread
5. When finished, Claude @mentions you with a summary and action buttons
6. Click "View Session" to see the full transcript, or "Create PR" to open a pull request

## User interface elements

* **View Session**: Opens the full Claude Code session in your browser
* **Create PR**: Creates a pull request from the session's changes
* **Retry as Code**: Retry a chat response as a coding session
* **Change Repo**: Select a different repository if Claude chose incorrectly

## Access and permissions

### User-level access

| Access Type | Requirement |
| :--- | :--- |
| Claude Code Sessions | Each user runs sessions under their own Claude account |
| Usage & Rate Limits | Sessions count against the individual user's plan limits |
| Repository Access | Users can only access repositories they've personally connected |

### Channel-based access control

* **Invite required**: Type `/invite @Claude` in any channel
* **Private channel support**: Works in both public and private channels

## Best practices

* **Be specific**: Include file names, function names, or error messages
* **Provide context**: Mention the repository or project
* **Define success**: Explain what "done" looks like
* **Use threads**: Reply in threads so Claude can gather full context

### When to use Slack vs. web

**Use Slack when**: Context already exists in a Slack discussion, or you want to kick off a task asynchronously.

**Use the web directly when**: You need to upload files, want real-time interaction, or are working on longer tasks.

## Troubleshooting

### Sessions not starting

1. Verify your Claude account is connected in the Claude App Home
2. Check that you have Claude Code on the web access enabled
3. Ensure you have at least one GitHub repository connected

### Repository not showing

1. Connect the repository at [claude.ai/code](https://claude.ai/code)
2. Verify your GitHub permissions
3. Try disconnecting and reconnecting your GitHub account

### Authentication errors

1. Disconnect and reconnect your Claude account in the App Home
2. Ensure you're signed into the correct Claude account
3. Check that your Claude plan includes Claude Code access

## Current limitations

* **GitHub only**: Currently supports repositories on GitHub
* **One PR at a time**: Each session can create one pull request
* **Rate limits apply**: Sessions use your individual Claude plan's rate limits
* **Web access required**: Users must have Claude Code on the web access
