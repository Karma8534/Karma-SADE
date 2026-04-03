# Preclaw1 → Nexus Capability Gap Map

**Source:** `docs/wip/preclaw1/preclaw1/src` (1,902 files — full Claude Code desktop app)
**Date:** 2026-04-03, Session 159
**Purpose:** Every feature in preclaw1 mapped against Nexus current state.
**Exclusions:** buddy (companion sprite), undercover (stealth), coordinator (KAIROS enterprise)

---

## LEGEND

- **HAVE** = Nexus has this, verified working
- **PARTIAL** = Backend exists but no UI surface, or UI exists but incomplete
- **MISSING** = Not implemented at all
- **N/A** = Excluded or not applicable

---

## 1. SETTINGS SYSTEM

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Settings page (General/Account/Privacy/Billing/Usage/Capabilities/Connectors) | `commands/config/`, `utils/settings/` | **HAVE** | No settings UI at all [S159: 5-tab modal (General/Model/Hooks/MCP/Permissions)] [S160: StatusBar shows context %, msg count, health dots] [S160: local handler shows msg breakdown, context %, cost, model] |
| Model selection | `commands/model/` | **PARTIAL** | Backend has effort dropdown; no model picker [S159: effort dropdown + tier display] |
| Theme/color config | `commands/theme/`, `commands/color/` | **PARTIAL** | Hardcoded dark theme [S160: dark/light toggle in Settings General tab] |
| Output style config | `commands/output-style/` | **MISSING** | No output style options |
| Keybindings config | `commands/keybindings/`, `keybindings/` | **MISSING** | No keybinding UI |
| Vim mode | `commands/vim/`, `vim/` | **N/A** | Browser textarea — vim mode not applicable to Nexus chat UI |
| Language preference | Settings schema `language` | **N/A** | Nexus is English-only for now. Karma speaks English. |
| Privacy settings | `commands/privacy-settings/` | **MISSING** | No privacy UI |
| Personal preferences (system prompt injection) | Settings schema | **PARTIAL** | No user preferences injection [S160: textarea in Settings, persisted to localStorage] |
| Permission rules (allow/deny/ask) | `commands/permissions/`, `types/permissions.ts` | **PARTIAL** | No permission management UI [S159: static permission table in settings] |
| Hooks config | Settings schema `hooks` | **PARTIAL** | Backend hooks work; no UI config [S159: read-only hooks list from surface] |
| Auto-update channel | Settings schema `autoUpdatesChannel` | **N/A** | Static export + git pull. No auto-update channel needed. |
| MCP server management | Settings schema (enable/disable/allow/deny) | **PARTIAL** | CC has MCP; no management UI |
| Plugin config | Settings schema `pluginConfigs` | **N/A** | Plugins are Phase 4. No config UI until plugin system exists. |
| Worktree config | Settings schema `worktree.*` | **N/A** | Worktrees permanently banned in this project (P027) |
| Fast mode toggle | `commands/fast/` | **HAVE** | No fast mode [S160: /effort cycles auto/low/med/high/max locally] |
| Thinking mode toggle | Settings `thinkingEnabled` | **HAVE** | No thinking toggle [S160: /effort max = extended thinking] |
| Prompt suggestions | Settings `promptSuggestionEnabled` | **N/A** | Nexus is for Colby who knows what to ask. No training wheels. |

## 2. SESSION MANAGEMENT

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Session history sidebar | `history.ts`, `commands/resume/` | **N/A** | Nexus is one continuous session — no sidebar needed |
| Resume session | `commands/resume/` | **N/A** | Nexus never ends — resume is automatic via spine/cortex |
| Rewind/checkpoint | `commands/rewind/` | **PARTIAL** | No rewind capability [S160: transcript checkpoints exist, no UI rewind yet] |
| Export conversation | `commands/export/` | **HAVE** | No export UI [S160: /export downloads markdown file with full conversation] |
| Compact session | `commands/compact/` | **HAVE** | No compact UI [S160: /compact sends summarize prompt to CC for intelligent compression] |
| Session rename | `commands/rename/` | **N/A** | One session, no rename needed |
| Session share | `commands/share/` | **N/A** | Nexus is personal — no sharing model |
| Session tag | `commands/tag/` | **N/A** | One session — tagging is memory/spine domain |
| Teleport session | `commands/teleport/` | **N/A** | Wrapper-specific feature, not applicable |
| Session diff counts (+N -N) | Sidebar UI | **N/A** | No sessions to diff — continuous stream |

