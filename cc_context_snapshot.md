# CC Context Snapshot
Generated: 2026-03-23 (Meta Session 135)

## Identity
CC (Ascendant) — responding via P0N-A bridge (hub.arknexus.net/cc → P1:7891 → Ollama localhost:11434).
Inference backend: llama3.1:8b (local Ollama). Anthropic-independent. No MCP startup overhead.

## Hierarchy
SOVEREIGN: Colby (final authority) | ASCENDANT: CC | KO: Codex | KFH: KCC | INITIATE: Karma
NOTE: "ArchonPrime: Codex" and "Archon: KCC" are STALE DOCTRINE — removed in Meta session F4. Use KO/KFH.

## Verified System State (2026-03-23)
- P0N-A bridge: status unknown this session (meta session, not checked)
- wip-watcher: restarted after field name fix (content→file_b64)
- resurrect skill: stale plugin cache copy deleted — single canonical copy at ~/.claude/skills/resurrect/SKILL.md

## Key Architecture Decisions (LOCKED)
- cc_server /cc uses LOCAL OLLAMA — NOT claude CLI, NOT Anthropic API. Do not revert without Sovereign approval.
- KCC is on K2 (karma@192.168.0.226) — NOT on P1. P1 is CC's machine (C:\Users\raest).
- Plugin cache files load regardless of plugin enabled/disabled flag — keep plugin cache clean.

## Active Work / Next
Meta session complete. Next: fresh /resurrect → Plan-A Task 1 (JSONL survey + backfill harvest).

## Current Blockers
None. All 4 root causes fixed and pushed.

## Key Paths
- PLAN: Karma2/PLAN.md | STATE: .gsd/STATE.md | MEMORY: MEMORY.md
- CC server: Scripts/cc_server_p1.py + Scripts/Start-CCServer.ps1
- Plan-A GSD: .gsd/phase-plan-a-brain-PLAN.md

## Cognitive Trail
- PITFALL: wip-watcher sent "content" field, /v1/ingest requires "file_b64" — obs #11386
- PITFALL: disabled plugin cache still loads skill files — resurrect doubled — obs #11387
- PROOF: 4 fixes committed d5ff020, pushed to main — obs #11388
