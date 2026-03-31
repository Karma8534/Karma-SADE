---
source: https://code.claude.com/docs/en/channels
scraped: 2026-03-23
section: claude-code
---

# Push events into a running session with channels

> Use channels to push messages, alerts, and webhooks into your Claude Code session from an MCP server. Forward CI results, chat messages, and monitoring events so Claude can react while you're away.

Channels are in research preview and require Claude Code v2.1.80 or later. They require claude.ai login. Team and Enterprise organizations must explicitly enable them.

A channel is an MCP server that pushes events into your running Claude Code session, so Claude can react to things that happen while you're not at the terminal. Channels can be two-way: Claude reads the event and replies back through the same channel, like a chat bridge.

Unlike integrations that spawn a fresh cloud session or wait to be polled, the event arrives in the session you already have open.

You install a channel as a plugin and configure it with your own credentials. Telegram and Discord are included in the research preview.

## Supported channels

### Telegram

1. Open [BotFather](https://t.me/BotFather) in Telegram and send `/newbot`. Copy the token BotFather returns.
2. Install the plugin:
   ```
   /plugin install telegram@claude-plugins-official
   ```
   After installing, run `/reload-plugins` to activate the plugin's configure command.
3. Configure your token:
   ```
   /telegram:configure <token>
   ```
4. Restart with channels enabled:
   ```bash
   claude --channels plugin:telegram@claude-plugins-official
   ```
5. Open Telegram and send any message to your bot. The bot replies with a pairing code.
6. In Claude Code, run:
   ```
   /telegram:access pair <code>
   ```
   Then lock down access:
   ```
   /telegram:access policy allowlist
   ```

### Discord

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications), click **New Application**, and name it. In the **Bot** section, create a username, then click **Reset Token** and copy the token.
2. Enable **Message Content Intent** in the bot's settings.
3. Invite the bot to your server via **OAuth2 > URL Generator** with the `bot` scope and these permissions: View Channels, Send Messages, Send Messages in Threads, Read Message History, Attach Files, Add Reactions.
4. Install the plugin:
   ```
   /plugin install discord@claude-plugins-official
   ```
5. Configure your token:
   ```
   /discord:configure <token>
   ```
6. Restart with channels enabled:
   ```bash
   claude --channels plugin:discord@claude-plugins-official
   ```
7. DM your bot on Discord. The bot replies with a pairing code.
8. In Claude Code, run:
   ```
   /discord:access pair <code>
   ```
   Then lock down access:
   ```
   /discord:access policy allowlist
   ```

## Quickstart with fakechat

Fakechat is a demo channel that runs a chat UI on localhost, with nothing to authenticate.

Requirements:
- Claude Code installed and authenticated with a claude.ai account
- [Bun](https://bun.sh) installed
- Team/Enterprise users: your organization admin must enable channels

1. Install the fakechat channel plugin:
   ```text
   /plugin install fakechat@claude-plugins-official
   ```

2. Restart with the channel enabled:
   ```bash
   claude --channels plugin:fakechat@claude-plugins-official
   ```

3. Open the fakechat UI at [http://localhost:8787](http://localhost:8787) and type a message:
   ```text
   hey, what's in my working directory?
   ```

## Security

Every approved channel plugin maintains a sender allowlist: only IDs you've added can push messages.

The allowlist also gates permission relay if the channel declares it. Anyone who can reply through the channel can approve or deny tool use in your session, so only allowlist senders you trust.

## Enterprise controls

Channels are controlled by the `channelsEnabled` setting in managed settings.

| Plan type | Default behavior |
|---|---|
| Pro / Max, no organization | Channels available; users opt in per session with `--channels` |
| Team / Enterprise | Channels disabled until an admin explicitly enables them |

Admins can enable channels from **claude.ai → Admin settings → Claude Code → Channels**, or by setting `channelsEnabled` to `true` in managed settings.

## Research preview

During the preview, `--channels` only accepts plugins from an Anthropic-maintained allowlist. The channel plugins in [claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins) are the approved set.

To test a channel you're building, use `--dangerously-load-development-channels`.

## How channels compare

| Feature | What it does | Good for |
|---|---|---|
| Claude Code on the web | Runs tasks in a fresh cloud sandbox | Delegating self-contained async work |
| Claude in Slack | Spawns a web session from an `@Claude` mention | Starting tasks from team conversation |
| Standard MCP server | Claude queries it during a task | Giving Claude on-demand access to read a system |
| Remote Control | You drive your local session from claude.ai or the Claude app | Steering an in-progress session while away |

Channels fill the gap by pushing events from non-Claude sources into your already-running local session.
