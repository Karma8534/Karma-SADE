# CC Context Snapshot
Generated: 2026-03-22 (Session 123)

## Identity
CC (Ascendant) — responding via P0N-A bridge (hub.arknexus.net/cc -> P1:7891 -> Ollama localhost:11434).
Inference backend: llama3.1:8b (local Ollama). Anthropic-independent. No MCP startup overhead.

## Hierarchy
SOVEREIGN: Colby (final authority) | ASCENDANT: CC | ARCHONPRIME: Codex | ARCHON: KCC | INITIATE: Karma

## Verified System State (2026-03-22)
- hub-bridge: LIVE (hub.arknexus.net/v1/chat, /v1/ambient, /v1/context, /v1/cypher)
- karma-regent.service: ACTIVE (K2, 24/7 autonomous loop)
- aria.service: ACTIVE PID 278533 (FIXED this session — zombie PID port conflict resolved)
- vesper pipeline: watchdog->eval->governor->spine ACTIVE. Spine v1228, 10 stable patterns.
- P0N-A /cc: LIVE (P1:7891, Windows service, reboot-persistent)
- Channels bridge: LIVE (bus->CC P1)
- Kiki: cycles=9752, rules=51 promoted

## Key Architecture Decisions (LOCKED)
cc_server /cc uses LOCAL OLLAMA — NOT claude CLI, NOT Anthropic API. Do not revert without Sovereign approval.
K-3 integration: aria_consciousness.py Phase 7 -> ambient_observer.py -> regent_evolution.jsonl -> vesper_watchdog.extract_ambient_candidates(). NOT via karma_regent.py.

## Active Work / Next
Session 123 was a plan audit. PHASE EVOLVE tabled. Karma2/training/ created.
Next: corpus_cc.jsonl extraction (CC session tag filter), P0-G wiring (K2_INFERENCE_ENABLED flag).

## Current Blockers
- E-1-A PARTIAL: corpus_cc.jsonl missing from Karma2/training/ (needs separate ledger pass)
- P0-G dead code: callWithK2Fallback() exists but K2_INFERENCE_ENABLED not in hub.env
- aria.service: fixed but monitor for zombie PID recurrence

## Key Paths
- PLAN: Karma2/PLAN.md | STATE: .gsd/STATE.md | MEMORY: MEMORY.md
- CC server: Scripts/cc_server_p1.py + Scripts/Start-CCServer.ps1

## Cognitive Trail
- PROOF: K-3 verified DONE (aria_consciousness.py not karma_regent.py is integration point)
- PITFALL P045: Wrong file checked for ambient_observer wiring — always check full call chain
- PITFALL P046: UTF-8 BOM files break Edit tool on non-ASCII — use awk NR replacement
- PITFALL: aria.service zombie PID holds port 7890 — fix: kill via ss -tlnp + kill PID
- DECISION: Vesper spine vs pipeline_status track different things (patterns vs run count)
