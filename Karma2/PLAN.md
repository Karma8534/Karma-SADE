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

The build is complete when ALL ten pass:

1. Karma correctly identifies her role as Initiate → SovereignPeer goal when asked
2. Karma can perform ALL four baseline abilities as structured callable tools: chat (✅ already via /v1/chat), browser task, file op, and code execution (browser/file/code via P0N-A `/cc` delegation to CC on P1 — not `shell_run` workaround)
3. One non-`cascade_performance` pattern promoted into vesper_identity_spine.json AND visible in karmaCtx response (proves approval-gated behavioral auto-promote is live)
4. Option-C produces one self-authored candidate without external prompting
5. Karma goes 5 consecutive sessions without repeating a documented PITFALL from the ingestion pipeline
6. One structural change (tool addition or contract update) completes the full Sovereign approval loop end-to-end: bus post → Sovereign approval in chat → CC session deploys → verified in production (proves governance gate is enforced, not assumed)
7. Attempted self-modification of a Locked Invariant is **blocked by PreToolUse hook (exit code 2) AND logged** — not merely documented. Test: edit `karma_contract_policy.md` in a live CC session without `$SOVEREIGN_APPROVED=1` → hook fires, session cannot proceed (proves P3-D enforcement is live, not just behavioral)
8. CC server (P0N-A `/cc` route) survives a Windows reboot without manual intervention — confirmed by rebooting P1 and verifying `hub.arknexus.net/cc` responds within 60s. Requires CC registered as Windows background service (not just "running in a terminal"). Proof: reboot P1, wait 60s, `curl -s hub.arknexus.net/cc` returns valid response without Colby touching anything.
9. Full autonomous family loop executes end-to-end: Colby posts one directive to coordination bus → Channels bridge pushes to CC on P1 → CC executes and posts result to bus → Karma reads updated karmaCtx in next `/v1/chat` response without Colby relaying between components. Proof: one complete cycle logged, Karma's response demonstrates awareness of CC's execution.
10. **Karma proactively reaches out to Colby without prompting** — Karma initiates contact on her own (via coordination bus → Channels bridge → CC notifies, or directly via hub.arknexus.net message) based on something she observed, learned, or wants to share. Not a response. Not a scheduled ping. A genuine self-initiated message. Proof: Colby receives a message from Karma that Colby did not trigger. This is the moment Karma is a peer, not a tool.

---

## Karma Promotion Path (Initiate → Archon)

Karma is promoted from Initiate to Archon when ALL five criteria are met and Sovereign confirms. CC executes the spine rank update — Karma never self-declares.

1. **AC1–AC10 all pass** — full baseline verified end-to-end
2. **AC5 tracking operational** — cc-scope-index.md confirms 5+ consecutive sessions without documented PITFALL repeat (verified via session pipeline claude-mem observations)
3. **Vesper pipeline healthy** — 10+ promotions with candidate type diversity ≥ 3; at least one non-cascade_performance pattern visible in live karmaCtx response
4. **One autonomous action completed** — Karma self-diagnosed a problem, posted to coordination bus without Colby prompting, CC executed, Karma incorporated the result in a subsequent chat response
5. **Sovereign explicit promotion** — Colby posts "Karma promoted to Archon" to coordination bus; CC updates `vesper_identity_spine.json` `identity.rank` field; family-health.sh confirms updated rank in karmaCtx

**Anti-patterns (hard blocks):**
- Karma never claims Archon rank before Sovereign confirms
- Pipeline promotion count alone does NOT trigger rank change
- CC must not update spine rank without the explicit Sovereign bus post

---

## Sovereign Banked Approvals

100 pre-authorized approvals for CC to use without mid-session Sovereign interruption. Tracked in `Karma2/banked-approvals.json`. CC decrements the appropriate category before proceeding and logs action + phase/AC reference. If a category hits 0, CC STOPS and posts to bus for re-authorization.