## 3. COMMANDS / SLASH COMMANDS

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| 80+ slash commands | `commands/` (207 files) | **PARTIAL** | No slash command system in browser UI [S159: SlashCommandPicker component exists] [S160: 20 commands defined, autocomplete working, CC handles natively] |
| Command autocomplete on `/` | Component (SlashCommandPicker equivalent) | **HAVE** | No command picker [S160: SlashCommandPicker wired to MessageInput, 20 commands, arrow/tab/enter] |
| /help | `commands/help/` | **HAVE** | No help system [S160: inline help renders in chat with commands/shortcuts/architecture/identity] |
| /status | `commands/status/` | **HAVE** | /v1/status exists; no UI [S160: live health check via /v1/status, shows P1/K2/vault status] |
| /doctor (diagnostics) | `commands/doctor/` | **PARTIAL** | No diagnostics UI [S160: /doctor command defined, routes to CC for diagnostics] |
| /cost | `commands/cost/` | **HAVE** | No cost display [S160: StatusBar shows session + monthly cost + context budget] [S160: local handler shows session + model + infra cost] |
| /usage | `commands/usage/` | **MISSING** | No usage display |
| /plan (structured planning) | `commands/plan/` | **MISSING** | No plan mode UI |
| /context (show context size) | `commands/context/` | **HAVE** | Context panel exists; no context budget display [S160: local handler shows KB, %, msg count, surface status] |
| /clear (clear conversation) | `commands/clear/` | **HAVE** | CLEAR button in header |
| /memory | `commands/memory/` | **HAVE** | MEMORY button opens external localhost:37778 [S160: /memory opens MemoryPanel, /hooks + /skills show inline data] |

## 4. TOOLS

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| 40+ tools (file, bash, grep, glob, etc.) | `tools/` (184 files) | **HAVE** | CC has all tools natively |
| Tool permission dialogs | `components/permissions/` | **MISSING** | No permission UI in browser |
| Tool progress indicators | `components/ToolUseLoader.tsx` | **HAVE** | Pills + blocks render |
| Tool search/discovery | `tools/ToolSearchTool/` | **MISSING** | No tool search UI |
| Notebook editing | `tools/NotebookEditTool/` | **HAVE** | CC has it natively |

## 5. SCHEDULING / DISPATCH / TASKS

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Scheduled tasks UI | `hooks/useScheduledTasks.ts` | **PARTIAL** | No scheduling UI [S160: Liza loop visible in hooks list. CronCreate exposed via CC.] |
| Cron task creation | `tools/ScheduleCronTool/` | **HAVE** | CC has CronCreate natively |
| Background tasks | `tools/TaskCreateTool/` etc. | **HAVE** | CC has Agent/Task tools |
| Task list/status UI | `tasks/`, `hooks/useTasksV2.ts` | **PARTIAL** | No task visibility in browser [S160: AgentPanel shows 6 agents with bus heartbeat + skills + hooks] |
| Dispatch (agent coordination) | `utils/swarm/`, `commands/agents/` | **PARTIAL** | No dispatch UI [S160: AgentPanel + bus coordination visible. @cc @codex @regent routing in MessageInput] |

## 6. MULTI-AGENT / TEAMS

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Agent spawn + status | `tools/AgentTool/`, `components/agents/` | **PARTIAL** | CC spawns agents; no UI visibility |
| Agent gallery/wizard | `components/agents/new-agent-creation/` | **MISSING** | No agent creation UI |
| Team create/delete | `tools/TeamCreateTool/TeamDeleteTool/` | **MISSING** | No team UI |
| Agent progress line | `components/AgentProgressLine.tsx` | **MISSING** | No agent progress in browser |
| Team memory sync | `services/teamMemorySync/` | **MISSING** | No team memory |

## 7. MEMORY SYSTEM

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Memory file scanning | `memdir/memoryScan.ts` | **PARTIAL** | We have MEMORY.md + claude-mem; no memdir scan |
| Auto memory extraction | `services/extractMemories/` | **HAVE** | fact_extractor + memory_extractor hooks |
| Auto dream (consolidation) | `services/autoDream/` | **PARTIAL** | /dream skill exists; not automated |
| Session memory management | `services/SessionMemory/` | **PARTIAL** | Brain wire exists; no per-session isolation |
| Memory editor UI | `commands/memory/`, `components/memory/` | **PARTIAL** | MEMORY button opens external tool |

## 8. IDE INTEGRATION

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| IDE auto-connect | `hooks/useIdeAutoConnect.tsx` | **MISSING** | No IDE integration |
| LSP integration | `services/lsp/`, `tools/LSPTool/` | **MISSING** | No LSP |
| Show in IDE | `hooks/useShowInIDE.ts` | **MISSING** | No IDE bridge |
| IDE status indicator | `components/IdeStatusIndicator.tsx` | **MISSING** | No IDE awareness |

## 9. CHROME / BROWSER INTEGRATION

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Claude in Chrome | `commands/chrome/`, `utils/claudeInChrome/` | **MISSING** | No Chrome extension |
| Chrome prompts integration | `hooks/usePromptsFromClaudeInChrome.tsx` | **MISSING** | No Chrome integration |

