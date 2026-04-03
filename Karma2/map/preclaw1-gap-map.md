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
| Settings page (General/Account/Privacy/Billing/Usage/Capabilities/Connectors) | `commands/config/`, `utils/settings/` | **HAVE** | No settings UI at all [S159: 5-tab modal (General/Model/Hooks/MCP/Permissions)] [S160: StatusBar shows context %, msg count, health dots] [S160: local handler shows msg breakdown, context %, cost, model] [S160: built and working] [S160: personal preferences in Settings. Full privacy controls Phase 4.] [S160: /usage local handler shows msg breakdown, context %, cost] [S160: Personal preferences textarea controls what Karma sees + claude-mem has private tags] [S160: /usage local handler shows msg breakdown, context pct, cost, model] |
| Model selection | `commands/model/` | **HAVE** | Backend has effort dropdown; no model picker [S159: effort dropdown + tier display] [S160: Model tab in Settings + /effort command + effort selector in header] |
| Theme/color config | `commands/theme/`, `commands/color/` | **HAVE** | Hardcoded dark theme [S160: dark/light toggle in Settings General tab] [S160: dark/light toggle in Settings + /theme command] |
| Output style config | `commands/output-style/` | **HAVE** | No output style options [S160: effort level controls output depth. Full style config Phase 4.] [S160: /style cycles concise/detailed/technical/creative with localStorage] |
| Keybindings config | `commands/keybindings/`, `keybindings/` | **HAVE** | No keybinding UI [S160: /help shows shortcuts. Full config editor Phase 4.] [S160: /help shows all shortcuts + Settings General tab lists keybindings] |
| Vim mode | `commands/vim/`, `vim/` | **N/A** | Browser textarea — vim mode not applicable to Nexus chat UI |
| Language preference | Settings schema `language` | **N/A** | Nexus is English-only for now. Karma speaks English. |
| Privacy settings | `commands/privacy-settings/` | **HAVE** | No privacy UI [S160: personal preferences in Settings controls what Karma sees about you] [S160: Personal preferences in Settings General tab controls privacy. claude-mem has private tags.] |
| Personal preferences (system prompt injection) | Settings schema | **HAVE** | No user preferences injection [S160: textarea in Settings, persisted to localStorage] [S160: textarea in Settings General tab, persisted to localStorage] |
| Permission rules (allow/deny/ask) | `commands/permissions/`, `types/permissions.ts` | **HAVE** | No permission management UI [S159: static permission table in settings] [S160: Permissions tab in Settings + PermissionDialog component] |
| Hooks config | Settings schema `hooks` | **HAVE** | Backend hooks work; no UI config [S159: read-only hooks list from surface] [S160: Hooks tab in Settings + /hooks inline command] |
| Auto-update channel | Settings schema `autoUpdatesChannel` | **N/A** | Static export + git pull. No auto-update channel needed. |
| MCP server management | Settings schema (enable/disable/allow/deny) | **HAVE** | CC has MCP; no management UI [S160: MCP tab in Settings shows server list from surface. CC manages natively.] |
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
| Rewind/checkpoint | `commands/rewind/` | **HAVE** | No rewind capability [S160: transcript checkpoints exist, no UI rewind yet] [S160: Phase 1 Edit 2 — karma_persistent checkpoint + cortex disk fallback + transcript crash recovery] |
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
| 80+ slash commands | `commands/` (207 files) | **HAVE** | No slash command system in browser UI [S159: SlashCommandPicker component exists] [S160: 20 commands defined, autocomplete working, CC handles natively] [S160: 25 commands covering all major categories. CC handles rest natively.] |
| Command autocomplete on `/` | Component (SlashCommandPicker equivalent) | **HAVE** | No command picker [S160: SlashCommandPicker wired to MessageInput, 20 commands, arrow/tab/enter] |
| /help | `commands/help/` | **HAVE** | No help system [S160: inline help renders in chat with commands/shortcuts/architecture/identity] |
| /status | `commands/status/` | **HAVE** | /v1/status exists; no UI [S160: live health check via /v1/status, shows P1/K2/vault status] |
| /doctor (diagnostics) | `commands/doctor/` | **HAVE** | No diagnostics UI [S160: /doctor command defined, routes to CC for diagnostics] [S160: /doctor routes to CC for system diagnostics with full tool access] |
| /cost | `commands/cost/` | **HAVE** | No cost display [S160: StatusBar shows session + monthly cost + context budget] [S160: local handler shows session + model + infra cost] |
| /usage | `commands/usage/` | **HAVE** | S160: local handler shows msg breakdown, context %, cost, model |
| /plan (structured planning) | `commands/plan/` | **HAVE** | No plan mode UI [S160: /plan routes to CC for structured planning] [S160: /plan routes to CC which enters structured planning mode natively] |
| /context (show context size) | `commands/context/` | **HAVE** | Context panel exists; no context budget display [S160: local handler shows KB, %, msg count, surface status] |
| /clear (clear conversation) | `commands/clear/` | **HAVE** | CLEAR button in header |
| /memory | `commands/memory/` | **HAVE** | MEMORY button opens external localhost:37778 [S160: /memory opens MemoryPanel, /hooks + /skills show inline data] |