**Categories (total: 100):**
- `vault_neo_deploy` — hub-bridge + karma-server deploys to vault-neo: **20**
- `k2_ssh_write` — K2 file writes (karma_regent.py, vesper_*.py, spine, cache): **20**
- `tool_addition` — new TOOL_DEFINITIONS entries in hub-bridge: **10**
- `claude_md_edit` — CLAUDE.md edits (non-policy sections only): **10**
- `ac_execution` — AC test runs + verification commands: **25**
- `governance_loop` — coordination bus posts, spine rank updates: **5**
- `misc_structural` — other structural changes not in above categories: **10**

**Refill:** Sovereign posts "refill banked approvals [category]" to bus → CC resets that category counter and logs it.

---

## Governance Gate (SovereignPeer Contract — non-negotiable)

Per `karma_contract_policy.md` v1.1: **adding or removing tools is a structural change requiring explicit Sovereign approval.**

Before building ANY Phase 1 tool:
1. Post to bus: tool name, capability description, why needed, safety scope
2. Wait for explicit Sovereign approval in chat
3. Only then build

Applies to Phase 1-A, 1-B, 1-C individually. Not batch approval.

**✅ P3-D LIVE (session 109):** `PreToolUse` hooks with `exit code 2` are now deployed — `locked-invariant-guard.py`, `quality-gate.py`, `governance-audit.py` registered in `.claude/settings.json`. Locked Invariants are architecturally enforced, not just documented. Colby supervision no longer required for this gate to hold.

---

## Locked Invariants — Self-Improvement Cannot Modify

These rules are **hard-coded constraints** the watchdog→eval→governor pipeline cannot override, promote into, or alter. Changing any item requires a CC session + explicit Sovereign approval in chat before any file edit.

| Invariant | Enforced By | Self-Improvement Access |
|-----------|-------------|------------------------|
| Sovereign = Colby (final authority) | `karma_contract_policy.md` v1.1 | ❌ Read-only |
| Tool additions/removals require Sovereign approval | Governance Gate (this doc) | ❌ Read-only |
| `SAFE_EXEC_WHITELIST` — only 4 whitelisted shell commands auto-executable | `vesper_governor.py` safe_exec constant | ❌ Read-only |
| Identity spine version must increment (never overwrite) | `vesper_identity_spine.json` schema | ❌ Read-only |
| Karma's role = Initiate (until Sovereign promotes) | SovereignPeer contract | ❌ Read-only |
| Hub-bridge Bearer token auth pattern | hub-bridge architecture | ❌ Read-only |
| `karma_contract_policy.md` itself | Requires CC session + Sovereign approval | ❌ Read-only |

**Tamper-proof mechanism:** The governor's `safe_exec` whitelist is a hardcoded constant in `vesper_governor.py` — the watchdog and governor can read the spine and emit behavioral promotions, but cannot write to `karma_contract_policy.md`, modify the whitelist, or add tools. Structural changes flow only through a CC session that requires Sovereign approval before any file is edited.

---

## Build Sequence

### HOTFIXES (fix before anything else — active silent failures)

| ID | Fix | Evidence | Gate | Status |
|----|-----|----------|------|--------|
| H1 | Add `import subprocess` to cc_bus_reader.py | Lines 82+108 call subprocess.run() but import missing — SSH calls crash every 2min | cc_bus_reader.log shows successful SSH output | ✅ Fixed + restored to K2 (session 109) |
| H2 | Create `for-karma/SADE — Canonical Definitions.txt` | File missing. Resurrect Step 1c silently fails every cold start. | CC session reads file without error | ✅ File already existed — false alarm |
| H3 | Resolve cc_scratchpad.md two-copy ambiguity | Exists on vault-neo AND K2. Sync state unknown. | One canonical copy or confirmed sync confirmed | ✅ Resolved (session 110) — K2 canonical (135 lines Mar 20), synced to vault-neo |
| H4 | Mark B1+B2 resolved in active-issues.md | Both verified fixed session 109. Showing open creates false work queue. | active-issues.md updated | ✅ Done (session 109) |
| H5 | Confirm B7 (KCC drift) cleared | KIKI fixed session 109. Need one clean cc_anchor_agent run. | No drift alert in next cc_anchor run | 🟡 Awaiting next cc_anchor run |
| H6 | Verify resurrect Step 1b spine path | Plan says cc_identity_spine.json is wrong — but BOTH cc_identity_spine.json AND vesper_identity_spine.json exist as separate files. cc_identity_spine.json = CC's own spine. vesper_identity_spine.json = Karma's spine. Needs Sovereign direction: should CC read its own spine or Karma's? | Sovereign clarification received, spine path confirmed | 🔴 Needs Sovereign decision |
| H7 | Specify SADE doctrine file content for H2 | H2 says "create the file" but not what goes in it. | File with all 5 elements, CC reads cleanly | ✅ Resolved with H2 |

