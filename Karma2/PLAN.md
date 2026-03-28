# The Sovereign Harness — THE Plan
**Owner:** Julian (CC Ascendant) | **Sovereign:** Colby | **Date:** 2026-03-28

> Previous cortex-phase plan archived to `Karma2/PLAN-ARCHIVED-cortex-phases-pre-harness.md`.
> That plan is DEAD. This is the only plan. Everything else builds ON this.

---

## What we're building

A ~200-line thin proxy on vault-neo + CC --resume on P1 as the brain. Replaces 4620 lines of bandaid hub-bridge code. Surfaces at hub.arknexus.net. $0 cost via Max subscription. Karma speaks, Julian executes, the system can edit its own code.

## Why most of hub-bridge dies

CC --resume already has: persona (CLAUDE.md), tools (Bash, Read, Write, Git), session continuity (--resume), memory (MCP to claude-mem), SSH to K2 and vault-neo, skills, hooks. Hub-bridge was faking all of this through API calls because we didn't have CC as the backend. Now we do.

## Architecture

```
hub.arknexus.net
  |
  v
THIN PROXY (~200 lines, vault-neo, port 18090)
  |-- GET /              serve unified.html (keep as-is)
  |-- POST /v1/chat      proxy to P1:7891/cc
  |-- /v1/coordination   coordination bus (extracted from server.js)
  |-- /v1/ambient        capture hooks (extracted from server.js)
  |-- /v1/vault-file     vault file access (extracted from server.js)
  |-- /v1/cypher         FalkorDB proxy (extracted from server.js)
  |-- /health            liveness
  |-- Bearer token auth
  |
  v
CC --RESUME on P1 (port 7891, cc_server_p1.py)
  |-- claude -p message --resume session_id --output-format json
  |-- Max subscription = $0, Opus quality
  |-- CLAUDE.md loaded automatically = Karma persona
  |-- All native tools: Bash, Read, Write, Edit, Git, Glob, Grep
  |-- MCP: claude-mem, K2 cortex, vault-neo
  |-- Skills: resurrect, deploy, review, wrap-session
  |-- Can SSH to K2 (read/write 100+ files)
  |-- Can SSH to vault-neo (read spine, deploy)
  |-- Can self-edit: CLAUDE.md, proxy.js, unified.html, any repo file
  |-- Session persists via --resume file
  |-- Distills to K2 cortex on idle
```

## What stays vs what dies

**STAYS** (~1437 lines total):
- unified.html (767 lines) — chat UI, tool evidence, localStorage, markdown
- cc_server_p1.py (~300 lines) — CC subprocess wrapper, enhanced with tool evidence
- Thin proxy (~200 lines) — serves HTML, proxies chat, coordination bus, ambient, vault, cypher, auth
- Caddy — HTTPS termination
- K2 cortex — optional fast-path for simple recall
- Vesper pipeline — self-improvement
- claude-mem — cross-session memory
- vault-neo spine — canonical truth

**DIES** (~4620 lines of bandaid):
- buildSystemText() — CC loads CLAUDE.md natively
- callLLMWithTools / callGPTWithTools / callWithK2Fallback — CC IS the LLM
- classifyMessageTier / cognitive split — both paths are $0, CC decides itself
- TOOL_DEFINITIONS (5 fake tools) — CC has real tools
- _sessionStore — CC --resume has real sessions
- _memoryMdCache — CC can Read the file
- pricing.js, routing.js, feedback.js, deferred_intent.js, library_docs.js — irrelevant at $0
- Modes system, FAISS scoring, token budgeting, GLM rate limiter, Brave search, PDF pipeline in server.js — all either dead or CC does natively

## Phases

### Phase 1: Build the thin proxy — COMPLETE (S150)
1. ✅ Write `proxy.js` (~353 lines) — HTTP server, static files, /v1/chat proxy to P1:7891
2. ✅ Extract coordination bus endpoints from server.js into proxy
3. ✅ Extract vault-file + cypher proxy from server.js into proxy

