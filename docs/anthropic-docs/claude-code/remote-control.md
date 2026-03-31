---
source: https://code.claude.com/docs/en/remote-control
scraped: 2026-03-23
section: claude-code
---

# Continue local sessions from any device with Remote Control

> Continue a local Claude Code session from your phone, tablet, or any browser using Remote Control. Works with claude.ai/code and the Claude mobile app.

Remote Control is available on all plans. On Team and Enterprise, it is off by default until an admin enables the Remote Control toggle in Claude Code admin settings.

Remote Control connects claude.ai/code or the Claude app to a Claude Code session running on your machine. When you start a Remote Control session on your machine, Claude keeps running locally the entire time, so nothing moves to the cloud.

With Remote Control you can:
- **Use your full local environment remotely**: your filesystem, MCP servers, tools, and project configuration all stay available
- **Work from both surfaces at once**: the conversation stays in sync across all connected devices
- **Survive interruptions**: if your laptop sleeps or your network drops, the session reconnects automatically

Unlike Claude Code on the web, which runs on cloud infrastructure, Remote Control sessions run directly on your machine.

Remote Control requires Claude Code v2.1.51 or later. Check your version with `claude --version`.

## Requirements

- **Subscription**: available on Pro, Max, Team, and Enterprise plans. API keys are not supported.
- **Authentication**: run `claude` and use `/login` to sign in through claude.ai
- **Workspace trust**: run `claude` in your project directory at least once to accept the workspace trust dialog

## Start a Remote Control session

### Server mode

Navigate to your project directory and run:
```bash
claude remote-control
```

The process stays running in your terminal in server mode, waiting for remote connections.

Available flags:

| Flag | Description |
|---|---|
| `--name "My Project"` | Set a custom session title visible in the session list |
| `--spawn <mode>` | How concurrent sessions are created: `same-dir` (default) or `worktree` |
| `--capacity <N>` | Maximum number of concurrent sessions. Default is 32. |
| `--verbose` | Show detailed connection and session logs. |
| `--sandbox` / `--no-sandbox` | Enable or disable sandboxing for filesystem and network isolation. |

### Interactive session

To start a normal interactive Claude Code session with Remote Control enabled:
```bash
claude --remote-control
```

Or with a name:
```bash
claude --remote-control "My Project"
```

### From an existing session

If you're already in a Claude Code session, use the `/remote-control` (or `/rc`) command:
```text
/remote-control
```

Or with a name:
```text
/remote-control My Project
```

## Connect from another device

Once a Remote Control session is active, you have a few ways to connect:

- **Open the session URL** in any browser to go directly to the session on claude.ai/code
- **Scan the QR code** shown alongside the session URL. With `claude remote-control`, press spacebar to toggle the QR code display.
- **Open claude.ai/code or the Claude app** and find the session by name in the session list

## Enable Remote Control for all sessions

To enable it automatically for every interactive session, run `/config` inside Claude Code and set **Enable Remote Control for all sessions** to `true`.

## Connection and security

Your local Claude Code session makes outbound HTTPS requests only and never opens inbound ports on your machine. All traffic travels through the Anthropic API over TLS. The connection uses multiple short-lived credentials, each scoped to a single purpose and expiring independently.

## Remote Control vs Claude Code on the web

| Feature | Remote Control | Claude Code on the web |
|---|---|---|
| Where code runs | Your machine | Anthropic-managed cloud infrastructure |
| Local MCP servers, tools | Available | Not available |
| Continues if you close laptop | No | Yes |

Use Remote Control when you're in the middle of local work and want to keep going from another device. Use Claude Code on the web when you want to kick off a task without any local setup or work on a repo you don't have cloned.

## Limitations

- **One remote session per interactive process**: outside of server mode, each Claude Code instance supports one remote session at a time
- **Terminal must stay open**: Remote Control runs as a local process. If you close the terminal, the session ends
- **Extended network outage**: if your machine is awake but unable to reach the network for more than roughly 10 minutes, the session times out

## Troubleshooting

### "Remote Control is not yet enabled for your account"

The eligibility check can fail with certain environment variables present:
- `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` or `DISABLE_TELEMETRY`: unset them and try again
- `CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`, or `CLAUDE_CODE_USE_FOUNDRY`: Remote Control requires claude.ai authentication

If none of these are set, run `/logout` then `/login` to refresh.

### "Remote Control is disabled by your organization's policy"

This error has three distinct causes. Run `/status` first to see which login method and subscription you're using:
- **You're authenticated with an API key or Console account**: Remote Control requires claude.ai OAuth. Run `/login` and choose the claude.ai option.
- **Your Team or Enterprise admin hasn't enabled it**: Remote Control is off by default on these plans. An admin can enable it at claude.ai/admin-settings/claude-code
- **The admin toggle is grayed out**: your organization has a data retention or compliance configuration that is incompatible with Remote Control

### "Remote credentials fetch failed"

Re-run with `--verbose` to see the full error:
```bash
claude remote-control --verbose
```

Common causes:
- Not signed in: run `claude` and use `/login` to authenticate
- Network or proxy issue: a firewall or proxy may be blocking the outbound HTTPS request
