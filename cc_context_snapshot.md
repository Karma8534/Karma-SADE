# CC Context Snapshot
Generated: 2026-03-23 (Session 130)

## Identity
CC (Ascendant) — responding via P0N-A bridge (hub.arknexus.net/cc -> P1:7891 -> Ollama localhost:11434).
Inference backend: llama3.1:8b (local Ollama). Anthropic-independent. No MCP startup overhead.

## Hierarchy
SOVEREIGN: Colby (final authority) | ASCENDANT: CC | ARCHONPRIME: Codex | ARCHON: KCC | INITIATE: Karma

## Verified System State (2026-03-23)
- hub-bridge: Up (anr-hub-bridge, claude-haiku-4-5-20251001 default)
- karma-server: Up (anr-karma-server)
- anr-vault-search: Up HEALTHY - 2551 FAISS vectors (FIXED Session 130: 3 bugs resolved)
- anr-vault-api: Up HEALTHY
- falkordb: Up
- Ledger: 200,866+ entries
- FAISS index: 2551 vectors (now includes 124 anthropic-docs entries)

## Key Architecture Decisions (LOCKED)
cc_server /cc uses LOCAL OLLAMA - NOT claude CLI, NOT Anthropic API. Do not revert without Sovereign approval.

## Active Work / Next
COMPLETED Session 130: K-2 Anthropic Docs Scrape
- 170 .md files scraped from platform.claude.com (128) + code.claude.com (30)
- All files in docs/anthropic-docs/{agent-sdk,api,agents-and-tools,build-with-claude,test-and-evaluate,about-claude,claude-code}/
- 124 ledger entries tagged anthropic-docs, knowledge, k2-scrape
- FAISS search verified: hooks.md at 0.487, mcp-connector.md at 0.556
- Scripts/batch-ingest-docs.ps1 created for future re-ingestion

NEXT: Check PLAN.md for K-3 or next phase. Likely K-3 ambient pipeline quality fixes.

## Current Blockers
None blocking K-2. K-3 not yet started.

## Key Paths
- PLAN: Karma2/PLAN.md | STATE: .gsd/STATE.md | MEMORY: MEMORY.md
- CC server: Scripts/cc_server_p1.py + Scripts/Start-CCServer.ps1
- Docs: docs/anthropic-docs/ (170 files, FAISS indexed)

## Cognitive Trail
- PROOF: K-2 complete - 170 docs scraped, 124 ledger entries, 2551 FAISS vectors (#10209)
- PITFALL P056: vault-search null-ID entries deduplicate to 1 slot - fixed with line_N synthetic IDs (#10210)
- PITFALL P057: value-keyed content not indexed, coordination tag filter required (#10212)
- DECISION: WebFetch + 6 parallel agents covers 170 pages in 15min; Playwright not needed for static docs (#10232)