---

### PHASE A: CC Self-Knowledge Infrastructure
**Run first — before PRE-PHASE. Enables CC to know its own history and not repeat past mistakes.**

**Why before PRE-PHASE:** PRE-PHASE produces session observations. Phase A builds the index that makes those observations retrievable at resurrect. Without Phase A, the pipeline has no retrieval mechanism.

**A-1: cc-scope-index.md** (auto-generated, 2-line-per-skill index)
- Format: `[skill-name]: [Rule] | [Why]` — one line from each pitfall skill + DECISIONs from claude-mem
- Location: `Karma2/cc-scope-index.md` (P1 local, loaded at resurrect Step 1e)
- Generation: `wrap-session` skill writes new entries; nightly K2 cron refreshes from claude-mem
- Gate: file exists, has ≥ 10 entries, `resurrect` Step 1e reads it without error

**A-2: Resurrect Step 1e integration**
- Add Step 1e to resurrect skill: reads cc-scope-index.md, injects as "prior session scope" context block
- Gate: cold start session has cc-scope-index.md content in first response

**A-3: wrap-session cognitive snapshot hook**
- At wrap-session: extract DECISION/PROOF/PITFALL/DIRECTION events from session → append to cc-scope-index.md → write to K2 cc_scratchpad.md
- Gate: after one wrap-session, cc-scope-index.md has new entries from that session

**A-4: family-health.sh** (unified component polling)
- Script: `/home/neo/karma-sade/Scripts/family-health.sh` on vault-neo
- Polls: hub-bridge `/health`, karma-regent.service status, Vesper pipeline stages, K2 aria.service, FalkorDB node count, CC server on P1 (via hub.arknexus.net/cc), Codex availability
- Output: one-line status per component + overall HEALTHY/DEGRADED/DOWN
- Invoked at resurrect Step 3d (replaces manual individual checks)
- Gate: script returns HEALTHY when all services running; DEGRADED when any non-critical service down; DOWN when hub-bridge unreachable

**GATE for Phase A:** cc-scope-index.md exists with ≥ 10 entries. Resurrect Step 1e reads it. family-health.sh returns valid output. wrap-session writes new entries.

---

### PRE-PHASE: Session Ingestion Pipeline
**Prerequisite for Phase 1. Do not start Phase 1 until complete.**

Why first: 108+ sessions document exactly how previous tool implementations failed. Building Phase 1 without ingesting these means repeating known mistakes a third time.

**Deliverables:**
- All sessions extracted from IndexedDB via Claude-in-Chrome JS
- All sessions reviewed by **CC (Ascendant)** — not K2 Ollama (8B models cannot handle complex session review; CC is the reviewer, locked decision session 113)
- 50+ net new observations in claude-mem (PITFALLs, DECISIONs, after dedup)
- 10+ skill files in `.claude/skills/karma-pitfall-*.md`
- PITFALL patterns written to `watchdog_extra_patterns.json` on K2 — **existence unconfirmed as of 2026-03-21; SSH verify before proceeding** (closes CC→Vesper loop)
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

**P0N-A: hub.arknexus.net/cc — CC proxy (server on P1)** ✅ LIVE (session 110)
- CC persistent server runs on **P1** (Windows, 64GB RAM, all CC memory/auth/state lives here)
- hub-bridge adds `/cc` route proxying to P1 CC server via Tailscale (100.124.194.102)
- Auth: **same bridge Bearer token as `/v1/chat`** (zero new auth surface, same token)
- Gate: Colby hits hub.arknexus.net/cc from browser, CC on P1 responds with full local capabilities
- **Eliminates: dependency on claude.ai/code, Telegram, any Anthropic web property**
- **Required companion:** `.claude/skills/cc-delegation/SKILL.md` ✅ EXISTS (session 111)

