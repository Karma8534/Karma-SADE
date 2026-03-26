# Karma Context Summary
Last updated: 2026-03-26 (Session 145 — Architecture Reconciliation)

## Runtime Truth (verified)

| Machine | Model | Context | Speed | Layer | Role |
|---------|-------|---------|-------|-------|------|
| K2 (192.168.0.226) | qwen3.5:4b | 32K | 58 tok/s | CORTEX | Primary working memory |
| P1 (PAYBACK) | qwen3.5:4b | 32K | 58 tok/s | CORTEX | Fallback working memory |
| vault-neo | — | — | — | SPINE + ORCHESTRATOR | Truth + routing + enforcement |
| Anthropic API | claude-haiku-4-5-20251001 | — | — | CLOUD | Deep reasoning (credits exhausted as of S144) |

## Architecture (five layers)

- **SPINE:** vault ledger (207K+), FalkorDB (4789+ nodes), FAISS (193K+), MEMORY.md, persona files, claude-mem. Canonical truth. Lives on vault-neo.
- **ORCHESTRATOR:** hub-bridge routing, buildSystemText(), cc_regent, karma-regent, resurrect skill. Loads spine, enforces directives, routes cortex vs cloud. Persistent personality executor.
- **CORTEX:** qwen3.5:4b 32K on K2 (primary) / P1 (fallback). Active working set, cheap recall, standard chat ($0). NOT canonical identity. Hydrated from spine by orchestrator.
- **CLOUD:** Anthropic API. Complex reasoning, tool orchestration. $cost. Currently blocked (credits exhausted).
- **CC:** Claude Code on P1. Julian's hands. Code, files, git, deployments.

## Continuity Services (running on K2)

| Service | What | Status |
|---------|------|--------|
| julian-cortex.service | K2:7892, qwen3.5:4b cortex | ✅ active |
| karma-regent.service | Vesper pipeline, behavioral self-improvement | ✅ active |
| cc-regent | CC continuity subagent | ✅ active |
| aria.service | Flask API, shell_run bridge | ✅ active |
| karma-kiki | Autonomous task agent | ✅ active |

## Foundation Status

| Phase | Status |
|-------|--------|
| Phase 1: Build the Brain | ✅ COMPLETE (S144) |
| Phase 2: Wire CC → Cortex | IN PROGRESS — Task 2-1 next |
| Phase 3: Wire Karma → Cortex | PARTIAL — 3-1 done, 3-2/3-3 remain |
| Phase 4: Wire P1 Fallback | PARTIAL — 4-1 done, 4-2/4-3/4-4 remain |
| Phase 5: Browser + IndexedDB | DEFERRED BY RULE — Sovereign gate required |
| Phase 6: Voice + Presence | DEFERRED BY RULE — Sovereign gate required |

## Open Blockers

- **Anthropic API credits exhausted** — Haiku path returns 400. Cortex $0 path is only working chat path.
- **Chrome 146 CDP** — --remote-debugging-port flag accepted but port never binds. Phase 5 (deferred).
- **B4 reboot** — CC server reboot survival unverified. Sovereign action.

## Key Decisions (active)

- Cortex is working memory, NOT canonical identity (Session 145 reconciliation)
- Orchestrator (hub-bridge + regents) enforces persistent personality across runtimes
- Spine (vault-neo infrastructure) is the single source of truth
- K2 primary, P1 fallback — never invert (obs #18441)
- Foundation first: Phases 5-6 deferred until Sovereign verifies Phases 1-4
