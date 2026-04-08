# Nexus 5.6.0 Build Context
**Date:** 2026-04-07 | **Session:** S162

## What We're Building
MemPalace-enhanced memory architecture for Karma Nexus. 7 HIGH-priority primitives extracted from MemPalace v3.0.0 (obs #25022), adopted into Phases 1 and 3 of the Nexus plan.

## Design Decisions
1. **4-Layer Stack is a RENAME, not new code.** buildSystemText() already has identityBlock, memoryMdCache, karmaCtx, semanticCtx. We name them L0-L3.
2. **Hooks are direct ports** from MemPalace shell scripts. Minimal adaptation.
3. **General extractor is pure regex** — no LLM dependency. Port marker sets from MemPalace.
4. **AAAK dialect** is a new Python module — no existing equivalent.
5. **Agent diaries** use claude-mem with project namespacing — no new infrastructure.
6. **Temporal KG** adds properties to FalkorDB Entity nodes — schema extension, not replacement.
7. **Duplicate detection** queries anr-vault-search before ledger append — new middleware.

## What We're NOT Doing
- NOT replacing ChromaDB with anything (MemPalace uses ChromaDB; we use FAISS — keep FAISS)
- NOT building a full MCP server (MemPalace has one; we already have hub-bridge tools)
- NOT implementing onboarding wizard (MemPalace has one; Karma has resurrect)
- NOT changing the palace_graph BFS traversal (we have FalkorDB for this)

## Constraints
- hub-bridge is JS (server.js). No Python in hub-bridge.
- karma-server is Python. Schema changes go here.
- Scripts/ for standalone Python tools.
- Hooks are bash scripts in .claude/hooks/.
- NEVER edit on vault-neo. Edit locally → push → pull → rebuild.

## Phase 0 Status: ALREADY BUILT (S160)
Verified in ground truth: gap_map.py, vesper_eval hard gate, vesper_governor smoke gate, karma_persistent gap_closure — all exist at Scripts/ with correct features.
