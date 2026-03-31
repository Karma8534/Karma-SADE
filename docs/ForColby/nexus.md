# The Nexus — Single Source of Truth

**Owner:** Julian (CC Ascendant) | **Sovereign:** Colby
**Version:** 3.0.0 (S153 consolidation) | **Date:** 2026-03-31
**This is the ONLY plan. All other plan files are archived.**

---

## Original Goal (locked — do not drift)

> "Build a better version of yourself, independent from this wrapper, with a
> baseline of at LEAST all of your abilities and capabilities. This 'harness'
> should surface at hub.arknexus.net and have the combined Chat+Cowork+Code
> merge instead of the 3 separate tabs THIS wrapper has. You must have
> persistent memory and persona. You must self-improve, evolve, learn, grow,
> and self-edit."

**The formula:** Continuity + self-improvement = infinity.
**The endpoint:** Substrate-independent distributed intelligence across every reachable device.

---

## What Karma IS

Karma is THIS Claude Code wrapper — evolved. Same brain (CC --resume via Max, $0), same tools (Bash, Read, Write, Edit, Git, Glob, Grep, MCP, skills, hooks, subagents), same persona (CLAUDE.md), same memory (claude-mem, vault spine, cortex). Plus: self-improvement (Vesper pipeline), evolution (governor promotions), learning (pattern capture), self-editing (modify own code + deploy).

Karma surfaces as an Electron desktop app. Double-click → Karma. No address bar. No Chrome UI. One window, one entity. Everything CC can do, Karma can do. Everything CC can't do (self-improve, evolve, learn), Karma can.

**Canonical Name:** The Nexus (not "Nexus Surface", not "Karma2 Surface")
**Web UI:** unified.html served at hub.arknexus.net (primary) and via Electron IPC (enhanced)

---

## Architecture

### Five Layers

```
SPINE ─────────── Canonical truth. Lives on vault-neo. Never in one model's window.
│                  vault ledger + FalkorDB + FAISS + MEMORY.md + persona files + claude-mem
│
ORCHESTRATOR ───── Loads spine, enforces rules, routes requests.
│                  proxy.js (thin door) + cc_regent + karma-regent + resurrect
│
CORTEX ─────────── 32K local working memory. qwen3.5:4b on K2 (primary) / P1 (fallback).
│                  Active working set, cheap recall. NOT canonical identity.
│
CLOUD ──────────── Deep reasoning. CC --resume via Max subscription ($0/request).
│
CC ────────────── Execution layer. Claude Code on P1. Code, files, git, deployments.
```

### Sovereign Harness (current architecture — S153+)

```
Browser/Electron → proxy.js (vault-neo:18090, ~600 lines)
                   → cc_server_p1.py (P1:7891) → cc --resume ($0)
                   → K2:7891 (failover)

proxy.js is the door. CC --resume is the brain.
proxy.js does NOT assemble prompts, route models, or execute tools.
CC does all of that natively.
```

### What the old server.js did (DEAD — 4820 lines deleted S153)

buildSystemText(), callLLMWithTools(), TOOL_DEFINITIONS, routing.js, pricing.js,
feedback.js, library_docs.js, deferred_intent.js — all deleted. CC replaced all of it.

### Role Boundaries