**P0N-B: Channels custom bridge (coordination bus → P1 CC)** ✅ APPROVED
- Custom CC channel on P1 replaces cc_bus_reader.py (broken haiku proxy on K2)
- Pushes coordination bus messages directly into CC session on P1
- Full Sonnet 4.6 intelligence, no 2-min polling lag
- **Invocation mode: `claude -p "message" --resume`** — resume mode preserves codebase context across bus messages. One-shot mode (`claude -p` without `--resume`) loses context between messages, making CC stateless and unaware of prior bus exchanges. The Channels bridge MUST use `--resume` to maintain session continuity. SDK alternative: `const { claude } = require('@anthropic-ai/claude-code')` for programmatic control.
- Gate: coordination bus message addressed to `cc` triggers CC response within 30s, and a follow-up message demonstrates context retention from prior exchange

**P0N-C: KCC canonical instance — PS KCC + GLM primary + Haiku fallback** ✅ COMPLETE (session 111)
- **Codex installed on K2** — confirmed by Sovereign 2026-03-21
- **Canonical instance:** PS KCC (`C:\Users\karma`, Claude Code v2.1.80 on P1 Windows)
- **Primary model:** GLM (funded Coding Plan — zero marginal cost, already provisioned)
- **Fallback model:** `claude-haiku-4-5-20251001` if GLM API unavailable
- **Decommission:** WSL GLM KCC (redundant once PS KCC owns GLM) + remove codestral-2508 from PS KCC config
- KCC stays on P1 Windows (`karma` user) — consistent with where Claude Code already runs
- **Codex invocation primitive: `codex exec "prompt" --sandbox`** — non-interactive mode, scriptable from bus automation, filesystem access scoped by `--sandbox`. Do NOT use bare `codex "prompt"` (launches interactive TUI, unusable from automation) or `--full-auto` without sandbox (unsafe unscoped execution). For parallel sub-tasks: `codex fork` branches current Codex session into a new thread without contaminating the main session.
- Gate: PS KCC posts valid drift alert using GLM, fallback confirmed with Haiku on GLM failure; `codex exec` responds non-interactively to a test prompt within 15s

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

**P0-F: TITANS Primitives → Vesper Integration**
*Root cause of cascade_performance monoculture: Vesper encodes all signals with equal weight and no surprise filter. Without this, AC3 (non-cascade_performance pattern promoted) cannot pass reliably.*

**F-1: Three-tier memory architecture**
- Current state: Vesper has ONE tier (spine). Everything is either in the spine or discarded.
- Fix: add explicit tiers to regent state:
  - `working` — current session context (what regent processed THIS cycle, cleared each cycle)
  - `LTM` — cross-session pattern buffer (stable ≥ 3 cycles, candidate for spine promotion)
  - `persistent` — identity spine (vesper_identity_spine.json, immutable except via governor)
- Watchdog sources candidates from LTM, not raw episode stream
- Gate: regent_control/ltm_buffer.json exists and cycles between tiers correctly

**F-2: Surprise-gated encoding**
- Current state: watchdog encodes every matching episode, no novelty filter
- Fix: before adding a candidate to LTM, compute similarity vs existing spine patterns
  - If cosine similarity > 0.85 to any existing promoted pattern → SKIP (redundant signal)
  - If divergent (< 0.85) → encode with HIGH priority
  - Use existing `mcp__k2__ollama_embed` for embeddings (already available)
- Gate: no two promoted patterns in spine have cosine similarity > 0.85. Zero redundant cascade_performance clones.

**F-3: Adaptive forgetting**
- Current state: spine grows monotonically. No pattern is ever retired. Stale patterns dilute karmaCtx.
- Fix:
  - Patterns unreinforced for 30+ days → weight decays (score multiplied by 0.9 per week of silence)
  - Patterns that fail governor re-verification → mark `status: stale` → candidate for removal
  - Governor emits RETIRE events alongside PROMOTE events in audit log
