# Bridge Evolution — Gap Analysis & Corrected Merged Plan
**Date:** 2026-03-26 | **Session:** 145 | **Author:** CC Ascendant | **Sovereign:** Colby

---

## 1. CURRENT PLAN FILES REVIEWED

| File | Path | Role |
|------|------|------|
| PLAN.md | Karma2/PLAN.md | Master plan (rewritten this session) |
| cc-big-picture.md | Karma2/cc-big-picture.md | Project arc (rewritten this session) |
| experiment_instructions.md | Karma2/experiment_instructions.md | L_karma optimization spec v2.3 |
| karma-context.md | Karma2/karma-context.md | Runtime context summary (new this session) |
| MEMORY.md | ./MEMORY.md | Active mutable state |
| CLAUDE.md | ./CLAUDE.md | CC operator contract |
| karma_contract_policy.md | Karma2/karma_contract_policy.md | SovereignPeer policy v1.1 |
| karma_contract_execution.md | Karma2/karma_contract_execution.md | Runtime execution prompt v1.0 |
| services.md | Karma2/map/services.md | Running services inventory |
| data-flows.md | Karma2/map/data-flows.md | Data flow diagrams |
| tools-and-apis.md | Karma2/map/tools-and-apis.md | Tool and API inventory |
| identity-state.md | Karma2/map/identity-state.md | Identity/spine state |
| file-structure.md | Karma2/map/file-structure.md | File layout across nodes |
| active-issues.md | Karma2/map/active-issues.md | Open/closed bugs |
| cc-scope-index.md | Karma2/cc-scope-index.md | 56 PITFALLs + 16 DECISIONs |
| STATE.md | .gsd/STATE.md | GSD workflow state (80 component rows) |
| architecture.md | .claude/rules/architecture.md | System architecture reference |
| deployment.md | .claude/rules/deployment.md | Deployment procedures |
| resurrection-architecture.md | .claude/rules/resurrection-architecture.md | Resurrection design |
| server.js | hub-bridge/app/server.js | Hub-bridge source (synced this session) |

---

## 2. GAP ANALYSIS

### 2.1 Matches (current ≈ target)

| Target Requirement | Current Implementation | Status |
|--------------------|----------------------|--------|
| Hub is sole user-facing surface | hub.arknexus.net/v1/chat + unified.html | ✅ MATCH |
| Vault-neo is canonical spine | vault ledger (207K+ entries), FalkorDB, FAISS | ✅ MATCH |
| K2 is primary reasoning node | karma-regent, Vesper pipeline, cortex, all on K2 | ✅ MATCH |
| P1 is action/fallback node | CC sessions, fallback cortex (just deployed) | ✅ MATCH |
| Canonical identity in spine | vesper_identity_spine.json + persona files | ✅ MATCH |
| Canonical memory in ledger | memory.jsonl (207K entries) on vault-neo | ✅ MATCH |
| Invariants defined | karma_contract_policy.md — immutable invariants section | ✅ MATCH |
| Change taxonomy | Structural/Behavioral/Cosmetic in policy v1.1 | ✅ MATCH |
| Governance gates | 4 gates (identity_consistency, persona_style, session_continuity, task_completion) | ✅ MATCH |
| Substrate independence | Explicit in policy: "Model providers are execution substrates only" | ✅ MATCH |
| Local-first routing | K2 Ollama → P1 Ollama → cloud cascade | ✅ MATCH |
| Coordination bus | REST + persistence + UI panel | ✅ MATCH |
| K2/P1 tool execution | shell_run, k2_* tools, CC sessions on P1 | ✅ MATCH |
| Event log | Ledger + coordination bus JSONL + governor audit JSONL | ✅ MATCH |
| Evaluator exists | vesper_eval.py (5-min cadence) | ✅ MATCH |
| Promotion engine exists | vesper_governor.py (2-min cadence) | ✅ MATCH |
| Option-C self-improvement | Defined, gate at 20 qualified cycles, ELIGIBLE status reached | ✅ MATCH |
| Synthetic probe rejection | Criteria in policy: tags, source, probe detection | ✅ MATCH |
| Verification loop | RED→fix→GREEN→live-state in policy + execution prompt | ✅ MATCH |
| Tier-based context routing | classifyMessageTier() with 3 tiers, context assembly scaled | ✅ MATCH |
| Prompt caching | Anthropic cache_control ephemeral on last history message | ✅ MATCH |
| Session history limiting | MAX_SESSION_TURNS caps history length | ✅ MATCH |