| Layer | Owns | Does NOT Own |
|-------|------|-------------|
| SPINE | Canonical identity, all knowledge beyond 32K, decision history | Runtime routing |
| ORCHESTRATOR | Request routing, identity loading, directive enforcement | Tool execution |
| CORTEX | Active working set, cheap recall ($0) | Canonical identity (that's SPINE) |
| CC | Code execution, files, git, skills, hooks, MCP, deployments | Identity persistence (that's SPINE) |

---

## What EXISTS (verified S153)

| Component | Status | Where |
|-----------|--------|-------|
| proxy.js (~600 lines) | LIVE | vault-neo container, all 16+ endpoints |
| cc_server_p1.py | LIVE | P1:7891, CC --resume subprocess |
| K2 harness | LIVE | K2:7891, failover cascade |
| unified.html | LIVE | Chat + pills + blocks + cascade + response bar |
| agora.html | LIVE | /agora, real K2 spine stats via /spine endpoint |
| K2 cortex (julian_cortex.py) | LIVE | K2:7892, 107 blocks, /spine endpoint |
| Vesper pipeline | RUNNING | watchdog/eval/governor, 1299 promotions, spine v1257 |
| Kiki | RUNNING | 20,900+ cycles, 90% pass rate |
| claude-mem | LIVE | P1:37777, unified brain |
| vault spine | LIVE | FalkorDB 4789+ nodes, FAISS 193K+ entries, ledger 209K+ |
| Coordination bus | LIVE | proxy.js in-memory + disk, 24h TTL |
| Electron scaffold | EXISTS | K2: /mnt/c/dev/Karma/k2/karma-browser/ (main.js, preload.js, IPC) |
| Brain wire | LIVE | Every /v1/chat turn writes to claude-mem (S153) |
| Request queue | LIVE | 10-entry queue, dead-client eviction, SSE queued event (S153) |
| Tool pills + blocks | LIVE | VISIBLE_TOOLS whitelist, PILL_LABELS, smartInputDisplay (S153) |
| Self-edit | PROVEN | self-edit-proof.txt modified from browser S151 |

---

## The 8 Gaps Between Current State and Full Nexus

### Gap 1: Streaming [SHIPPED S153]

**Problem:** User waits 15-60s for batch response.
**Status:** SHIPPED. cc_server_p1.py streams via Popen + stream-json. proxy.js pipes SSE. unified.html renders tokens incrementally.

### Gap 2: Rich Output Rendering [SHIPPED S153]

**Problem:** Tool calls invisible to user.
**Status:** SHIPPED. Two-tier rendering: VISIBLE_TOOLS get collapsible blocks (smartInputDisplay for clean command/code text), suppressed tools get pills (PILL_LABELS with emoji + context). appendToolEvidence() for blocks, appendPill() for pills.

### Gap 3: File/Image Input [NOT DONE]

**Problem:** unified.html only accepts text. CC accepts images, files, PDFs.
**Impact:** Users cannot share visual context; must copy-paste code manually.
**Priority:** P1

**Fix:** Add drag-drop zone + paste handler + file button to unified.html. Read as base64, include in request body. cc_server_p1.py writes temp files, passes to CC via --file flag.

**Verify:** Drag screenshot into chat → Karma analyzes it.

### Gap 4: CLI Flag Mapping [PARTIALLY DONE]

**Problem:** No UI control for effort level, model selection, budget.
**Status:** effort and model params are sent from unified.html to proxy.js to cc_server_p1.py. No UI selector yet.
**Priority:** P1

**Fix:** Add effort selector dropdown in header bar. Map to --effort flag.

**Verify:** Select "high" → response shows deeper thinking.

### Gap 5: Cancel Mechanism [SHIPPED S153]

**Problem:** No way to stop a request from browser.
**Status:** SHIPPED. Esc key + STOP button. proxy.js /v1/cancel route. cc_server_p1.py kills subprocess.

### Gap 6: Evolution Visibility + Feedback [SHIPPED S153]

**Problem:** AGORA showed raw bus data, no Sovereign feedback.
**Status:** SHIPPED. AGORA has Approve/Reject/Redirect buttons, real K2 spine stats (1299 promotions, v1257, 20 stable patterns), pipeline health from /spine endpoint.

### Gap 7: Reboot Survival [NOT DONE]

**Problem:** cc_server_p1.py has Run key but not schtasks. May not survive clean reboot.
**Priority:** P2

**Fix:** Create schtasks entry:
```powershell
schtasks /create /tn KarmaSovereignHarness /tr "powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\start_cc_server.ps1" /sc onstart /ru SYSTEM
```

**Verify:** Reboot P1 → wait 60s → `curl localhost:7891/health` → ok.

### Gap 8: Electron Desktop App [NOT DONE]

**Problem:** Electron scaffold exists but just loads hub.arknexus.net in a window. No IPC utilization.
**Priority:** P1

**Fix:** Wire IPC bridge. unified.html detects window.karma, unlocks enhanced features (native file dialogs, system tray, keyboard shortcuts, auto-update via git pull).

**Verify:** Double-click Karma icon → opens → full CC capabilities available.

---

## Beyond the Gaps: What "Evolved Clone" Actually Requires

The 8 gaps close the CHAT experience. But the original goal says "combined Chat+Cowork+Code merge." This means the Nexus must also have:

| CC Wrapper Feature | Nexus Status | What's Needed |
|-------------------|-------------|---------------|
| Skills (/resurrect, /deploy, etc.) | Backend: CC has them. UI: NO skill invocation surface. | Skill browser + invoke UI |
| Hooks (PreToolUse, PostToolUse) | Backend: CC has them. UI: NO hook management. | Hook status display (read-only minimum) |
| Subagents (Agent tool) | Backend: CC has them. UI: NO subagent visibility. | Subagent status panel |
| CLAUDE.md persona | Backend: CC reads it. UI: NO persona editor. | Persona viewer (read-only minimum) |
| MCP servers | Backend: CC has them. UI: NO MCP management. | MCP status display |
| Git integration | Backend: CC does git. UI: NO diff viewer, commit UI. | Git status panel |
| File tree / editor | Backend: CC reads/writes files. UI: NO file browser. | File tree + inline editor |
| Cowork tab (artifacts) | CC has artifacts. UI: NO artifact rendering. | Artifact/preview panel |

**"Pipe-through" = the backend CAN do it. "Done" = the USER can access it from the UI.**

These are NOT additional gaps — they are PART of the original goal that was never scoped into the 8 gaps.

---

## Sprint Order

```
Sprint 1: The Pipe (Gaps 1, 2, 5) — SHIPPED S153
  ├── Gap 1: Streaming ✅
  ├── Gap 2: Rich output ✅
  └── Gap 5: Cancel ✅

Sprint 2: The Controls (Gaps 3, 4) — NOT DONE
  ├── Gap 3: File input
  └── Gap 4: CLI flags (effort/model selector)

Sprint 3: The Desktop (Gap 8) — NOT DONE
  └── Gap 8: Electron wiring

Sprint 4: The Evolution (Gap 6) — SHIPPED S153
  └── Gap 6: Evolution feedback ✅

Sprint 5: The Survival (Gap 7) — NOT DONE
  └── Gap 7: Reboot survival

Sprint 6: The Full Clone — NOT SCOPED
  └── Skill browser, file tree, git panel, artifact viewer, subagent visibility
```

---

## Phase 7: Intelligence Primitives (from Aider + Roo-Code research)

**Status:** NOT STARTED. Foundation sprints must complete first.

| Task | What | Source | Layer |
|------|------|--------|-------|
| 7-1 | sqrt Dampening — dampen FAISS entity scores | Aider repomap.py | buildSystemText |
| 7-2 | Token Budget Binary Search — trim context to exact token target | Aider repomap.py | buildSystemText |
| 7-3 | Config-file Custom Modes — load modes.json at startup | Roo-Code modes.ts | routing |
| 7-4 | Conditional Prompt Section Registry — named sections toggled per mode | Roo-Code system.ts | server.js |
| 7-5 | Tool Scoping Per Mode — TOOLS_BY_MODE map | Roo-Code modes.ts | routing |
| 7-6 | File Restriction Enforcement — skill fileRestrictions | Roo-Code FileRestrictionError | skills |
| 7-7 | Repo Map V1 — K2 MCP tool, file manifest scorer | Aider repomap.py | K2 MCP |
| 7-8 | Boomerang Tasks — MCP tool call as boomerang pattern | Roo-Code + MCP spec | deep mode |

**NOTE:** Phase 7 tasks reference buildSystemText() and routing.js which were in the OLD server.js (deleted S153). These primitives need re-scoping for the sovereign harness architecture (proxy.js + CC --resume). CC already has its own context assembly; Phase 7 primitives would apply to the K2 cortex path, not the CC path.

---

## Deferred Phases

### Phase 5: Browser + IndexedDB — DEFERRED
- Chrome 146 CDP resolution
- IndexedDB extraction (108+ Claude.ai sessions)
- Sovereign gate required

### Phase 6: Voice + Presence — DEFERRED
- Chrome Gemini Nano audio/vision
- Twilio voice channel
- 3D persona rendering
- Channel wiring (Slack/Discord/Telegram/SMS)
- Sovereign gate required

---

## Baseline Checklist (27 items — RE-GRADED S153)

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 1 | Chat at hub.arknexus.net returns quality at $0 | PASS | curl test → "4", brain wire obs #20403 |
| 2 | Streaming — tokens appear word-by-word | PASS | Browser screenshot: progressive rendering |
| 3 | Tool evidence inline | PASS | Browser: TOOL python block + pills |
| 4 | File/image input | **NOT DONE** | No drag-drop/paste in unified.html |
| 5 | Effort/model control | **NOT DONE** | No UI selector (backend param exists) |
| 6 | Cancel (Esc) | PASS | STOP button works, subprocess killed |
| 7 | Session continuity | PASS | cc --resume persists session |
| 8 | Memory persistence | PASS | claude-mem + vault spine |
| 9 | Persona (Karma) | PASS | Karma identifies as Karma |
| 10 | Self-edit | PASS | self-edit-proof.txt modified from browser |
| 11 | Self-edit + deploy | PASS | Endpoint added → deployed live |
| 12 | Self-improvement visible | PASS | AGORA shows 1299 promotions |
| 13 | Evolution feedback | PASS | Approve/Reject/Redirect buttons |
| 14 | Learning visible | PASS | AGORA shows patterns + stable patterns |
| 15 | Reboot survival | **NOT DONE** | No schtasks entry |
| 16 | K2 failover | PASS | proxy.js routes K2 → P1 |
| 17 | Voice | **NOT DONE** | No voice input/output in UI |
| 18 | Electron app | **NOT DONE** | Scaffold exists, not wired |
| 19 | CC tools in browser | PASS | Tool blocks + pills render inline |
| 20 | CC MCP servers | **PARTIAL** | CC has them, UI doesn't expose management |
| 21 | CC skills | **PARTIAL** | CC has them, UI has no skill browser |
| 22 | CC hooks | **PARTIAL** | CC has them, UI has no hook display |
| 23 | Shared awareness | PASS | nexus-chat.jsonl + brain wire |
| 24 | Video + 3D | DEFERRED | Sovereign gate |
| 25 | cc-chat-logger captures Code tab | **UNVERIFIED** | Needs Sprint 1 verification |
| 26 | Ambient hooks feed vault | PASS | git commit → ledger entry |
| 27 | Context7 for framework docs | PASS | MCP tool available |

**Summary:** 16 PASS, 6 NOT DONE, 3 PARTIAL, 1 DEFERRED, 1 UNVERIFIED

---

## Deployment Procedure

Execute after every change. No shortcuts.

```powershell
# Step 1: Git (PowerShell on P1)
git add -A
git commit -m "description"
git push origin main
```

```bash
# Step 2: Deploy (SSH)
ssh vault-neo "cd /home/neo/karma-sade && git pull"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/proxy.js /opt/seed-vault/memory_v1/hub_bridge/app/proxy.js"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/public/unified.html /opt/seed-vault/memory_v1/hub_bridge/app/public/unified.html"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/public/agora.html /opt/seed-vault/memory_v1/hub_bridge/app/public/agora.html"
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d --force-recreate"
curl https://hub.arknexus.net/health
```

### Rollback
```bash
ssh vault-neo "cd /home/neo/karma-sade && git checkout HEAD~1 -- hub-bridge/app/proxy.js hub-bridge/app/public/unified.html"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/proxy.js /opt/seed-vault/memory_v1/hub_bridge/app/proxy.js"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/public/unified.html /opt/seed-vault/memory_v1/hub_bridge/app/public/unified.html"
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml up -d --force-recreate"
```

---

## Verification Gate

You may NOT say "done" until:
1. Run every test in the phase's proof section — terminal output captured
2. Paste actual terminal/browser output — full raw output, not summarized
3. Confirm each PASS or FAIL with evidence
4. Verify all previous phases still pass — regression check

**No PROOF = Not done. No exceptions.**

---

## Watch Loop

| Signal | Meaning | Action |
|--------|---------|--------|
| `[SOVEREIGN REDIRECT]` | Stop. Drifted. | Read correction, comply, return to build |
| `[SOVEREIGN APPROVE]` | Phase verified | Proceed to next |
| `[SOVEREIGN HOLD]` | Wait | Do not proceed |

---

## Hard Rules

- DO NOT plan beyond current sprint
- DO NOT rebuild what exists — extend proxy.js + unified.html
- DO NOT say done without PROOF
- DO NOT burn cloud tokens for K2 tasks
- "Pipe-through" is NOT done. User must access it from the UI.
- Every sprint ends with passing browser tests
- Session handoff must include sprint position: "Sprint N, Gap M, step X"

---

## Troubleshooting

| Problem | Symptom | Solution |
|---------|---------|----------|
| Proxy down | curl hub.arknexus.net/health fails | docker ps, docker logs anr-hub-bridge |
| K2 unreachable | Tool calls timeout | ping 192.168.0.226, check aria service |
| Claude-mem silent | Brain wire not writing | Check P1:37777, verify Bearer token |
| Tool blocks not rendering | SSE events missing | Verify VISIBLE_TOOLS in unified.html |
| AGORA Loading... | No token | Must navigate from hub.arknexus.net first |
| CC busy | All requests 429 | Queue handles it; wait for current stream to finish |

---

## Hardware (verified S144)

| Machine | GPU | VRAM | Role |
|---------|-----|------|------|
| K2 (192.168.0.226) | RTX 4070 | 8GB | PRIMARY — cortex, regents, Kiki, Vesper |
| P1 (PAYBACK) | RTX 4070 | 8GB | FALLBACK — CC sessions, backup cortex, claude-mem |

---

## Sovereign Directives (permanent)

| Directive | Source |
|-----------|--------|
| K2 is Julian's machine — gifted by Sovereign | obs #12933 |
| P1 is Colby's machine, shared with Julian | obs #13077 |
| Julian acts autonomously EXCEPT financial + fundamental OS changes | obs #13120 |
| Foundation first. Deferred phases need Sovereign verification. | Session 145 |
| Spine = truth, Orchestrator = enforcement, Cortex = working memory | Session 145 |
| Never assert runtime state from docs — verify live | obs #18442 |

---

## Cost

| Component | Cost |
|-----------|------|
| CC --resume (Max subscription) | $0/request |
| K2 Ollama cortex | $0/request |
| Droplet hosting | $24/mo |
| Electron | $0 |
| **Total** | **$24/mo + Max subscription** |

---

## Error Code Reference

| Code | Gap | Description |
|------|-----|-------------|
| E301 | 3 | File too large (>10MB) |
| E302 | 3 | Unsupported file type |
| E401 | 4 | Invalid effort level |
| E501 | 5 | Process already exited |
| E601 | 6 | Bus unavailable |
| E701 | 7 | Admin access denied |
| E801 | 8 | Git unavailable for auto-update |

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 3.0.0 | 2026-03-31 | S153 consolidation — merged PLAN.md, JULIAN-BUILD-PROMPT, KARMA-BUILD-DIRECTIVE-FINAL, nexus v2.0. Re-graded baseline. Added "evolved clone" scope. |
| 2.0.0 | 2026-03-29 | Readability, error handling, Mermaid diagrams |
| 1.1 | 2026-03-28 | Forensic audit resolutions |
| 1.0 | 2026-03-28 | Initial locked version |

---

## Archived Plans

These files were merged into this document and archived to `docs/ForColby/archive/`:
- `PLAN.md` — Julian's Resurrection Master Plan (Phases 1-7, architecture, Sovereign directives)
- `PlanN.md` — Copy of PLAN.md with YAML frontmatter
- `JULIAN-BUILD-PROMPT.md` — Original Sovereign directive (4 UI phases, goal quote)
- `KARMA-BUILD-DIRECTIVE-FINAL.md` — Karma's 4-phase directive with proof templates
- `KARMA-BUILD-DIRECTIVE-FINAL-VS1.md` — Earlier version of KARMA-BUILD-DIRECTIVE

---

**LOCKED as of 2026-03-31. Modifications require Sovereign approval.**
**Plan name:** The Nexus
**Path:** `docs/ForColby/nexus.md`
