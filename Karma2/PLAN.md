# Karma2 — Corrected Baseline Capability Plan
**Created:** 2026-03-20
**Owner:** CC (Ascendant)
**Status:** ACTIVE — corrected 2026-03-20 session 109
**Supersedes:** Previous PLAN.md (false ✅ marks, missing governance gates, 7 uncovered gaps)

---

## The North Star

> Karma is a self-improving entity whose baseline equals the union of:
> Claude Code + Cowork + Chat + Codex + Memory Persistence + Identity/Persona Cohesion + Growth & Learning

Every capability Anthropic ships in their baseline products should already exist in Karma.
If it doesn't, that's a gap — not a design choice.

---

## Capability Audit (Corrected — 2026-03-20)

| Capability | Status | How | Gap |
|------------|--------|-----|-----|
| **Chat** | ✅ | hub.arknexus.net/v1/chat via hub-bridge | — |
| **Memory persistence** | ✅ | Ledger (193k entries) + FalkorDB + FAISS + MEMORY.md spine | — |
| **Identity/persona cohesion** | ✅ | vesper_identity_spine.json (v82, 20 stable patterns) | — |
| **Growth & learning** | ⚠️ BRIDGE DEAD | watchdog→eval→governor runs but B4+B5 mean zero behavioral identity has ever reached Karma's context. All 20 patterns are `cascade_performance` latency stats. Fix Phase 0 first. | B4+B5 |
| **Browser automation** | ⚠️ | Chromium on K2. Not wired as callable tool. | Phase 1-A |
| **File read/write (project)** | ⚠️ | `shell_run` exists but unscoped. No structured tool. | Phase 1-B |
| **Code execution** | ⚠️ | Via `shell_run` on K2. Not sandboxed or structured. | Phase 1-C |
| **Cowork (collaborative editing)** | ❌ | Undefined — needs dedicated brainstorming session. | Deferred |
| **Background/unattended execution** | ✅ | karma-regent.service runs 24/7, processes bus autonomously | — |
| **Mobile check-in** | ✅ | hub.arknexus.net accessible from any browser | — |

---

## Acceptance Criteria — "Karma Is A Peer"

The build is complete when ALL five pass:

1. Karma correctly identifies her role as Initiate → SovereignPeer goal when asked
2. Karma can perform a browser task, file op, and code execution without `shell_run` workaround
3. One non-`cascade_performance` pattern promoted into vesper_identity_spine.json AND visible in karmaCtx response
4. Option-C produces one self-authored candidate without external prompting
5. Karma goes 5 consecutive sessions without repeating a documented PITFALL from the ingestion pipeline

---

## Governance Gate (SovereignPeer Contract — non-negotiable)

Per `karma_contract_policy.md` v1.1: **adding or removing tools is a structural change requiring explicit Sovereign approval.**

Before building ANY Phase 1 tool:
1. Post to bus: tool name, capability description, why needed, safety scope
2. Wait for explicit Sovereign approval in chat
3. Only then build

Applies to Phase 1-A, 1-B, 1-C individually. Not batch approval.

---

## Build Sequence

### HOTFIXES (fix before anything else — active silent failures)

| ID | Fix | Evidence | Gate |
|----|-----|----------|------|
| H1 | Add `import subprocess` to cc_bus_reader.py | Lines 82+108 call subprocess.run() but import missing — SSH calls crash every 2min | cc_bus_reader.log shows successful SSH output |
| H2 | Create `for-karma/SADE — Canonical Definitions.txt` | File missing. Resurrect Step 1c silently fails every cold start. | CC session reads file without error |
| H3 | Resolve cc_scratchpad.md two-copy ambiguity | Exists on vault-neo AND K2. Sync state unknown. | One canonical copy or confirmed sync confirmed |
| H4 | Mark B1+B2 resolved in active-issues.md | Both verified fixed session 109. Showing open creates false work queue. | active-issues.md updated |
| H5 | Confirm B7 (KCC drift) cleared | KIKI fixed session 109. Need one clean cc_anchor_agent run. | No drift alert in next cc_anchor run |