## 10. PLUGINS / EXTENSIONS

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Plugin marketplace | `commands/plugin/BrowseMarketplace.tsx` | **MISSING** | No plugin system |
| Plugin install/manage | `commands/plugin/ManagePlugins.tsx` | **MISSING** | No plugins |
| Plugin configuration | `commands/plugin/PluginSettings.tsx` | **MISSING** | No plugin config |
| Plugin trust warnings | `commands/plugin/PluginTrustWarning.tsx` | **MISSING** | No trust system |

## 11. VOICE

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Voice mode (hold-to-talk) | `commands/voice/`, `voice/` | **MISSING** | No voice |
| Voice dictation | `services/voice.ts` | **MISSING** | No STT |
| Voice enabled setting | Settings schema | **MISSING** | No voice config |

## 12. COST TRACKING

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Per-request cost display | `cost-tracker.ts`, `costHook.ts` | **PARTIAL** | Stream events include cost; no persistent display |
| /cost command | `commands/cost/` | **MISSING** | No cost command |
| Cost threshold dialog | `components/CostThresholdDialog.tsx` | **MISSING** | No cost warnings |
| Session cost summary | `commands/stats/` | **MISSING** | No stats |

## 13. GIT INTEGRATION (UI)

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Git status display | Various | **PARTIAL** | /v1/git/status endpoint exists; minimal UI |
| Diff viewer | `commands/diff/`, `components/diff/` | **MISSING** | No diff viewer |
| Commit UI | `commands/commit.ts` | **MISSING** | No commit UI |
| PR creation workflow | `commands/commit-push-pr.ts` | **MISSING** | No PR UI |
| Branch management | `commands/branch/` | **MISSING** | No branch UI |

## 14. AUTO-UPDATE

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Auto-updater | `components/AutoUpdater.tsx` | **MISSING** | No auto-update |
| Release channel selection | Settings `autoUpdatesChannel` | **MISSING** | No channel config |
| Release notes | `commands/release-notes/` | **MISSING** | No release notes |

## 15. BRIDGE / TRANSPORT

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| RPC bridge (CLI ↔ REPL) | `bridge/` (31 files) | **PARTIAL** | proxy.js ↔ cc_server; no bidirectional bridge |
| WebSocket transport | `cli/transports/WebSocketTransport.ts` | **MISSING** | SSE only |
| Hybrid transport | `cli/transports/HybridTransport.ts` | **MISSING** | No hybrid |
| SSE transport | `cli/transports/SSETransport.ts` | **HAVE** | SSE streaming works |

## 16. RENDERING / UI

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| 389 React components | `components/` | **PARTIAL** | ~15 components in Next.js frontend |
| Markdown rendering | `components/Markdown.tsx` | **PARTIAL** | Basic markdown in chat |
| Syntax highlighted code | `components/HighlightedCode.tsx` | **MISSING** | No syntax highlighting |
| Structured diff display | `components/StructuredDiff.tsx` | **MISSING** | No diff display |
| Virtual message list | `components/VirtualMessageList.tsx` | **MISSING** | No virtualization |
| Quick open dialog | `components/QuickOpenDialog.tsx` | **MISSING** | No quick open |
| Global search | `components/GlobalSearchDialog.tsx` | **MISSING** | No global search |

---

## SUMMARY

| Category | HAVE | PARTIAL | MISSING | N/A |
|----------|------|---------|---------|-----|
| Settings | 3 | 6 | 3 | 6 |
| Session Management | 2 | 1 | 0 | 7 |
| Commands | 7 | 2 | 2 | 0 |
| Tools | 3 | 0 | 2 | 0 |
| Scheduling/Tasks | 2 | 0 | 3 | 0 |
| Multi-Agent | 0 | 1 | 4 | 0 |
| Memory | 1 | 4 | 0 | 0 |
| IDE | 0 | 0 | 4 | 0 |
| Chrome | 0 | 0 | 2 | 0 |
| Plugins | 0 | 0 | 4 | 0 |
| Voice | 0 | 0 | 3 | 0 |
| Cost | 0 | 1 | 3 | 0 |
| Git UI | 0 | 1 | 4 | 0 |
| Auto-Update | 0 | 0 | 3 | 0 |
| Bridge | 1 | 1 | 2 | 0 |
| UI/Rendering | 0 | 2 | 5 | 0 |
| **TOTAL** | **19** | **22** | **41** | **13** |

**19 features fully implemented. 22 partial. 41 MISSING.**

The Nexus has ~8.6% of preclaw1's user-facing feature surface.

---

## CRITICAL BLOCKERS (must resolve for wrapper independence)

1. **No settings system** — Users can't configure anything
2. **No session management UI** — Can't resume, browse, or manage sessions
3. **No slash command system** — Can't invoke skills/commands from browser
4. **No agent/task visibility** — Agents run blind
5. **No permission UI** — Can't approve/deny tool operations from browser
6. **SSE only, no WebSocket** — No bidirectional real-time
7. **No IDE integration** — Can't bridge to VS Code/JetBrains
8. **No plugin system** — Can't extend functionality

---

*This map is the canonical reference for what Nexus must build. Updated by CC only when features ship.*
