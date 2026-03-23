# CC Context Snapshot
Generated: 2026-03-23 (Session 128)

## Identity
CC (Ascendant) -- responding via P0N-A bridge (hub.arknexus.net/cc -> P1:7891 -> Ollama localhost:11434).
Inference backend: llama3.1:8b (local Ollama). Anthropic-independent. No MCP startup overhead.

## Hierarchy
SOVEREIGN: Colby (final authority) | ASCENDANT: CC | ARCHONPRIME: Codex | ARCHON: KCC | INITIATE: Karma

## Verified System State (2026-03-23)
- aria.service: RUNNING PID 423990 (fixed Session 127 -- zombie+drop-in fix)
- karma-regent.service: RUNNING PID 243460 (systemd-managed, confirmed Session 127)
- anr-hub-bridge: Up 18 minutes (rebuilt Session 127 -- /v1/cypher LIVE)
- karma-server: Up 42h HEALTHY
- All vault containers: HEALTHY

## Key Architecture Decisions (LOCKED)
cc_server /cc uses LOCAL OLLAMA -- NOT claude CLI, NOT Anthropic API. Do not revert without Sovereign approval.
resurrect CASE C: C-DIRECTIVE (action verb -> write GSD plan + execute Task 1, never brainstorm) | C-AMBIGUOUS (rare, only case for brainstorming)

## Active Work / Next
Session 128: resurrect+wrap-session hardening complete. CASE C trap root-caused and fixed.
Next: K-1 IndexedDB extraction -- .gsd/phase-k1-PLAN.md pre-created (5 tasks).
Task 1: Navigate to claude.ai via Claude-in-Chrome MCP to verify browser connection.

## Current Blockers
- K-1: NOT STARTED (real IndexedDB 108+ sessions). Claude-in-Chrome MCP must be available.
- E-1-A: corpus_cc.jsonl pending (tabled with PHASE EVOLVE)
- P0-G: callWithK2Fallback() dead code (K2_INFERENCE_ENABLED missing from hub.env)
- PROOF-A: Codex automated ArchonPrime (GSD docs created, Task 1 pending)
- B2: K-3 mechanism broken (aria ran once, now fixed -- needs re-verification)

## Key Paths
- PLAN: Karma2/PLAN.md | STATE: .gsd/STATE.md | MEMORY: MEMORY.md
- CC server: Scripts/cc_server_p1.py + Scripts/Start-CCServer.ps1

## Cognitive Trail
- PITFALL P054: resurrect CASE C triggers brainstorming when item 2 is a directive with no GSD plan (obs #10097)
- DECISION: CASE C split into C-DIRECTIVE (write GSD+execute) and C-AMBIGUOUS (only case for brainstorming) (obs #10102)
- PROOF: cc_email_daemon _read_state_blockers() TDD verified: 5 OPEN / 14 FIXED / 1 FALSE POSITIVE from STATE.md (obs #10098)
- B003: vague MEMORY.md item 2 (X OR Y) is protocol violation -- causes CASE C at next resurrect
- .gsd/phase-k1-PLAN.md pre-created to guarantee CASE A at next session start