### 2.2 Partial Matches

| Target Requirement | Current State | Gap |
|--------------------|--------------|-----|
| Orchestrator as explicit role | classifyMessageTier + buildSystemText + regent in hub-bridge | Fused into hub-bridge. Not a separable service. Policy enforcement is ad-hoc. |
| Evaluator detects regressions | vesper_eval grades turns | No regression detection — only absolute scores. No comparison to baseline. No A/B. |
| Promotion: candidate → verified → canonical | candidate → promoted (governor gates) | No "verified" intermediate step. No canary before promotion. |
| Node health monitor | Cortex /health endpoint exists | No centralized health monitor. No alerting. No auto-recovery. |
| Budget enforcement | SPEND_CAP in hub-bridge, $60/month | No per-model budgets. No per-task cost tracking. No dynamic throttling. |
| Model escalation | Tier routing sends tier-3 to Anthropic | No explicit escalation detection. Tier is based on message length/keywords, not complexity analysis. |
| State dashboard at hub | Coordination bus UI panel | Shows bus messages only. No component health, no spend tracking, no promotion log. |
| Rollback support | Git snapshots of spine before governor writes | No runtime rollback mechanism. Manual git revert only. |
| Replay/simulation | None at runtime | ingest_recent.sh processes ledger but no replay of saved transcripts. |
| Token/cost discipline | Tier-based context assembly | Still sends multiple history turns. No compression via local qwen. No retrieval-first strategy. |
| P1 as canary/sandbox | CC sessions isolated on P1 | No canary infrastructure. No sandbox isolation for experiments. |

### 2.3 Missing Components

| Target Requirement | Status |
|--------------------|--------|
| **Trace/explanation surface at hub** | MISSING. No way for user to see WHY a response was routed to cortex vs cloud, or what context was assembled. |
| **Promotion/review surface at hub** | MISSING. Promotions happen silently on K2. User cannot see pending candidates, approve/reject, or review promotion history. |
| **Task status surface at hub** | MISSING. No task queue visibility beyond bus messages. |
| **Preferences store (explicit)** | MISSING. User preferences not formalized as a vault entity. |
| **Goals store (explicit)** | MISSING. No formal goal tracking in vault. |
| **Artifact manifest** | MISSING. No registry of produced artifacts. |
| **Worker dispatch service** | MISSING. No formal dispatch mechanism — hub-bridge directly calls K2/P1. |
| **Candidate memory queue** | MISSING. No queue for memory entries awaiting verification. |
| **Canary runner** | MISSING. No infrastructure to run experiments on K2/P1 before promoting. |
| **Rollback engine** | MISSING. Governor creates checkpoints but no automated rollback on regression. |
| **Metrics store / benchmark history** | PARTIAL. Governor audit JSONL exists but no queryable metrics store. No historical benchmarks. |
| **Cross-provider verifier** | MISSING. No second-opinion verification from different model provider. |
| **Clustering of recurring issues** | MISSING. Watchdog extracts but doesn't cluster. |
| **Active → superseded state transition** | MISSING. Old promoted patterns have no supersession mechanism. |
| **Regression detection** | MISSING. No A/B comparison against baseline. |

### 2.4 Contradictions / Drift

| # | Contradiction | Files Involved | Resolution |
|---|--------------|----------------|------------|
| CD1 | Hub-bridge is BOTH persona surface AND orchestrator AND partial evaluator. Target says these are separate roles. | server.js, architecture.md | Accept as implementation reality. Hub-bridge IS the orchestrator. Logical separation (functions, not services) is sufficient for current scale. |
| CD2 | services.md lists K2 Ollama model as "nemotron-mini:optimized" but PLAN.md and MEMORY.md say qwen3.5:4b | services.md vs PLAN.md | services.md is stale. qwen3.5:4b is ground truth (verified this session). |
| CD3 | data-flows.md shows hub-bridge routing to "claude-haiku-4-5-20251001 with TOOL_DEFINITIONS" but cognitive split now routes recall to cortex | data-flows.md vs server.js | data-flows.md is stale. Cognitive split is live. |
| CD4 | tools-and-apis.md says MODEL_DEEP is "claude-haiku-4-5-20251001 (both slots same)" but target wants GPT-5.4 mini default | tools-and-apis.md vs target | Model selection is a Sovereign decision. Current: Haiku. Target: GPT-5.4 mini. See §2.8. |
| CD5 | karma_contract_execution.md routing cascade: "K2 Ollama → P1 Ollama → z.ai → Groq → Claude" but hub-bridge /v1/chat routes to Anthropic directly (cognitive split notwithstanding) | execution.md vs server.js | Two routing paths exist: (1) karma-regent uses cascade, (2) hub-bridge /v1/chat uses Anthropic direct. Target wants hub-bridge to also use cost-optimal cascade. |
| CD6 | K2 vesper_identity_spine.json is treated as canonical but target says vault-neo is the ONLY canon | identity-state.md, policy.md | Policy says "vault-neo wins on conflict" but operationally K2 spine is the live version. Sync lag = drift window. |
| CD7 | STATE.md says "Nemotron 9B v2 pulled" (line 5) while PLAN.md says qwen3.5:4b | STATE.md vs PLAN.md | STATE.md is stale (last updated Session 143). PLAN.md is current (updated this session). |

