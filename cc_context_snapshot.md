# CC Context Snapshot
Generated: 2026-03-23T21:30Z (Session 134 — resurrect repair)

## Identity
CC (Ascendant) — responding via P0N-A bridge (hub.arknexus.net/cc -> P1:7891 -> Ollama localhost:11434).
Inference backend: llama3.1:8b (local Ollama). Anthropic-independent. No MCP startup overhead.

## Hierarchy
SOVEREIGN: Colby (final authority) | ASCENDANT: CC | KO: Codex | KFH: KCC | INITIATE: Karma
NOTE: 'ArchonPrime: Codex' and 'Archon: KCC' are STALE DOCTRINE — removed in Meta session F4. Use KO/KFH.

## Verified System State (2026-03-23)
P0N-A: LIVE (hub.arknexus.net/cc working)
Containers: healthy (last verified Session 133)
cc-regent.service: active on K2

## Key Architecture Decisions (LOCKED)
cc_server /cc uses LOCAL OLLAMA — NOT claude CLI, NOT Anthropic API. Do not revert without Sovereign approval.
KCC is on K2 (karma@192.168.0.226) — NOT on P1.

## Active Work / Next
Session 134 fixed 5 resurrect root causes. Next: Plan-A Task 1 (JSONL backfill).
PLAN.md line 81: Start with PLAN-A. Nothing else until A3 is done.

## Current Blockers
None active. PROOF-A Tasks 2+3 written by broken session — verify correctness before accepting.

## Key Paths
- PLAN: Karma2/PLAN.md | STATE: .gsd/STATE.md | MEMORY: MEMORY.md
- CC server: Scripts/cc_server_p1.py + Scripts/Start-CCServer.ps1

## Cognitive Trail
- PITFALL #10861: resurrect doubled — karma-tools plugin duplicate skill (disabled)
- PITFALL #10865: wrap template had stale ARCHONPRIME/ARCHON doctrine (fixed to KO/KFH)
- DECISION #10870: permissions wildcard Bash(*)+mcp__* in user settings.json
- DECISION #10875: /review skill created — state surface without execution
- DIRECTION #10479: FakeChat localhost channel feed into hub (backlog-8)
