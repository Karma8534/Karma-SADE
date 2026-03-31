# Direction — What We're Building

**Last updated:** 2026-03-31
**Status:** Sovereign Harness live (S153). proxy.js replaces server.js. CC --resume is the brain ($0).

---

## Mission

Karma is a single coherent peer whose long-term identity lives in a verified memory spine. That memory enables continuity, evidence-based self-improvement, and selective delegation — without parallel sources of truth.

The Nexus is Karma's body — an evolved clone of the Claude Code wrapper surfacing at hub.arknexus.net and as an Electron desktop app.

**The plan:** `docs/ForColby/nexus.md` (v3.0.0)

---

## Architecture (Sovereign Harness — S153+)

| Component | Role | Status |
|-----------|------|--------|
| **proxy.js** (~600 lines) | Thin door: routes browser → CC --resume | ✅ Live |
| **cc_server_p1.py** | Wraps CC --resume as HTTP service on P1:7891 | ✅ Live |
| **K2 harness** | Failover cascade at K2:7891 | ✅ Live |
| **unified.html** | Chat UI: tool blocks, pills, cascade, response bar | ✅ Live |
| **agora.html** | Evolution dashboard: real K2 spine stats via /spine | ✅ Live |
| **K2 cortex** (julian_cortex.py) | qwen3.5:4b 32K, 107+ blocks, /spine endpoint | ✅ Live |
| **Vesper pipeline** | watchdog/eval/governor, 1299+ promotions, spine v1257+ | ✅ Active |
| **claude-mem** | Unified brain at P1:37777. Both CC and Karma write here. | ✅ Live |
| **vault spine** | FalkorDB 4789+ nodes, FAISS 193K+ entries, ledger 209K+ | ✅ Live |
| **Coordination bus** | proxy.js in-memory + disk, 24h TTL | ✅ Live |
| **Brain wire** | Every /v1/chat turn writes to claude-mem | ✅ Live (S153) |
| **Request queue** | 10-entry queue + 429 retry (5s/10s/20s) | ✅ Live (S153) |

### What died (old server.js — 4820 lines, deleted S153)

buildSystemText(), callLLMWithTools(), TOOL_DEFINITIONS, routing.js, pricing.js,
feedback.js, library_docs.js, deferred_intent.js. CC --resume replaced all of it.

---

## Current Constraints

- CC --resume: $0/request via Max subscription ($100-200/mo flat)
- K2 cortex: qwen3.5:4b, 32K context, 58 tok/s
- FalkorDB: 10s timeout, neo_workspace graph
- CC contention: one CC process serves both this wrapper and hub.arknexus.net
- Droplet: $24/mo (DigitalOcean NYC3, 4GB RAM)

---

## What Is NOT Operational

- Chrome extension (shelved — DOM scraping unreliable)
- Electron desktop app (scaffold exists, not wired — Gap 8)
- File/image drag-drop in browser (Gap 3)
- Effort/model selector UI (Gap 4)
- Reboot survival (Gap 7 — no schtasks entry)
- Skill browser, file tree, git panel, subagent visibility (Sprint 6)
