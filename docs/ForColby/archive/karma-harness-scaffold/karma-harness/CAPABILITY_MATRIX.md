# Karma Harness — Capability Matrix
## Source: All 3 repos read in full (2026-03-31)

---

## SOURCE 1: claude-code (Leaked Anthropic Source)
**~1,900 files, 512K+ lines, TypeScript/Bun/React+Ink**

### Tools (every tool Karma must implement)
| Tool | Description | Karma Implementation |
|------|-------------|----------------------|
| BashTool | Shell command execution with security validation | ✅ Sandbox exec API |
| PowerShellTool | PowerShell execution (Windows) | ✅ Sandbox exec API |
| FileReadTool | Read files incl. images, PDFs, notebooks | ✅ Backend file service |
| FileWriteTool | Create / overwrite files | ✅ Backend file service |
| FileEditTool | Partial string-replacement edits | ✅ Backend file service |
| GlobTool | File pattern matching | ✅ Backend file service |
| GrepTool | ripgrep-based content search | ✅ Backend file service |
| WebFetchTool | Fetch URL content | ✅ Backend tool |
| WebSearchTool | Web search | ✅ Perplexity Sonar API |
| AgentTool | Spawn sub-agents | ✅ Agent spawner service |
| SkillTool | Execute named skills | ✅ Skills system |
| MCPTool | MCP server tool invocation | ✅ MCP proxy layer |
| LSPTool | Language Server Protocol integration | ✅ LSP service |
| NotebookEditTool | Jupyter notebook editing | ✅ Notebook service |
| TaskCreateTool | Create tasks | ✅ Task manager |
| TaskUpdateTool | Update tasks | ✅ Task manager |
| TaskGetTool | Get task status | ✅ Task manager |
| TaskListTool | List tasks | ✅ Task manager |
| TaskStopTool | Stop task | ✅ Task manager |
| TaskOutputTool | Get task output | ✅ Task manager |
| SendMessageTool | Inter-agent messaging | ✅ Message bus |
| TeamCreateTool | Create agent teams | ✅ Team orchestrator |
| TeamDeleteTool | Delete agent teams | ✅ Team orchestrator |
| EnterPlanModeTool | Enter plan mode | ✅ Mode manager |
| ExitPlanModeTool | Exit plan mode | ✅ Mode manager |
| EnterWorktreeTool | Git worktree isolation | ✅ Git service |
| ExitWorktreeTool | Exit git worktree | ✅ Git service |
| CronCreateTool | Scheduled triggers | ✅ Scheduler |
| CronDeleteTool | Delete scheduled trigger | ✅ Scheduler |
| CronListTool | List scheduled triggers | ✅ Scheduler |
| RemoteTriggerTool | Remote triggers | ✅ Webhook service |
| SleepTool | Proactive wait | ✅ Async sleep |
| SyntheticOutputTool | Structured output generation | ✅ Output formatter |
| AskUserQuestionTool | Prompt user for input | ✅ UI interaction |
| BriefTool | Brief/attachment uploads | ✅ File upload |
| ConfigTool | Read/write config settings | ✅ Config service |
| TodoWriteTool | Write todo list | ✅ Task manager |
| ToolSearchTool | Deferred tool discovery | ✅ Tool registry |
| ListMcpResourcesTool | List MCP resources | ✅ MCP proxy |
| ReadMcpResourceTool | Read MCP resource | ✅ MCP proxy |

### Commands (slash commands Karma must support)
| Command | Description |
|---------|-------------|
| /commit | Git commit |
| /review | Code review (ultrareview) |
| /compact | Context compression |
| /mcp | MCP server management |
| /config | Settings management |
| /doctor | Environment diagnostics |
| /login / /logout | Auth management |
| /memory | Persistent memory management |
| /skills | Skill management |
| /tasks | Task management |
| /vim | Vim mode toggle |
| /diff | View changes |
| /cost | Usage cost tracking |
| /theme | Theme switching |
| /context | Context visualization |
| /pr_comments | View PR comments |
| /resume | Restore previous session |
| /share | Share session |
| /plan | Plan mode |
| /branch | Git branch management |
| /rewind | Rewind to previous state |
| /export | Export conversation |
| /stats | Usage statistics |
| /status | System status |
| /help | Help system |
| /hooks | Hook management |
| /permissions | Permission management |
| /model | Model selection |
| /output-style | Output style config |
| /keybindings | Keybinding config |
| /voice | Voice input toggle |
| /effort | Effort level control |
| /fast | Fast mode toggle |
| /passes | Multi-pass config |
| /thinkback | Thinking replay |
| /rename | Rename session |
| /tag | Tag sessions |
| /plugin | Plugin management |
| /install-github-app | GitHub app installer |
| /install-slack-app | Slack app installer |
| /desktop / /mobile | Platform handoff |
| /agents | Agent management |

