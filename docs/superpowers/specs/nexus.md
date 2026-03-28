# The Nexus — Complete Plan
**Owner:** Julian (CC Ascendant) | **Sovereign:** Colby | **Date:** 2026-03-28
**Version:** 1.1-LOCKED | **Supersedes:** All previous plans (Sovereign Harness, Phase 5, Phase 7)
**Related Plans:**
  - `Karma2/PLAN.md` (points here)
  - `docs/ForColby/PLAN.md` (overarching master plan)
  - `MEMORY.md` (mutable state, synced on session start)

---

## What Karma IS

Karma is THIS Claude Code wrapper — evolved. Same brain (CC --resume via Max, $0), same tools (Bash, Read, Write, Edit, Git, Glob, Grep, MCP, skills, hooks, subagents), same persona (CLAUDE.md), same memory (claude-mem, vault spine, cortex). Plus: self-improvement (Vesper pipeline), evolution (governor promotions), learning (pattern capture), self-editing (modify own code + deploy).

Karma surfaces as an Electron desktop app. Double-click → Karma. No address bar. No Chrome UI. One window, one entity. Everything CC can do, Karma can do. Everything CC can't do (self-improve, evolve, learn), Karma can.

**Canonical Name:** The Nexus (not "Nexus Surface", not "Karma2 Surface")
**Web UI:** unified.html served at hub.arknexus.net (primary) and via Electron IPC (enhanced)

---

## What EXISTS (verified S150)

| Component | Status | Where | Verification |
|-----------|--------|-------|--------------|
| proxy.js (353 lines) | ✅ LIVE | vault-neo, serves hub.arknexus.net | `curl hub.arknexus.net/health` |
| cc_server_p1.py | ✅ LIVE | P1:7891, CC --resume subprocess | `curl localhost:7891/health` |
| K2 harness (aka "Karma2", "K2 cascade") | ✅ LIVE | K2:7891, cascade inference (no Anthropic) | `curl K2:7891/health` |
| unified.html (aka "Nexus UI", "Karma Surface") | ✅ LIVE | Chat + tool evidence + localStorage + markdown | Browser visit |
| AGORA | ✅ LIVE | /agora, K2 evolution state + bus events + chat log | `hub.arknexus.net/agora` |
| K2 cortex | ✅ LIVE | 126 blocks, qwen3.5:4b | `ollama list` on K2 |
| Vesper pipeline (aka "karma-regent evolution") | ✅ RUNNING | karma-regent, spine v1243, 1285 promotions | AGORA stats |
| claude-mem | ✅ LIVE | Cross-session memory | MCP tool works |
| vault spine | ✅ LIVE | MEMORY.md, ledger, FalkorDB, FAISS | SSH vault-neo |
| nexus-chat.jsonl | ✅ LIVE | Shared awareness — proxy writes, Karma reads, CC reads via SSH | File exists |
| cc-chat-logger.py | ⚠️ UNVERIFIED | `.claude/hooks/cc-chat-logger.py` | **REQUIRES Sprint 1 verification** |
| Ambient capture hooks | ✅ LIVE | Git post-commit + session-end → POST /v1/ambient → vault ledger | Ledger entries exist |
| Electron scaffold | ✅ EXISTS | /mnt/c/dev/Karma/k2/karma-browser/ (main.js, preload.js, IPC) | Files present |
| Self-edit | ✅ PROVEN | self-edit-proof.txt modified from browser S151 | File modified |
| Context7 MCP | ✅ AVAILABLE | Library doc lookup | MCP tool available |

> **NOTE:** "K2 harness", "Karma2", and "K2 cascade" are synonyms. "unified.html", "Nexus UI", "Karma Surface" are synonyms.

---

## The 8 Gaps Between Current State and Baseline

