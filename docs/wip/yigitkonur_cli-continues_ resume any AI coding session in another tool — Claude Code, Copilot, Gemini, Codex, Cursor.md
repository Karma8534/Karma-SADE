# yigitkonur_cli-continues_ resume any AI coding session in another tool — Claude Code, Copilot, Gemini, Codex, Cursor

*Converted from: yigitkonur_cli-continues_ resume any AI coding session in another tool — Claude Code, Copilot, Gemini, Codex, Cursor.PDF*



---
*Page 1*


cli-continues
Code Issues 3 More
Watch 3
resume any AI coding session in another tool — Claude Code, Copilot, Gemini, Codex, Cursor
MIT license
497 stars 44 forks 3 watching 3Branches 8Tags Activity
Public repository
main 3Branches 8Tags Go to file t Go to file Add file Code
github-actions[bot] chore: release v3.0.0 [skip publish] d0babe7 · yesterday
.github/workflows fix(ci): respect major version bumps in beta publi… 2 days ago
src feat: add registry-driven cross-tool flag forwarding 2 days ago
.gitignore feat!: v3.0.0 major refactor — typed schemas, libr… 2 days ago
CHANGELOG.md chore: bump to v2.7.0, update docs for Droid sup… 3 days ago
CLAUDE.md refactor: introduce adapter registry pattern for ex… 2 days ago
LICENSE continues v2.6.5 — resume AI coding sessions a… 3 days ago
README.md feat: add registry-driven cross-tool flag forwarding 2 days ago
biome.json feat!: v3.0.0 major refactor — typed schemas, libr… 2 days ago
demo.mp4 continues v2.6.5 — resume AI coding sessions a… 3 days ago
package.json chore: release v3.0.0 [skip publish] yesterday
pnpm-lock.yaml feat!: v3.0.0 major refactor — typed schemas, libr… 2 days ago
tsconfig.json continues v2.6.5 — resume AI coding sessions a… 3 days ago
vitest.config.ts continues v2.6.5 — resume AI coding sessions a… 3 days ago
continues
Pick up where you left off — seamlessly continue AI coding sessions across Claude, Copilot, Gemini, Codex, OpenCode, Droid & Cursor.
npx continues
demo.mp4


---
*Page 2*


0:00
nnppmm vv33..00..00 LLiicceennssee MMIITT
Why?
Have you ever hit your daily limit on Claude Code mid-debug? Or burned through your Gemini quota right when things were getting interesting?
You've built up 30 messages of context — file changes, architecture decisions, debugging history. And now you either wait hours for the limit to
reset, or start fresh in another tool and explain everything from scratch.
continues reads your session from any supported tool, extracts the context, and injects it into whichever tool you switch to. Your
conversation history, file changes, and working directory all come along.
Features
🔄 Cross-tool handoff — Move sessions between Claude, Copilot, Gemini, Codex, OpenCode, Droid & Cursor
🔍 Auto-discovery — Scans all 7 tools' session directories automatically
🛠 Tool activity extraction — Parses shell commands, file edits, MCP tool calls, patches, and more from every session
🧠 AI reasoning capture — Extracts thinking blocks, agent reasoning, and model info for richer handoffs
📋 Interactive picker — Browse, filter, and select sessions with a beautiful TUI
⚡ Quick resume — / — one command, done
continues claude continues codex 3
🖥 Scriptable — JSON/JSONL output, TTY detection, non-interactive mode
📊 Session stats — to see everything at a glance
continues scan
Installation
No install needed — just run:
npx continues
Or install globally:


---
*Page 3*


npm install -g continues
Both continues and cont work as commands after global install.
Quick Start
# Interactive session picker — browse, pick, switch tools
continues
# List all sessions across every tool
continues list
# Grab a Claude session and continue it in Gemini
continues resume abc123 --in gemini
# Pass launch flags to the destination tool during cross-tool handoff
continues resume abc123 --in codex --yolo --search --add-dir /tmp
# Quick-resume your latest Claude session (native resume)
continues claude
Usage
Interactive Mode (default)
Just run . It walks you through:
continues
1. Filter by directory, CLI tool, or browse all
2. Pick a session
3. Choose which CLI tool to continue in (only shows other tools — the whole point is switching)
When you run from a project directory, it prioritizes sessions from that directory first:
continues
┌ continues — pick up where you left off
│
│ ▸ 12 sessions found in current directory
│ Found 1042 sessions across 7 CLI tools
│ claude: 723 codex: 72 cursor: 68 copilot: 39 opencode: 38 droid: 71 gemini: 31
│
◆ Filter sessions
│ ● This directory (12 sessions)
│ ○ All CLI tools (904 sessions)
│ ○ Claude (723)
│ ○ Codex (72)
│ ○ Copilot (39)
│ ○ Droid (71)
│ ○ Opencode (38)
│ ○ Gemini (31)
│ ○ Cursor (68)
└
◆ Select a session (12 available)
│ [claude] 2026-02-19 05:28 my-project Debugging SSH tunnel config 84a36c5d
│ [copilot] 2026-02-19 04:41 my-project Migrate presets from Electron c2f5974c
│ [codex] 2026-02-18 23:12 my-project Fix OpenCode SQLite parser a1e90b3f
│ ...
└
◆ Continue claude session in:
│ ○ Gemini
│ ○ Copilot
│ ○ Codex
│ ○ OpenCode
│ ○ Droid


