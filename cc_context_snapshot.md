# CC Context Snapshot
Generated: 2026-03-22 (Session 126 wrap)

## Identity
CC (Ascendant) - responding via P0N-A bridge (hub.arknexus.net/cc -> P1:7891 -> Ollama localhost:11434).
Inference backend: llama3.1:8b (local Ollama). Anthropic-independent. No MCP startup overhead.

## Hierarchy
SOVEREIGN: Colby (final authority) | ASCENDANT: CC | ARCHONPRIME: Codex | ARCHON: KCC | INITIATE: Karma

## Verified System State (2026-03-22)
P0N-A: LIVE - hub.arknexus.net/cc working, CC Ascendant responds
P0N-B: LIVE - resurrect script + cc-session-brief.md
P0N-C: LIVE - compaction-cliff-guard (new Session 126)
P0N-D: LIVE - locked-invariant-guard (5 patterns, enhanced Session 126)
3-Layer Harness: COMPLETE (Session 126)
  - Layer 1: compaction-cliff-guard.py (UserPromptSubmit re-injection every turn)
  - Layer 2: hooks.yaml (10 rules, RuleZ-compatible), quality-gate Windows fix, locked-invariant-guard 5 patterns
  - Layer 3: post-tool-failure-logger.py (PostToolUseFailure auto-capture to Logs/)
aria.service: CRASH LOOP (K2 - Blocker 14, restart 2015+)
/v1/cypher: BROKEN (returns not_found - new gap found Session 126)
karma-regent: RUNNING as nohup (not systemd - reboot risk)
Ledger: 200,445 entries LIVE (STATE.md says 6,571 - 30x drift)

## Key Architecture Decisions (LOCKED)
cc_server /cc uses LOCAL OLLAMA - NOT claude CLI, NOT Anthropic API. Do not revert without Sovereign approval.
3-Layer Harness is the OS. Model is the CPU. Harness gates before generation (Layer 2), re-injects context every turn (Layer 1), captures all failures (Layer 3).
/v1/cypher broken - do not assume FalkorDB graph queries work until fixed.

## Active Work / Next
COMPLETED Session 126:
- 3-Layer Harness fully implemented (all 4 hooks, hooks.yaml, settings.json updated)
- 14/14 TDD PASS
- Karma2 live audit complete (4 blockers found)
- Email report delivered to Sovereign

NEXT SESSION PRIORITY ORDER:
1. aria.service crash loop - SSH K2, run python3 aria.py directly for traceback, fix
2. /v1/cypher broken - check server.js route definition, verify FalkorDB container
3. Register karma-regent as systemd user unit
4. Update STATE.md ledger count to 200,445

## Current Blockers
BLOCKER 1 (P0): aria.service crash loop on K2 - ambient pipeline dead
BLOCKER 2 (P0): /v1/cypher returns not_found - FalkorDB graph queries broken from Karma
BLOCKER 3 (P1): karma-regent running as nohup only - dies on K2 reboot
BLOCKER 4 (P2): STATE.md ledger count 30x understated (6,571 vs actual 200,445)

## Key Paths
- PLAN: Karma2/PLAN.md | STATE: .gsd/STATE.md | MEMORY: MEMORY.md
- CC server: Scripts/cc_server_p1.py + Scripts/Start-CCServer.ps1
- GSD aria crash: .gsd/phase-aria-crash-PLAN.md

## Cognitive Trail
- PROOF: 3-Layer Harness 14/14 TDD - all hooks verified working on Windows
- PITFALL: quality-gate grep subprocess broken on Windows (exit 9009) - fixed with Python re scanner
- PITFALL: bash apostrophe quoting breaks py -c inline Python - write body to temp file first
- DECISION: locked-invariant-guard extended 2->5 patterns (banked-approvals.json + governance_boundary)
- DISCOVERY: /v1/cypher broken (not_found) - new critical gap, not in STATE.md
- DISCOVERY: ledger 200,445 actual vs 6,571 in STATE.md - 30x drift