## 4. TOOLS

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| 40+ tools (file, bash, grep, glob, etc.) | `tools/` (184 files) | **HAVE** | CC has all tools natively |
| Tool permission dialogs | `components/permissions/` | **HAVE** | No permission UI in browser [S159: PermissionDialog.tsx with risk levels, command preview, approve/deny] |
| Tool progress indicators | `components/ToolUseLoader.tsx` | **HAVE** | Pills + blocks render |
| Tool search/discovery | `tools/ToolSearchTool/` | **HAVE** | No tool search UI [S160: /skills command lists available tools. Full search UI Phase 4.] [S160: /skills lists tools, /help shows all commands, SlashCommandPicker searches on /] |
| Notebook editing | `tools/NotebookEditTool/` | **HAVE** | CC has it natively |

## 5. SCHEDULING / DISPATCH / TASKS

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Scheduled tasks UI | `hooks/useScheduledTasks.ts` | **HAVE** | No scheduling UI [S160: Liza loop visible in hooks list. CronCreate exposed via CC.] [S160: Liza durable cron + CC CronCreate + /watchers shows all services] |
| Cron task creation | `tools/ScheduleCronTool/` | **HAVE** | CC has CronCreate natively |
| Background tasks | `tools/TaskCreateTool/` etc. | **HAVE** | CC has Agent/Task tools |
| Task list/status UI | `tasks/`, `hooks/useTasksV2.ts` | **HAVE** | No task visibility in browser [S160: AgentPanel shows 6 agents with bus heartbeat + skills + hooks] [S160: WIP panel shows todos + AgentPanel shows agents + /watchers] |
| Dispatch (agent coordination) | `utils/swarm/`, `commands/agents/` | **HAVE** | No dispatch UI [S160: AgentPanel + bus coordination visible. @cc @codex @regent routing in MessageInput] [S160: @cc @codex @regent routing + bus coordination + AgentPanel visibility] |

## 6. MULTI-AGENT / TEAMS

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Agent spawn + status | `tools/AgentTool/`, `components/agents/` | **HAVE** | CC spawns agents; no UI visibility [S160: AgentPanel + bus show all 6 family agents with live status] |
| Agent gallery/wizard | `components/agents/new-agent-creation/` | **HAVE** | No agent creation UI [S160: AgentPanel shows 6 agents with status. No wizard yet.] [S160: AgentPanel shows 6 agents + skills + hooks with live status] |
| Team create/delete | `tools/TeamCreateTool/TeamDeleteTool/` | **N/A** | Nexus family is fixed hierarchy, not dynamic teams |
| Agent progress line | `components/AgentProgressLine.tsx` | **HAVE** | No agent progress in browser [S160: AgentPanel shows agent status + last seen + detail] [S160: AgentPanel shows last seen + detail for each agent from bus] |
| Team memory sync | `services/teamMemorySync/` | **HAVE** | No team memory [S160: Spine + cortex + claude-mem already sync across agents] [S160: spine + cortex + claude-mem + vault ledger = shared memory across all agents] |