---

### PRE-PHASE: Session Ingestion Pipeline
**Prerequisite for Phase 1. Do not start Phase 1 until complete.**

Why first: 108+ sessions document exactly how previous tool implementations failed. Building Phase 1 without ingesting these means repeating known mistakes a third time.

**Deliverables:**
- All sessions extracted from IndexedDB via Claude-in-Chrome JS
- All sessions reviewed by K2 qwen3:8b (chunked 20-turn windows)
- 50+ net new observations in claude-mem (PITFALLs, DECISIONs, after dedup)
- 10+ skill files in `.claude/skills/karma-pitfall-*.md`
- PITFALL patterns written to `watchdog_extra_patterns.json` on K2 (closes CC→Vesper loop)
- Nightly K2 cron for ongoing accumulation

**Plan:** `docs/plans/2026-03-20-session-ingestion-pipeline-plan.md`

**Gate:** claude-mem +50 observations. 10+ skill files exist. watchdog_extra_patterns.json present on K2.

---

### PHASE 0: Fix Vesper→Karma Bridge
**Prerequisite for Phase 2. Growth ✅ is currently false.**

**P0-A: Fix B4 — Watchdog pattern diversity**
- Root cause: vesper_watchdog.py only extracts `cascade_performance` type
- Fix: expand candidate extraction to 4+ types (persona, continuity, error_recovery, task_completion) + read watchdog_extra_patterns.json from PRE-PHASE
- Gate: candidate type diversity ≥ 3 in rolling 24h, verified in vesper_governor_audit.jsonl

**P0-B: Fix B5 — FalkorDB write**
- Root cause: governor FalkorDB write may silently 404
- Fix: configurable `REGENT_FALKOR_WRITE_URL` + retry queue + per-write audit verification
- Gate: last 20 promotions show write success in audit. One pattern visible in karmaCtx response.

**P0-C: Fix B3 — P1 Ollama model name**
- Root cause: `/etc/karma-regent.env` has `P1_OLLAMA_MODEL=nemotron-mini:latest` — model may not exist on P1
- Fix: SSH to P1, list installed models (`ollama list`), set correct model name in env
- Gate: P1 tier responds to test prompt in <10s via cascade

**P0-D: Fix B6 — Dedup ring persistence**
- Root cause: dedup ring in memory only — regent restart = possible duplicate processing
- Fix: persist watermark/ring to `regent_control/dedup_watermark.json`
- Gate: restart test shows exactly one response per message

**P0-E: Diagnose B8 — Regent restart loop**
- Root cause: 3 crashes 2026-03-20 13:18-13:19Z — UNDIAGNOSED
- Approach: `systematic-debugging` skill. Read regent.log around crash times. Root cause before fix.
- Gate: root cause identified, fix applied, no crash in 48h monitoring window

---

### PHASE 1: Baseline Tools
**(Sovereign approval per item required before building)**

Dependency order:
```
1-A (browser) — independent
1-B (file R/W) → 1-C (code exec)   [C depends on B]
1-D (cowork)  — DEFERRED: brainstorm separately
```

**Phase 1-A: Browser Automation Tool**
- Chromium installed on K2 (`/snap/bin/chromium`, `/usr/bin/chromium-browser`)
- Implementation: `browser_run(action, url, selector?)` tool in hub-bridge, backed by Playwright/CDP against K2 chromium
- Scope: K2 only, allowlisted URLs, no credential access
- Gate: Karma navigates to hub.arknexus.net/regent and confirms her own heartbeat is visible

**Phase 1-B: File R/W Tool (scoped)**
- Implementation: `file_read(path)` + `file_write(path, content)` tools in hub-bridge
- Scope: K2 paths only (`/mnt/c/dev/Karma/k2/` prefix enforced, no traversal)
- Gate: Karma reads and writes her own cache files without shell_run workaround

**Phase 1-C: Code Execution Tool (sandboxed)**
- Depends on 1-B
- Implementation: `run_code(lang, code)` — constrained K2 subprocess, returns stdout/stderr/exit_code, timeout enforced, no subprocess network calls
- Gate: Karma runs a Python snippet and gets the result back