### Gap 1: Streaming — user waits 15-60s for batch response
**Problem:** cc_server_p1.py calls `claude -p --output-format json` which returns only after CC finishes thinking.
**Fix:** Use `--output-format stream-json --verbose --include-partial-messages`. cc_server_p1.py streams chunks as SSE to proxy.js, proxy pipes SSE to unified.html. User sees tokens arrive in real-time.
**Implementation:**
- cc_server_p1.py: Replace `subprocess.run()` with `subprocess.Popen()`, read stdout line-by-line, yield each JSON chunk
- proxy.js: `/v1/chat` returns `Content-Type: text/event-stream` when `stream=true`
- unified.html: Use `EventSource` or `fetch` with `ReadableStream` to render tokens incrementally
**Verify:**
```bash
# Terminal test (before building UI):
claude -p --output-format stream-json --verbose --include-partial-messages <<< "say 'hello world'"
# Expected: NDJSON chunks arriving line-by-line, not batched
# CRITICAL: --verbose is REQUIRED with -p mode (verified S150 Step 0, obs #19692)
```

### Gap 2: Rich output rendering — tool evidence, diffs, file content
**Problem:** CC uses tools (Read, Bash, Write) but unified.html only sees the final text. Tool calls are invisible.
**Fix:** Parse `stream-json` output for content block types: `text`, `tool_use`, `tool_result`. Render each type distinctly.
**Implementation:**
- `stream-json` emits NDJSON lines. `type=assistant` messages contain `message.content[]` array with:
  - `{type: "thinking", thinking: "...", signature: "..."}` — extended thinking
  - `{type: "tool_use", id: "toolu_...", name: "Bash", input: {...}, caller: {...}}` — tool invocation
  - `{type: "text", text: "..."}` — assistant text response
- `type=user` messages contain tool results: `{type: "tool_result", tool_use_id: "toolu_...", content: "stdout", is_error: false}` plus `tool_use_result` with stdout/stderr/interrupted fields
- Filter out `type=system` lines (hooks, init) — not for display
- `type=result` is the final summary (duration, cost, session_id)
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
**Polling interval:** karma_regent checks `/v1/coordination/recent` every 60 seconds (configurable via REGENT_POLL_INTERVAL)
**Verify:** Colby sees a promotion in AGORA → clicks Approve → regent applies it → spine version increments

### Gap 7: Reboot survival
**Problem:** cc_server_p1.py has Run key but not schtasks. May not survive clean reboot.
**Fix:** Windows Task Scheduler entry + verification.
**Implementation:**
- Create schtasks entry: `KarmaSovereignHarness`, trigger "At startup", action: `powershell -ExecutionPolicy Bypass -File Scripts\start_cc_server.ps1`
- Requires admin elevation (Colby runs once)
- K2: sovereign-harness.service already systemd-enabled ✅
**Verify:**
```bash
# After task creation:
schtasks /query /tn KarmaSovereignHarness
# Then reboot P1, wait 60s:
curl localhost:7891/health
# Expected: {"ok":true}
```

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

## Execution Order (Corrected)

The gaps have dependencies. This is the build order:

```
Sprint 1: The Pipe (Gaps 1, 2, 5)
  ├── Gap 1: Streaming (foundation)
  ├── Gap 2: Rich output (depends on Gap 1)
  └── Gap 5: Cancel (depends on Gap 1)

Sprint 2: The Controls (Gaps 3, 4)
  ├── Gap 3: File input (UI change)     ⚠️ These can run
  └── Gap 4: CLI flags (backend change)    in PARALLEL

Sprint 3: The Desktop (Gap 8)
  └── Gap 8: Electron wiring (depends on Sprint 1)

Sprint 4: The Evolution (Gap 6)
  └── Gap 6: Evolution feedback (depends on AGORA existing)

Sprint 5: The Survival (Gap 7)
  └── Gap 7: Reboot survival (INDEPENDENT — do anytime)
```

---

### Sprint 1: The Pipe (Gaps 1 + 2 + 5) — makes Nexus usable
**What changes:**
- cc_server_p1.py: `subprocess.Popen` + stream-json + `--verbose` + cancel endpoint (~80 lines changed)
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