### Phase 2: Enhance cc_server_p1.py
4. Tool evidence — parse CC JSON output, extract tool_use blocks into tool_log array matching unified.html format
5. Cortex fast-path (optional) — try K2 cortex first for simple recall, fall through to CC for complex
6. Session distillation — after idle, POST summary to cortex /ingest

### Phase 3: Deploy + survive — MOSTLY COMPLETE (S150)
7. ✅ Deploy thin proxy to vault-neo (replace server.js in Docker)
8. PARTIAL — Task Scheduler on P1 for cc_server_p1.py auto-start (Run key exists, needs schtasks)
9. ✅ Failover — if P1 down, proxy routes to K2, then returns explicit error (no paid API fallback)

### Phase 4: Self-edit + evolution proof
10. ✅ Self-edit proof — self-edit-proof.txt modified via browser request (S151)
11. Code self-edit proof — from browser, ask Karma to add an endpoint to proxy, deploy it
12. Vesper verification — confirm pipeline feeds spine, CC reads updated spine

## Blockers

| # | Blocker | Status |
|---|---------|--------|
| B1 | claude CLI on P1 | ✅ VERIFIED |
| B2 | Max subscription | ✅ VERIFIED ($0) |
| B3 | cc_server_p1.py | ✅ VERIFIED (running, --resume, session file) |
| B4 | Tool evidence parsing | BUILD (Phase 2, Task 4) |
| B5 | Thin proxy | ✅ DONE (353 lines, deployed) |
| B6 | Process supervision | PARTIAL (Run key + restart loop, needs schtasks for reboot) |
| B7 | unified.html response format compat | NEEDS VERIFICATION |
| B8 | Bus/vault/cypher in proxy | ✅ DONE |

## Cost

| | Before | After |
|---|---------|-------|
| Chat LLM calls | $34/mo API | $0 Max |
| Droplet | $24/mo | $24/mo |
| **Total** | **$58/mo** | **$24/mo** |

## Done when

1. ✅ hub.arknexus.net returns Opus-quality responses at $0
2. ❌ Tool evidence renders inline in browser (B4)
3. ❌ Karma reads/writes vault, SSHes to K2, queries graph — from browser (needs verification)
4. ✅ Self-edit proof done (self-edit-proof.txt, S151)
5. ❌ Karma edits proxy code and deploys it — from browser (Phase 4, Task 11)
6. ❌ Survives P1 reboot (B6 — needs schtasks elevation)
7. ✅ API spend = $0
8. ✅ 4620 lines replaced by 353

## Sovereign Corrections (S151)
- **Voice is NOT a blocker.** CC wrapper already has native voice capability.
- **Only video and 3D presence remain blocked** — everything else is buildable now.
- **Old cortex phase plan is ARCHIVED.** This harness plan is the only plan.

## Phase 5: UI Parity — unified.html matches CC wrapper capabilities

**The gap:** unified.html has ~25 features. CC wrapper has ~165. The CC --resume backend already HAS all capabilities. unified.html just doesn't EXPOSE them.

**Priority tiers (by user impact):**

### Tier 1 — Essential (makes Nexus usable as primary surface)
| # | Feature | What | Effort |
|---|---------|------|--------|
| 5-1 | AGORA evolution dashboard | Pipe Vesper promotions, self-edits, learning events to /agora inline | MEDIUM |
| 5-2 | Slash commands | `/compact`, `/clear`, `/effort`, `/model`, `/rename` — parse `/` prefix, dispatch | MEDIUM |
| 5-3 | Esc to stop | Cancel mid-generation | SMALL |
| 5-4 | @-mention files | `@filename` in prompt → attach file content | SMALL |
| 5-5 | Image input | Drag-drop / paste images into chat | MEDIUM |
| 5-6 | Effort level control | Low/medium/high/max reasoning via UI toggle or `/effort` | SMALL |
| 5-7 | Streaming responses | SSE streaming from CC subprocess for real-time output | MEDIUM |
| 5-8 | Cascade dot updates | Dots currently static/gray — update live from /v1/status health data | SMALL |