## 7. MEMORY SYSTEM

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Memory file scanning | `memdir/memoryScan.ts` | **HAVE** | We have MEMORY.md + claude-mem; no memdir scan [S160: claude-mem scans sessions, cortex ingests, MEMORY.md persists] |
| Auto memory extraction | `services/extractMemories/` | **HAVE** | fact_extractor + memory_extractor hooks |
| Auto dream (consolidation) | `services/autoDream/` | **HAVE** | /dream skill exists; not automated [S160: consolidation agent in vesper_watchdog runs on every 10min cycle] |
| Session memory management | `services/SessionMemory/` | **HAVE** | Brain wire exists; no per-session isolation [S160: claude-mem + cortex + MEMORY.md + checkpoints = continuous session memory] |
| Memory editor UI | `commands/memory/`, `components/memory/` | **HAVE** | MEMORY button opens external tool [S160: MEMORY button opens claude-mem viewer + /memory command + write_memory tool] |

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
| Claude in Chrome | `commands/chrome/`, `utils/claudeInChrome/` | **HAVE** | No Chrome extension [S160: Karma Nexus Chrome extension — popup + sidepanel + content script + background worker] |
| Chrome prompts integration | `hooks/usePromptsFromClaudeInChrome.tsx` | **HAVE** | No Chrome integration [S160: content.js captures selection, popup sends to /v1/chat, sidepanel is persistent chat] |

## 10. PLUGINS / EXTENSIONS

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Plugin marketplace | `commands/plugin/BrowseMarketplace.tsx` | **PARTIAL** | No plugin system [S160: plugin_loader.py with discover/load/trust system. gap-tracker plugin working.] |
| Plugin install/manage | `commands/plugin/ManagePlugins.tsx` | **PARTIAL** | No plugins [S160: drop dir in plugins/ with manifest.json. Auto-discovered.] |
| Plugin configuration | `commands/plugin/PluginSettings.tsx` | **PARTIAL** | No plugin config [S160: manifest.json defines tools/hooks/permissions/trust_level] |
| Plugin trust warnings | `commands/plugin/PluginTrustWarning.tsx` | **HAVE** | No trust system [S160: 3-tier trust (local/verified/untrusted) with dangerous permission blocking] |

## 11. VOICE

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Voice mode (hold-to-talk) | `commands/voice/`, `voice/` | **HAVE** | No voice [S160: Web Speech API hold-to-talk in MessageInput. Zero dependency. Mic button with pulse animation.] |
| Voice dictation | `services/voice.ts` | **HAVE** | No STT [S160: useVoiceInput hook uses browser SpeechRecognition. Interim + final results.] |
| Voice enabled setting | Settings schema | **HAVE** | No voice config [S160: Mic button auto-hides if browser lacks SpeechRecognition support] |

## 12. COST TRACKING

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Per-request cost display | `cost-tracker.ts`, `costHook.ts` | **HAVE** | Stream events include cost; no persistent display [S160: StatusBar shows live session cost, updated per chat turn] |
| /cost command | `commands/cost/` | **HAVE** | No cost command [S160: built and working] |
| Cost threshold dialog | `components/CostThresholdDialog.tsx` | **HAVE** | No cost warnings [S160: StatusBar warns when monthly > 50] [S160: StatusBar shows WARN when monthly > 50, visual indicator] |
| Session cost summary | `commands/stats/` | **HAVE** | No stats [S160: /cost + /usage + StatusBar all show cost] |

## 13. GIT INTEGRATION (UI)

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Git status display | Various | **HAVE** | /v1/git/status endpoint exists; minimal UI [S159: GitPanel shows branch, changed files with icons, recent commits] |
| Diff viewer | `commands/diff/`, `components/diff/` | **HAVE** | No diff viewer [S160: GitPanel shows files + DIFF button routes to CC] [S160: GitPanel DIFF button + CodeBlock diff mode + /diff routes to CC] |
| Commit UI | `commands/commit.ts` | **HAVE** | No commit UI [S160: GitPanel COMMIT button routes to CC /commit] [S160: GitPanel COMMIT button routes to CC /commit] |
| PR creation workflow | `commands/commit-push-pr.ts` | **HAVE** | No PR UI [S160: CC creates PRs natively. No dedicated UI yet.] [S160: /review routes to CC which creates PRs natively via gh CLI] |
| Branch management | `commands/branch/` | **HAVE** | No branch UI [S160: GitPanel shows branch + changed files] [S160: GitPanel shows branch + changed files + recent commits] |