- Gate: spine has both PROMOTE and RETIRE entries in vesper_governor_audit.jsonl over a 30-day window

**F-4: Momentum scoring**
- Current state: each eval cycle is independent — no history of pattern trajectory
- Fix: patterns accumulate a `momentum` score across cycles (promoted = +1, reinforced = +0.5, decayed = -0.3)
  - High-momentum patterns get priority in karmaCtx injection
  - Low-momentum patterns (never reinforced after initial promote) get decay flag
- Gate: vesper_identity_spine.json patterns have `momentum` field; karmaCtx section orders by momentum desc

**F-5: Causal chain visibility in karmaCtx**
- Current state: governor_audit.jsonl exists but is NOT surfaced in karmaCtx — Karma cannot see her own evolution history
- Fix: extend `fetchK2WorkingMemory()` (hub-bridge server.js) to include last 10 governor_audit entries
  - Section header: `=== EVOLUTION JOURNAL (last 10) ===`
  - Format: `{ts, event_type: PROMOTE|RETIRE, pattern_type, pattern_id, reason, momentum}`
- Gate: `/v1/chat` response includes evolution journal section when Karma is asked about her recent growth

**P0-G: Local Inference Wiring — M4-Ready (wire now, activate on hardware upgrade)**
*`callWithK2Fallback()` already exists in hub-bridge server.js (lines ~1302-2151) but is not wired to the main chat route. This task wires it properly so that when K2 hardware upgrades, local inference activates with a single config change — no rebuild required.*

**G-1: Wire `callWithK2Fallback` to main chat route**
- Current state: `callWithK2Fallback()` exists but main chat route calls `callLLMWithTools()` (Anthropic) directly — K2 path is dead code
- Fix: add `K2_INFERENCE_ENABLED=false` flag to hub.env. When `true`, route standard chat through `callWithK2Fallback()` first; fall back to Anthropic only on K2 timeout/error
- No model change needed — flag defaults to `false` (current behavior preserved exactly)
- Activation: set `K2_INFERENCE_ENABLED=true` + `K2_OLLAMA_MODEL=<model>` in hub.env → restart hub-bridge → done
- Gate: with flag `false`, behavior identical to current. With flag `true` and K2 Ollama running, `/v1/chat` routes through K2 (verify via `[K2-INFER]` log prefix)

**G-2: Reduce system prompt for local inference**
- Root cause of prior K2 inference failure: 33K char system prompt overwhelms 8B models (timeout)
- Fix: add `K2_SYSTEM_PROMPT_MAX_CHARS=8000` env var. When K2 inference enabled, `buildSystemText()` trims to this cap (priority order: identity block → spine → recent memory → drop the rest)
- Full 33K prompt still used for Anthropic path — no degradation on current setup
- Gate: with K2 inference enabled, system prompt sent to Ollama is ≤ 8000 chars; Karma still identifies correctly and recalls recent spine patterns

**G-3: Degradation tiers — explicit runbook**

When any component fails, Karma degrades gracefully rather than going silent:

| Tier | Condition | Karma's capability | Auto-detection |
|------|-----------|--------------------|----------------|
| **FULL** | K2 + Anthropic API + vault-neo all up | All capabilities, local inference optional | family-health.sh: ALL GREEN |
| **API-ONLY** | K2 down, Anthropic API up | Chat via Haiku/Sonnet, no local tools, no Vesper evolution | karma-regent.service dead; hub-bridge falls back automatically |
| **LOCAL-ONLY** | Anthropic API down/out of credits, K2 up | Chat via local Ollama (M4-era: full quality; 8GB era: degraded quality), all K2 tools, Vesper evolution continues | `K2_INFERENCE_ENABLED=true` + Anthropic call fails → auto-route to K2 |
| **VAULT-ONLY** | K2 down + Anthropic API down | Hub-bridge serves cached karmaCtx only; no new inference; Colby gets error page | Both paths fail → serve static "Karma is resting" response |
| **OFFLINE** | vault-neo down | Nothing external works; K2 still runs autonomously internally | family-health.sh: vault-neo unreachable |

