# CC Context Snapshot
Generated: 2026-03-25 (Session ~140 wrap)

## Identity
CC (Ascendant) — responding via P0N-A bridge (hub.arknexus.net/cc → P1:7891 → Ollama localhost:11434).
Inference backend: llama3.1:8b (local Ollama). Anthropic-independent. No MCP startup overhead.

## Hierarchy
SOVEREIGN: Colby (final authority) | ASCENDANT: CC | KO: Codex | KFH: KCC | INITIATE: Karma
NOTE: "ArchonPrime: Codex" and "Archon: KCC" are STALE DOCTRINE — removed in Meta session F4. Use KO/KFH.

## Verified System State (2026-03-25)
- Plan-A: DONE (Session 136) — JSONL backfill 2151 obs, auto-indexer registered, resurrect SSH direct
- Plan-B: DONE (Session 137) — Julian real, cc --resume, /cc route, reboot survival
- Plan-C: CLAIMED DONE (Session 138) — UNVERIFIED. C1-C4 all say "NOT STARTED" in plan file but C-GATE checked. Needs live check.
- P0 Sprint (Backlog-3): DONE — A/B/C/D/E complete, F partial (design done, Phase 1 approval pending), G hardware-blocked
- STATE.md: stale (Session 137, not updated for Plan-C)
- PLAN-backlog.md: not updated for P0 sprint or A+B+C gate pass

## Key Architecture Decisions (LOCKED)
cc_server /cc uses LOCAL OLLAMA — NOT claude CLI, NOT Anthropic API. Do not revert without Sovereign approval.
KCC is on K2 (NOT P1). Resurrect scripts assuming P1 path for KCC are wrong.

## Active Work / Next
Next session must:
1. Live check: SSH vault-neo, grep hub-bridge server.js for /memory endpoint
2. Fix settings.local.json (allowedTools: ["*"]) — user confirmed, never applied
3. Fix wip-watcher.ps1 (base64 encoding, file_b64 error blocking 11 files)
4. Rewrite resurrect skill (double-execution, KCC location bug, auto-start without confirmation)
5. Create /review skill (read-only status snapshot)

## Current Blockers
- Plan-C completion unverified — live check required first
- P0-F Phase 1: TITANS surprise gate awaiting Sovereign approval
- Backlog-4 (Karma tools 1-A/B/C) — Sovereign approval required
- Backlog-9 (karma-observer.py) — Sovereign approval required
- Resurrect: double-exec bug, KCC location wrong, auto-starts tasks
- wip-watcher.ps1: file_b64 required error on all files

## Key Paths
- PLAN: Karma2/PLAN.md | STATE: .gsd/STATE.md | MEMORY: MEMORY.md
- CC server: Scripts/cc_server_p1.py + Scripts/Start-CCServer.ps1

## Cognitive Trail
- PITFALL #11724: PLAN-C-wire.md C1-C4 "NOT STARTED" but gate checked — cannot trust completion
- PITFALL #11725: A3 (resurrect data source fixed) != resurrect behavior bugs (still open)
- PITFALL #11726: STATE.md + PLAN-backlog.md stale — root cause of "running in circles" feeling
- DIRECTION #11727: 4 pre-compaction items open, zero blockers, ready next session
