---
source: https://code.claude.com/docs/en/changelog
scraped: 2026-03-23
section: claude-code
---

# Changelog

> Release notes for Claude Code, including new features, improvements, and bug fixes by version.

This page is generated from the [CHANGELOG.md on GitHub](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md).

Run `claude --version` to check your installed version.

## Version 2.1.81 (March 20, 2026)

- Added `--bare` flag for scripted `-p` calls — skips hooks, LSP, plugin sync, and skill directory walks; requires `ANTHROPIC_API_KEY` or an `apiKeyHelper` via `--settings` (OAuth and keychain auth disabled); auto-memory fully disabled
- Added `--channels` permission relay — channel servers that declare the permission capability can forward tool approval prompts to your phone
- Fixed multiple concurrent Claude Code sessions requiring repeated re-authentication when one session refreshes its OAuth token
- Fixed voice mode silently swallowing retry failures and showing a misleading "check your network" message instead of the actual error
- Fixed voice mode audio not recovering when the server silently drops the WebSocket connection
- Fixed `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` not suppressing the structured-outputs beta header, causing 400 errors on proxy gateways forwarding to Vertex/Bedrock
- Fixed `--channels` bypass for Team/Enterprise orgs with no other managed settings configured
- Fixed a crash on Node.js 18
- Fixed unnecessary permission prompts for Bash commands containing dashes in strings
- Fixed plugin hooks blocking prompt submission when the plugin directory is deleted mid-session
- Fixed a race condition where background agent task output could hang indefinitely when the task completed between polling intervals
- Resuming a session that was in a worktree now switches back to that worktree
- Fixed `/btw` not including pasted text when used during an active response
- Fixed a race where fast Cmd+Tab followed by paste could beat the clipboard copy under tmux
- Fixed terminal tab title not updating with an auto-generated session description
- Fixed invisible hook attachments inflating the message count in transcript mode
- Fixed Remote Control sessions showing a generic title instead of deriving from the first prompt
- Fixed `/rename` not syncing the title for Remote Control sessions
- Fixed Remote Control `/exit` not reliably archiving the session
- Improved MCP read/search tool calls to collapse into a single "Queried `{server}`" line (expand with Ctrl+O)
- Improved `!` bash mode discoverability — Claude now suggests it when you need to run an interactive command
- Improved plugin freshness — ref-tracked plugins now re-clone on every load to pick up upstream changes
- Improved Remote Control session titles to refresh after your third message
- Updated MCP OAuth to support Client ID Metadata Document (CIMD / SEP-991) for servers without Dynamic Client Registration
- Changed plan mode to hide the "clear context" option by default (restore with `"showClearContextOnPlanAccept": true`)
- Disabled line-by-line response streaming on Windows (including WSL in Windows Terminal) due to rendering issues
- [VSCode] Fixed Windows PATH inheritance for Bash tool when using Git Bash (regression in v2.1.78)

## Version 2.1.80 (March 19, 2026)

- Added `rate_limits` field to statusline scripts for displaying Claude.ai rate limit usage (5-hour and 7-day windows with `used_percentage` and `resets_at`)
- Added `source: 'settings'` plugin marketplace source — declare plugin entries inline in settings.json
- Added CLI tool usage detection to plugin tips, in addition to file pattern matching
- Added `effort` frontmatter support for skills and slash commands to override the model effort level when invoked
- Added `--channels` (research preview) — allow MCP servers to push messages into your session
- Fixed `--resume` dropping parallel tool results — sessions with parallel tool calls now restore all tool_use/tool_result pairs instead of showing `[Tool result missing]` placeholders
- Fixed voice mode WebSocket failures caused by Cloudflare bot detection on non-browser TLS fingerprints
- Fixed 400 errors when using fine-grained tool streaming through API proxies, Bedrock, or Vertex
- Fixed `/remote-control` appearing for gateway and third-party provider deployments where it cannot function
- Fixed `/sandbox` tab switching not responding to Tab or arrow keys
- Improved responsiveness of `@` file autocomplete in large git repositories
- Improved `/effort` to show what auto currently resolves to, matching the status bar indicator
- Improved `/permissions` — Tab and arrow keys now switch tabs from within a list
- Improved background tasks panel — left arrow now closes from the list view
- Simplified plugin install tips to use a single `/plugin install` command instead of a two-step flow
- Reduced memory usage on startup in large repositories (~80 MB saved on 250k-file repos)
- Fixed managed settings (`enabledPlugins`, `permissions.defaultMode`, policy-set env vars) not being applied at startup when `remote-settings.json` was cached from a prior session