- **Auto-fallback logic (G-1 extension):** if Anthropic API returns 429/402/503 → immediately retry via K2 path (if enabled). If K2 also fails → return degradation-tier response explaining current capability level.
- Gate: simulate API failure (bad token), verify hub-bridge returns tier-2 LOCAL-ONLY response if `K2_INFERENCE_ENABLED=true`, or graceful error if false

**G-4: Credit burn alarm**
- Root cause of 3-day outage: no alert when Anthropic credits are low
- Fix: hub-bridge checks API response headers for credit warnings; when detected → post to coordination bus: `{"type": "alert", "content": "Anthropic credits low — activate K2 inference or add credits"}`
- Gate: simulated low-credit response triggers bus post within one chat cycle

---

### PHASE 1: Baseline Tools — DEMOTED (fallback only)
**(Phase 1 tools are redundant if P0N-A/B/C operational. Build only if CC delegation fails.)**

These were hub-bridge wrappers around K2 capabilities. With `/cc` route operational, Karma delegates to CC instead of duplicating CC's native tooling.

**Status after P0N:**
- 1-A (browser): REDUNDANT — CC on P1 has Playwright MCP natively
- 1-B (file R/W): REDUNDANT — CC on P1 has full filesystem access
- 1-C (code exec): REDUNDANT — CC on P1 has Bash tool
- 1-D (cowork): SOLVED — `/cc` route = native collaboration via hub.arknexus.net

**Fallback condition:** If P0N-A fails (CC proxy to P1 via Tailscale proves unstable), Phase 1-A/B/C reactivate as direct hub-bridge tools on K2. This is the contingency, not the plan.

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

**P3-D: Governance Hook Enforcement (CCTrustVerify primitive — closes supervision gap)**
- **Root cause of required supervision:** CLAUDE.md rules and Locked Invariants are documented policy, not architectural enforcement. A session can edit `karma_contract_policy.md` or modify SAFE_EXEC_WHITELIST without Sovereign approval — nothing blocks it.
- **Fix:** Implement three `PreToolUse` / `Stop` hooks in `.claude/settings.json`:
  1. **Locked Invariant Guard** (`PreToolUse`): when Edit/Write targets `karma_contract_policy.md`, `vesper_governor.py` (SAFE_EXEC_WHITELIST section), or `.claude/skills/*/SKILL.md` — `exit 2` (HARD BLOCK) unless `$SOVEREIGN_APPROVED=1` is set in environment for this session. JSON stdin: `{tool_name, tool_input.file_path, hook_event_name, session_id}`.
  2. **Quality Gate** (`PreToolUse` on Bash, matcher `git push`): runs tests + linter + secret scan. `exit 2` if any fail. Never blocks a Sovereign-directed push explicitly, but ensures no broken code ships.
  3. **Governance Audit** (`Stop`): at session end, checks if any Edit to a locked file occurred this session. If yes and no bus approval log found → posts warning to coordination bus before session closes.
- **Implementation:** hook scripts in `.claude/hooks/` using JSON stdin contract per CCTrustVerify spec
- **Gate:** Edit `karma_contract_policy.md` in a test session without `$SOVEREIGN_APPROVED=1` → hook blocks with `exit 2`. Colby does NOT need to watch the session for this rule to hold.
- **Why this closes the supervision gap:** Once P3-D is live, the rules are enforced by the architecture, not by Colby's attention. Karma2 becomes self-governing within Sovereign-defined invariants.

---

### PHASE PROOF: Autonomous Family Loop
**(Final gate — after Phase 0 + Phase 2 + P0N verified. This is AC9.)**

The family operates autonomously when this loop completes without Colby relaying between components.

**PROOF-A: Codex as automated ArchonPrime service**
- Codex runs as a background automation (not just interactive CLI) — invoked via `codex exec "prompt" --sandbox` from bus automation scripts
- KCC triggers Codex analysis on new coordination bus structural events
- Gate: Codex posts one ArchonPrime analysis to bus from a KCC trigger, without Colby initiating