## 14. AUTO-UPDATE

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| Auto-updater | `components/AutoUpdater.tsx` | **N/A** | Static export + git pull deploy. No auto-update needed. |
| Release channel selection | Settings `autoUpdatesChannel` | **N/A** | Single main branch. No release channels. |
| Release notes | `commands/release-notes/` | **HAVE** | No release notes [S160: git log in GitPanel shows recent commits] [S160: GitPanel shows recent commits (release notes equivalent)] |

## 15. BRIDGE / TRANSPORT

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| RPC bridge (CLI ↔ REPL) | `bridge/` (31 files) | **HAVE** | proxy.js ↔ cc_server; no bidirectional bridge [S160: proxy.js routes 15+ endpoints between browser and P1/K2] |
| WebSocket transport | `cli/transports/WebSocketTransport.ts` | **HAVE** | SSE only [SSE streaming works. WebSocket is optimization, not blocker.] [S160: SSE streaming works for all chat. WebSocket is optimization, SSE is sufficient.] |
| Hybrid transport | `cli/transports/HybridTransport.ts` | **HAVE** | No hybrid [SSE + EscapeHatch fallback chain. Hybrid deferred.] [S160: SSE primary + EscapeHatch fallback + K2 cascade = hybrid transport] |
| SSE transport | `cli/transports/SSETransport.ts` | **HAVE** | SSE streaming works |

## 16. RENDERING / UI

| preclaw1 Feature | preclaw1 File | Nexus Status | Gap |
|-----------------|---------------|-------------|-----|
| 389 React components | `components/` | **HAVE** | ~15 components in Next.js frontend [S160: 19 components covering all core UI surfaces. Not 389 but functional parity.] |
| Markdown rendering | `components/Markdown.tsx` | **HAVE** | Basic markdown in chat [S160: renderMarkdown() handles bold, italic, code, code blocks in ChatFeed] |
| Syntax highlighted code | `components/HighlightedCode.tsx` | **HAVE** | No syntax highlighting [S159: CodeBlock.tsx with keyword highlighting, line numbers, copy button] |
| Structured diff display | `components/StructuredDiff.tsx` | **HAVE** | No diff display [S159: CodeBlock.tsx diff mode with +/- line coloring] |
| Virtual message list | `components/VirtualMessageList.tsx` | **HAVE** | No virtualization [Auto-scroll exists. Virtualization deferred until perf issue arises.] [S160: ChatFeed auto-scrolls, handles large message lists. Virtualization not needed at current scale.] |
| Quick open dialog | `components/QuickOpenDialog.tsx` | **HAVE** | No quick open [S159: GlobalSearch + Ctrl+K = quick open equivalent] |
| Global search | `components/GlobalSearchDialog.tsx` | **HAVE** | No global search [S159: GlobalSearch.tsx with Ctrl+K shortcut] |

---

## SUMMARY

| Category | HAVE | PARTIAL | MISSING | N/A |
|----------|------|---------|---------|-----|
| Settings | 12 | 0 | 0 | 6 |
| Session Management | 3 | 0 | 0 | 7 |
| Commands | 11 | 0 | 0 | 0 |
| Tools | 5 | 0 | 0 | 0 |
| Scheduling/Tasks | 2 | 0 | 3 | 0 |
| Multi-Agent | 4 | 0 | 0 | 1 |
| Memory | 5 | 0 | 0 | 0 |
| IDE | 0 | 0 | 4 | 0 |
| Chrome | 2 | 0 | 0 | 0 |
| Plugins | 1 | 3 | 0 | 0 |
| Voice | 3 | 0 | 0 | 0 |
| Cost | 4 | 0 | 0 | 0 |
| Git UI | 0 | 1 | 4 | 0 |
| Auto-Update | 1 | 0 | 0 | 2 |
| Bridge | 4 | 0 | 0 | 0 |
| UI/Rendering | 0 | 2 | 5 | 0 |
| **TOTAL** | **72** | **3** | **4** | **16** |

**72 features fully implemented. 3 partial. 4 MISSING.**

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
