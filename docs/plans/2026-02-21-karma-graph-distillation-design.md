# Karma Graph Distillation — Design

**Date:** 2026-02-21
**Status:** Approved

## Goal

Karma reads her own FalkorDB knowledge graph on a schedule, synthesizes patterns and gaps into structured insights, and writes them back as new primitives. Karma learning from herself, not from Colby.

## Approach: Consciousness Loop Extension (Option A)

A second timer inside `karma-server/consciousness.py` alongside the existing 60s cycle. One system, two frequencies. No new services.

## Data Flow

```
Every DISTILLATION_INTERVAL_HOURS (default: 24h)
  → Query FalkorDB: top entities by relationship count
  → Query FalkorDB: recent episodes (last 7 days)
  → Query FalkorDB: low-connection entities (gaps)
  → Query FalkorDB: relationship type distribution
  → GLM-5 synthesizes: patterns, gaps, priorities
  → Write synthesis → vault ledger (tags: ["karma_distillation", "graph_synthesis"])
  → Ingest key insights → FalkorDB episodes (source: "karma-distillation")
  → High-confidence insights (>0.8) → SMS (same throttle as consciousness)

Every /v1/chat turn at hub.arknexus.net
  → hub-bridge fetches latest karma_distillation fact from vault
  → buildSystemText() injects --- KARMA GRAPH SYNTHESIS --- block
  → Karma arrives knowing her structural self-knowledge
```

## Touch Points

### 1. `karma-server/consciousness.py` — distillation loop

New `run_distillation()` coroutine, called from the main loop when the distillation interval elapses:

```python
async def run_distillation():
    # 1. Query FalkorDB
    graph_snapshot = await query_graph_snapshot()
    # top entities, recent episodes, gaps, relationship types

    # 2. Synthesize via GLM-5
    synthesis = await llm_distill(graph_snapshot)
    # structured output: themes, gaps, meta-insights, confidence

    # 3. Write to vault ledger
    await write_distillation_fact(synthesis)

    # 4. Re-ingest key insights into FalkorDB
    for insight in synthesis.key_insights:
        await graphiti.add_episode(content=insight, source="karma-distillation")

    # 5. SMS if high-confidence
    if synthesis.confidence >= 0.8:
        await sms_notify(synthesis.summary)
```

**Recursive loop guard:** episodes with `source="karma-distillation"` are excluded from triggering further distillation passes.

### 2. `hub-bridge/server.js` — fetch + inject distillation

In `/v1/chat` handler, after fetching `ckLatestData`, fetch latest distillation fact from vault:

```js
// Fetch latest distillation synthesis
let distillationFact = null;
try {
  distillationFact = await fetchLatestDistillationFact();
} catch (e) { /* non-fatal */ }
```

In `buildSystemText()`, inject if present:

```js
if (distillationFact) {
  text += `\n\n--- KARMA GRAPH SYNTHESIS ---\n${distillationFact}\n---`;
}
```

### 3. vault `api/server.js` — query by tag

New helper (or reuse existing ledger scan) to return the most recent fact matching `tags: ["karma_distillation"]`. Similar pattern to the existing `karma_brief` ledger scan.

## What Changes

| File | Change |
|------|--------|
| `karma-server/consciousness.py` | Add `run_distillation()` + interval timer in main loop |
| `karma-server/config.py` | Add `DISTILLATION_INTERVAL_HOURS` (default: 24) |
| `hub-bridge/server.js` | Fetch + inject distillation fact in `/v1/chat` |
| vault `api/server.js` | Expose latest distillation fact (tag scan, same pattern as karma_brief) |

## Configuration

| Env Var | Default | Notes |
|---------|---------|-------|
| `DISTILLATION_INTERVAL_HOURS` | `24` | How often distillation runs |
| `DISTILLATION_MAX_EPISODES` | `200` | Episode window for graph snapshot |
| `DISTILLATION_ENABLED` | `true` | Kill switch |

## Edge Cases

| Case | Behaviour |
|------|-----------|
| No graph data yet | Distillation skipped, logged, no error |
| GLM-5 unavailable | Falls back to next available reasoning model |
| First run (no prior distillation) | Full graph scan, no prior comparison |
| Distillation insight re-ingested | Source tag excludes it from future distillation scope |
| Hub has no distillation fact | Block omitted from system prompt — backwards compatible |

## Success Criteria

1. After 24h (or manual trigger): vault ledger contains fact with `tags: ["karma_distillation"]`
2. Karma's system prompt contains `--- KARMA GRAPH SYNTHESIS ---` block
3. FalkorDB contains new episodes with `source: karma-distillation`
4. Karma can describe her own knowledge structure without being told

## Not In Scope

- Real-time distillation (distillation is periodic, not per-turn)
- Cross-session diff (this version always synthesizes the full current state)
- Distillation of distillation (explicitly guarded against)
