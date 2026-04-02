# Sprint 6: Memory Operating Discipline — Design Context

## What We're Building
Upgrade Karma's memory pipeline from flat log injection to intelligent, gated, compressed recall.

## Current State (verified 2026-04-02)
- Ledger: 225,537 entries. 479 have memcube metadata (all tier=raw). 225,058 lack memcube.
- MemCube schema v1 deployed: version, tier, lineage, promotion_state, decay_policy
- Cortex: K2:7892, qwen3.5:4b, 32K ctx, 144 knowledge blocks
- FAISS: 193K+ entries indexed, auto-reindex
- FalkorDB: 4789+ nodes (neo_workspace graph)
- Vesper pipeline: 1284+ promotions, 20 stable patterns

## Design Decisions
1. **Backfill memcube**: NOT needed for 225K historical entries. Forward-only — new entries get memcube. Historical entries get memcube lazily during recall (if selected, upgrade then).
2. **Tier classification**: Run on K2 cortex as a batch job using keyword heuristics (not LLM — too expensive). Tiers: raw (default), distilled (has extracted fact), stable (Vesper-promoted), archived (>90 days, low access).
3. **Gated recall**: Implemented in julian_cortex.py /query endpoint. Score each candidate against query. Drop below threshold. Top-K only.
4. **Compression**: Implemented in julian_cortex.py. After gate, compress selected blocks into fact bundle before injecting into LLM context.
5. **Local-window priority**: Cortex already does this (conversation messages first, then knowledge blocks). Formalize ordering.
6. **Migration/fusion**: Vesper governor already promotes patterns. Add tier upgrade rules.

## What We're NOT Doing
- Backfilling 225K historical entries with memcube
- LLM-based tier classification (too expensive)
- Modifying vault-api schema (memcube already present)
- Building a new database (FAISS + FalkorDB stay)
