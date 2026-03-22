# CC Context Snapshot
Generated: 2026-03-22 (Session 122 wrap)

## Identity
CC (Ascendant) — responding via P0N-A bridge (hub.arknexus.net/cc → P1:7891 → Ollama localhost:11434).
Inference backend: llama3.1:8b (local Ollama). Anthropic-independent. No MCP startup overhead.

## Hierarchy
SOVEREIGN: Colby (final authority) | ASCENDANT: CC | ARCHONPRIME: Codex | ARCHON: KCC | INITIATE: Karma

## Verified System State (2026-03-22)
- anr-hub-bridge: Up 3+ hours
- karma-server: Up 26+ hours (healthy)
- anr-vault-search, anr-vault-db, anr-vault-api, falkordb: all Up
- E-1-A COMPLETE: Scripts/corpus_builder.py (146 lines), 2817 Alpaca pairs in Logs/corpus_alpaca.jsonl
- vault-neo synced to commit 8c6e93a (feat(e1a): corpus builder)

## Key Architecture Decisions (LOCKED)
cc_server /cc uses LOCAL OLLAMA — NOT claude CLI, NOT Anthropic API. Do not revert without Sovereign approval.
corpus_builder.py --limit caps OUTPUT PAIRS, not raw entries fetched.
Windows file reads on corpus output require explicit encoding='utf-8'.

## Active Work / Next
Completed: E-1-A (corpus builder, 2817 Alpaca pairs from vault ledger).
Next: E-2-A Step 1 — verify K2 WSL prerequisites (nvidia-smi, python3, curl) before Unsloth Studio install.
GSD docs pre-created: .gsd/phase-e2a-CONTEXT.md + .gsd/phase-e2a-PLAN.md

## Current Blockers
None.

## Key Paths
- PLAN: Karma2/PLAN.md | STATE: .gsd/STATE.md | MEMORY: MEMORY.md
- CC server: Scripts/cc_server_p1.py + Scripts/Start-CCServer.ps1
- Corpus: Scripts/corpus_builder.py -> Logs/corpus_alpaca.jsonl (2817 pairs)

## Cognitive Trail
- PROOF #9814: E-1-A complete — corpus_builder.py 2817 Alpaca pairs from 3191 raw hub+chat entries
- PITFALL #9818: --limit must cap output pairs not raw entries (original capped raw, produced fewer than N)
- PITFALL #9819: Windows open() needs explicit encoding='utf-8' for non-ASCII content
- DRIFT resolved: MEMORY.md said K-3 next; bus Session 121 wrap said E-1-A; GSD plan existed — E-1-A was correct