## Version 2.1.79 (March 18, 2026)

- Added `--console` flag to `claude auth login` for Anthropic Console (API billing) authentication
- Added "Show turn duration" toggle to the `/config` menu
- Fixed `claude -p` hanging when spawned as a subprocess without explicit stdin
- Fixed Ctrl+C not working in `-p` (print) mode
- Fixed `/btw` returning the main agent's output instead of answering the side question when triggered during streaming
- Fixed voice mode not activating correctly on startup when `voiceEnabled: true` is set
- Fixed left/right arrow tab navigation in `/permissions`
- Fixed `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` not preventing terminal title from being set on startup
- Fixed custom status line showing nothing when workspace trust is blocking it
- Fixed enterprise users being unable to retry on rate limit (429) errors
- Fixed `SessionEnd` hooks not firing when using interactive `/resume` to switch sessions
- Improved startup memory usage by ~18MB across all scenarios
- Improved non-streaming API fallback with a 2-minute per-attempt timeout
- `CLAUDE_CODE_PLUGIN_SEED_DIR` now supports multiple seed directories separated by the platform path delimiter
- [VSCode] Added `/remote-control` — bridge your session to claude.ai/code to continue from a browser or phone
- [VSCode] Session tabs now get AI-generated titles based on your first message
- [VSCode] Fixed the thinking pill showing "Thinking" instead of "Thought for Ns" after a response completes

## Version 2.1.78 (March 17, 2026)

- Added `StopFailure` hook event that fires when the turn ends due to an API error (rate limit, auth failure, etc.)
- Added `${CLAUDE_PLUGIN_DATA}` variable for plugin persistent state that survives plugin updates
- Added `effort`, `maxTurns`, and `disallowedTools` frontmatter support for plugin-shipped agents
- Terminal notifications (iTerm2/Kitty/Ghostty popups, progress bar) now reach the outer terminal when running inside tmux with `set -g allow-passthrough on`
- Response text now streams line-by-line as it's generated
- Fixed `git log HEAD` failing with "ambiguous argument" inside sandboxed Bash on Linux
- Fixed `cc log` and `--resume` silently truncating conversation history on large sessions (>5 MB) that used subagents
- Fixed infinite loop when API errors triggered stop hooks that re-fed blocking errors to the model
- Fixed `deny: ["mcp__servername"]` permission rules not removing MCP server tools before sending to the model
- Fixed `sandbox.filesystem.allowWrite` not working with absolute paths
- **Security:** Fixed silent sandbox disable when `sandbox.enabled: true` is set but dependencies are missing — now shows a visible startup warning
- Fixed `.git`, `.claude`, and other protected directories being writable without a prompt in `bypassPermissions` mode
- Fixed ctrl+u in normal mode scrolling instead of readline kill-line
- Fixed voice mode modifier-combo push-to-talk keybindings requiring a hold instead of activating immediately
- Fixed voice mode not working on WSL2 with WSLg (Windows 11)
- Fixed `--worktree` flag not loading skills and hooks from the worktree directory
- Fixed `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS` and `includeGitInstructions` setting not suppressing the git status section in the system prompt
- Fixed Bash tool not finding Homebrew and other PATH-dependent binaries when VS Code is launched from Dock/Spotlight
- Fixed washed-out Claude orange color in VS Code/Cursor/code-server terminals that don't advertise truecolor support
- Added `ANTHROPIC_CUSTOM_MODEL_OPTION` env var to add a custom entry to the `/model` picker
- Fixed `ANTHROPIC_BETAS` environment variable being silently ignored when using Haiku models
- Fixed queued prompts being concatenated without a newline separator
- Improved memory usage and startup time when resuming large sessions
- [VSCode] Fixed a brief flash of the login screen when opening the sidebar while already authenticated
- [VSCode] Fixed "API Error: Rate limit reached" when selecting Opus

---

For earlier versions, see the [full CHANGELOG.md on GitHub](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md).