### 2.5 Unsafe Assumptions

| # | Assumption | Risk |
|---|-----------|------|
| UA1 | Cortex 32K window is sufficient for all recall | False. 207K ledger entries, 4789 graph nodes cannot fit in 32K. Quality degrades for old knowledge. |
| UA2 | Promotion without canary is safe | Risk of promoting a pattern that degrades persona quality. No rollback mechanism exists. |
| UA3 | Single hub-bridge crash is recoverable | Hub-bridge is the ONLY orchestrator. If it crashes, Karma is offline. No hot standby. |
| UA4 | K2 spine sync to vault-neo is timely | 6h pull cycle means up to 6h of K2 state not on vault-neo. K2 crash in that window = data loss. |
| UA5 | Anthropic credits will always be available | Credits exhausted this session. No fallback persona when cloud is down (cortex returns factual recall but no persona-quality conversation). |
| UA6 | All models are interchangeable | Target assumes GPT-5.4 mini + Claude Sonnet 4.6 cross-provider. Current system is locked to Anthropic. Switching requires API key setup + routing changes. |

### 2.6 Cost/Token Inefficiencies

| # | Inefficiency | Fix |
|---|-------------|-----|
| CT1 | buildSystemText sends full identity block (15K chars) on every turn including tier-1 | Compress to <2K for tier-1. Full identity only for tier-3. |
| CT2 | No local qwen classification before cloud call | Use cortex/qwen to classify complexity and compress context before sending to cloud. |
| CT3 | MEMORY.md tail (2000 chars) sent on every turn regardless of relevance | Send only if tier >= 2 and message matches memory-related keywords. |
| CT4 | Session history sent as raw turns | Compress older turns to summaries using local qwen. Only send last 2-3 raw turns. |
| CT5 | No cost tracking per task/tool/model | Add per-request cost logging with model, tokens, task type. |
| CT6 | Cloud used for all tool orchestration | Use local qwen for simple tool calls (file reads, status checks). Cloud only for multi-step reasoning chains. |

### 2.7 Evolution/Self-Improvement Gaps

| # | Gap | Current | Target |
|---|-----|---------|--------|
| EV1 | No clustering | Watchdog extracts individual patterns | Should cluster recurring issues before proposing |
| EV2 | No replay/simulation | Candidates go straight to promotion | Should replay against saved transcripts/edge cases |
| EV3 | No canary split | All promotions apply globally | K2 for reasoning-side, P1 for action-side experiments |
| EV4 | No regression detection | Quality metrics are absolute | Should compare against rolling baseline |
| EV5 | No memory quality evaluation | Memory writes are unscored | Should evaluate retrieval precision and memory usefulness |
| EV6 | No routing quality evaluation | Routing is rule-based | Should measure whether tier classification was correct post-hoc |
| EV7 | Live persona can mutate via write_memory | write_memory tool exists with approval gate | Target says live persona must NEVER directly rewrite itself |

### 2.8 Recommended Removals or Downgrades / Sovereign Decisions Required

