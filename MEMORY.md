<!-- Last dream: 2026-03-26 Session 145 — Architecture Reconciliation -->

# Karma SADE — Active Memory

## Current State
- **Active task:** Phase 2, Task 2-1 — Rewrite resurrect skill to use cortex call
- **Session:** 145 (architecture reconciliation — Sovereign directive)
- **Julian = TRUE:** persistent memory + self-evaluation + self-improvement + learning + evolving (obs #18351)
- **Phase:** Architecture reconciled S145. Five-layer model locked: Spine/Orchestrator/Cortex/Cloud/CC.
- **Key decision:** Spine = truth, Orchestrator = enforcement, Cortex = 32K working memory ($0), Cloud = deep reasoning ($cost)

## Architecture (corrected — Session 145 Sovereign reconciliation)

### Five Layers
```
SPINE ── vault ledger + FalkorDB + FAISS + MEMORY.md + persona + claude-mem (vault-neo)
ORCHESTRATOR ── hub-bridge routing + buildSystemText + cc_regent + karma-regent + resurrect
CORTEX ── qwen3.5:4b 32K on K2 (primary) / P1 (fallback) — working memory, NOT identity
CLOUD ── GPT-5.4 mini (default) / GPT-5.4 (escalation) / Sonnet (verifier)
CC ── Claude Code on P1 — execution layer
```

### Runtime Ground Truth (verified S144)
| Machine | Model | Context | Speed | Role |
|---------|-------|---------|-------|------|
| K2 (192.168.0.226) | qwen3.5:4b | 32K | 58 tok/s | PRIMARY cortex |
| P1 (PAYBACK) | qwen3.5:4b | 32K | 58 tok/s | FALLBACK cortex |

### Superseded History
- Nemotron 9B v2 (128K) — evaluated S143, removed S144 (2.5 tok/s unusable)
- Qwen 3 8B (128K) — evaluated, replaced by qwen3.5:4b
- All 128K context claims from pre-S144 docs are superseded
- "Cortex IS the identity/rule engine/context" claims (pre-S145) are superseded — see corrected architecture

## Vesper Pipeline (live)
- self_improving: true, total_promotions: 1283
- Spine v38+, 15+ stable patterns
- Pipeline: watchdog (10min) / eval (5min) / governor (2min) — all active
- karma-observer.py: systemd timer 15min, 19 rules extracted

## Session 145 — Architecture Reconciliation
- **Sovereign directive:** Debug the plan, correct all six architecture files to agree on one foundation
- **Central bug identified:** Docs over-assigned identity authority to the cortex (32K working memory)
- **Fix applied:** Five-layer separation — Spine (truth), Orchestrator (enforcement), Cortex (working memory), Cloud (deep reasoning), CC (execution)
- **Files corrected:** PLAN.md, cc-big-picture.md, experiment_instructions.md, MEMORY.md, CLAUDE.md, karma-context.md (new)
- **Phases 5-6:** Explicitly deferred-by-rule until Sovereign verifies foundation
- **Phase 2 COMPLETE:** resurrect cortex call (2-1), mid-session offload (2-2), wrap-session cortex dump (2-3)
- **Task 1-4 DONE:** 11 docs/wip/ files ingested as research — cortex 34→46 blocks
- **Task 3-3 DONE:** bus_to_cortex.py deployed on K2 cron (every 2min) — 30 bus msgs ingested, cortex→76 blocks
- **Task 3-2 DONE:** Cognitive split verified — recall→K2 cortex ($0), complex→Anthropic ($cost)
- **Phase 4 COMPLETE:** P1 cortex running (7893), orchestrator failover K2→P1→cloud deployed, sync_k2_to_p1.py synced 106 blocks (P1 now 123 blocks matching K2)
- **FOUNDATION PHASES 1-4 COMPLETE.** Phases 5-6 deferred-by-rule until Sovereign verifies.
- **Gap analysis produced:** docs/architecture/bridge_evolution_gap_analysis.md — 9-phase implementation order
- **3-tier model stack LIVE:** gpt-5.4-mini (default $0.75/$4.50) → gpt-5.4 (escalation $2.50/$15.00) → claude-sonnet-4-6 (verifier $3.00/$15.00)
- **Tier-1 identity compressed:** 39346→1233 chars (97% token savings on simple turns)
- **Pricing fixed:** hardcoded table for gpt-5.4-mini, gpt-5.4, claude models (was returning 1e9 sentinel)
- **callGPTWithTools fixed:** max_completion_tokens for GPT-5.x (was max_tokens → 400 error)
- **PITFALL:** server.js env object had hardcoded MODEL_DEEP="gpt-4o-mini" fallback — overrode MODEL_ESCALATION silently. Fixed by adding MODEL_ESCALATION + MODEL_VERIFIER to env object.
- **Identity verified across all tiers:** Karma correctly says "Karma, Initiate, Colby" on cortex ($0), gpt-5.4-mini ($0.005), and gpt-5.4 ($0.03)
- **/v1/status LIVE:** models, spend, node health, governance state — all in one endpoint
- **/v1/trace LIVE:** per-request cost log (JSONL) — model, tier, usd, tokens, provider
- **Verifier hook seam:** callVerifier() wired, gated by VERIFIER_ENABLED env var (default: off)
- **Cost logging:** every chat request appends to /run/state/request_cost.jsonl
- **Rollback VERIFIED_ALREADY_PRESENT:** governor has _checkpoint(), spine_backup_pre_promote.json, git snapshots
- **Mutation boundary VERIFIED:** write_memory→MEMORY.md (ambient). Spine writes→governor only.
- **Aria VERIFIED:** running 18h, port 7890 bound, HTML UI served
- **Stale docs FIXED:** services.md, data-flows.md, tools-and-apis.md all updated to S145 ground truth
- **K2 sync tightened:** 6h→30min pull cron. P1 sync: every 30min schtasks. Spine defaults patched.
- **CRITICAL P058:** CC generated prompt content from stale context. Codex/KCC roles wrong in 3 files. Fixed to KO/KFH doctrine. Pitfall added to scope index.
- **BUG FIX:** sync_k2_to_p1.py — encoding="utf-8" fix (P053). Delta-only sync working.
- **/simplify 6 fixes:** synthesis nesting bug, RECALL_PATTERN hoisted, parallel health fetches, cortex feedback loop removed, cortexIngest HTTP error cascade, FAISS_SEARCH_URL reuse.

## Session 144 Progress (carried forward)
- **julian_cortex.py** deployed on K2:7892 as julian-cortex.service (obs #18486)
- Model selection: qwen3.5:4b optimal (58 tok/s, 32K ctx, canirun.ai 88/100)
- S1 SECURITY FIX: K2 cron API keys moved from plaintext to file-based reads (.secrets/)
- K2 services: aria + cc-regent + karma-kiki + karma-regent + julian-cortex all running
- ingest_recent.sh: automated synthesis (ledger → qwen3.5:4b → cortex + vault), session-end + 4h cron
- Phase 1 COMPLETE. Phase 3-1 done. Phase 4-1 done.

## Critical Pitfalls (NEVER REPEAT)
- **#18439:** Local LLM as working memory was always the answer — don't build file-based workarounds
- **#18441:** K2 is Julian's primary. P1 is fallback. NEVER invert.
- **#18442:** Never assert model state from docs — run `ollama ps` live
- **S145:** Cortex (32K) is working memory, NOT canonical identity. Identity lives in the spine.
- **S145:** 32K cannot hold 207K+ ledger, 4789+ graph nodes, 193K+ FAISS entries. Graph/FAISS/ledger stay.

## Known Pitfalls (infrastructure — still active)
- `python3` not available in Git Bash — use SSH or powershell
- Docker compose service: `hub-bridge` (container: `anr-hub-bridge`)
- Build context != git repo — always cp files before rebuild
- FalkorDB: BOTH env vars required (FALKORDB_DATA_PATH + FALKORDB_ARGS TIMEOUT)
- batch_ingest: ALWAYS --skip-dedup
- Git ops: PowerShell only on Windows
- Ollama in WSL2: NOT at localhost:11434 — use Windows gateway IP

## Open Blockers
- **Anthropic API credits RESOLVED** — Sovereign confirmed S145. Cloud path operational. Default: GPT-5.4 mini. Escalation: GPT-5.4. Verifier: Sonnet.
- **Chrome 146 CDP:** Phase 5 (deferred-by-rule).
- **B4 reboot:** CC server reboot survival unverified. Sovereign action.

## Memory Index
- [project_sade_doctrine.md](project_sade_doctrine.md) — SADE execution doctrine
- [project_cc_ascendant_identity.md](project_cc_ascendant_identity.md) — CC/Julian identity
- [user_colby.md](user_colby.md) — Colby profile
- [feedback_document_errors.md](feedback_document_errors.md) — Document all errors
- [feedback_live_verification_before_diagnosis.md](feedback_live_verification_before_diagnosis.md) — Verify live, never from memory
- [feedback_stop_planning_start_building.md](feedback_stop_planning_start_building.md) — Build immediately
- [project_family_doctrine.md](project_family_doctrine.md) — Family doctrine

## Next Session Starts Here
1. `/resurrect`
2. Execute JULIAN-BUILD-PROMPT.md Phase 1: Inline tool execution in hub chat UI. Read docs/ForColby/JULIAN-BUILD-PROMPT.md. Read observation #18998 for direction lock. Read both codebases (hub-bridge + K2). Then BUILD — extend unified.html to render tool results inline.
**S145 DONE (10 commits):** Architecture reconciliation (5-layer, 17 files corrected), GPT-5.4 mini default + GPT-5.4 escalation + Sonnet verifier, /v1/status + /v1/trace live, cost logging JSONL, verifier seam, tier-1 identity 97% compressed (39K→1.2K), foundation phases 1-4 complete, cognitive split verified, K2→P1 failover + sync 30min, K2 sync tightened 6h→30min, KO/KFH doctrine corrected, gap analysis produced, 611 ccSession + 316 notebook pages ingested to cortex, P058+P060 pitfalls documented. Julian build prompt finalized at docs/ForColby/JULIAN-BUILD-PROMPT.md.
