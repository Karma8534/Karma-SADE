# Design: Watermark-Based Graphiti Entity Extraction
**Date:** 2026-03-04
**Status:** Approved
**Author:** Claude Code + Colby

---

## Problem

3049 bulk-ingested episodes exist as Episodic nodes only — no Entity or relationship nodes.
`--skip-dedup` bypasses Graphiti entirely, so no entity extraction has occurred since Session 59.
Karma can recall past episodes (via FAISS) but cannot reason across sessions (no structured knowledge graph).

## Goal

Re-enable Graphiti entity extraction for all new episodes going forward (forward-only).
Historical episodes remain Episodic-only. Knowledge graph grows from today onward.

## Approach: Watermark File

### Data Flow

```
Ledger (memory.jsonl)
  ├── Lines 0 → watermark:  SKIP (already processed)
  └── Lines watermark → end: Graphiti mode → Episodic + Entity + RELATES_TO → FalkorDB
                                                     ↓
                                           Watermark advances
```

### Watermark File
- **Location:** `/opt/seed-vault/memory_v1/ledger/.batch_watermark` (host-side, persisted)
- **Format:** single integer — last processed line number in memory.jsonl
- **Init:** first run with no watermark → sets to current line count → skips all 3049 historical
- **Advance:** only on successful Graphiti processing; failures leave watermark in place for retry

### batch_ingest.py Changes
1. **Watermark read/init at startup** — `WATERMARK_PATH` env var (default: `/ledger/.batch_watermark`)
2. **Safety cap: 200 episodes max per run** — Graphiti timeouts start ~250; cap gives headroom for medium volume; excess picked up next cron window
3. **Per-episode watermark advance** — watermark moves forward one line per successful episode; stops at first failure
4. `--skip-dedup` flag preserved for manual bulk ops

### Cron Change
Drop `--skip-dedup` from cron command. Graphiti mode becomes the default.

### Deployment
1. Edit `batch_ingest.py` on P1 → git commit → push
2. `ssh vault-neo`: git pull → cp to karma-core build context → docker rebuild
3. Initialize watermark before restart: `wc -l /ledger/memory.jsonl > /opt/seed-vault/memory_v1/ledger/.batch_watermark`
4. Confirm ledger volume is mounted into karma-server container (check compose file)
5. Update cron: drop `--skip-dedup`
6. Run batch manually, verify Entity node count increases in FalkorDB

## Constraints
- No retroactive extraction on 3049 historical episodes
- `--skip-dedup` retained as manual flag for bulk ops
- Watermark file must survive container rebuilds (host volume mount required)
- 200 episode cap is hard — not configurable at runtime (avoid accidental override)

## Out of Scope
- Caching optimization (separate task, shelved)
- Retroactive entity extraction
- Changes to FAISS indexing
