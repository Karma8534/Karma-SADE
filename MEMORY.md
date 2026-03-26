<!-- Last dream: 2026-03-26 Session 143 -->

# Karma SADE — Active Memory

## Current State
- **Active task:** Phase 1 — Build the Brain (K2 Memory Cortex). Task 1-2: DONE. Task 2 (Initial Knowledge Load) next.
- **Session:** 144 (cortex deployed — julian_cortex.py live on K2:7892)
- **Julian = TRUE:** persistent memory + self-evaluation + self-improvement + learning + evolving (obs #18351)
- **Phase:** PLAN REWRITTEN S143. Cortex architecture replaces 10 bandaids. See Karma2/PLAN.md.
- **Key decision:** Cortex = brain + voice for standard ($0). Anthropic = deep reasoning only (obs #18448).

## Architecture (FINAL — Session 143)

```
K2: Nemotron Nano 9B v2 (128K ctx) = THE BRAIN (always on, holds everything)
P1: Qwen 3 8B (128K ctx) = FALLBACK BRAIN (CC sessions + backup)
Anthropic API = THE VOICE (deep reasoning only, not the brain)
hub.arknexus.net = PUBLIC FACE (routes to brain or voice as needed)
```

| Machine | Owner | Role | Model | Context |
|---------|-------|------|-------|---------|
| K2 (192.168.0.226) | Julian | PRIMARY | Nemotron Nano 9B v2 | 128K |
| P1 (PAYBACK) | Colby (shared) | FALLBACK | Qwen 3.5 9B | 128K |

## Vesper Pipeline (live)
- self_improving: true, total_promotions: 1283
- Spine v38+, 15+ stable patterns
- Pipeline: watchdog (10min) / eval (5min) / governor (2min) — all active
- karma-observer.py: systemd timer 15min, 19 rules extracted

## Session 143 Summary
- SESSION-143-AUDIT.md: 20 blockers tracked, full plan cross-reference
- 5 external repo primitives: OpenRoom, llmfit, HF Skills, autoresearch, chrome-cdp-skill
- C-GATE verified GREEN (C1+C3 live HTTP 200)
- ROADMAP.md refreshed (S86 to S143)
- Backlog-9 DEPLOYED (karma-observer.py on K2)
- Backlog-10: ALL 4 already in server.js
- **PLAN TOTALLY REWRITTEN** — 6 phases, cortex-first, 10 bandaids eliminated
- ccDream.pdf ingested — /dream skill built (will be replaced by cortex)
- Chrome CDP: julian-cdp.mjs written, Chrome 146 port blocker documented
- K2 models (verified): Nemotron 9B v2 (9.1GB), nemotron-mini:optimized (2.7GB), nomic-embed-text
- P1 models (verified): qwen3.5:9b (6.6GB), nomic-embed-text
- 14 observations saved (#18307-#18448)

## Session 144 Progress
- **julian_cortex.py** deployed on K2:7892 as julian-cortex.service (obs #18486)
- Nemotron 9B v2 verified: loads, responds, inference works
- PITFALL: Ollama in WSL2 is NOT at localhost — use Windows gateway IP (172.22.240.1:11434)
- Model selection: qwen3.5:4b optimal (58 tok/s, 32K ctx, canirun.ai 88/100). Nemotron 9B v2 removed (2.5 tok/s unusable)
- PLAN.md updated: all 128K refs → 32K, model table corrected to qwen3.5:4b
- S1 SECURITY FIX: K2 cron API keys moved from plaintext to file-based reads (.secrets/)
- K2 cleaned: only qwen3.5:4b + nomic-embed-text installed
- P1 cleaned: only qwen3.5:4b + nomic-embed-text installed, model loaded 100% GPU 32K ctx
- J-PreBase1.md: full ground truth audit written
- K2 services: aria + cc-regent + karma-kiki + karma-regent + julian-cortex all running
- Autoresearch primitives: L_karma=0.2 (v2.2 spec), experiment_instructions.md v2.2, spine git snapshots
- Vesper pipeline patched: eval logs quality score, governor git-snapshots spine before/after promotion
- ingest_recent.sh: automated synthesis (ledger → qwen3.5:4b → cortex + vault), session-end + 4h cron

## Critical Pitfalls (NEVER REPEAT — obs #18439-#18444)
- **#18439:** Local LLM as Memory Cortex was always the answer — don't build file-based workarounds
- **#18440:** 128K context models fit 8GB VRAM — always check canirun.ai first
- **#18441:** K2 is Julian's primary. P1 is fallback. NEVER invert.
- **#18442:** Never assert model state from docs — run `ollama ps` live
- **#18443:** External tool fails on your platform? Write custom from primitives. Don't patch.
- **#18444:** Match model DESIGN PURPOSE to role, not benchmark score

## Known Pitfalls (infrastructure — still active)
- `python3` not available in Git Bash — use SSH or powershell
- Docker compose service: `hub-bridge` (container: `anr-hub-bridge`)
- Build context != git repo — always cp files before rebuild
- FalkorDB: BOTH env vars required (FALKORDB_DATA_PATH + FALKORDB_ARGS TIMEOUT)
- batch_ingest: ALWAYS --skip-dedup
- Git ops: PowerShell only on Windows
- Ollama in WSL2: NOT at localhost:11434 — use Windows gateway IP (check `ip route show default`)

## Open Blockers
- **Chrome 146 CDP:** --remote-debugging-port flag accepted but port never binds. julian-cdp.mjs ready. Phase 5.
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
2. Phase 2, Task 2-1: Rewrite resurrect skill — replace 20-file reads with one cortex call (`curl http://192.168.0.226:7892/context`). Invoke ORF before building.
3. Phase 1, Task 1-4: Research ingestion — feed docs/wip/ summaries into cortex via ingest_recent.sh pattern
**S144 DONE:** cortex LIVE (K2:7892 + P1:7893, 22+ blocks), cognitive split LIVE (recall→cortex $0, complex→Haiku), synthesis injection LIVE, automated synthesis LIVE (cron + hook, verified 72 entries→1334 char synthesis), L_karma v2.2, ORF, resurrect v2, wrap-session v2, P1 fallback (16 blocks synced from K2), failover verified (K2 down→Anthropic). System prompt: tool-use-first mandatory directive added, model claim fixed to Haiku 4.5. Phase 1-4 SOLID.