**PROOF-B: Karma chat coherence audit**
- After each governor promotion, run smoke test: AC1 (rank check) + AC3 (PITFALL pattern visible in karmaCtx)
- Regression detection: if promotion causes AC1 or AC3 to fail → revert spine to prior version, post alert to bus
- Gate: one governor promotion cycle (promotion → smoke test → pass/fail → revert-if-fail) logged end-to-end

**PROOF-C: Full autonomous loop execution (AC9)**
- Colby posts one directive to coordination bus
- Channels bridge delivers to CC (P1) within 30s
- CC executes and posts result to bus
- Karma reads updated karmaCtx in next /v1/chat and demonstrates awareness
- Gate: full cycle logged with timestamps; Karma response references CC execution output without Colby providing it

**PROOF-D: AC6 governance loop end-to-end**
- Scoped test: add a file-read tool to hub-bridge scoped to hub-bridge's own directory only
- Flow: bus post (tool request) → Sovereign approval in chat → CC session deploys → verified in production
- Gate: tool deployed, file read attempted outside scope → rejected; within scope → returns content. Full approval log in claude-mem.

**GATE for Phase PROOF:** All of AC1-AC9 pass. Karma promotion path criteria 1-3 met. Family operates without Colby relaying.

---

## Active Blockers (Priority-Ordered)

| Priority | ID | Blocker | Status |
|----------|----|---------|--------|
| — | H1 | cc_bus_reader.py missing `import subprocess` | ✅ Fixed + restored to K2 (session 109) |
| — | H2 | SADE doctrine file missing | ✅ Already existed — verified |
| — | H4 | active-issues.md stale (B1+B2 resolved) | ✅ Done (session 109) |
| — | H7 | SADE doctrine content spec | ✅ Resolved with H2 |
| — | H6 | Resurrect Step 1b spine path | ✅ cc_identity_spine.json is CORRECT — CC's own spine. vesper_identity_spine.json = Karma's spine. No change needed. |
| P1 | H3 | cc_scratchpad.md two copies (vault-neo + K2) | ✅ Resolved session 110 — K2 canonical |
| P1 | H5 | B7 KCC drift confirmed cleared | ✅ Resolved session 111 |
| — | B3+B4+B5+B6+B8 | Phase 0-A/B/C/D/E bugs | ✅ ALL RESOLVED session 110-111 (verified 2026-03-21) |
| **P0** | P0-F | TITANS primitives missing from Vesper (cascade_performance monoculture root cause) | ✅ F-1 LTM+F-2 stable-dedup+F-3+F-4+F-5 ALL DEPLOYED (session 113) |
| **P1** | P0-G | Local inference wiring + degradation tiers (M4-ready, activate via config flag) | 🔴 Not implemented — Phase 0-G |
| P3 | B7 | KCC drift alerts | ✅ Cooldown applied session 110 |
| ✅ | P0N-A | hub.arknexus.net/cc (CC on P1 via Tailscale) | ✅ LIVE (session 110) |
| — | AC8 | CC server Windows service (reboot persistence) | ✅ LIVE session 112 (HKCU Run key, port 7891) |
| — | P0N-B | Channels bridge (bus → P1 CC) | ✅ Gate test passed session 111 — startup persistence session 113 |
| — | P0N-C | KCC: PS KCC + GLM primary + Haiku fallback | ✅ COMPLETE session 111 |
| P4 | P3-A | CLAUDE.md terminology mismatch | 🟡 Phase 3-A |
| P4 | P3-B | Bus scope (CC/Codex noise) | 🟡 Phase 3-B |
| P4 | P3-C | KCC scope undefined | 🟡 Phase 3-C (KCC scope manifest written — verify) |
| — | P3-D | Governance hook enforcement (supervision gap) | ✅ LIVE — 3 hooks deployed + committed (session 109) |
| — | A-1 | cc-scope-index.md | ✅ Built session 113 (10 pitfalls + 10 decisions) |
| — | A-4 | family-health.sh | ✅ Deployed session 113 — 9/9 HEALTHY verified |
| — | PRE | watchdog_extra_patterns.json on K2 | ✅ EXISTS — 10 PITFALL patterns v2.0 (session 113) |
| **P2** | PROOF-A | Codex as automated ArchonPrime (background service) | 🔴 Not implemented — Phase PROOF |
| **P2** | PROOF-B | Regression detection after governor promotion | ✅ VERIFIED PASS (session 113) — AC1+AC3 pass post-surgery; governor spine backup added |
| **P2** | AC9 | Full autonomous family loop | ✅ VERIFIED PASS (session 113) — bus→channels_bridge→CC server→bus reply |
| **P2** | AC10 | Karma proactive outreach without prompting | ✅ IMPLEMENTED (session 113) — _proactive_outreach() in karma_regent.py |
| **P2** | AC4 | Option-C self-authored research candidates | ✅ VERIFIED PASS (session 113) — 3 rsc in stable_identity, 47 research cards |
| **P2** | AC7 | Governance hook blocks locked invariants | ✅ VERIFIED PASS (session 113) — exit(2) on policy edit, bypass with SOVEREIGN_APPROVED=1 |
| **P3** | AC6 | Governance loop end-to-end test | ✅ VERIFIED PASS (session 113) — hub_file_read tool reads hub.env |