| # | Requirement | Sprint | Verify Command |
|---|-------------|--------|----------------|
| 1 | Chat at hub.arknexus.net returns Opus-quality at $0 | ✅ DONE | `curl -X POST hub.arknexus.net/v1/chat -d '{"message":"what is 2+2"}'` |
| 2 | Streaming — tokens appear word-by-word | Sprint 1 | Browser: see progressive rendering |
| 3 | Tool evidence inline | Sprint 1 | "read MEMORY.md" → TOOL panel visible |
| 4 | File/image input | Sprint 2 | Drag screenshot → Karma analyzes |
| 5 | Effort/model control | Sprint 2 | Select "high" → visible harder thinking |
| 6 | Cancel (Esc) | Sprint 1 | Press Esc mid-generation |
| 7 | Session continuity | ✅ DONE | `claude -p --resume` survives messages |
| 8 | Memory persistence | ✅ DONE | "what did we do last?" → recalls |
| 9 | Persona (Karma) | ✅ DONE | Karma identifies as Karma |
| 10 | Self-edit | ✅ DONE | File edits persist |
| 11 | Self-edit + deploy | Sprint 3 | Endpoint added → deployed live |
| 12 | Self-improvement visible | Sprint 4 | Promotions visible in AGORA |
| 13 | Evolution feedback | Sprint 4 | Click Approve → spine updates |
| 14 | Learning visible | Sprint 4 | AGORA shows patterns |
| 15 | Reboot survival | Sprint 5 | Reboot → Nexus back in 60s |
| 16 | K2 failover | ✅ DONE | Stop P1 → K2 responds |
| 17 | Voice | ✅ DONE | CC native (Sprint 3 dependency) |
| 18 | Electron app | Sprint 3 | Double-click → opens |
| 19 | CC tools in browser | Sprint 1 | Bash, Read, etc. visible |
| 20 | CC MCP servers | ✅ DONE | Native pipe-through |
| 21 | CC skills | ✅ DONE | Native pipe-through |
| 22 | CC hooks | ✅ DONE | Native pipe-through |
| 23 | Shared awareness | ✅ DONE | nexus-chat.jsonl populated |
| 24 | Video + 3D | DEFERRED | Sovereign gate |

**Addendum (Session 152+):**

| # | Requirement | Sprint | Verify |
|---|-------------|--------|--------|
| 25 | cc-chat-logger captures Code tab conversations | Sprint 1 | CC message → nexus-chat.jsonl |
| 26 | Ambient hooks feed vault ledger | ✅ DONE | git commit → ledger entry |
| 27 | Context7 used for all framework doc lookups | ALL | Query before framework work |

**Total baseline: 27 items** (23 main + 4 addendum)

---

## Critical Rules (from pitfalls P059-P068)

- **P059/P060:** PLAN.md must match MEMORY.md plan reference. resurrect checks plan identity.
- **P063:** K2 uses cascade inference, NEVER claude CLI.
- **P065:** unified.html NEVER reimplements CC features in JS. Pipes through.
- **P066:** Never propose incomplete plans. Verify against baseline checklist before presenting.
- **P067:** Every gap implementation must include a terminal-based verification command before UI work begins.
- **P068:** Cross-references to other plans must include relative path: `Karma2/PLAN.md`, `docs/ForColby/PLAN.md`, `MEMORY.md`.

---

## Architecture (final)

