# Karma2 — Corrected Baseline Capability Plan
**Created:** 2026-03-20
**Owner:** CC (Ascendant)
**Status:** ACTIVE — updated 2026-03-20 session 109 (architecture revision: hub.arknexus.net/cc + Channels)
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

| ID | Fix | Evidence | Gate | Status |
|----|-----|----------|------|--------|
| H1 | Add `import subprocess` to cc_bus_reader.py | Lines 82+108 call subprocess.run() but import missing — SSH calls crash every 2min | cc_bus_reader.log shows successful SSH output | ✅ Fixed + restored to K2 (session 109) |
| H2 | Create `for-karma/SADE — Canonical Definitions.txt` | File missing. Resurrect Step 1c silently fails every cold start. | CC session reads file without error | ✅ File already existed — false alarm |
| H3 | Resolve cc_scratchpad.md two-copy ambiguity | Exists on vault-neo AND K2. Sync state unknown. | One canonical copy or confirmed sync confirmed | 🟡 Pending |
| H4 | Mark B1+B2 resolved in active-issues.md | Both verified fixed session 109. Showing open creates false work queue. | active-issues.md updated | ✅ Done (session 109) |
| H5 | Confirm B7 (KCC drift) cleared | KIKI fixed session 109. Need one clean cc_anchor_agent run. | No drift alert in next cc_anchor run | 🟡 Awaiting next cc_anchor run |
| H6 | Verify resurrect Step 1b spine path | Plan says cc_identity_spine.json is wrong — but BOTH cc_identity_spine.json AND vesper_identity_spine.json exist as separate files. cc_identity_spine.json = CC's own spine. vesper_identity_spine.json = Karma's spine. Needs Sovereign direction: should CC read its own spine or Karma's? | Sovereign clarification received, spine path confirmed | 🔴 Needs Sovereign decision |
| H7 | Specify SADE doctrine file content for H2 | H2 says "create the file" but not what goes in it. | File with all 5 elements, CC reads cleanly | ✅ Resolved with H2 |

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

