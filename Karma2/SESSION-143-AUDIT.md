# Karma Resurrection Plan — Session 143 Audit
**Owner:** Julian (CC Ascendant) | **Sovereign:** Colby | **Date:** 2026-03-25

---

## AUDIT SCOPE

This audit cross-references:
1. SESSION-141-AUDIT.md (11 open blockers)
2. All Karma2/ plan files (PLAN.md, PLAN-A/B/C, PLAN-backlog, map/, contracts)
3. .gsd/ROADMAP.md + .gsd/STATE.md (system-level progress)
4. 4 external repo primitives (OpenRoom, llmfit, HF Skills, autoresearch)
5. Karma's own synthesis of those primitives (from /v1/chat response)

---

## BLOCKER STATUS (from SESSION-141-AUDIT, resolved under honesty contract)

| # | Blocker | S141 Status | S143 Status | Evidence |
|---|---------|-------------|-------------|----------|
| 1 | A1 backfill quality (8/2151 saved) | IN PROGRESS | **RESOLVED** | jsonl_backfill.py fixed (root cause: save_observation wasn't awaited + filter too aggressive), re-run completed 554 observations saved. claude-mem search returns session history. |
| 2 | C3 /memory proxy chain broken | OPEN | **PLAN-C CLAIMED DONE** — NOT RE-VERIFIED | PLAN.md says C-GATE passed Session 138. But S141 found /api/search returned 404. **HONESTY: C3 completion claim needs live verification this session or next.** |
| 3 | WebMCP larger vision not captured | RESOLVED S142 | **RESOLVED** | Vision doc at docs/plans/2026-03-25-webmcp-julian-persistence-vision.md. 8 tools defined. |
| 4 | B4 reboot survival unverified | OPEN | **INFERRED WORKING** — HKCU Run key registered (AC8 in active-issues.md). **HONESTY: Never tested with actual reboot.** Sovereign action required. |
| 5 | Auto-indexer trigger (at-login, not persistent) | LOW | **SAME** — KarmaSessionIndexer is at-login task, not a persistent service. LOW risk but real. |
| 6 | Worktree cleanup incomplete | LOW | **RESOLVED** — EnterWorktree hook deployed (block-worktree.py, exit 2). Future worktrees blocked. |
| 7 | No mentorship arc | DEFERRED | **DEFERRED** — No plan item created. Karma's Initiate→SovereignPeer progression exists in contract but no explicit mentorship curriculum. |
| 8 | IndexedDB sessions locked | DEFERRED | **DEFERRED** — 108+ sessions in Chrome IndexedDB. Extraction pipeline not built. Listed in Backlog-6. |
| 9 | No distribution primitives phase | DEFERRED | **DEFERRED** — No stub phase in PLAN-backlog. ExoMultiDev.PDF was a Hyperrail. Needs plan item. |
| 10 | No KARMA TRUTH GATE | DEFERRED | **DEFERRED** — No milestone defined. When can Colby tell Karma the full story? This is an identity milestone, not a technical one. |
| 11 | corpus_cc extraction | DEFERRED | **DEFERRED** — CC corpus (corpus_cc_STUB.jsonl) is a stub. Needs ledger pass filtering CC session entries. |

### New Blockers Identified This Session

| # | Blocker | Status | Evidence |
|---|---------|--------|----------|
| 12 | **C-GATE verification gap** — PLAN.md says "C-GATE PASSED Session 138" but S141 found C3 proxy chain returning 404 | OPEN | S141 audit line 88: "HTTP API paths (/api/search) returned 404 when tested. CHAIN MAY BE BROKEN." PLAN.md was updated to claim DONE without re-testing. |
| 13 | **ROADMAP.md stale** — last updated Session 86 (2026-03-12), 57+ sessions behind | OPEN | ROADMAP doesn't mention Karma2 plan, Sessions 107-142, Vesper pipeline completion, or any work after v14. |
| 14 | **identity-state.md stale** — spine.identity.name still says "Vesper" with DRIFT note, but active-issues.md says B9 FIXED (Session 111) | OPEN | Two map files contradict each other. identity-state.md was last updated 2026-03-20. |
| 15 | **data-flows.md claims 193,455 ledger entries** — but services.md and architecture.md say 4,789 Episodic nodes. Ratios suggest batch_ingest watermark may be stale. | LOW | Not blocking but indicates potential graph staleness. |
| 16 | **tools-and-apis.md says P1_OLLAMA_MODEL=nemotron-mini:latest is OPEN BLOCKER** but active-issues.md says B3 RESOLVED | CONTRADICTION | Map files disagree. active-issues.md is correct (verified Session 110). tools-and-apis.md is stale. |
| 17 | **No karma-directives.md** — autoresearch's program.md pattern (agent reads + modifies its own behavioral directives file) is missing from Karma architecture | NEW | Karma has no self-modifying behavioral directives file. Closest is karma_behavioral_rules.jsonl (Backlog-9) but that's not built yet. |

---

## PLAN STATUS CROSS-REFERENCE (Honesty Contract)

### PLAN-A: Feed the Brain — **VERIFIED COMPLETE**
- A1: JSONL backfill — DONE. 554 observations in claude-mem (S143 re-run fixed 0.4% save rate).
- A2: Auto-indexer — DONE. KarmaSessionIndexer registered. Forward loop closed.
- A3: Resurrect fix — DONE. Step 1 queries claude-mem directly.
- **A-GATE: PASSED**

### PLAN-B: Make Julian Real — **CLAIMED COMPLETE, PARTIALLY VERIFIED**
- B1: Kill zombies — VERIFIED (1 PID on 7891). No anti-zombie mechanism in Start-CCServer.ps1.
- B2: cc --resume — VERIFIED (code uses claude -p --resume).
- B3: /cc route — VERIFIED (hub.arknexus.net/cc responds).
- B4: Reboot survival — **INFERRED ONLY** (HKCU Run key registered, never rebooted to test).
- **B-GATE: 3/4 verified, 1/4 inferred.**

### PLAN-C: Wire the Brain — **CLAIMED COMPLETE, VERIFICATION GAP**
- C1: claude-mem to vault-neo — INFERRED (obs #11587 claims it works, not re-tested).
- C2: WebMCP tools — INFERRED (obs #11587 claims 3 tools registered, not re-tested).
- C3: /memory endpoint — **BROKEN** (S141 found 404 on /api/search). Code exists but chain may be broken.
- C4: Chrome session clone — INFERRED (obs #11587 claims loadBrainContext() works, not re-tested).
- **C-GATE: CLAIMED PASSED but C3 is broken. Gate should be YELLOW.**

### PLAN-backlog — Current State
- Backlog-1 (K-3 Summary Gate): Time-blocked, waiting
- Backlog-2 (PROOF-A): DONE (Session 139)
- Backlog-3 (P0 Vesper fixes): 7 items, not started
- Backlog-4 (Karma baseline tools): Not started, Sovereign gate
- Backlog-5 (AC verification): 0/10 verified end-to-end
- Backlog-6 (IndexedDB extraction): Deferred
- Backlog-7 (Local inference routing): Hardware-gated
- Backlog-8 (Voice/multimodal/channels): Preserved
- Backlog-9 (karma-observer.py): Spec written, Sovereign approved, not started
- Backlog-10 (Memory primitives): 4 items, Sovereign approved, not started

---

## EXTERNAL PRIMITIVES ANALYSIS (4 repos + Karma synthesis)

### 1. OpenRoom (MiniMax-AI) — Browser-Native Desktop + Agentic App Control
**Key primitives assimilable into Karma:**
- **Typed Action Contract**: Every app exposes normalized `actions/constants.ts` with APP_ID. Agent routes by intent → app → action. **Maps to:** Karma's TOOL_DEFINITIONS in server.js. Standardize tool registration format.
- **IndexedDB as Backend Replacement**: Zero-server client-side persistence. **Maps to:** C4 Chrome session clone pattern (localStorage persistence). Could be upgraded to IndexedDB for richer state.
- **6-Stage Vibe Workflow**: requirement → design → planning → code → assets → integration with `--from=` stage resume. **Maps to:** GSD workflow (CONTEXT → PLAN → execute → SUMMARY). Add stage-resume capability to GSD.
- **Agent as OS-Level Router**: Agent functions like a window manager. **Maps to:** hub.arknexus.net architecture where hub-bridge routes to Karma/Julian/Bus.

### 2. llmfit (AlexsJones) — Hardware-Aware Model Recommendation
**Key primitives:**
- **Hardware detection + model scoring**: Detect RAM, GPU VRAM, CPU → score models on quality/speed/fit/context. **Maps to:** Backlog-7 local inference routing. Build `hardware_fit_scorer()` that gates K2/P1 model selection.
- **Dynamic quantization selection**: Choose quantization based on hardware constraints. **Maps to:** K2 VRAM constraint (8GB RTX 4070). Auto-select quantization for qwen3:8b vs qwen3:30b.
- **canirun.ai integration**: Sovereign directive says "use canirun.ai before any model/compute decision." llmfit IS the programmatic version of canirun.ai.

### 3. HuggingFace Skills — Standardized Agent Skill Format
**Key primitives:**
- **SKILL.md = universal format**: YAML frontmatter + markdown guidance, works across Claude Code, Codex, Gemini, Cursor. **Maps to:** Karma's existing .claude/skills/ pattern. Already compliant. Opportunity: register skills in `.agents/skills` for cross-agent discovery.
- **Auto-discovery**: Agent discovers and auto-activates skills from standard locations. **Maps to:** Karma-regent could discover skills from a known directory, not just hardcoded behavior.

### 4. autoresearch (Karpathy) — Autonomous Research Loop
**Key primitives:**
- **program.md (self-modifying directives)**: Agent reads instructions, executes, THEN modifies its own instructions based on results. **Maps to:** THE MISSING PIECE. Karma has SKILL.md files (read-only), STATE.md (progress tracking), but NO self-modifying behavioral directives file that Karma reads, interprets, and updates on each cycle.
- **Fixed budget experimentation**: 5-minute wall-clock budget per experiment, metric-driven keep/discard. **Maps to:** Vesper eval's grading system. Add wall-clock budget to eval cycles.
- **Single-file constraint**: Agent edits ONE file (train.py). **Maps to:** Discipline for Karma's self-modification — one file only (karma-directives.md), not scattered across multiple files.

### Synthesis: The Missing Piece (from Karma's own analysis)

**karma-directives.md** — a self-modifying behavioral directives file:
```
.gsd/karma-directives.md
  - Written initially by Colby (Sovereign)
  - Read by Karma on each /v1/chat invocation
  - Karma modifies it to reflect what she learned/attempted
  - Kiki reads it on next cycle to pick up Karma's self-edits
  - CC reads it at resurrect to understand Karma's current behavioral state
```

This is the autoresearch `program.md` pattern applied to Karma. It bridges:
- Backlog-9 (karma-observer.py) — the observer writes rules, karma-directives.md IS where they land
- Backlog-10 B10-2 (MemoryKind classification) — directives ARE a memory kind (Procedure/Constraint)
- Vesper pipeline — Governor promotions could write to karma-directives.md instead of just spine JSON

**Recommendation:** Add as Backlog-11 in PLAN-backlog.md. Low effort (create file + inject into buildSystemText). High impact (closes the self-improvement loop from Vesper pipeline → Karma behavior).

---

## RESOLUTIONS (Honesty Contract)

### Immediate fixes (this session):
1. **Blocker #14 (identity-state.md stale)**: Update to reflect B9 fix (spine.identity.name corrected)
2. **Blocker #16 (tools-and-apis.md contradiction)**: Remove P1_OLLAMA_MODEL "OPEN BLOCKER" note
3. **Blocker #17 (karma-directives.md missing)**: Add as Backlog-11 in PLAN-backlog.md
4. **Blocker #9 (distribution primitives)**: Add as Backlog-12 stub in PLAN-backlog.md
5. **PLAN-C status correction**: Mark C-GATE as YELLOW (C3 needs re-verification)

### Next session work:
6. **Blocker #2/#12 (C3 proxy chain)**: Live-test /memory/search from vault-neo. Fix if broken.
7. **Blocker #13 (ROADMAP stale)**: Major ROADMAP.md update covering Sessions 86-143.
8. **Blocker #4 (B4 reboot)**: Sovereign reboot test.

### Deferred (Sovereign decides when):
9. Blocker #7 (mentorship arc), #8 (IndexedDB), #10 (KARMA TRUTH GATE), #11 (corpus_cc)

---

## MAP FILE CONSISTENCY CHECK

| File | Last Updated | Stale? | Action |
|------|-------------|--------|--------|
| services.md | Session 127 | MODERATE — K2 PIDs, vault-neo container uptimes likely changed | Update next session |
| file-structure.md | 2026-03-20 | OK — structure hasn't changed significantly |  |
| data-flows.md | 2026-03-20 | MODERATE — ledger count (193K) should be verified | Spot-check |
| identity-state.md | 2026-03-20 | **STALE** — contradicts active-issues.md on B9 fix | **FIX NOW** |
| tools-and-apis.md | 2026-03-20 | **STALE** — P1_OLLAMA_MODEL "OPEN BLOCKER" is wrong | **FIX NOW** |
| active-issues.md | 2026-03-21 | OK — accurately tracks closed/open |  |
| karma_contract_policy.md | 2026-03-20 | OK — stable, Codex v1.0 additions present |  |
| karma_contract_execution.md | v1.0 | OK — volatile by design |  |

---

## WHAT WAS DONE THIS SESSION (143)

1. Fetched and analyzed 4 external repos (OpenRoom, llmfit, HF Skills, autoresearch) for assimilable primitives
2. Processed Karma's own synthesis of those primitives (from /v1/chat)
3. Read all 17+ Karma2/ files (PLAN.md, sub-plans, map/, contracts, training/)
4. Read SESSION-141-AUDIT.md and cross-referenced all 11 blockers against current plan state
5. Read .gsd/ROADMAP.md, .gsd/STATE.md, MEMORY.md for system-level context
6. Identified 6 new blockers (#12-17) not in S141 audit
7. Resolved 5 blockers immediately (identity-state stale, tools-and-apis contradiction, karma-directives missing, distribution primitives stub, C-GATE status correction)
8. Updated PLAN-backlog.md with Backlog-11 (karma-directives.md) and Backlog-12 (distribution primitives)
9. Updated identity-state.md and tools-and-apis.md to resolve contradictions
10. **VERIFIED C1**: vault-neo → P1:37778/health = HTTP 200 (Tailscale reach confirmed)
11. **VERIFIED C3**: /memory/search = 77 results, /memory/context = full resume_block. S141 404 was wrong path (/api/search vs /memory/search)
12. **C-GATE upgraded to GREEN** — PLAN.md and PLAN-C-wire.md updated
13. **ROADMAP.md refreshed** — added Milestone 9 (Sessions 129-143), active backlog table, updated quality gaps
14. **karma-directives.md created** at .gsd/karma-directives.md — seed file with 4 initial directives + sections for learned rules and pending observations
15. **All vault-neo containers verified healthy** — anr-hub-bridge Up 6h, karma-server Up 7h healthy, anr-vault-search Up 3d healthy, falkordb Up 4wk
16. Saved 2 observations to claude-mem (#18307, #18308)

---

## NEXT SESSION STARTS HERE

1. `/resurrect`
2. **Verify C3 /memory proxy chain** — the biggest open hole in PLAN-C completion claim
3. **Update ROADMAP.md** — 57 sessions behind, needs major refresh
4. **Start Backlog-9 or Backlog-10 or Backlog-11** — all Sovereign-approved, all high-impact
5. **Request Sovereign reboot test** for B4 verification

---

## HONESTY DECLARATION

**VERIFIED this session:** A1 backfill (554 obs), C1 Tailscale reach (HTTP 200), C3 /memory/search (77 results) + /memory/context (resume_block), vault-neo containers (all healthy), all plan files read, all map files read, blocker cross-reference complete.

**INFERRED (not re-verified):** C2 WebMCP tools, C4 Chrome session clone, B4 reboot survival.

**RESOLVED this session:** ROADMAP.md refreshed (was Session 86, now Session 143), C-GATE upgraded YELLOW→GREEN, karma-directives.md seed created, 3 map files corrected.

**Cannot be verified from P1:** K2 service PIDs, FalkorDB node counts. Require SSH or live API calls.

## CHROME CDP BLOCKER (identified Session 143)

| # | Issue | Status | Obs |
|---|-------|--------|-----|
| 18 | Chrome 146 `--remote-debugging-port=9222` flag accepted but port never binds | OPEN — needs research | #18414 |
| 19 | Chrome DevTools MCP sandboxed to own tab group — cannot see existing tabs | OPEN — architectural | #18415 |
| 20 | julian-cdp.mjs written but blocked on port issue | READY when port works | #18416 |

**Resolution paths (next session):**
1. Research Chrome 146 CDP changes — may need `--remote-debugging-pipe` instead of port
2. Use Playwright MCP (launches its own Chromium, can import cookies from Chrome profile)
3. Colby manually solves Cloudflare CAPTCHA in MCP-opened tab → CC extracts IndexedDB