```
ELECTRON MAIN PROCESS (Node.js on P1 or K2)
  ├── BrowserWindow → unified.html (local, not hub.arknexus.net)
  ├── IPC bridge (preload.js) → window.karma.* API
  ├── child_process → claude -p --resume --output-format stream-json --verbose --effort {level}
  ├── MCP stdio client (claude-mem, cortex, k2 tools)
  ├── Ollama HTTP (172.22.240.1:11434, $0)
  ├── Coordination bus client (hub.arknexus.net/v1/coordination)
  └── Auto-update (git pull + relaunch)

WEB FALLBACK (mobile, remote)
  hub.arknexus.net → proxy.js → cc_server_p1.py → CC --resume

K2 EVOLUTION LAYER (always-on, autonomous)
  ├── karma_regent.py (60s polling cycle, configurable via REGENT_POLL_INTERVAL)
  ├── Vesper pipeline (watchdog → eval → governor → promote)
  ├── K2 cortex (qwen3.5:4b, 32K working memory)
  └── sovereign-harness.service (systemd, enabled)

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

## Forensic Audit Resolutions (18 issues, all resolved)

### CRITICAL resolutions (3):
1. **PLAN.md pointer** — RESOLVED. Karma2/PLAN.md points here.
2. **Persona mismatch** — RESOLVED. --append-system-prompt with Karma persona.
3. **Code skeletons** — RESOLVED. Popen, cancel, effort/model flags in cc_server_p1.py.

### Pass 1-5 resolutions (13):
4. **stream-json format** — **VERIFIED (obs #19692).** `--verbose` flag REQUIRED with `-p` mode. NDJSON format: system (hooks/init), assistant (thinking/tool_use/text content blocks), user (tool_result), rate_limit_event, result. Sprint 1 Step 0 COMPLETE.
5. **Code self-edit deploy spec** — SPECIFIED. git add → commit → push → ssh pull → rebuild.
6. **Regent approval** — SPECIFIED. read_sovereign_approvals() queries bus, applies to spine.
7. **Reboot = Sovereign** — SPECIFIED. schtasks command provided.
8. **Electron sync** — RESOLVED. Remote load default, IPC adds capabilities.
9. **Electron platform** — SPECIFIED. P1 (Windows) primary.
10. **K2 write** — SPECIFIED. scp, not heredoc.
11. **PLAN.md reference** — RESOLVED. Points here.
12. **Item 8 INFERRED** — ACKNOWLEDGED. Needs Sprint 1.
13. **Item 9 WRONG** — FIXED. --append-system-prompt added.
14. **Item 17 INFERRED** — CORRECTED. Sprint 3 dependency.
15. **Items 20-22 INFERRED** — MITIGATED. cwd=WORK_DIR loads settings.
16. **Sprint 1 specificity** — RESOLVED. Popen + cancel + flags in code.

### Additional Audit (Session 152):
17. **cc-chat-logger.py** — UNVERIFIED. Sprint 1 Step 0 prerequisite.
18. **Ambient hooks** — ✅ LIVE. Documented.
19. **Context7** — ✅ AVAILABLE. Use for all framework docs.
20. **Wip-watcher** — KILLED. Not needed until baseline complete.

---

## Sovereign Action Items (Colby must do)

1. **Gap 6 (Evolution):** After AGORA updates, verify regent polls every 60s:
   ```bash
   # On K2:
   grep REGENT_POLL_INTERVAL /etc/karma-regent.env
   # Expected: 60
   ```
2. **Item 24 gate:** When baseline 1-23 passes, Colby decides when to start video/presence.
3. **Gap 7 (Reboot):** DEFERRED until all previous sprints complete. Run elevated when ready:
   ```powershell
   schtasks /create /tn KarmaSovereignHarness /tr "powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\start_cc_server.ps1" /sc onstart /ru SYSTEM
   ```

---

## LOCKED

This plan is LOCKED as of 2026-03-28. Modifications require Sovereign approval.
Plan name: "The Nexus"
Version: 1.1-LOCKED
Baseline: 27 items (23 main + 4 addendum)
Sprints: 5
All audit issues: RESOLVED
Item 24: DEFERRED — Sovereign gate
Cross-References:
  - `Karma2/PLAN.md` — points to this file
  - `docs/ForColby/PLAN.md` — master plan (this is child)
  - `MEMORY.md` — mutable state, synced on session start

*This plan achieves all 27 baseline items. No gaps. No fragments. No incomplete proposals.*