---
*Page 4*


│ ○ Cursor
└
If no sessions are found for the current directory, all sessions are shown automatically.
Non-interactive
continues list # List all sessions
continues list --source claude --json # JSON output, filtered
continues list --jsonl -n 10 # JSONL, limit to 10
continues scan # Session discovery stats
continues rebuild # Force-rebuild the index
list output:
Found 894 sessions (showing 5):
[claude] 2026-02-19 05:28 dev-test/SuperCmd SSH tunnel config debugging 84a36c5d
[copilot] 2026-02-19 04:41 migrate-to-tauri Copy Presets From Electron c2f5974c
[codex] 2026-02-18 23:12 cli-continues Fix OpenCode SQLite parser a1e90b3f
[gemini] 2026-02-18 05:10 my-project Tauri window management 96315428
[opencode] 2026-02-14 17:12 codex-session-picker Where does Codex save JSON files ses_3a2d
Quick Resume
Resume the Nth most recent session from a specific tool using native resume (no context injection — fastest, preserves full history):
continues claude # Latest Claude session
continues codex 3 # 3rd most recent Codex session
continues copilot # Latest Copilot session
continues gemini 2 # 2nd most recent Gemini session
continues opencode # Latest OpenCode session
continues droid # Latest Droid session
continues cursor # Latest Cursor session
Cross-tool Handoff
This is the whole point. Start in one tool, finish in another:
# You were debugging in Claude, but hit the rate limit.
# Grab the session ID from `continues list` and hand it off:
continues resume abc123 --in gemini
# Or pick interactively — just run `continues`, select a session,
# and choose a different tool as the target.
# In picker flows, forward destination flags after `--`
continues pick -- --model gpt-5 --sandbox workspace-write
continues extracts your conversation context (messages, file changes, pending tasks) and injects it as a structured prompt into the target
tool. The target picks up with full awareness of what you were working on.
When forwarding flags in cross-tool mode, continues maps common interactive settings to the selected target tool (model,
sandbox/permissions, yolo/auto-approve, extra directories, etc.). Any flag that is not mapped is passed through as-is to the destination CLI.
How It Works
1. Discovery → Scans session directories for all 7 tools
2. Parsing → Reads each tool's native format (JSONL, JSON, SQLite, YAML)
3. Extraction → Pulls recent messages, file changes, tool activity, AI reasoning
4. Summarizing → Groups tool calls by type with concise one-line samples


---
*Page 5*