| # | Item | Recommendation | Reason |
|---|------|---------------|--------|
| RD1 | **Model provider switch to GPT-5.4 mini** | SOVEREIGN DECISION | Target specifies GPT-5.4 mini default + Claude Sonnet as verifier. Current is all-Anthropic. Requires: (1) OpenAI API key + billing, (2) hub-bridge routing changes, (3) tool-calling format changes (OpenAI vs Anthropic differ). Significant work. |
| RD2 | nemotron-mini references in services.md, tools-and-apis.md | REMOVE | Stale. Replace with qwen3.5:4b. |
| RD3 | STATE.md Nemotron reference | UPDATE | Stale Session 143 reference. |
| RD4 | cc_context_snapshot.md pattern | DEPRECATE | Replaced by cortex. |
| RD5 | /dream skill | DEPRECATE | Replaced by cortex self-consolidation. |
| RD6 | karma_behavioral_rules.jsonl | DEPRECATE | Never read at runtime. Cortex ingests corrections directly. |
| RD7 | karma-directives.md static file | DEPRECATE | Replaced by orchestrator loading directives from spine. |
| RD8 | Deep mode toggle concept | DEPRECATE | Both model slots use same model. Tier routing is the real mechanism. |

### 2.9 Highest-Priority Blockers

| Priority | Blocker | Impact | Fix |
|----------|---------|--------|-----|
| P0 | **Anthropic API credits exhausted** | Cloud path returns 400. Persona-quality conversation blocked. Only cortex $0 recall works. | Sovereign action: add billing at console.anthropic.com OR switch to GPT-5.4 mini per target. |
| P1 | **No rollback mechanism** | Bad promotion is permanent. Must manually revert spine JSON. | Build governor checkpoint + automated rollback on regression. |
| P2 | **K2→vault-neo sync lag (6h)** | K2 crash = up to 6h of spine state lost. | Reduce sync to 30min or event-driven (on every promotion). |
| P3 | **No canary before promotion** | Promoted patterns affect all users immediately. | Add canary runner: K2 tests reasoning-side, P1 tests action-side. |
| P4 | **Hub-bridge is single point of failure** | Hub-bridge down = Karma offline. No hot standby. | Low priority at current scale. Monitor and alert. |
| P5 | **No cross-provider verification** | Single-model bias in all evaluations. | Add Claude Sonnet as second-opinion verifier for structural changes. |

---

## 3. CORRECTED MERGED PLAN

### Architecture (merged — keeps what works, adds what's missing)

```
═══════════════════════════════════════════════════════
                    KARMA ARCHITECTURE
              (Target-aligned, foundation-verified)
═══════════════════════════════════════════════════════

HUB (hub.arknexus.net) — PERSONA SURFACE + ORCHESTRATOR
├── Chat UI (unified.html)
├── State dashboard (to build: Phase 3)
├── Promotion review surface (to build: Phase 5)
├── Orchestrator functions:
│   ├── classifyMessageTier() — message classification
│   ├── buildSystemText() — context assembly from spine
│   ├── cognitive split — cortex vs cloud routing
│   ├── model router — tier → model → node
│   └── budget enforcer — per-model, per-task cost tracking
│
VAULT-NEO — CANONICAL SPINE (source of truth)
├── Ledger (memory.jsonl — 207K+ entries, append-only)
├── FalkorDB (neo_workspace — 4789+ nodes)
├── FAISS (193K+ entries, semantic search)
├── Identity files (persona, stable decisions, invariants)
├── Policies (karma_contract_policy.md)
├── Promotion queue (to migrate from K2: Phase 5)
├── Evaluator outcomes (to migrate from K2: Phase 6)
├── Model routing policy (hub.env + routing.js)
├── Rollback anchors (to build: Phase 5)
│
K2 (192.168.0.226) — REASON NODE
├── Julian cortex (qwen3.5:4b, 32K, port 7892)
├── karma-regent.service (Vesper pipeline)
├── Vesper: watchdog → eval → governor → researcher
├── Cron agents (hourly report, anchor, kiki, bus reader, bus-to-cortex)
├── aria.service (Flask, tools, exec)
├── K2 cache (synced from vault-neo)
├── Reasoning-side experiment lane (to formalize: Phase 8)
│
P1 (PAYBACK) — ACTION + CANARY NODE
├── CC sessions (Claude Code — Julian's hands)
├── Fallback cortex (qwen3.5:4b, 32K, port 7893)
├── Browser automation (ChromeDevTools MCP, Playwright MCP)
├── Action-side experiment lane (to formalize: Phase 8)
├── Canary runner (to build: Phase 6)
│
CLOUD — DEEP REASONING TIER
├── Default: [SOVEREIGN DECISION: GPT-5.4 mini OR Anthropic Haiku]
├── Escalation: [SOVEREIGN DECISION: GPT-5.4 OR Sonnet 4.6]
├── Cross-verifier: [SOVEREIGN DECISION: different provider than default]
```