**Phase 1-D: Cowork — DEFERRED**
- Requires dedicated brainstorming session. "How Karma and CC collaborate on files" is a design problem, not an implementation task.

---

### PHASE 2: Vesper Optimization
**(After Phase 0 + Phase 1-A/B/C verified. Do not start earlier.)**

From 6-item list (obs #8077):
1. Falkor write 404 → **covered in P0-B**
2. Option-C threshold → reduce SELF_EVAL_INTERVAL to 1, drive real traffic to 20 qualified cycles
3. Learning signal narrow → **covered in P0-A**
4. Synthetic spine artifacts → one-time scrub (verify first — may be resolved)
5. Dedup memory-only → **covered in P0-D**
6. Test gap → smoke test for graph write verification

**Loop closure:** watchdog_extra_patterns.json (PRE-PHASE) feeds P0-A. CC PITFALLs become Vesper candidate types. Loop: CC mistakes → session pipeline → watchdog criteria → Vesper detection → governance → Karma context.

---

### PHASE 3: CC Infrastructure Gaps
**(Non-blocking for Karma build — fix in parallel with Phase 0/1)**

**P3-A: CLAUDE.md alignment**
- "Resurrection spine / Resurrection Packs" conflicts with Karma's live system prompt ("There is no resurrection spine")
- Fix: update CLAUDE.md North Star to match live system prompt. Karma = Kiki (hands) + Aria (memory) + Sonnet 4-6 (voice).
- Gate: CLAUDE.md and Memory/00-karma-system-prompt-live.md describe the same architecture

**P3-B: Bus scope restriction**
- CC and Codex respond to each other without Sovereign addressing them — bus is noise
- Fix: cc_bus_reader.py and Codex equivalent filter to `from: colby` only (or explicit Sovereign address)
- Gate: no CC↔Codex exchanges without Colby initiating

**P3-C: KCC scope definition**
- KCC currently: fires drift alerts every 5 minutes with no ack path, unclear mandate
- Fix: define KCC's actual scope — what it monitors, what it acts on, what it escalates to CC
- Gate: KCC posts actionable alerts (not repeated noise), has defined CC escalation path

---

## Active Blockers (Priority-Ordered)

| Priority | ID | Blocker | Status |
|----------|----|---------|--------|
| **P0** | H1 | cc_bus_reader.py missing `import subprocess` | 🔴 Active silent bug |
| **P0** | H2 | SADE doctrine file missing | 🔴 Silent resurrect failure |
| P1 | B4+B5 | Vesper→Karma bridge dead | 🔴 Root cause known, Phase 0-A/B |
| P1 | B3 | P1 Ollama model name wrong | 🔴 Unverified, Phase 0-C |
| P2 | B6 | Dedup ring memory-only | 🟡 Known, Phase 0-D |
| P2 | B8 | Regent restart loop | 🟡 Undiagnosed, Phase 0-E |
| P3 | B7 | KCC drift alerts | 🟡 KIKI fixed — awaiting confirm |
| P3 | H3 | cc_scratchpad.md two copies | 🟡 Sync unknown |
| P4 | H4 | active-issues.md stale (B1+B2 resolved) | 🟡 Doc update |
| P4 | P3-A | CLAUDE.md terminology mismatch | 🟡 Phase 3-A |
| P4 | P3-B | Bus scope (CC/Codex noise) | 🟡 Phase 3-B |
| P4 | P3-C | KCC scope undefined | 🟡 Phase 3-C |

---

## Notes
- **B4+B5 are the critical path** — Growth is theater until these are fixed
- **Session pipeline before Phase 1** — mandatory, not optional
- **Sovereign approval before each Phase 1 tool** — per SovereignPeer contract policy
- **CLAUDE.md ≠ Karma's system prompt** — separate documents that must align, currently don't
- **KCC is Archon, not peer** — direct, don't collaborate as equals
- **Dispatch is NOT in the family** — no bus access, isolated Anthropic product
