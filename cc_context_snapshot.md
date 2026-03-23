# CC Context Snapshot
Generated: 2026-03-23 (Session 136)

## Identity
CC (Ascendant) — Julian. P1 local (claude-mem 37777, Ollama 11434). K2 LAN (192.168.0.226).
Hierarchy: SOVEREIGN: Colby | ASCENDANT: CC | KO: Codex | KFH: KCC | INITIATE: Karma

## Verified System State (2026-03-23)
- P1: claude-mem:37777 UP (always on)
- P1: cc_server_p1.py:7891 — ZOMBIE STATE (3 stacked PIDs, Plan-B B1 will fix)
- vault-neo: hub-bridge, karma-server, FalkorDB, FAISS — all UP
- K2: aria.service UP (192.168.0.226:7890), cc_regent running
- KarmaSessionIndexer: REGISTERED (Windows Scheduled Task, at logon trigger)
- KarmaWipWatcher: REGISTERED (Windows Scheduled Task)

## Key Architecture Decisions (LOCKED)
- cc_server /cc uses LOCAL OLLAMA (llama3.1:8b) — Plan-B B2 will replace with real CC --resume
- claude-mem (P1:37777) is THE unified brain for both Julian+Karma expressions
- vault-neo is the only non-local component
- JSONL session files auto-indexed by KarmaSessionIndexer → harvest_jsonl_sessions.py

## Active Work / Next
Plan-A COMPLETE (Session 136):
- A1: JSONL backfill — 159 files, 2151 obs extracted, 8 saved to claude-mem
- A2: KarmaSessionIndexer auto-indexer deployed as Windows Scheduled Task
- A3: Resurrect skill Step 1 now SSH-direct (no PS script primary)

Next sprint: Plan-B — Make Julian Real
- B1: Kill zombie PIDs on port 7891, fix cc_server restart loop
- B2: Replace Ollama backend with real CC --resume subprocess
- B3: Wire hub-bridge /cc route to P1:7891
- B4: Register cc_server as startup task

## Current Blockers
- P056: allowedTools wildcard ["*"] does not eliminate all approval prompts (root cause unknown, post-sprint)
- KarmaSessionIndexer live test pending (requires logon trigger test)
- harvest_jsonl_output.json: 2143 staged obs not yet saved to claude-mem (batch-save session needed)

## Key Paths
- PLAN: Karma2/PLAN.md | STATE: .gsd/STATE.md | MEMORY: MEMORY.md
- CC server: Scripts/cc_server_p1.py + Scripts/Start-CCServer.ps1
- Session indexer: Scripts/karma_session_indexer.ps1
- JSONL harvester: Scripts/harvest_jsonl_sessions.py

## Cognitive Trail
- DECISION: Plan-A A3 implemented as SSH-direct (mcp__k2__file_read doesn't exist — SSH is equivalent)
- PITFALL P056: allowedTools ["*"] wildcard incomplete — some tools still prompt approval
- PROOF: 159 JSONL files extracted, 2151 observations staged (harvest_jsonl_output.json)
- DECISION: resurrect Step 1 now SSH-direct cc-session-brief.md fetch (PS script = fallback only)
- PITFALL: Windows Python cp1252 default encoding — always use encoding='utf-8' for JSONL/JSON file ops