### Services Karma Must Implement
| Service | Description |
|---------|-------------|
| Query Engine | LLM API caller: streaming, tool-call loops, thinking mode, retry, token counting |
| Memory (memdir) | Persistent memory directory — auto-extract + load on session start |
| Session Storage | Transcript recording, session persistence |
| Context Compression (compact) | Compress conversation context when approaching limits |
| Cost Tracker | Per-session token cost tracking |
| File History | Snapshot file states before edits |
| Permission System | Per-tool permission model: default/plan/bypass/auto |
| Plugin Loader | Load built-in and third-party plugins |
| MCP Client | Connect to MCP servers, invoke tools |
| LSP Manager | Language server connections |
| OAuth | OAuth 2.0 auth flow |
| Feature Flags | Runtime feature flag evaluation |
| Analytics | Session analytics + telemetry |
| IDE Bridge | VS Code / JetBrains extension bridge |
| Multi-Agent Coordinator | Orchestrate parallel sub-agents |
| Team Memory Sync | Sync memory across agent teams |
| Remote Sessions | Run sessions remotely |

### Key Architecture Patterns
- **Streaming responses** via WebSocket/SSE
- **Tool-call loops** — model keeps calling tools until task complete
- **Thinking mode** — extended reasoning before responding
- **Permission gate** on every tool call
- **Context compaction** when approaching token limit
- **File state cache** — knows what files changed in session
- **Parallel sub-agents** via AgentTool + TeamCreate
- **Skills** — reusable SKILL.md files injected into context
- **MCP protocol** — connect external tool servers

---

## SOURCE 2: Continuous Claude v3
**109 skills, 32 agents, 30 hooks, PostgreSQL+pgvector**

### Key Capabilities to Add
| Capability | Description |
|-----------|-------------|
| **TLDR 5-Layer Code Analysis** | L1:AST → L2:CallGraph → L3:CFG → L4:DFG → L5:PDG. 95% token savings vs raw file reads |
| **Session Handoffs (YAML)** | Auto-save session state to YAML before compaction/end — resume with full context |
| **Continuity Ledger** | Persistent ledger tracking all changes, file claims, decisions across sessions |
| **Memory Daemon** | Background process that extracts learnings from sessions using headless Claude |
| **Skill Activation System** | Hook that injects relevant skill hints on every user message |
| **32 Specialized Agents** | scout, oracle, kraken, arbiter, sleuth, phoenix, plan-agent, debug-agent, etc. |
| **Semantic Index (BGE)** | FAISS vector index over all 5 TLDR layers — semantic code search |
| **Workflow Chains** | /fix, /build, /tdd, /refactor — multi-agent orchestrated workflows |
| **Archival Memory (pgvector)** | Long-term semantic memory stored in PostgreSQL with BGE-large embeddings |
| **Pre-Compact Hook** | Auto-creates handoff YAML before context compaction fires |
| **Compiler-in-the-Loop** | pyright/ruff run after every file edit (shift-left validation) |
| **Math System** | SymPy, Z3, Pint integration for symbolic math |
| **Blackboard** | Shared state board for inter-agent communication within session |
| **File Claims** | Lock files during editing to prevent agent conflicts |
| **Context Query Agent** | Dedicated agent for semantic context retrieval |
| **Session Analyst** | Post-session analysis and learning extraction |
| **Discovery Interview** | Guided requirement clarification workflow |
| **Premortem** | Risk analysis before implementation |

### 32 Agent Definitions
aegis, agentica-agent, arbiter, architect, atlas, braintrust-analyst,
chronicler, context-query-agent, critic, debug-agent, herald, judge,
kraken, liaison, maestro, memory-extractor, onboard, oracle, pathfinder,
phoenix, plan-agent, plan-reviewer, profiler, research-codebase,
review-agent, scout, scribe, sentinel, session-analyst, sleuth, spark,
surveyor, validate-agent, warden

