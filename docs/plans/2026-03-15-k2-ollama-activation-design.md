# K2 Ollama Activation — Local-First Inference

**Date:** 2026-03-15
**Status:** Implementing
**Decision:** Activate K2 Ollama as primary inference for all Karma chat. Anthropic as fallback only.

## Context

- `callWithK2Fallback()` deployed in hub-bridge server.js (Session 85, lines 1302-2151)
- Code tries K2 Ollama first, falls back to Anthropic on failure
- Currently **disabled** — `K2_OLLAMA_URL` not set in hub.env
- `qwen3-coder-30b-a3b` available on K2 (MoE: 30B params, 3B active — efficient on RTX 4070 8GB)
- Ollama running at localhost:11434 on P1
- `nomic-embed-text` available locally for future embedding replacement

## Architecture

```
User → hub.arknexus.net → hub-bridge (vault-neo)
  → [1] K2 Ollama via Tailscale (100.75.109.92:11434) — qwen3-coder-30b-a3b
  → [2] Anthropic Haiku API (cloud fallback if K2 unreachable)

CC (P1) → localhost:11434 → Ollama direct (LAN, always available)
```

### Fallback Layers
| Priority | Path | Latency | Cost |
|----------|------|---------|------|
| 1 | vault-neo → Tailscale → K2 Ollama | ~50-100ms network + 4-7s inference | $0 |
| 2 | Anthropic Haiku API | ~1-2s | $1.00/$5.00 per 1M tokens |

CC leverages localhost:11434 directly for its own operations (evaluation, benchmarks, analysis) — zero cloud dependency for CC-initiated work.

## Activation Steps

1. Verify Ollama reachable from vault-neo via Tailscale
2. Add to hub.env: `K2_OLLAMA_URL=http://100.75.109.92:11434/v1` and `K2_OLLAMA_MODEL=qwen3-coder-30b-a3b`
3. `cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml up -d`
4. Verify hub-bridge logs show `[INIT] K2 Ollama client ready`
5. Send test chat and confirm K2 routing in logs

## Phase 2 (next session): Replace OpenAI Embeddings
- Switch anr-vault-search from text-embedding-3-small (OpenAI) to nomic-embed-text (local Ollama)
- Kills OpenAI API dependency entirely

## Phase 3 (horizon): Full Sovereignty
- All inference local. External APIs = optional augmentation only.
- CC evaluates Karma quality on local vs cloud to build evidence.
- Family north star: zero external API dependence.
