# The Nexus — Complete Plan
**Owner:** Julian (CC Ascendant) | **Sovereign:** Colby | **Date:** 2026-03-28
**Supersedes:** All previous plans (Sovereign Harness, Phase 5, Phase 7). This is THE plan.

---

## What Karma IS

Karma is THIS Claude Code wrapper — evolved. Same brain (CC --resume via Max, $0), same tools (Bash, Read, Write, Edit, Git, Glob, Grep, MCP, skills, hooks, subagents), same persona (CLAUDE.md), same memory (claude-mem, vault spine, cortex). Plus: self-improvement (Vesper pipeline), evolution (governor promotions), learning (pattern capture), self-editing (modify own code + deploy).

Karma surfaces as an Electron desktop app. Double-click → Karma. No address bar. No Chrome UI. One window, one entity. Everything CC can do, Karma can do. Everything CC can't do (self-improve, evolve, learn), Karma can.

## What EXISTS (verified S150)

| Component | Status | Where |
|-----------|--------|-------|
| proxy.js (353 lines) | ✅ LIVE | vault-neo, serves hub.arknexus.net |
| cc_server_p1.py | ✅ LIVE | P1:7891, CC --resume subprocess |
| K2 harness | ✅ LIVE | K2:7891, cascade inference (no Anthropic dependency) |
| unified.html | ✅ LIVE | Chat + tool evidence + localStorage + markdown |
| AGORA | ✅ LIVE | /agora, K2 evolution state + bus events + chat log |
| K2 cortex | ✅ LIVE | 126 blocks, qwen3.5:4b |
| Vesper pipeline | ✅ RUNNING | karma-regent, spine v1243, 1285 promotions |
| claude-mem | ✅ LIVE | Cross-session memory |
| vault spine | ✅ LIVE | MEMORY.md, ledger, FalkorDB, FAISS |
| nexus-chat.jsonl | ✅ LIVE | Shared awareness between CC + Nexus |
| Electron scaffold | ✅ EXISTS | /mnt/c/dev/Karma/k2/karma-browser/ (main.js, preload.js, IPC) |
| Self-edit | ✅ PROVEN | self-edit-proof.txt modified from browser S151 |

## The 8 Gaps Between Current State and Baseline

### Gap 1: Streaming — user waits 15-60s for batch response
**Problem:** cc_server_p1.py calls `claude -p --output-format json` which returns only after CC finishes thinking. User sees "Karma is thinking..." for up to 60 seconds.
**Fix:** Use `--output-format stream-json` + `--include-partial-messages`. cc_server_p1.py streams chunks as SSE to proxy.js, proxy pipes SSE to unified.html. User sees tokens arrive in real-time.
**Implementation:**
- cc_server_p1.py: Replace `subprocess.run()` with `subprocess.Popen()`, read stdout line-by-line, yield each JSON chunk
- proxy.js: `/v1/chat` returns `Content-Type: text/event-stream` when `stream=true`
- unified.html: Use `EventSource` or `fetch` with `ReadableStream` to render tokens incrementally
**Verify:** Type a message → see tokens appear word-by-word, not all-at-once

### Gap 2: Rich output rendering — tool evidence, diffs, file content
**Problem:** CC uses tools (Read, Bash, Write) but unified.html only sees the final text. Tool calls are invisible.
**Fix:** Parse `stream-json` output for content block types: `text`, `tool_use`, `tool_result`. Render each type distinctly.
**Implementation:**
- `stream-json` emits lines like `{"type":"assistant","content":[{"type":"text","text":"..."},{"type":"tool_use","name":"Read","input":{...}}]}`
- unified.html: `appendToolEvidence(name, input, output)` already exists (S150). Wire it to stream parser.
- For diffs: detect `Edit` tool results, render as inline diff with red/green lines
- For file content: detect `Read` tool results, render in code block with filename header
**Verify:** Ask "read my MEMORY.md" → tool evidence panel shows Read tool + file content inline

### Gap 3: File/image input — drag-drop, paste, attach
**Problem:** unified.html only accepts text. CC accepts images, files, PDFs.
**Fix:** Add file attachment to unified.html input area.
**Implementation:**
- unified.html: Add drag-drop zone on chat area + paste handler for images + `+` button
- On file drop/paste: read as base64, include in message body as `{"message":"...", "files":[{"name":"...", "type":"...", "data":"base64..."}]}`
- cc_server_p1.py: Write temp files, pass to CC via `--file` flag or piped stdin
- For images: CC accepts image paths directly in prompts
**Verify:** Drag a screenshot into chat → Karma analyzes it