5. Handoff → Generates a structured context document
6. Injection → Launches target tool with the context pre-loaded
Tool Activity Extraction
Every tool call from the source session is parsed, categorized, and summarized. The handoff document includes a Tool Activity section so the
target tool knows exactly what was done — not just what was said.
Shared formatting helpers ( + per-tool formatters in ) keep summaries consistent across
SummaryCollector src/utils/tool-summarizer.ts
all 7 CLIs. Adding support for a new tool type is a one-liner.
What gets extracted per CLI:
Tool Extracted
Claude Bash commands (with exit codes), Read/Write/Edit (file paths), Grep/Glob, WebFetch/WebSearch, Task/subagent
Code dispatches, MCP tools ( mcp__* ), thinking blocks → reasoning notes
exec_command/shell_command (grouped by base command: , , etc.), apply_patch (file paths from patch format),
Codex CLI npm git
web_search, write_stdin, MCP resources, agent_reasoning → reasoning notes, token usage
Gemini CLI read_file/write_file (with diffStat : +N -M lines), thoughts → reasoning notes, model info, token usage (accumulated)
Copilot CLI Session metadata from workspace.yaml (tool calls not persisted by Copilot)
OpenCode Messages from SQLite DB or JSON fallback (tool-specific parts TBD)
Factory Create/Read/Edit (file paths), Execute/Bash (shell commands), LS, MCP tools ( context7___* , etc.), thinking blocks →
Droid reasoning notes, todo tasks, model info, token usage from companion
.settings.json
Cursor Bash/terminal commands, Read/Write/Edit/apply_diff (file paths), Grep/codebase_search, Glob/list_directory/file_search,
(CLI) WebFetch, WebSearch, Task/subagent dispatches, MCP tools ( mcp__* ), thinking blocks → reasoning notes
Example handoff output:
## Tool Activity
- **Bash** (×47): `$ npm test → exit 0` · `$ git status → exit 0` · `$ npm run build → exit 1`
- **Edit** (×12): `edit src/auth.ts` · `edit src/api/routes.ts` · `edit tests/auth.test.ts`
- **Grep** (×8): `grep "handleLogin" src/` · `grep "JWT_SECRET"` · `grep "middleware"`
- **apply_patch** (×5): `patch: src/utils/db.ts, src/models/user.ts`
## Session Notes
- **Model**: claude-sonnet-4
- **Tokens**: 45,230 input, 12,847 output
- 💭 Need to handle the edge case where token refresh races with logout
- 💭 The middleware chain order matters — auth must come before rate limiting
Session Storage
continues reads session data from each tool's native storage. Read-only — it doesn't modify or copy anything.
Tool Location Format
Claude Code ~/.claude/projects/ JSONL
GitHub Copilot ~/.copilot/session-state/ YAML + JSONL
Google Gemini CLI ~/.gemini/tmp/*/chats/ JSON
OpenAI Codex ~/.codex/sessions/ JSONL
OpenCode ~/.local/share/opencode/ SQLite
Factory Droid ~/.factory/sessions/ JSONL + JSON
Cursor (CLI) ~/.cursor/projects/*/agent-transcripts/ JSONL
Session index cached at ~/.continues/sessions.jsonl. Auto-refreshes when stale (5 min TTL).


---
*Page 6*


Commands
continues Interactive TUI picker (default)
continues list List all sessions
continues resume <id> Resume by session ID
continues resume <id> --in <tool> Cross-tool handoff
continues scan Session discovery statistics
continues rebuild Force-rebuild session index
continues <tool> [n] Quick-resume Nth session from tool
continues / continues pick
Interactive session picker. Requires a TTY.
Flag Description
-s, --source <tool> Pre-filter to one tool
--no-tui Disable interactive mode
--rebuild Force-rebuild index first
-- ... Forward raw launch flags to selected destination tool
continues list (alias: ls)
Flag Description Default
-s, --source <tool> Filter by tool all
-n, --limit <number> Max sessions to show 50
--json Output as JSON array —
--jsonl Output as JSONL —
--rebuild Force-rebuild index first —
continues resume <id> (alias: r)
Flag Description Default
-i, --in <tool> Target tool for cross-tool handoff —
--no-tui Skip interactive prompts —
... unknown flags In cross-tool mode, map common flags and pass unmapped ones directly to destination CLI —
continues scan
Flag Description
--rebuild Force-rebuild index first
continues <tool> [n]
Quick-resume using native resume (same tool, no context injection).
Tools: claude, copilot, gemini, codex, opencode, droid, cursor. Default n is 1.
Conversion Matrix
All 42 cross-tool paths are supported and tested:


---
*Page 7*


→ Claude → Copilot → Gemini → Codex → OpenCode → Droid → Cursor
Claude — ✅ ✅ ✅ ✅ ✅ ✅
Copilot ✅ — ✅ ✅ ✅ ✅ ✅
Gemini ✅ ✅ — ✅ ✅ ✅ ✅
Codex ✅ ✅ ✅ — ✅ ✅ ✅
OpenCode ✅ ✅ ✅ ✅ — ✅ ✅
Droid ✅ ✅ ✅ ✅ ✅ — ✅
Cursor ✅ ✅ ✅ ✅ ✅ ✅ —
Same-tool resume is available via continues <tool> shortcuts (native resume, not shown in matrix).
Requirements
Node.js 22+ (uses built-in node:sqlite for OpenCode parsing)
At least one of: Claude Code, GitHub Copilot, Gemini CLI, Codex, OpenCode, Factory Droid, or Cursor Agent CLI (agent)
Development
Releases
8tags
Packages
No packages published
Contributors 6
Languages
TypeScript98.4% JavaScript1.6%