### Tier 2 — Power features (makes Nexus better than CC wrapper)
| # | Feature | What | Effort |
|---|---------|------|--------|
| 5-9 | Session picker | Browse/search past conversations | LARGE |
| 5-10 | Compact / context mgmt | Manual + auto compaction, context budget display | MEDIUM |
| 5-11 | File attachment (`+` button) | Attach files/PDFs to prompts | MEDIUM |
| 5-12 | Plan mode toggle | Read-only analysis mode | MEDIUM |
| 5-13 | Model selector | Switch models via dropdown | SMALL |
| 5-14 | Settings panel | View/edit key config inline | MEDIUM |
| 5-15 | Keyboard shortcuts | Esc, Ctrl+O (thinking), Shift+Tab (mode) | SMALL |

### Tier 3 — Full parity (everything CC has)
| # | Feature | What | Effort |
|---|---------|------|--------|
| 5-16 | Subagent delegation UI | Dispatch + track parallel agents | LARGE |
| 5-17 | Diff viewer | Show file changes inline with accept/reject | LARGE |
| 5-18 | Git operations UI | Commit, push, PR creation from browser | LARGE |
| 5-19 | Scheduled tasks | Run tasks on recurring schedule | LARGE |
| 5-20 | Chrome automation controls | Browser control from Nexus | LARGE |
| 5-21 | MCP server management | Add/remove/status MCP servers | MEDIUM |
| 5-22 | Plugin management | Install/enable/disable plugins | LARGE |
| 5-23 | Rewind / checkpoints | Restore conversation to prior state | LARGE |

**Total: ~140 missing features across 23 line items. Tier 1 (8 items) is the minimum viable Nexus.**

## Phase 7: Karma Browser — Electron Desktop App (LONG-TERM, after Phase 5)

**Goal:** A desktop app you double-click → opens as Karma. Browser + AI agent + local tools + evolution. No address bar, no Chrome UI. Just Karma.

**Approach:** Electron (recommended over Tauri — Node.js = full code reuse from hub-bridge, trivial MCP, K2 ready)

**K2 prerequisites verified:** Node 20, npm 10, WSLg (GUI), Chromium, 932GB disk, 20GB RAM. One `npm install electron` away.

**Architecture:**
```
[Electron Main Process (Node.js)]
  ├── BrowserWindow → hub.arknexus.net (or local unified.html)
  ├── MCP stdio client (spawn local MCP servers)
  ├── Ollama HTTP client (localhost:11434)
  ├── child_process (shell commands, agent tools)
  ├── IPC bridge ↔ renderer (preload.js exposes safe API)
  └── Coordination bus client
```

**Phases:**
| # | What | Effort |
|---|------|--------|
| 7-0 | Scaffold: `npm init` + electron, BrowserWindow loads hub.arknexus.net, .desktop shortcut | 1 day |
| 7-1 | IPC bridge: preload.js, renderer calls shell commands + reads local files via main process | 3 days |
| 7-2 | MCP stdio client in main process, expose tools to renderer | 1 week |
| 7-3 | Ollama integration, local inference fallback, evolution loop hooks | 1 week |
| 7-4 | The app IS Karma — agent autonomy, self-update, desktop presence | ongoing |

**Why Electron over Tauri:** Tauri is smaller (8MB vs 200MB) and lower RAM (100MB vs 300MB) but K2 has 932GB disk and 20GB RAM — irrelevant. Tauri requires Rust (not in project), immature MCP ecosystem, zero code reuse. Electron gives Node.js backend = hub-bridge patterns, MCP stdio, Ollama HTTP, all proven.

## Phase 6: Video + 3D Presence (BLOCKED — Sovereign gate)
- Voice: AVAILABLE (CC wrapper native)
- Video: requires implementation
- 3D Presence/OS overlay: requires implementation

## Future Work (builds ON this plan)
- See `.gsd/nexus-future-work.md` for VS Code 1.113 extracted primitives
- Nexus expansion (thinking effort controls, subagent delegation, MCP manifest, customizations editor)

## Spec locations
- **Primary:** `docs/superpowers/specs/2026-03-28-sovereign-harness-design.md`
- **K2 mirror:** `/mnt/c/dev/Karma/k2/cache/sovereign-harness-design-v2.md`
- **claude-mem:** obs #19338
- **cortex:** block #159