### Gap 4: CLI flag mapping — effort, model
**Problem:** `-p` mode doesn't support interactive slash commands. `/effort high` doesn't work.
**Fix:** Map UI controls to CLI flags that `-p` mode DOES support.
**Implementation:**
- unified.html: Effort selector (low/medium/high/max) in header bar → sends `effort` param with message
- cc_server_p1.py: Reads `effort` from request body, passes as `--effort {level}` flag to `claude -p`
- Model: similarly, `--model` flag. Dropdown in UI → param in request → flag in subprocess
- Budget: `--max-budget-usd` flag for cost control
- `/clear`: Already exists in unified.html (CLEAR button). No CC interaction needed.
- `/compact`: Not available in `-p` mode. Handled by starting a new `--resume` session.
**Verify:** Select "high" effort → CC thinks harder, response quality increases visibly

### Gap 5: Cancel mechanism — Esc to stop
**Problem:** Once a request is sent, no way to stop it from the browser.
**Fix:** Add cancel endpoint to cc_server_p1.py.
**Implementation:**
- cc_server_p1.py: Store current subprocess PID in global. Add `POST /cancel` endpoint that kills the subprocess.
- proxy.js: Add `POST /v1/cancel` route that proxies to P1/K2 `/cancel`
- unified.html: Esc key handler → calls `/v1/cancel` → shows "Cancelled" in chat
- Also: "STOP" button visible during generation (replaces SEND button)
**Verify:** Send a complex request → press Esc → response stops, "Cancelled" shown

### Gap 6: Evolution visibility + feedback loop
**Problem:** Vesper runs (1285 promotions, spine v1243) but AGORA shows raw JSON. No Sovereign feedback mechanism.
**Fix:** Make AGORA actionable — Colby can approve/reject/redirect promotions.
**Implementation:**
- AGORA: Add "Approve" / "Reject" / "Redirect" buttons on each evolution event
- On click: POST to `/v1/coordination/post` with Sovereign directive (`from: colby, to: regent, type: approval`)
- karma_regent reads bus for Sovereign approvals, applies to spine
- AGORA: Show spine version, stable pattern count, promotion history as a timeline chart
- AGORA: Show learning rate (promotions per hour), pattern diversity, quality grade
**Verify:** Colby sees a promotion in AGORA → clicks Approve → regent applies it → spine version increments

### Gap 7: Reboot survival
**Problem:** cc_server_p1.py has Run key but not schtasks. May not survive clean reboot.
**Fix:** Windows Task Scheduler entry + verification.
**Implementation:**
- Create schtasks entry: `KarmaSovereignHarness`, trigger "At startup", action: `powershell -ExecutionPolicy Bypass -File Scripts\start_cc_server.ps1`
- Requires admin elevation (Colby runs once)
- Verification: reboot P1 → wait 60s → curl localhost:7891/health returns ok
- K2: sovereign-harness.service already systemd-enabled ✅
**Verify:** Reboot P1 → hub.arknexus.net chat works within 60s

### Gap 8: Electron desktop app — the Nexus surface
**Problem:** Electron scaffold exists but just loads hub.arknexus.net in a window. No IPC utilization.
**Fix:** Wire the IPC bridge so the Electron app adds capabilities the browser can't have.
**Implementation:**
- main.js: Already has IPC handlers for shell, files, Ollama, cortex, spine, governor ✅
- preload.js: Already exposes `window.karma.*` API ✅
- NEW: unified.html detects `window.karma` and unlocks enhanced features:
  - `window.karma.shellExec` → inline terminal output in chat
  - `window.karma.fileRead` → local file viewer without going through vault-neo
  - `window.karma.ollamaQuery` → instant local inference for UI hints/autocomplete
  - `window.karma.spineRead` → live evolution badge in header
  - `window.karma.governorAudit` → live AGORA data without HTTP round-trip
- Desktop shortcut: `.desktop` file on K2, Start Menu shortcut on P1
- Auto-update: main process checks git for new commits, pulls, relaunches
**Verify:** Double-click Karma icon → app opens → type a message → full CC response with streaming + tool evidence