### 30 Hook Types
- UserPromptSubmit: skill activation hints injection
- PostToolUse: index handoffs, TLDR re-index, dirty flag tracking
- PreToolUse: permission checks, compiler-in-the-loop
- Stop/SubagentStop: auto-handoff, daemon wake
- SessionStart: ledger load, memory recall, symbol index warm

---

## SOURCE 3: Open Claude Cowork (Composio)
**Electron + Node.js + Express + Claude Agent SDK**

### Key Capabilities to Add
| Capability | Description |
|-----------|-------------|
| **Multi-Provider Support** | Claude Agent SDK + Opencode SDK — swap providers live |
| **Persistent Sessions** | Session ID maintained across messages, context never lost |
| **Real-time Streaming** | SSE token-by-token streaming to UI |
| **Tool Visualization** | Sidebar showing tool inputs/outputs as they execute |
| **500+ App Integrations** | Composio Tool Router: Gmail, Slack, GitHub, Drive, Calendar, etc. |
| **Skills Support** | SKILL.md files in .claude/skills/ auto-loaded |
| **Multi-chat Sessions** | Multiple conversations open simultaneously |
| **Messaging Bot Mode** | WhatsApp/Telegram/Signal/iMessage integration (Clawdbot) |
| **Browser Automation** | Navigate, click, fill forms, screenshot via Composio |
| **Scheduling** | Natural language reminders + cron jobs |
| **Dark-themed Modern UI** | Clean desktop-class interface |

---

## FULL KARMA CAPABILITY CHECKLIST
### Everything Karma Must Have At Baseline

#### Core Engine
- [ ] Streaming LLM query engine (tool-call loops, thinking mode, retry)
- [ ] Smart model router (7 providers, complexity-based routing)
- [ ] Permission system (default/plan/bypass/auto modes)
- [ ] Context compaction with pre-compact handoff
- [ ] Token cost tracker per session
- [ ] File state cache (snapshot before edits)

#### Tools (40 total)
- [ ] BashTool / PowerShellTool
- [ ] FileRead / FileWrite / FileEdit / Glob / Grep
- [ ] WebFetch / WebSearch
- [ ] AgentTool (sub-agent spawner)
- [ ] SkillTool
- [ ] MCPTool / ListMcpResources / ReadMcpResource
- [ ] LSPTool
- [ ] NotebookEditTool
- [ ] Task CRUD tools (Create/Update/Get/List/Stop/Output)
- [ ] SendMessageTool
- [ ] TeamCreate / TeamDelete
- [ ] EnterPlanMode / ExitPlanMode
- [ ] EnterWorktree / ExitWorktree
- [ ] CronCreate / CronDelete / CronList
- [ ] RemoteTriggerTool
- [ ] SleepTool
- [ ] SyntheticOutputTool
- [ ] AskUserQuestionTool
- [ ] BriefTool
- [ ] ConfigTool
- [ ] TodoWriteTool
- [ ] ToolSearchTool

#### Memory & Persistence
- [ ] Persistent memory directory (memdir)
- [ ] Auto memory extraction (daemon)
- [ ] pgvector semantic memory
- [ ] Session handoffs (YAML)
- [ ] Continuity ledger
- [ ] Archival memory with BGE embeddings
- [ ] File history snapshots
- [ ] Team memory sync

#### Agents & Orchestration
- [ ] Multi-agent coordinator
- [ ] 32 specialized agent definitions
- [ ] Blackboard (inter-agent shared state)
- [ ] File claims (edit locking)
- [ ] Agent team management

#### Code Intelligence
- [ ] TLDR 5-layer code analysis (AST/CallGraph/CFG/DFG/PDG)
- [ ] Semantic FAISS index
- [ ] LSP integration (go-to-definition, hover, diagnostics)
- [ ] Compiler-in-the-loop (pyright/ruff post-edit)
- [ ] Jupyter notebook support

#### Skills & Workflows
- [ ] 109 skill definitions
- [ ] Skill activation hook (auto-inject on user message)
- [ ] Workflow chains: /fix, /build, /tdd, /refactor
- [ ] Discovery interview workflow
- [ ] Premortem analysis workflow