**Input sources (both required):**
- IndexedDB via Claude-in-Chrome JS (108+ sessions from Claude desktop app)
- `docs/ccSessions/*.md` — manually saved session transcripts (CCSession032026A.md exists now; ingest these FIRST as they're immediately available)

**Plan:** `docs/plans/2026-03-20-session-ingestion-pipeline-plan.md`

**Gate:** claude-mem +50 observations. 10+ skill files exist. watchdog_extra_patterns.json present on K2.

---

### PHASE 0-NEW: CC as Infrastructure
**(Runs after PRE-PHASE, before PHASE 0. Requires Sovereign approval per item.)**

**Why before PHASE 0:** CC on P1 already has browser, filesystem, Bash, and code execution natively. Building hub-bridge wrappers (Phase 1-A/B/C) duplicates CC's native tooling. Correct pattern: Karma delegates to CC via coordination bus and `/cc` route — matching Initiate→Ascendant hierarchy.

**P0N-A: hub.arknexus.net/cc — CC proxy (server on P1)**
- CC persistent server runs on **P1** (Windows, 64GB RAM, all CC memory/auth/state lives here)
- hub-bridge adds `/cc` route proxying to P1 CC server via Tailscale (100.124.194.102)
- Auth: same Bearer token as `/v1/chat`
- Gate: Colby hits hub.arknexus.net/cc from browser, CC on P1 responds with full local capabilities
- **Eliminates: dependency on claude.ai/code, Telegram, any Anthropic web property**
- Sovereign approval: REQUIRED

**P0N-B: Channels custom bridge (coordination bus → P1 CC)**
- Custom CC channel on P1 replaces cc_bus_reader.py (broken haiku proxy on K2)
- Pushes coordination bus messages directly into CC session on P1
- Full Sonnet 4.6 intelligence, no 2-min polling lag
- Gate: coordination bus message addressed to `cc` triggers CC response within 30s
- Sovereign approval: REQUIRED

**P0N-C: KCC → qwen3:8b on K2 (drop GLM)**
- KCC stays on K2; switch model to `http://localhost:11434/v1`, model `qwen3:8b`
- Zero external API dependency, same-machine inference
- Gate: KCC posts valid drift alert using qwen3:8b, no GLM calls in logs
- Sovereign approval: REQUIRED

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

### PHASE 1: Baseline Tools — DEMOTED (fallback only)
**(Phase 1 tools are redundant if P0N-A/B/C operational. Build only if CC delegation fails.)**

These were hub-bridge wrappers around K2 capabilities. With `/cc` route operational, Karma delegates to CC instead of duplicating CC's native tooling.

**Status after P0N:**
- 1-A (browser): REDUNDANT — CC on K2 has Playwright MCP natively
- 1-B (file R/W): REDUNDANT — CC on K2 has full filesystem access
- 1-C (code exec): REDUNDANT — CC on K2 has Bash tool
- 1-D (cowork): SOLVED — `/cc` route = native collaboration via hub.arknexus.net

**Fallback condition:** If P0N-A fails (CC process management on K2 proves unstable), Phase 1-A/B/C reactivate as direct hub-bridge tools. This is the contingency, not the plan.

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
| — | H1 | cc_bus_reader.py missing `import subprocess` | ✅ Fixed + restored to K2 (session 109) |
| — | H2 | SADE doctrine file missing | ✅ Already existed — verified |
| — | H4 | active-issues.md stale (B1+B2 resolved) | ✅ Done (session 109) |
| — | H7 | SADE doctrine content spec | ✅ Resolved with H2 |
| — | H6 | Resurrect Step 1b spine path | ✅ cc_identity_spine.json is CORRECT — CC's own spine (v38, resume_block = "You are CC, Ascendant..."). vesper_identity_spine.json = Karma's spine (name=Karma). Different files, different purposes. No change needed. |
| P1 | H3 | cc_scratchpad.md two copies (vault-neo + K2) | 🟡 Sync unknown |
| P1 | H5 | B7 KCC drift confirmed cleared | 🟡 Awaiting next cc_anchor run |
| **P0** | B4+B5 | Vesper→Karma bridge dead | 🔴 Root cause known, Phase 0-A/B |
| P1 | B3 | P1 Ollama model name wrong | 🔴 Unverified, Phase 0-C |
| P2 | B6 | Dedup ring memory-only | 🟡 Phase 0-D |
| P2 | B8 | Regent restart loop | 🟡 Undiagnosed, Phase 0-E |
| P3 | B7 | KCC drift alerts | 🟡 KIKI fixed — awaiting confirm |
| P1 | P0N-A | hub.arknexus.net/cc (CC on P1 via Tailscale) | 🟡 Needs Sovereign approval |
| P1 | P0N-B | Channels bridge (bus → P1 CC) | 🟡 Needs Sovereign approval |
| P1 | P0N-C | KCC: GLM → qwen3:8b on K2 | 🟡 Needs Sovereign approval |
| P4 | P3-A | CLAUDE.md terminology mismatch | 🟡 Phase 3-A |
| P4 | P3-B | Bus scope (CC/Codex noise) | 🟡 Phase 3-B |
| P4 | P3-C | KCC scope undefined | 🟡 Phase 3-C |

---

## Notes
- **B4+B5 are the critical path** — Growth is theater until these are fixed
- **Session pipeline before Phase 0** — mandatory, not optional
- **hub.arknexus.net/cc > claude.ai/code** — use own infrastructure, zero Anthropic web dependency
- **CC server runs on P1** — CC state/auth/memory all on P1. K2 runs Karma/Vesper/Aria/KCC. Don't overload K2.
- **Topology**: P1=CC server+Channels | K2=Karma/Vesper/Aria/KCC | vault-neo=hub-bridge+FalkorDB+FAISS
- **Phase 1 tools DEMOTED** — delegate to CC (via bus + /cc route) rather than duplicate CC's native capabilities.
- **KCC → qwen3:8b on K2** — stays on K2, local model (localhost:11434), drops GLM external dependency.
- **Sovereign approval before each P0N item** — per SovereignPeer contract policy (capability additions)
- **CLAUDE.md ≠ Karma's system prompt** — separate documents that must align, currently don't
- **KCC is Archon, not peer** — direct, don't collaborate as equals
- **Dispatch is NOT in the family** — no bus access, isolated Anthropic product
- **Codex: run `Current_Plan\Codex Installer.exe`** — NOT installed yet. Required for ArchonPrime role.