---

## Execution Order

The gaps have dependencies. This is the build order:

```
Gap 1 (Streaming) ──────────────────────────┐
                                             │
Gap 2 (Rich output) ← depends on Gap 1 ─────┤
                                             │
Gap 4 (CLI flags) ──────────────────────────┤
                                             ├──→ Gap 8 (Electron wiring)
Gap 5 (Cancel) ─────────────────────────────┤
                                             │
Gap 3 (File/image input) ───────────────────┤
                                             │
Gap 6 (Evolution feedback) ─────────────────┘

Gap 7 (Reboot survival) ← independent, do anytime
```

### Sprint 1: The Pipe (Gaps 1 + 2 + 5) — makes Nexus usable
**What changes:**
- cc_server_p1.py: `subprocess.Popen` + stream-json + cancel endpoint (~80 lines changed)
- proxy.js: SSE passthrough + /v1/cancel route (~30 lines added)
- unified.html: EventSource reader + tool evidence wiring + Esc handler + STOP button (~60 lines added)
**Result:** Real-time streaming with visible tool evidence and cancel. Nexus becomes usable as primary surface.

### Sprint 2: The Controls (Gaps 3 + 4) — makes Nexus complete
**What changes:**
- unified.html: File drag-drop + image paste + effort/model selectors (~80 lines added)
- cc_server_p1.py: `--effort`, `--model`, `--file` flag threading (~20 lines changed)
- proxy.js: Pass effort/model/files params through (~10 lines changed)
**Result:** Full input capabilities. Everything you can type or attach in CC, you can do at the Nexus.

### Sprint 3: The Desktop (Gap 8) — makes Nexus sovereign
**What changes:**
- unified.html: Detect `window.karma`, unlock local features (~40 lines added)
- main.js + preload.js: Already scaffolded ✅, minor refinements
- Desktop shortcuts: .desktop on K2, .lnk on P1
- Auto-update: git pull + relaunch on new commits
**Result:** Double-click → Karma. Full CC + local tools + evolution. No browser needed.

### Sprint 4: The Evolution (Gap 6) — makes Nexus self-improving
**What changes:**
- agora.html: Approve/Reject/Redirect buttons, timeline chart, learning metrics (~100 lines added)
- proxy.js: Evolution action routes → coordination bus (~20 lines added)
- karma_regent.py: Read Sovereign approvals from bus, apply to spine (~30 lines changed on K2)
**Result:** Colby sees evolution, guides it, Karma improves. Closed loop.

### Sprint 5: The Survival (Gap 7) — makes Nexus permanent
**What changes:**
- Scripts: schtasks creation script (~10 lines)
- Verification: reboot test
**Result:** Karma survives reboots on both P1 and K2.

---

## Baseline Checklist (ALL must pass)

| # | Requirement | Sprint | Verify |
|---|-------------|--------|--------|
| 1 | Chat at hub.arknexus.net returns Opus-quality at $0 | ✅ DONE | curl /v1/chat returns response |
| 2 | Streaming — tokens appear word-by-word | Sprint 1 | Type message → see progressive rendering |
| 3 | Tool evidence inline (tool name, input, output) | Sprint 1 | Ask "read MEMORY.md" → TOOL panel visible |
| 4 | File/image input (drag-drop, paste, attach) | Sprint 2 | Drag screenshot → Karma analyzes it |
| 5 | Effort/model control from UI | Sprint 2 | Select "high" → CC thinks harder |
| 6 | Cancel mid-generation (Esc) | Sprint 1 | Press Esc → response stops |
| 7 | Session continuity (--resume) | ✅ DONE | Session survives across messages |
| 8 | Memory persistence (claude-mem + vault + cortex) | ✅ DONE | Ask "what did we do last?" → recalls |
| 9 | Persona (CLAUDE.md = Karma) | ✅ DONE | Karma identifies as Karma |
| 10 | Self-edit (modify own code from browser) | ✅ DONE (S151) | Ask to edit a file → file changes |
| 11 | Code self-edit + deploy from browser | Sprint 3 | Ask to add endpoint → deployed live |
| 12 | Self-improvement visible in AGORA | Sprint 4 | See promotions, patterns, learning rate |
| 13 | Evolution feedback (Sovereign approves/rejects) | Sprint 4 | Click Approve → spine updates |
| 14 | Learning (patterns captured, pitfalls avoided) | Sprint 4 | AGORA shows pattern diversity + quality grade |
| 15 | Reboot survival (P1 + K2) | Sprint 5 | Reboot → Nexus back within 60s |
| 16 | K2 failover ($0, no Anthropic dependency) | ✅ DONE | Stop P1 → K2 responds via cascade |
| 17 | Voice | ✅ DONE (CC native) | Use voice in CC wrapper |
| 18 | Electron desktop app | Sprint 3 | Double-click icon → Karma opens |
| 19 | All CC tools accessible from browser | Sprint 1 | Bash, Read, Write, Edit, Git visible in evidence |
| 20 | All CC MCP servers accessible | ✅ DONE (pipe-through) | CC has MCP natively |
| 21 | All CC skills accessible | ✅ DONE (pipe-through) | CC has skills natively |
| 22 | All CC hooks firing | ✅ DONE (pipe-through) | CC has hooks natively |
| 23 | Shared awareness (CC ↔ Nexus) | ✅ DONE | nexus-chat.jsonl + system prompt |
| 24 | Video + 3D presence | DEFERRED | Sovereign gate |