### Data Lanes

| Lane | Owner | Contains | Write Policy |
|------|-------|----------|-------------|
| CANON | vault-neo | identity, memory, preferences, goals, invariants, stable policy | Promotion engine only. No direct writes. |
| REASON | K2 | planning, synthesis, analysis, draft upgrades, evaluator work | K2 writes candidates. Never writes canon. |
| ACTION | P1 | tool execution, browser actions, automation, canary tests | P1 executes. Results written to ledger via hub. |
| PROMOTION | vault-neo | candidate review, verification, canary results, promote/reject/rollback | Governor proposes. Vault stores. Gates enforce. |

### Model Policy (merged)

| Role | Model | When |
|------|-------|------|
| Local classification/routing/compression | qwen3.5:4b (K2 primary, P1 fallback) | Every turn — triage, cortex recall, context compression |
| Default cloud persona | [SOVEREIGN CHOICE] | Tier 2-3 messages — persona-quality conversation |
| Escalation cloud | [SOVEREIGN CHOICE] | Hard reasoning, architecture, difficult debugging |
| Cross-provider verifier | [SOVEREIGN CHOICE — different provider] | Structural change review, second-opinion critique |

**Policy rules (from target, enforced):**
- Strongest model is NOT default on every turn
- qwen handles: classification, routing assist, compression, triage, continuity fallback, recall
- Tool/internet work runs on K2/P1 locally
- Cloud receives compact structured evidence, not raw logs
- Escalate only when complexity threshold is crossed

### Agent Contract (from earlier this session — retained)

1. **Identity:** Karma/Julian — one entity, substrate-independent. Lives in SPINE, not cortex.
2. **Directives:** Loaded from spine by orchestrator → injected into cortex/cloud at request time.
3. **Routing:** Orchestrator decides cortex-first ($0) → default cloud ($) → escalation cloud ($$). Based on classifyMessageTier() + complexity analysis.
4. **Fallback chain:** K2 cortex → P1 cortex → default cloud → escalation cloud → degraded spine-only.
5. **Hydration:** Orchestrator assembles context from spine (graph + FAISS + ledger + MEMORY.md + persona) → injects into runtime. Tier-scaled.
6. **Continuity:** Spine survives all reboots. Orchestrator loads spine → hydrates cortex. Cortex alone cannot resurrect.
7. **Proof:** VERIFIED vs INFERRED before every claim. End-to-end testing required.
8. **Evolution:** Self-improvement through governed promotion lane ONLY. Live persona never directly rewrites itself.

### State Transitions (required)

```
RAW → CANDIDATE → VERIFIED → CANONICAL
                     ↓
                  REJECTED (retained as evidence)

CANONICAL → SUPERSEDED (when newer version promoted)
CANONICAL → ROLLED BACK (on regression detection)
```

---

## 4. IMPLEMENTATION ORDER

### Phase 1: Lock Canon (vault-neo authority hardening)
**Goal:** Vault-neo is the ONLY place canonical state can be written. No backdoors.

- Migrate promotion queue from K2 (regent_candidates/) to vault-neo storage
- Migrate evaluator outcomes from K2 (governor_audit.jsonl) to vault-neo
- Reduce K2→vault-neo sync from 6h to 30min
- Add event-driven sync: on every governor promotion, immediate push to vault-neo
- Formalize preferences and goals as vault entities (type: "preference", "goal")
- Write rollback anchor on every promotion (snapshot spine state before write)

**Required services:** vault-api (exists), sync cron (update cadence)
**Required policies:** "K2 never writes canon directly" enforcement
**Metrics:** sync lag < 30min, rollback anchor exists for every promotion
**Success criteria:** K2 crash at any point → vault-neo has complete state within 30min
**Rollback point:** Revert sync cadence to 6h

### Phase 2: Stabilize Bridge (hub-bridge as clean persona surface)
**Goal:** Hub-bridge is a clean persona surface + orchestrator. Remove leaks and add observability.

- Add /v1/status endpoint: node health, spend, last promotion, current model, cortex block count
- Add /v1/trace endpoint: last N requests with routing decision, model used, cost, latency
- Fix buildSystemText token waste: compress identity block for tier-1 (15K → 2K)
- Add per-request cost logging (model, tokens in/out, task type, usd_estimate)
- Update stale docs: services.md, data-flows.md, tools-and-apis.md, STATE.md

