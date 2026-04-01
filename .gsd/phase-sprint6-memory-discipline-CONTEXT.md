# Sprint 6: Memory Operating Discipline — CONTEXT

## What we're building
Seven memory pipeline upgrades (tasks 7-5 through 7-11) from nexus.md Phase 7B.
These transform Karma's memory from flat append-only logs into managed, tiered, compressed memory objects.

## Current state
- **Ledger:** JSONL at `/opt/seed-vault/memory_v1/ledger/memory.jsonl` (209K+ entries)
- **Schema:** `{type, content, tags, source, confidence, verification, created_at, id, updated_at}`
- **Retrieval:** FAISS (anr-vault-search) returns raw text. FalkorDB has 4789+ nodes.
- **Cortex:** julian_cortex.py holds 97 knowledge blocks, 24K char limit, returns raw blocks via /context
- **Vesper:** watchdog extracts candidates → eval scores → governor promotes to spine + FalkorDB

## Design decisions (locked)
1. Ledger is append-only — new fields added to new entries, old entries unchanged
2. All changes target K2 cortex path — CC --resume manages its own context natively
3. No new external dependencies — use existing Ollama, FAISS, FalkorDB
4. Backward compatible — retrieval must handle both old and new schema entries
5. MemCube fields are OPTIONAL on writes, DEFAULTED on reads (old entries get defaults)

## What we're NOT doing
- No PostgreSQL migration (we keep JSONL + FalkorDB + FAISS)
- No embedding-space projection (requires model training)
- No KV-cache compression (requires model-level changes)
- No end-to-end RL optimization
- No parameter editing / continual fine-tuning
