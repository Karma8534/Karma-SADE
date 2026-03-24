# CC Context Snapshot
Generated: 2026-03-24 (Session 138)

## Identity
CC (Ascendant) — responding via P0N-A bridge (hub.arknexus.net/cc → P1:7891 → CC subprocess --resume).
Inference backend: claude.cmd subprocess with --resume for session continuity. Real CC, not Ollama.

## Hierarchy
SOVEREIGN: Colby (final authority) | ASCENDANT: CC | KO: Codex | KFH: KCC | INITIATE: Karma
NOTE: "ArchonPrime: Codex" and "Archon: KCC" are STALE DOCTRINE — removed in Meta session F4. Use KO/KFH.

## Verified System State (2026-03-24)
- Plan-A: DONE (JSONL backfill, auto-indexer, resurrect SSH fix)
- Plan-B: DONE (cc_server_p1.py uses real CC subprocess, hub.arknexus.net/cc verified)
- Plan-C Task 1: DONE (claude-mem binding = 127.0.0.1, configurable via settings.json)
- Plan-C Task 2: DONE (vault-neo can reach P1:7891/memory/health via Tailscale — VERIFIED)
- Plan-C Tasks 3-5: PENDING (hub-bridge /memory endpoints, WebMCP, Chrome session clone)
- claude-mem bun worker: may be in zombie/dead state — MCP searches may fail mid-session
- cc_server_p1.py: running on P1:7891, PID 31308 (latest), managed by CC-Archon-Agent task (30min)

## Key Architecture Decisions (LOCKED)
- Memory proxy path: vault-neo → hub-bridge → P1:7891/memory/* → 127.0.0.1:37777 (NOT direct :37777)
- Port 37777 blocked by Windows Firewall for headless processes; port 7891 has existing allow rule
- cc_server /cc uses CC subprocess (claude.cmd --resume) — NOT Ollama

## Active Work / Next
Plan-C Task 3: Add /memory/search + /memory/save + /memory/context endpoints to hub-bridge (server.js)
These proxy to http://100.124.194.102:7891/memory/* via Tailscale
Auth: same HUB_CHAT_TOKEN Bearer token
Deploy via karma-hub-deploy skill

## Current Blockers
- claude-mem bun worker zombie: port 37777 socket shows PID 21240 (dead) — MCP tools fail until Claude Code restart
- CC-Archon-Agent scheduled task kills/restarts cc_server_p1.py every 30min — OK behavior, not a bug

## Key Paths
- PLAN: Karma2/PLAN.md | STATE: .gsd/STATE.md | MEMORY: MEMORY.md
- GSD active: .gsd/phase-plan-c-wire-PLAN.md (Tasks 3-5 remain)
- CC server: Scripts/cc_server_p1.py (has /memory/health, /memory/search, /memory/save endpoints)
- Memory proxy URL: http://100.124.194.102:7891/memory/*

## Cognitive Trail
- PROOF: vault-neo → http://100.124.194.102:7891/memory/health → {"ok":true} (Plan-C T2 verified)
- PITFALL: Windows Firewall silently blocks headless Python processes — no interactive popup for -WindowStyle Hidden, so port 37777 was never allowed despite rule existing for python.exe
- PITFALL: claude-mem zombie socket — dead process PID 21240 leaves socket in LISTEN state; urllib.urlopen hangs even with timeout set because zombie accepts TCP SYN/ACK at kernel level
- DECISION: Use cc_server_p1.py (port 7891) as memory proxy instead of direct claude-mem port — 7891 was interactively allowed, no firewall fights needed
- FIX: resurrect Step 1 now regenerates brief before reading — prevents stale-brief drift
