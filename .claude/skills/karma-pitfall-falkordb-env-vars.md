---
name: karma-pitfall-falkordb-env-vars
description: Use before any FalkorDB container creation or recreation. Both env vars are fatal if missing — container runs but data never persists or queries time out.
type: feedback
---

## Rule

FalkorDB container MUST have BOTH env vars. Missing either causes silent failure:

```bash
-e FALKORDB_DATA_PATH=/data
-e FALKORDB_ARGS='TIMEOUT 10000 MAX_QUEUED_QUERIES 100'
```

**Why:**
1. `FALKORDB_DATA_PATH=/data` — Without this, FalkorDB writes to internal path not on mounted volume. RDB never lands on host. Every container restart = empty graph. Verified 2026-02-22.
2. `TIMEOUT 10000` — Default is 1000ms. Past ~250 episodes, Graphiti dedup queries exceed 1s → cascade batch failure. `TIMEOUT 0` means "use default" NOT unlimited. Learned after 72% batch failure rate.
3. `MAX_QUEUED_QUERIES 100` — batch_ingest (concurrency=3) + live karma-server traffic can exceed 25 → "Max pending queries exceeded" errors. Verified with 40% error rate at 25, clean at 100.

**How to apply:**
Verify running container: `docker inspect falkordb | grep -E 'FALKORDB_DATA_PATH|FALKORDB_ARGS'`
Graph name is `neo_workspace` NOT `karma` (karma graph exists but is empty).

## Evidence

- Batch3 (2026-02-22): 72% failure rate — `TIMEOUT 0` caused same cascade as default 1000ms
- Batch4 (2026-02-23): 40% error rate — `MAX_QUEUED_QUERIES 25` saturated under live traffic
- Decision in CLAUDE.md Known Pitfalls (verified 2026-02-22+23)
