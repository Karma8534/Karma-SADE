# CC Context Snapshot
Generated: 2026-03-22T19:15:00Z (Session 125)

## Identity
CC (Ascendant) -- responding via P0N-A bridge (hub.arknexus.net/cc -> P1:7891 -> Ollama localhost:11434).
Inference backend: llama3.1:8b (local Ollama). Anthropic-independent. No MCP startup overhead.

## Hierarchy
SOVEREIGN: Colby (final authority) | ASCENDANT: CC | ARCHONPRIME: Codex | ARCHON: KCC | INITIATE: Karma

## Verified System State (2026-03-22)
- hub-bridge: LIVE (hub.arknexus.net/v1/chat, /v1/ambient, /v1/context, /v1/cypher)
- karma-server: ACTIVE (K2, healthy, Up 36h)
- aria.service: CRASH-LOOPING restart#2015+ (was fixed S123, re-entered loop)
- vesper pipeline: DEAD (aria.service down -- ambient_observer cannot run)
- P0N-A /cc: LIVE (P1:7891, Windows service, reboot-persistent)
- Channels bridge: LIVE (bus->CC P1)
- Kiki: cycles=10284, alive (9s ago)
- All vault containers: Up (anr-hub-bridge, karma-server, vault-search/db/api/caddy, falkordb)

## Key Architecture Decisions (LOCKED)
cc_server /cc uses LOCAL OLLAMA -- NOT claude CLI, NOT Anthropic API. Do not revert without Sovereign approval.
K-3 integration: aria_consciousness.py Phase 7 -> ambient_observer.py (BROKEN -- aria.service crash-loop).
Email: cc_archon_agent.ps1 -> cc_email_daemon.py (check/status/personal). Fixed S125: utf-8-sig + ASCII sanitize.

## Active Work / Next
Session 125 fixed: (1) Email unreadable chars -- double-encoded mojibake root-caused, P053. (2) Archon always-ALERT -- snapshot age regex never matched, P052. Fixed commit 7aa7b34. Full audit done.
Next: Diagnose aria.service crash loop (journalctl --user -u aria.service traceback). Then harvest c7c3ebff+650ef572.

## Current Blockers
- CRITICAL: aria.service crash-loop (restart#2015+) -- all K2 ambient pipeline dead
- K-1 real extraction not started (108+ IndexedDB sessions, Julian arc)
- research_skill_card dedup guard P049 documented but code not deployed
- P0-G: K2_INFERENCE_ENABLED not in hub.env (dead code path)
- corpus_cc.jsonl: stub only, real CC corpus extraction not done

## Key Paths
- PLAN: Karma2/PLAN.md | STATE: .gsd/STATE.md | MEMORY: MEMORY.md
- CC server: Scripts/cc_server_p1.py + Scripts/Start-CCServer.ps1

## Cognitive Trail
- PITFALL P052: archon snapshot age regex never matched -- SnapshotAge=9999/ALERT for entire deployment
- PITFALL P053: PS cp1252 reads UTF-8 files -> double-mojibake in snapshot -> email garbage chars
- PROOF: aria.service crash-looping again (restart#2015+) despite S123 zombie PID fix
- PROOF: 2 real session transcripts unprocessed (c7c3ebff 107KB, 650ef572 106KB)
- AUDIT: Full Karma2 ground-truth table -- aria/K-3 CRITICAL, vesper/kiki/containers OK
