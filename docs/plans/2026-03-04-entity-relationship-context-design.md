# Entity Relationship Context Design

**Date:** 2026-03-04
**Session:** 64 (Gap 1 — Cross-session reasoning)
**Status:** Approved

---

## Problem

Karma's entity graph (FalkorDB `neo_workspace`) contains Entity nodes and RELATES_TO edges, but
these relationships are never surfaced in `/v1/chat` responses. karmaCtx includes Entity nodes
in "Relevant Knowledge" but omits the edges between them. Pattern detection (recurring topics
across sessions) is also absent. Result: Karma cannot reason across sessions about connected facts.

---

## Decision

**Approach C: `/raw-context` for edges (per-message) + cached patterns (30min refresh)**

- RELATES_TO edges: queried per `/v1/chat` call — contextual, changes with conversation
- Pattern data: cached in karma-server memory, refreshed every 30min — changes at cron pace
- No hub-bridge changes needed
- Wire now, value accrues as Graphiti watermark builds entity graph over time

---

## Architecture

```
Current:
/v1/chat → Promise.all([fetchKarmaContext, fetchSemanticContext])
         → buildSystemText(karmaCtx, ...)
         karmaCtx: Recent episodes + Relevant Knowledge (Entity nodes)

After:
karmaCtx: [existing] + two new sections:
  § Entity Relationships  — RELATES_TO edges between relevant entities (per-message)
  § Recurring Topics      — top-10 entities by episode count (cached, 30min refresh)
```

hub-bridge: **zero changes**. `buildSystemText()` receives richer karmaCtx and includes it as-is.

---

## Cypher Queries

**Edge query** (per `/raw-context` call):
```cypher
MATCH (e1:Entity)-[r:RELATES_TO]->(e2:Entity)
WHERE e1.name IN $entityNames
RETURN e1.name AS from, r.fact AS relationship, e2.name AS to
LIMIT 20
```
`$entityNames` = entity names already present in Relevant Knowledge results.

**Pattern query** (cached, 30min refresh):
```cypher
MATCH (ep:Episodic)-[:MENTIONS]->(e:Entity)
RETURN e.name AS entity, count(ep) AS mentions
ORDER BY mentions DESC
LIMIT 10
```

---

## Output Format

Appended to existing karmaCtx text:

```
## Entity Relationships
Colby → works on → Karma
Karma → uses → FalkorDB
...

## Recurring Topics
1. Karma (47 episodes)
2. FalkorDB (31 episodes)
...
```

**Graceful degradation:**
- No RELATES_TO edges yet → section silently omitted (no empty headers)
- Pattern cache empty on first startup → section omitted until first refresh
- FalkorDB timeout → both new sections fail gracefully; existing karmaCtx returned intact

---

## Files Changed

- `karma-core/karma_server.py` — one file: `/raw-context` handler + pattern cache

---

## Deployment

1. Edit locally → `git commit` → `git push`
2. `ssh vault-neo "cd /home/neo/karma-sade && git pull"`
3. `cp karma-core/karma_server.py /opt/seed-vault/memory_v1/karma-core/karma_server.py`
4. `docker compose build --no-cache karma-server && docker compose up -d karma-server`
5. Verify `RestartCount=0`

---

## Tests

- Unit: Cypher helper functions with mocked FalkorDB responses
- Integration: hit `/raw-context` directly, assert new sections present
- Smoke: send `/v1/chat`, confirm relationship context appears in response