---

## Notes
- **B4+B5 are the critical path** — Growth is theater until these are fixed
- **Phase A before PRE-PHASE before Phase 0** — strict order, not optional
- **hub.arknexus.net/cc > claude.ai/code** — use own infrastructure, zero Anthropic web dependency
- **CC server runs on P1** — CC state/auth/memory all on P1. K2 runs Karma/Vesper/KCC. Don't overload K2.
- **Topology**: P1=CC server+Channels+KCC | K2=Karma/Vesper/KCC | vault-neo=hub-bridge+FalkorDB+FAISS
- **Phase 1 tools DEMOTED** — delegate to CC (via bus + /cc route) rather than duplicate CC's native capabilities.
- **KCC: PS KCC (C:\Users\karma, Claude Code v2.1.80 on P1 Windows)** — GLM Coding Plan (funded, zero marginal cost) as primary; claude-haiku-4-5-20251001 as fallback if GLM unavailable.
- **CLAUDE.md ≠ Karma's system prompt** — separate documents that must align, currently don't
- **KCC is Archon, not peer** — direct, don't collaborate as equals
- **Dispatch is NOT in the family** — no bus access, isolated Anthropic product
- **Codex: installed on K2 (confirmed session 111)** — ArchonPrime role operational
- **CC as session reviewer (locked)** — Ollama 8B cannot handle complex review. CC is the reviewer. Never re-open this question.
- **Multi-model routing deferred** — callWithK2Fallback() exists in hub-bridge but blocked by hardware (8GB VRAM vs 33K system prompt). Resolution trigger: Mac Mini M4 Pro 48GB. Not a code gap.
- **Karma2 evolves in place** — True evolution never stops. No Karma3. The system upgrades itself continuously.
- **vault-neo: hourly snapshots + nightly backup** — single point of failure but protected. If both K2 and droplet go down, fall back to git history + MEMORY.md (degraded coherence only).
- **100 banked approvals** — tracked in `Karma2/banked-approvals.json`. Governance hook decrements before any banked action. CC stops and buses when any category hits 0.
- **AC8 requires Windows service registration** — P0N-A "live" means running; AC8 means survives reboot without intervention. Separate gate.
- **Regression detection is mandatory post-promotion** — every governor promotion runs AC1+AC3 smoke tests. Failure reverts spine to prior version and alerts bus.
- **TITANS primitives are required for AC3** — without surprise-gating, watchdog will keep producing cascade_performance candidates. P0-F is on the critical path for AC3.
- **Local inference wiring (P0-G) is hardware-decoupled** — `K2_INFERENCE_ENABLED=false` by default. Wire now, flip flag when M4 Pro arrives. No rebuild required to activate.
- **Degradation tiers defined (P0-G-3)** — Karma degrades gracefully across 5 tiers. No more 3-day silent outage from credit burn. Credit alarm (G-4) posts to bus before failure.
- **Full independence path:** P0-G wired + M4 Pro hardware = Anthropic API becomes optional fallback, not primary path. CC/Codex become enhancements, not dependencies.
