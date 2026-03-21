---
name: karma-pitfall-batch-ingest-skip-dedup
description: Use before ANY batch_ingest.py execution or cron setup. --skip-dedup is mandatory for ALL runs, not just bulk backfill. Without it, watermark advances but 0 nodes are created.
type: feedback
---

## Rule

`batch_ingest.py` MUST always use `--skip-dedup`. This applies to the cron job AND manual runs. `--skip-dedup` is not a bulk-backfill-only flag.

**Why:** Session 70: Graphiti dedup mode silently fails at scale (3200+ Episodic nodes). Watermark advances ("All caught up" logged), 0 FalkorDB nodes created, no error. Discovered only by querying FalkorDB directly and finding node count unchanged. --skip-dedup uses direct Cypher write: 899 eps/s, 0 errors.

**How to apply:**
```bash
# CORRECT cron command (verify with: crontab -l | grep batch):
LEDGER_PATH=/ledger/memory.jsonl WATERMARK_PATH=/ledger/.batch_watermark python3 /app/batch_ingest.py --skip-dedup

# Reset watermark if needed:
docker exec karma-server sh -c 'echo N > /ledger/.batch_watermark'
```

Also:
- `LEDGER_PATH` inside container = `/ledger/memory.jsonl` (NOT `/opt/seed-vault/...`)
- Graphiti embedder requires `OPENAI_API_KEY` env var — set with `os.environ.setdefault()` in script
- FalkorDB has NO `datetime()` Cypher function — use plain ISO string properties

## Evidence

- Session 70: Watermark advanced, 0 nodes created. Root cause: Graphiti dedup queries timeout at scale.
- Session 70: `--skip-dedup` = 899 eps/s, 0 errors on same dataset.
- CLAUDE.md Known Pitfalls section