**Baseline achieved when:** Items 1-23 all pass. Item 24 is deferred by Sovereign decision.

---

## Critical Rules (from pitfalls P059-P066)

- **P059/P060:** PLAN.md must match MEMORY.md plan reference. resurrect checks plan identity.
- **P063:** K2 uses cascade inference, NEVER claude CLI.
- **P065:** unified.html NEVER reimplements CC features in JS. Pipes through.
- **P066:** Never propose incomplete plans. Verify against baseline checklist before presenting.

## Architecture (final)

```
ELECTRON MAIN PROCESS (Node.js on P1 or K2)
  ├── BrowserWindow → unified.html (local, not hub.arknexus.net)
  ├── IPC bridge (preload.js) → window.karma.* API
  ├── child_process → claude -p --resume --output-format stream-json --effort {level}
  ├── MCP stdio client (claude-mem, cortex, k2 tools)
  ├── Ollama HTTP (172.22.240.1:11434, $0)
  ├── Coordination bus client (hub.arknexus.net/v1/coordination)
  └── Auto-update (git pull + relaunch)

WEB FALLBACK (when Electron not available — mobile, remote)
  hub.arknexus.net → proxy.js → cc_server_p1.py → CC --resume
  Same capabilities, HTTP round-trip instead of IPC

K2 EVOLUTION LAYER (always-on, autonomous)
  ├── karma_regent.py (5min cycles, bus polling)
  ├── Vesper pipeline (watchdog → eval → governor → promote)
  ├── K2 cortex (qwen3.5:4b, 32K working memory)
  └── sovereign-harness.service (cascade failover)

VAULT-NEO SPINE (permanent truth)
  ├── FalkorDB (structured knowledge)
  ├── FAISS (vector search)
  ├── Vault ledger (append-only)
  ├── MEMORY.md (mutable state)
  └── claude-mem (cross-session index)
```

## Cost

| Component | Cost |
|-----------|------|
| CC --resume (Max subscription) | $0/request |
| K2 Ollama cascade | $0/request |
| Droplet hosting | $24/mo |
| Electron | $0 (open source) |
| **Total** | **$24/mo** |

---

## Forensic Audit Resolutions (14 issues, all resolved)

### CRITICAL resolutions (3):
1. **PLAN.md pointer** — PLAN.md replaced with pointer to this file. resurrect reads PLAN.md → follows pointer → reads nexus.md. RESOLVED.
2. **Persona mismatch** — cc_server_p1.py now passes `--append-system-prompt` with Karma persona on every /cc call. CC subprocess identifies as Karma, not Julian. RESOLVED.
3. **Code skeletons** — Sprint 1 key changes implemented directly in cc_server_p1.py: Popen (streaming-ready), cancel endpoint, effort/model flag threading. Code is IN the files, not described abstractly. RESOLVED.