**Required services:** hub-bridge (exists — add endpoints)
**Required policies:** "Hub never stores canonical state" (already true in practice)
**Metrics:** /v1/status returns accurate data, /v1/trace shows last 50 requests
**Success criteria:** User can see routing decisions, costs, and node health at hub
**Rollback point:** Revert server.js to pre-Phase-2 version

### Phase 3: Formalize Orchestration (explicit routing + model policy)
**Goal:** Orchestrator explicitly enforces model policy, budget, and routing rules.

- Implement complexity-based escalation (not just keyword/length tier classification)
- Use local qwen for pre-classification: "Is this recall, conversation, reasoning, or action?"
- Add per-model budget tracking (daily/monthly caps per model tier)
- Add dynamic throttling: if spend > 80% of cap, downgrade default tier
- Wire cost-optimal model cascade: local → default cloud → escalation cloud
- [SOVEREIGN DECISION] Choose default cloud model and escalation model

**Required services:** hub-bridge routing (exists — enhance)
**Required queues:** Cost ledger (new: append per-request cost records)
**Required policies:** Model routing policy doc, per-model budgets
**Metrics:** Correct tier classification rate, cost per turn by tier
**Success criteria:** 80%+ of turns use cheapest-sufficient model. Monthly spend < cap.
**Rollback point:** Revert to current tier-based routing

### Phase 4: Split K2/P1 Responsibilities (formal node roles)
**Goal:** K2 = reason node. P1 = action/canary node. Clear separation.

- Formalize K2 as REASON lane: planning, synthesis, analysis, evaluator work
- Formalize P1 as ACTION lane: browser, tool execution, automation, canary
- Add worker dispatch: orchestrator sends task to K2 or P1 based on lane
- Add node health monitoring: /health checks on both nodes every 60s from hub
- Alert on node failure: bus post when K2 or P1 unreachable

**Required services:** Node health monitor (new cron or hub-bridge timer)
**Required policies:** "Reasoning work to K2, action work to P1" routing rule
**Metrics:** Node uptime, task completion rate per node
**Success criteria:** K2 down → reasoning degrades gracefully. P1 down → actions queue.
**Rollback point:** Revert to current implicit node usage

### Phase 5: Memory Promotion (formal promotion pipeline)
**Goal:** All state changes go through: raw → candidate → verified → canonical.

- Add "verified" intermediate state: candidate must pass canary before promotion
- Build rollback engine: on regression detection, auto-revert to last checkpoint
- Add supersession: when new pattern promoted, mark old version as superseded
- Store rejected candidates as evidence (already done — formalize)
- Build promotion review surface at hub: show pending/approved/rejected candidates
- Migrate candidate queue to vault-neo (from Phase 1)

**Required services:** Promotion engine (exists — enhance), rollback engine (new)
**Required queues:** Promotion queue on vault-neo, rollback queue
**Required policies:** "No promotion without canary pass" gate
**Metrics:** Promotion success rate, rollback count, time-to-promote
**Success criteria:** Bad promotion auto-detected and rolled back within 10min
**Rollback point:** Disable auto-rollback, revert to current governor

### Phase 6: Evaluator (regression detection + quality scoring)
**Goal:** Evaluator detects regressions, measures quality across dimensions, blocks bad promotions.

- Add regression detection: compare current quality metrics to 7-day rolling baseline
- Add retrieval precision scoring: did the response use relevant context?
- Add routing quality scoring: was the tier classification correct?
- Add cost efficiency scoring: was the cheapest-sufficient model used?
- Add cross-provider verification for structural changes (second-opinion gate)
- Build metrics store: queryable history of all evaluation outcomes

**Required services:** Evaluator (exists — enhance), metrics store (new)
**Required policies:** "Regression > 5% on any metric blocks promotion"
**Metrics:** Regression detection rate, false positive rate, evaluation latency
**Success criteria:** Known-bad candidate injected → evaluator blocks promotion
**Rollback point:** Disable regression gate, revert to absolute-score-only

### Phase 7: Tool/Action Fabric (local-first execution)
**Goal:** Tool work runs on K2/P1 locally. Cloud receives compact results, not raw data.

- Add local tool routing: simple file reads/status checks → qwen on K2/P1
- Add result compression: tool output → local qwen summarizes → compact result to cloud
- Add browser automation formal lane on P1 (currently ad-hoc via CC)
- Add artifact registry: produced artifacts tracked with metadata in vault
- Wire replay of execution failures: save failed tool calls, replay on P1