#### Hooks System (30 hooks)
- [ ] UserPromptSubmit hooks
- [ ] PostToolUse hooks
- [ ] PreToolUse hooks
- [ ] Stop/SubagentStop hooks
- [ ] SessionStart hooks

#### Integrations
- [ ] MCP protocol (connect any MCP server)
- [ ] Composio Tool Router (500+ apps)
- [ ] GitHub integration
- [ ] Slack integration
- [ ] IDE bridge (VS Code / JetBrains)
- [ ] Voice input
- [ ] Browser automation

#### UI (Unified Chat+Cowork+Code)
- [ ] Real-time streaming responses (SSE/WebSocket)
- [ ] Tool execution visualization (sidebar)
- [ ] Monaco editor (full code editing)
- [ ] Integrated terminal (xterm.js)
- [ ] File browser
- [ ] Git diff viewer
- [ ] Multi-session tabs
- [ ] Context visualization
- [ ] Cost/usage display
- [ ] Vim mode
- [ ] Theme switching
- [ ] Plugin management UI

#### Self-Improvement (Karma-specific additions)
- [ ] Self-edit proposal engine
- [ ] 15-min approval window with auto-apply
- [ ] Edit log (applied/rejected history)
- [ ] Persona vault (persistent Karma identity)
- [ ] Session quality evaluator

---

## SOURCE 4: anthropics/claude-code (Official Anthropic Repo — v2.1.87)
**Official plugin library, settings schema, hooks, devcontainer, CHANGELOG**

### New Capabilities Found (not in other 3 repos)

#### Official Plugin System (full structure Karma must implement)
```
plugin-name/
├── .claude-plugin/plugin.json   ← Plugin manifest (name, version, description)
├── commands/                    ← Slash command .md files
├── agents/                      ← Agent definition .md files (with frontmatter)
├── skills/                      ← Skill .md files (with frontmatter + references/)
├── hooks/hooks.json             ← Hook event bindings
├── hooks/*.py or *.sh           ← Hook handler scripts
├── .mcp.json                    ← External MCP tool config
└── README.md
```

#### Official Plugins Karma Must Bundle
| Plugin | What It Does |
|--------|-------------|
| **feature-dev** | 7-phase feature development: code-explorer → code-architect → code-reviewer |
| **code-review** | 5 parallel review agents: CLAUDE.md compliance, bugs, history, PR history, comments |
| **pr-review-toolkit** | 6 specialized PR agents: comment-analyzer, pr-test-analyzer, silent-failure-hunter, type-design-analyzer, code-reviewer, code-simplifier |
| **commit-commands** | /commit, /commit-push-pr, /clean_gone |
| **hookify** | Rule-based hook engine (PreToolUse, PostToolUse, UserPromptSubmit, Stop) |
| **plugin-dev** | 8-phase plugin creation wizard, 7 expert skills |
| **security-guidance** | PreToolUse hook: 9 security pattern warnings |
| **ralph-wiggum** | Self-referential iteration loops (/ralph-loop, /cancel-ralph) |
| **explanatory-output-style** | SessionStart hook: inject educational context |
| **learning-output-style** | SessionStart hook: learning mode prompts |
| **frontend-design** | Auto-invoked skill for frontend work |
| **agent-sdk-dev** | /new-sdk-app command + SDK verifier agents |

#### Official Hook Events (complete list from CHANGELOG)
| Event | Trigger |
|-------|---------|
| UserPromptSubmit | User sends a message |
| PreToolUse | Before any tool executes |
| PostToolUse | After any tool executes |
| Stop | Agent wants to stop |
| StopFailure | Turn ends due to API error |
| SubagentStop | Sub-agent stops |
| TaskCreated | Task created via TaskCreate |
| CwdChanged | Working directory changes |
| FileChanged | File changes on disk |
| WorktreeCreate | Git worktree created |
| SessionEnd | Session ends |