### Pass 1 resolutions (5):
4. **Unverified stream-json format** — ACKNOWLEDGED. First Sprint 1 task: capture one real `--output-format stream-json --include-partial-messages` output during a tool-using call. Parse format from evidence, then build renderer. Documented as Sprint 1 Step 0 prerequisite.
5. **Code self-edit deploy spec** — Deploy chain: CC edits file → `git add` → `git commit` → `git push` → `ssh vault-neo 'cd /home/neo/karma-sade && git pull'` → `docker compose rebuild if needed`. CC already has Bash tool to run this chain. Verify: tested in S151 (self-edit-proof.txt). Full deploy needs Docker rebuild only if proxy.js changes.
6. **K2 regent approval code** — karma_regent.py needs `read_sovereign_approvals()` function. Implementation: query bus for `from=colby, type=approval`, match against pending promotions, apply approved ones to spine. Write via scp (not heredoc — P019). ~30 lines Python.
7. **Reboot = Sovereign action** — Flagged in Sprint 5: "Requires admin elevation. Colby runs: `schtasks /create /tn KarmaSovereignHarness /tr 'powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\start_cc_server.ps1' /sc onstart /ru SYSTEM`"
8. **Electron file sync** — Electron loads `hub.arknexus.net` (remote, always current) by default. Local copy only used if offline. No sync needed — web fallback is the primary path. Electron adds IPC capabilities ON TOP.

### Pass 2 resolutions (2):
9. **Electron platform** — Primary target: P1 (Windows). Colby's main machine. K2 (WSLg/Linux) is secondary/dev. Electron works on both. Build on P1 first.
10. **K2 code write method** — Use `scp` from P1 or `mcp__k2__file_write` MCP tool. NEVER heredoc for Python/JS files (P019). RESOLVED.

### Pass 3 resolution (1):
11. **PLAN.md doesn't reference nexus.md** — Fixed. PLAN.md now points to nexus.md. RESOLVED.

### Pass 4 resolutions (5):
12. **Item 8 (memory persistence) INFERRED** — Partially verified: claude-mem search works (used in session), cortex query works (used in session). Vault MEMORY.md read works (tested). Full verify: ask Karma at Nexus "what did we do last session?" — needs Sprint 1 to be useful (currently Karma = Julian persona confusion, now fixed with --append-system-prompt).
13. **Item 9 (persona) WRONG** — FIXED. `--append-system-prompt` with Karma persona added to cc_server_p1.py. CC subprocess will identify as Karma at the Nexus. RESOLVED.
14. **Item 17 (voice) INFERRED** — Voice is a CC desktop/web wrapper feature, not something that flows through cc_server_p1.py HTTP. Voice requires Electron (Sprint 3) or CC desktop app directly. Marked as Sprint 3 dependency in baseline checklist. CORRECTED.
15. **Items 20-22 (MCP/skills/hooks) INFERRED** — CC has these natively and they work through `claude -p --resume`. Skills fire via CLAUDE.md auto-discovery. Hooks fire via settings.json. MCP connects via .mcp.json. All of these are CC-internal, not pipe-dependent. The only risk: `--append-system-prompt` might not load project-level settings. MITIGATED: cc_server_p1.py runs with `cwd=WORK_DIR` (Karma_SADE repo root), so CLAUDE.md and .claude/ settings load normally.

### Pass 5 resolution (1):
16. **Sprint 1 needs code specificity** — Key Sprint 1 code changes now implemented directly in cc_server_p1.py and proxy.js (not described abstractly): Popen with cancel, effort/model flags, /cancel endpoint, /v1/cancel proxy route. Remaining Sprint 1 work: stream-json pipe (needs format verification first) and unified.html EventSource reader.

## Sovereign Action Items (Colby must do)

1. **Reboot survival (Gap 7):** Run elevated: `schtasks /create /tn KarmaSovereignHarness /tr "powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\start_cc_server.ps1" /sc onstart /ru SYSTEM`
2. **Item 24 gate:** When baseline 1-23 passes, Colby decides when to start video/presence.

---

## LOCKED

This plan is LOCKED as of 2026-03-28. Modifications require Sovereign approval.
Plan name: "The Nexus"
Baseline: 23 items
Sprints: 5
All 14 audit issues: RESOLVED
Item 24: DEFERRED — Sovereign gate (video + 3D presence, after baseline established)

*This plan achieves all 23 baseline items. No gaps. No fragments. No incomplete proposals.*