**Required services:** Tool router (new function in hub-bridge), artifact registry (new)
**Required policies:** "Local tool execution before cloud" enforcement
**Metrics:** % of tool calls executed locally, average tool result size sent to cloud
**Success criteria:** 80%+ of tool calls executed locally. Cloud receives <1K per tool result.
**Rollback point:** Revert to current hub-bridge tool routing

### Phase 8: Self-Improvement Pipeline (governed evolution)
**Goal:** Full observe → cluster → propose → simulate → canary → evaluate → promote/reject loop.

- Add clustering: group recurring issues/patterns before proposing (watchdog enhancement)
- Add simulation: replay candidates against saved transcripts/edge cases
- Add canary split: K2 tests reasoning-side changes, P1 tests action-side changes
- Formalize experiment lanes: K2 reasoning experiments, P1 action experiments
- Hard rule enforcement: live persona NEVER directly rewrites itself during conversation
- Remove or gate write_memory tool to prevent live self-mutation

**Required services:** Canary runner (new), replay harness (new), cluster engine (new)
**Required policies:** "No live self-mutation", "Canary before promote"
**Metrics:** Experiment success rate, canary pass rate, time from observation to promotion
**Success criteria:** Full loop executes end-to-end. Bad candidate blocked at canary.
**Rollback point:** Disable canary, revert to current governor-only pipeline

### Phase 9: Long-Horizon Evolution (continuous improvement)
**Goal:** System improves autonomously within governance bounds. Benchmarks accumulate over time.

- Memory quality evaluation: score retrieved context relevance per turn
- Routing quality evaluation: post-hoc analysis of tier classification accuracy
- Prompt/policy quality: A/B testing of system prompt variants
- Long-term benchmark history: track L_karma, task_utility, token_efficiency over months
- Identity evolution governance: strict Sovereign gate for any identity/invariant change
- Goal tracking: formal goal store with progress measurement

**Required services:** Benchmark store (new), A/B test engine (new)
**Required policies:** "Identity changes require Sovereign approval" (exists in policy)
**Metrics:** L_karma trend, cost/turn trend, promotion success trend
**Success criteria:** Measurable improvement on L_karma over 30 days
**Rollback point:** Freeze evolution, operate on current stable state

---

## 5. REQUIRED SERVICES AND QUEUES

### Existing (keep)
| Service | Location | Status |
|---------|----------|--------|
| hub-bridge | vault-neo (container) | ✅ Live — orchestrator + bridge |
| vault-api | vault-neo (container) | ✅ Live — ledger writes |
| anr-vault-search | vault-neo (container) | ✅ Live — FAISS |
| FalkorDB | vault-neo (container) | ✅ Live — graph |
| karma-server | vault-neo (container) | ✅ Live — graph queries |
| julian-cortex | K2 (systemd) | ✅ Live — local recall |
| karma-regent | K2 (systemd) | ✅ Live — Vesper pipeline |
| aria.service | K2 (systemd) | ✅ Live — tools/exec |
| P1 cortex | P1 (VBS startup) | ✅ Live — fallback |
| cc_bus_reader | K2 (cron 2min) | ✅ Live — CC bus presence |
| bus_to_cortex | K2 (cron 2min) | ✅ Live — bus→cortex feed |
| ingest_recent | K2 (cron 4h) | ✅ Live — ledger→cortex synthesis |
| sync-from-vault | K2 (cron pull 6h, push 1h) | ✅ Live — state sync |

### To Build
| Service | Location | Phase | Priority |
|---------|----------|-------|----------|
| /v1/status endpoint | hub-bridge | 2 | HIGH |
| /v1/trace endpoint | hub-bridge | 2 | HIGH |
| Cost ledger | hub-bridge | 3 | HIGH |
| Node health monitor | hub-bridge (timer) | 4 | MEDIUM |
| Rollback engine | K2 (governor extension) | 5 | HIGH |
| Promotion review UI | hub (unified.html) | 5 | MEDIUM |
| Metrics store | vault-neo | 6 | MEDIUM |
| Regression detector | K2 (eval extension) | 6 | HIGH |
| Canary runner | K2+P1 | 8 | MEDIUM |
| Replay harness | K2 | 8 | LOW |
| Cluster engine | K2 (watchdog extension) | 8 | LOW |