#### Official Settings Schema (key fields Karma must support)
```json
{
  "permissions": {
    "defaultMode": "default|plan|bypassPermissions|auto",
    "allow": ["Bash(git *)", "Edit(src/*)"],
    "deny": ["Bash(rm -rf *)"],
    "ask": ["Bash(npm *)"]
  },
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "filesystem": { "allowWrite": ["/tmp"] }
  },
  "model": "claude-haiku-4-5",
  "hooks": { ... },
  "mcpServers": { ... },
  "deniedMcpServers": ["server-name"],
  "allowedMcpServers": ["server-name"],
  "env": { "KEY": "value" },
  "enabledPlugins": ["plugin-name"],
  "strictKnownMarketplaces": true,
  "allowManagedHooksOnly": true,
  "allowManagedPermissionRulesOnly": true,
  "disableDeepLinkRegistration": false,
  "cleanupPeriodDays": 30
}
```

#### Official Agent Frontmatter Schema
```yaml
---
name: agent-name
description: When to invoke this agent (with examples)
tools: Glob, Grep, LS, Read, Bash, Edit, Write, WebFetch, WebSearch, TodoWrite
model: sonnet|opus|haiku
color: green|yellow|red|blue|purple
effort: low|medium|high
maxTurns: 10
disallowedTools: ["Bash"]
initialPrompt: "Auto-submitted first turn"
---
Agent system prompt here...
```

#### Official Skill Frontmatter Schema
```yaml
---
description: When this skill is auto-invoked
paths: ["src/**/*.ts", "*.py"]
effort: medium
---
Skill instructions here...
```

#### Key Architecture Details from CHANGELOG
- **Permission modes**: default / plan / bypassPermissions / auto
- **Effort levels**: low / medium / high / ultrathink (maps to thinking budget)
- **Context compaction**: auto-triggered, /compact manual, pre-compact hooks fire first
- **Session storage**: transcripts saved, /resume reloads full history
- **MCP OAuth**: RFC 9728, CIMD/SEP-991, Dynamic Client Registration
- **Sandbox**: Linux seccomp sandbox for Bash, configurable filesystem allow/deny
- **Remote Control**: bridge session to claude.ai/code for browser/phone continuation
- **Background agents**: run in parallel, output to files, TaskOutput reads them
- **Git worktrees**: --worktree flag, EnterWorktree/ExitWorktree tools
- **Voice mode**: push-to-talk, WebSocket transcription
- **IDE bridge**: VS Code extension, JetBrains plugin
- **Channels**: MCP servers push messages into session (--channels flag)
- **Rate limits**: 5-hour and 7-day windows tracked, displayed in statusline
- **Token display**: compact format (1.5m), cost tracker per session
- **CLAUDE.md**: project-level instructions loaded into every session context
- **Memory**: auto-extract from sessions, MEMORY.md index (25KB / 200 lines cap)
- **File history**: snapshots before edits, rewind capability
- **Thinking mode**: extended reasoning, configurable budget, ultrathink keyword
- **Parallel tool calls**: multiple tools execute simultaneously
- **Streaming**: line-by-line as generated, SSE fallback
- **Deep links**: claude-cli:// protocol handler
- **Managed settings**: enterprise policy via managed-settings.json + managed-settings.d/
- **Plugin data persistence**: $CLAUDE_PLUGIN_DATA survives updates
- **Plugin marketplace**: installable via /plugin, browseable, per-org allowlists
- **Conditional hooks**: if: field using permission rule syntax
- **OTEL telemetry**: OpenTelemetry traces/metrics/logs with configurable exporters

---

## FINAL DELTA: What official repo adds to Karma vs the other 3

1. **Complete plugin manifest format** — plugin.json schema, all frontmatter fields
2. **Full hook event list** — 11 event types including CwdChanged, FileChanged, TaskCreated, StopFailure
3. **Conditional hooks** — `if:` field for filtering when hooks run
4. **Managed settings** — enterprise policy enforcement layer
5. **Ralph-wiggum** — self-loop iteration pattern (critical for Karma's self-improve)
6. **Security-guidance plugin** — 9 security patterns on PreToolUse
7. **Rate limit tracking** — 5h/7d windows with UI display
8. **CLAUDE.md** — project-level instruction file loaded every session
9. **Deep links** — claude-cli:// protocol
10. **Channels** — MCP push-to-session
11. **Remote Control** — session handoff to browser/phone
12. **Devcontainer** — firewall-isolated sandbox setup (NET_ADMIN/NET_RAW caps)
13. **Official permission syntax** — Bash(git *), Edit(src/**), exact rule grammar
14. **Plugin options** — userConfig with sensitive:true → keychain storage
15. **initialPrompt** agent frontmatter — auto-submit first turn

