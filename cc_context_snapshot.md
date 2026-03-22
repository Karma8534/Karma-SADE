# CC Context Snapshot
Generated: 2026-03-22 (Session 119 wrap)

## Identity
CC (Ascendant) — responding via P0N-A bridge (hub.arknexus.net/cc -> P1:7891 -> Ollama localhost:11434).
Inference backend: llama3.1:8b (local Ollama). Anthropic-independent. No MCP startup overhead.

## Hierarchy
SOVEREIGN: Colby (final authority) | ASCENDANT: CC | ARCHONPRIME: Codex | ARCHON: KCC | INITIATE: Karma

## Verified System State (2026-03-22)
- hub-bridge: UP (rebuilt Session 118, /v1/ambient route added)
- karma-server: UP healthy (23h+)
- vault services (db/api/caddy/search): UP healthy
- K2 SSH tunnel: REACHABLE (verified this session)
- Ambient capture hooks: NOW FUNCTIONAL (session-end + git post-commit -> /v1/ambient)

## Key Architecture Decisions (LOCKED)
- cc_server /cc uses LOCAL OLLAMA - NOT claude CLI, NOT Anthropic API. Do not revert without Sovereign approval.
- /v1/ambient route: HUB_CAPTURE_TOKEN auth, buildVaultRecord() normalization, vaultPost(/v1/memory)

## Active Work / Next
Completed Session 118-119: /v1/ambient fix + resurrect hardening (B001+P043) + wrap-session 5 fixes.
Next: K-3 per PLAN.md (PHASE KNOWLEDGE - next corpus scrape/ingest task).

## Current Blockers
None critical.

## Key Paths
- PLAN: Karma2/PLAN.md | STATE: .gsd/STATE.md | MEMORY: MEMORY.md
- CC server: Scripts/cc_server_p1.py + Scripts/Start-CCServer.ps1

## Cognitive Trail
- PITFALL P043: cc-session-brief K2 status = Aria HTTP probe only, independent of SSH tunnel. Always attempt SSH directly.
- BLOCKER B001: resurrect Step 5 was prose not contract. Fixed: tool calls required in same response as announcement.
- PROOF: /v1/ambient route added to hub-bridge (commit ce2dff8). Ambient capture hooks now functional.
- PROOF: resurrect skill hardened - B001 execution contract + P043 SSH guard deployed.
- PROOF: wrap-session 5 fixes deployed - cc_scratchpad.md write, D003 git, bus post, /resurrect enforced, hash verify.
