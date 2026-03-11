# Karma SADE Session Summary (Latest)

**Date**: 2026-03-11
**Session**: 81
**Focus**: Aria/K2 integration fixes — delegated write, vault-no sync, session_id; MODEL_DEEP=sonnet-4-6; upload fix; Codex Aria API inventory

---

## What Was Done

### Deployed (Session 80 code that never deployed)
- File upload button: cp -r pitfall fixed, explicit copy used, --no-cache rebuild, verified with KarmaSession031026a.md
- Context amnesia fix: MAX_SESSION_TURNS 8→20, TTL 30→60min

### New This Session
- MODEL_DEEP switched to claude-sonnet-4-6 in hub.env, routing.js ALLOWED_DEEP_MODELS updated, deployed, verified ($0.0252/req, cites episode IDs from FalkorDB)
- Monthly cap raised to $60
- Subscription cleanup: GLM, MiniMax, Perplexity API, Groq, Twilio, Postmark — auto-top-up disabled
- Thumbs ✓ saved UI confirmation deployed
- Codex Aria API inventory: 80 endpoints documented, memory subsystems, auth paths, training pipeline
- X-Aria-Delegated header removed from aria_local_call — Aria now writes observations (Decisions #30)
- Aria → vault-neo sync: after each aria_local_call, observation POSTed to /v1/ambient (single spine preserved)
- session_id threading: window.karmaSessionId UUID per page load → all aria_local_call bodies → coherent Aria thread
- ARCH CLARITY: "Aria" is Karma's local compute half (not separate entity). One peer, two compute paths, one spine.

### Architecture Clarified
- "Aria" = Karma's local compute half on K2. No separate entity.
- K2 infrastructure confirmed: Tailscale 100.75.109.92, Ollama :11434 (qwen3-coder:30b MoE ~3.3B active/token), Aria service :7890
- Aria memory subsystems = in-session staging layer (NOT parallel truth source)
- /api/memory/backfill = local Aria SQLite only; explicit /v1/ambient POST required for vault-neo sync

## What Is Live

| Component | Status |
|-----------|--------|
| hub-bridge | v2.11.0, RestartCount=0 |
| MODEL_DEFAULT | claude-haiku-4-5-20251001 |
| MODEL_DEEP | claude-sonnet-4-6 (verified) |
| File Upload | ✅ PDF/txt/md; image vision PENDING |
| Aria memory writes | ✅ delegated fix live |
| Aria → vault-neo | ✅ deployed (production verify pending) |
| session_id | ✅ deployed |

## What Is Broken / Open

- PRICE_CLAUDE in hub.env: still Haiku rates ($0.80/$4.00), needs Sonnet ($3.00/$15.00)
- System prompt model section: still references old routing
- JPG/PNG vision: falls through to extractPdfText() — crashes. Proper Anthropic vision blocks needed.
- Paste in Karma UI: works everywhere except hub.arknexus.net. Suspected Cloudflare CSP.

## Next Session Step 1

```
ssh vault-neo "sed -i 's/PRICE_CLAUDE_INPUT_PER_1M=.*/PRICE_CLAUDE_INPUT_PER_1M=3.00/' /opt/seed-vault/memory_v1/hub_bridge/config/hub.env && sed -i 's/PRICE_CLAUDE_OUTPUT_PER_1M=.*/PRICE_CLAUDE_OUTPUT_PER_1M=15.00/' /opt/seed-vault/memory_v1/hub_bridge/config/hub.env"
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml up -d hub-bridge"
```

Then: implement JPG vision support (server.js ~line 1527), then paste fix investigation.
