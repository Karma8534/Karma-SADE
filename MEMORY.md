<!-- Last dream: 2026-03-27 Session 149 — Nexus Build + Phase 7 Complete -->

# Karma SADE — Active Memory

## Current State
- **Active task:** Nexus — inline evidence, tool access, cascade fix, Karma tool-use enforcement
- **Session:** 149 (Nexus build + Phase 7 complete + Karma behavioral fixes)
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
- self_improving: true, total_promotions: 1284
- Spine v1242, 15+ stable patterns
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

## Session 147 — Forensic Reconciliation (2026-03-27)
- **S147 directive:** Fix all wrongs identified in forensic pass of 17 ForColby files
- **routing.js:** MODEL_DEEP zombie removed from chooseModel() + validateModelEnv() (#M9)
- **server.js:109:** Distillation model hardcode fixed → process.env.MODEL_DEFAULT (#M1)
- **bus_to_cortex.py:** datetime.utcnow() → datetime.now(timezone.utc) (#M5)
- **PLAN.md:** Cloud layer corrected — GPT-5.4 mini/GPT-5.4/Sonnet (was "Anthropic API") (#T1.4/5)
- **cc-big-picture.md + MEMORY.md:** 1283→1284 promotions, v38+→v1242 spine version (#M8, #T1.1-3)
- **Already fixed (confirmed):** synthesis nesting, recall feedback loop, cortexIngest cascade
- **vesper_eval.py (K2):** _check_regression() added — rolling 20-entry baseline, >5% drop → REGRESSION signal to audit + bus (#T2.5)
- **hub-bridge deployed:** v2.12.0, restart count 0
- **Mutation boundary VERIFIED:** write_memory→MEMORY.md (ambient). Spine writes→governor only.
- **Aria VERIFIED:** running 18h, port 7890 bound, HTML UI served
- **Stale docs FIXED:** services.md, data-flows.md, tools-and-apis.md all updated to S145 ground truth
- **K2 sync tightened:** 6h→30min pull cron. P1 sync: every 30min schtasks. Spine defaults patched.
- **CRITICAL P058:** CC generated prompt content from stale context. Codex/KCC roles wrong in 3 files. Fixed to KO/KFH doctrine. Pitfall added to scope index.
- **BUG FIX:** sync_k2_to_p1.py — encoding="utf-8" fix (P053). Delta-only sync working.
- **/simplify 6 fixes:** synthesis nesting, RECALL_PATTERN hoist, parallel health, feedback loop, cortexIngest cascade, FAISS URL
- **Automations deployed:** credential-guard hook (P060), memory-reminder hook, context7 MCP, Docker MCP, /simplify added to wrap-session Step 3.5
- **cc_bus_reader.py (T3.3):** cortex-first routing implemented — classify_tier() routes simple→cortex($0), complex→Anthropic($). Fallback: cortex unreachable→Anthropic. MODEL env var (was hardcoded). datetime.utcnow() fixed. ANTHROPIC_KEY no longer hard-fails. Live on K2 + synced to Scripts/.
- **ACTIONABLE_FROM LOCKED (#19119):** {"colby", "karma", "regent"} — true family + intra-entity body only. Codex(KO) + KCC(KFH) excluded. Full agent bus = clusterfuck (historical). Sovereign decision 2026-03-27.

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

## Known Pitfalls (S147 — new)
- **P062 (#19103):** `datetime.utcnow()` is a recurring K2 bug — found in 3 scripts across 2 sessions. Pre-deploy scan: `grep -r "utcnow" /mnt/c/dev/Karma/k2/`
- **P063 (#19104):** K2 scripts silently diverge from local repo `Scripts/`. Always diff before commit. K2 = source of truth; Scripts/ = mirror.
- **P064 (#19105):** `ACTIONABLE_FROM` divergence unresolved — P3-B (colby-only) in local repo vs expanded set on K2. **OPEN SOVEREIGN DECISION REQUIRED.**
- **P065 (#19107):** LLM model names hardcoded in K2 cron scripts. All model refs must use `os.environ.get()`. Grep check: `grep -n '"claude-\|"gpt-' k2/scripts/*.py`
- **P066 (#19108):** Hard-exit on missing cloud API key even when local cortex path can serve. Never `sys.exit()` on missing cloud credential when a local path exists.

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

## Session 148 — Intelligence Primitives Plan (2026-03-27)
- **ORF x3 completed:** Aider (sqrt dampening, token budget binary search, repo map) + Roo-Code (tool scoping, boomerang, prompt registry, file restriction, config modes) primitives evaluated and merged into PLAN.md
- **Phase 7 added:** 8 tasks — 7-1 through 7-8. See docs/ForColby/PLAN.md.
- **PLAN.md state corrected:** Phases 2, 3, 4 all marked COMPLETE (were stale-pending since S145)
- **MCP insight:** Task 7-7 → add to existing K2 MCP server (not new endpoint). Task 7-8 → MCP call IS boomerang pattern, already half-built. (obs #19149)
- **FastMCP pattern locked:** All new K2 capabilities = `@mcp.tool()` in existing server. Never a new port.
- **P062-P066 pitfalls documented:** datetime.utcnow() recurrence, K2/Scripts/ drift, ACTIONABLE_FROM (resolved), hardcoded model names, hard-exit on missing cloud key
- **ACTIONABLE_FROM LOCKED:** {colby, karma, regent} — Sovereign decision 2026-03-27 (obs #19119)
- **Cortex:** 126 blocks after session dump (rotated older blocks)

## Session 149 (2026-03-27) — Nexus Build + Phase 7 Complete
- Phase 7 all 8 tasks deployed: sqrt dampening, token budget, named sections, modes, tool scoping, file restrictions, repo map, boomerang
- Nexus 9-gate live verification passed (browser + API)
- K2 cortex fixed: think:False + MAX_KNOWLEDGE_CHARS 24K (was 100K, 90s→2.7s)
- MODEL_DEFAULT reverted to claude-haiku-4-5-20251001 (gpt-5.4-mini refuses tools — P068)
- Single nexus mode: collapsed 3 modes → 1. All tools always.
- 7 tool-use-first rules added to Karma system prompt
- UI: inline tool evidence, markdown rendering, copy button, scroll arrows, cascade dots updated
- 11 research docs ingested to cortex (Task 1-4 done)
- Cortex refusal fallthrough: CORTEX_REFUSAL regex detects "I cannot" and falls to cloud
- 8 known issues documented in STATE.md for post-stabilization
- P067: cortex /health passes while /query hangs
- P068: gpt-5.4-mini ignores tool-use instructions
- Simplify review: 6 code quality fixes applied (hoisted constants, unified serialization, removed dead defaults)

## Session 150 (2026-03-28) — Sovereign Harness OPERATIONAL
- **ROOT CAUSE FIXED:** cc_server_p1.py WinError 2 — was using list-based subprocess([claude.cmd,...]) without shell. Fixed: [NODE_EXE, CLAUDE_CLI_JS] direct node.exe invocation bypasses .cmd wrapper entirely.
- **NODE_EXE:** C:\Program Files\nodejs\node.exe ✅ exists
- **CLAUDE_CLI_JS:** C:\Users\raest\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\cli.js ✅ exists
- **PROOF:** hub.arknexus.net/v1/chat → sovereign-proxy → P1:7891/cc → node cli.js → {"ok":true,"assistant_text":"ONLINE"} (obs #19412)
- **PITFALL:** Tailscale health check timeout was 3s — too tight for transient spikes. Fixed to 8s in proxy.js.
- **PITFALL:** Multiple stale Python processes accumulate on port 7891. Always `Get-Process python* | Stop-Process -Force` before restart.
- **proxy.js deployed** to vault-neo with 8s health check timeout

## Next Session Starts Here
1. `/resurrect`
2. Browser smoke test at hub.arknexus.net — verify Karma responds via sovereign harness in real browser session