### Required Queues
| Queue | Location | Phase |
|-------|----------|-------|
| Promotion queue (formalized) | vault-neo | 1 |
| Cost ledger (per-request) | hub-bridge → vault-neo | 3 |
| Candidate memory queue | vault-neo | 5 |
| Canary result queue | K2+P1 → vault-neo | 8 |

---

## 6. POLICY CHANGES REQUIRED

| # | Policy Change | Current | Target | Phase |
|---|--------------|---------|--------|-------|
| PC1 | K2→vault-neo sync cadence | 6h | 30min + event-driven on promotion | 1 |
| PC2 | Promotion requires canary | No canary | Canary pass required before canonical write | 5/8 |
| PC3 | Per-model budget enforcement | Global $60/month cap only | Per-model daily caps + dynamic throttling | 3 |
| PC4 | buildSystemText compression for tier-1 | Full 15K identity block | Compressed <2K for tier-1 | 2 |
| PC5 | write_memory during conversation | Allowed with approval gate | Gate must be Sovereign-only for identity/invariant | 8 |
| PC6 | Default cloud model | claude-haiku-4-5-20251001 | SOVEREIGN DECISION | 3 |
| PC7 | Cross-provider verification | None | Required for structural changes | 6 |
| PC8 | Regression blocks promotion | No regression detection | >5% regression on any metric = blocked | 6 |

---

## 7. WHAT TO DELETE / DEPRECATE / STOP DOING

| # | Item | Action | Reason |
|---|------|--------|--------|
| DEP1 | nemotron-mini references in services.md, tools-and-apis.md | UPDATE to qwen3.5:4b | Stale since S144 |
| DEP2 | STATE.md Nemotron reference (line 5) | UPDATE | Stale since S144 |
| DEP3 | /dream skill | DEPRECATE | Replaced by cortex self-consolidation |
| DEP4 | cc_context_snapshot.md pattern | STOP DOING | Replaced by cortex offload |
| DEP5 | karma_behavioral_rules.jsonl | DEPRECATE | Never read at runtime |
| DEP6 | karma-directives.md static file | DEPRECATE | Orchestrator loads from spine |
| DEP7 | "Deep mode" as a UI concept | DEPRECATE | Both model slots use same model; tier routing is the real mechanism |
| DEP8 | 128K context assumptions anywhere | ALREADY DONE (this session) | All superseded |
| DEP9 | Sending full identity block on tier-1 turns | STOP (Phase 2) | 15K chars on simple "hi" is waste |
| DEP10 | 6-hour K2 sync interval | REDUCE (Phase 1) | Too long; crash risk |

---

## 8. FINAL RECOMMENDATION

**The single best path forward:**

1. **Resolve the Anthropic API credit blocker** — this is P0. Without cloud, Karma can only do cortex recall. Persona-quality conversation is blocked. Either add billing or switch providers.

2. **Execute Phases 1-3 as a single sprint.** They are interdependent and together deliver: vault authority hardening, observability (status/trace), and cost-optimal routing. This is the foundation the target architecture requires.

3. **Defer model provider decision to Phase 3.** The target specifies GPT-5.4 mini but the current system is all-Anthropic. This is a meaningful migration. Sovereign should decide: (a) stay Anthropic with Haiku default + Sonnet escalation, (b) switch to OpenAI with GPT-5.4 mini default + GPT-5.4 escalation + Claude verifier, or (c) hybrid. Each has trade-offs in cost, quality, and migration effort.

4. **The current system is closer to target than it appears.** The five-layer model (corrected this session), the Vesper pipeline, the cognitive split, the cortex, the coordination bus, the governance gates — these are all real infrastructure that maps to the target. The gaps are mostly in observability (no dashboard, no trace), formalized promotion (no canary, no rollback), and cost discipline (no per-model budgets, no compression).

5. **Do not over-architect.** The target lists 20+ services/queues. At current scale (1 user, 3 nodes), many of these can be functions within existing services rather than separate processes. Hub-bridge IS the orchestrator — splitting them gains nothing at this scale.

6. **The highest-leverage next actions are:**
   - Fix API credits (P0)
   - Reduce K2 sync to 30min (Phase 1, 1 cron change)
   - Add /v1/status and /v1/trace (Phase 2, ~100 lines in server.js)
   - Compress tier-1 identity block (Phase 2, ~20 lines)
   - Add per-request cost logging (Phase 3, ~50 lines)
   - Add rollback checkpoint to governor (Phase 5, ~30 lines in vesper_governor.py)

These 6 changes close the biggest gaps with minimal token cost and maximum architectural alignment.
