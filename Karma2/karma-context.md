# Karma Context Summary
Last updated: 2026-03-27 (Session 145 — Architecture Reconciliation + Model Stack)

## Runtime Truth (verified S145)

| Machine | Model | Context | Speed | Layer | Role |
|---------|-------|---------|-------|-------|------|
| K2 (192.168.0.226) | qwen3.5:4b | 32K | 58 tok/s | CORTEX | Primary working memory (711+ blocks) |
| P1 (PAYBACK) | qwen3.5:4b | 32K | 58 tok/s | CORTEX | Fallback working memory (123+ blocks) |
| vault-neo | — | — | — | SPINE + ORCHESTRATOR | Truth + routing + enforcement |
| OpenAI API | gpt-5.4-mini | 400K | — | CLOUD (default) | Standard persona chat ($0.75/$4.50 per 1M) |
| OpenAI API | gpt-5.4 | 1M | — | CLOUD (escalation) | Deep reasoning ($2.50/$15.00 per 1M) |
| Anthropic API | claude-sonnet-4-6 | — | — | CLOUD (verifier) | Cross-provider second opinion ($3.00/$15.00 per 1M) |

## Architecture (five layers — corrected S145)

- **SPINE:** vault ledger (209K+), FalkorDB (4789+ nodes), FAISS (193K+), MEMORY.md, persona files, claude-mem. Canonical truth. Lives on vault-neo.
- **ORCHESTRATOR:** hub-bridge routing, buildSystemText(), classifyMessageTier(), cognitive split, cc_regent, karma-regent, resurrect skill. Loads spine, enforces directives, routes cortex vs cloud. Persistent personality executor.
- **CORTEX:** qwen3.5:4b 32K on K2 (primary) / P1 (fallback). Active working set, cheap recall, standard chat ($0). NOT canonical identity. Hydrated from spine by orchestrator.
- **CLOUD:** GPT-5.4 mini (default tier 1-2), GPT-5.4 (escalation tier 3), Claude Sonnet 4.6 (verifier — gated, default off). Karma speaks through these when cortex cannot answer.
- **CC:** Claude Code on P1. Julian's hands. Code, files, git, deployments.

## Routing Chain
```
User message → hub-bridge classifyMessageTier()
  → Recall pattern? → K2 cortex ($0) → P1 cortex → cloud fallback
  → Tier 1-2? → gpt-5.4-mini ($0.005/turn avg)
  → Tier 3 / deep? → gpt-5.4 ($0.03/turn avg)
  → Structural change? → claude-sonnet-4-6 verifier (if VERIFIER_ENABLED)
```

## Continuity Services (running on K2)

| Service | What | Status |
|---------|------|--------|
| julian-cortex.service | K2:7892, qwen3.5:4b cortex, 711+ blocks | active |
| karma-regent.service | Vesper pipeline, spine v1242, 1284 promotions | active |
| cc-regent | CC continuity subagent | active |
| aria.service | Flask API, shell_run bridge, port 7890 | active |
| karma-kiki | Autonomous task agent | active |

## Sovereign Visibility (deployed S145)
- **/v1/status** — models, spend ($31.60/$60), node health, governance state
- **/v1/trace** — per-request cost log (model, tier, usd, tokens, provider)
- **CASCADE** — hub UI compact node health display
- **AGORA** — shared bus event surface at /agora

## Foundation Status

| Phase | Status |
|-------|--------|
| Phase 1: Build the Brain | COMPLETE (S144) |
| Phase 2: Wire CC → Cortex | COMPLETE (S145) |
| Phase 3: Wire Karma → Cortex | COMPLETE (S145) — cognitive split live |
| Phase 4: Wire P1 Fallback | COMPLETE (S145) — failover + sync |
| Phase 5: Browser + IndexedDB | DEFERRED BY RULE |
| Phase 6: Voice + Presence | DEFERRED BY RULE |

## Open Blockers
- **Chrome 146 CDP** — Phase 5 (deferred-by-rule).
- **B4 reboot** — CC server reboot survival unverified. Sovereign action.

## Key Decisions (active)
- Decision #35: GPT-5.4 mini default, GPT-5.4 escalation, Sonnet verifier (S145)
- Cortex is working memory, NOT canonical identity (S145 reconciliation)
- Orchestrator (hub-bridge) enforces persistent personality across runtimes
- Spine (vault-neo infrastructure) is the single source of truth
- K2 primary, P1 fallback — never invert (obs #18441)
- Foundation first: Phases 5-6 deferred until Sovereign verifies
