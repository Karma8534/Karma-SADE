# Entity Relationship Context Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Surface RELATES_TO relationship edges and recurring topic patterns from FalkorDB into every `/v1/chat` response via `build_karma_context()`.

**Architecture:** Two new sections appended to karmaCtx: "Entity Relationships" (per-message RELATES_TO query using entities already returned by `query_knowledge_graph`) + "Recurring Topics" (top-10 entities by episode count, cached in-memory and refreshed every 30 minutes). All changes in one file: `karma-core/server.py`. Hub-bridge zero changes.

**Tech Stack:** Python, FastAPI, FalkorDB (redis protocol), asyncio, pytest

---

## Context (read before starting)

- **File:** `karma-core/server.py` (all changes here)
- **`get_falkor()`** at line 339 — returns redis connection; use `r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)`
- **`config.GRAPHITI_GROUP_ID`** — the FalkorDB graph name (`neo_workspace`)
- **`query_knowledge_graph()`** at line 352 — returns `[{"name": str, "summary": str}, ...]` (the Entity nodes already in karmaCtx)
- **`query_entity_relationships()`** at line 510 — ALREADY EXISTS but wrong: takes one name, returns `type(rel)` not `r.fact`. Do NOT modify it. Add new function alongside.
- **`build_karma_context()`** at line 776 — builds karmaCtx string. Entity loop at lines 817-823. Add new sections after line 823.
- **`startup()`** at line 2572 — FastAPI `@app.on_event("startup")`. Wire pattern refresh here.
- **Tests:** `karma-core/tests/` — existing tests use `pytest`. Run with: `cd karma-core && python -m pytest tests/ -v`
- **Build context:** Droplet build is from `/opt/seed-vault/memory_v1/karma-core/` (NOT git repo). Always sync before rebuild.
- **Graphiti RELATES_TO edges** have a `fact` property (meaningful description). `type(rel)` just returns "RELATES_TO" and is NOT useful.

---

## Task 1: Pattern Cache Functions + Tests (TDD)

**Files:**
- Create: `karma-core/tests/test_entity_relationship_context.py`
- Modify: `karma-core/server.py` (add after line 349)

### Step 1: Write the failing tests

Create `karma-core/tests/test_entity_relationship_context.py`:

```python
"""Tests for entity relationship context features."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock


def test_pattern_cache_starts_empty():
    """_pattern_cache is empty list on module import."""
    import importlib
    import server
    importlib.reload(server)
    assert server._pattern_cache == []


def test_refresh_pattern_cache_populates_cache():
    """_refresh_pattern_cache() stores results from FalkorDB query."""
    import server

    mock_result = [
        ["header"],                        # index 0: column names (ignored)
        [["Karma", 47], ["FalkorDB", 31]]  # index 1: rows
    ]

    with patch.object(server, "get_falkor") as mock_get_falkor:
        mock_r = MagicMock()
        mock_r.execute_command.return_value = mock_result
        mock_get_falkor.return_value = mock_r

        server._refresh_pattern_cache()

    assert len(server._pattern_cache) == 2
    assert server._pattern_cache[0] == {"entity": "Karma", "mentions": 47}
    assert server._pattern_cache[1] == {"entity": "FalkorDB", "mentions": 31}


def test_refresh_pattern_cache_graceful_on_error():
    """_refresh_pattern_cache() does not raise on FalkorDB failure."""
    import server
    server._pattern_cache = [{"entity": "OldData", "mentions": 5}]

    with patch.object(server, "get_falkor") as mock_get_falkor:
        mock_get_falkor.side_effect = Exception("FalkorDB unavailable")
        server._refresh_pattern_cache()  # must not raise

    # Cache preserved on error
    assert server._pattern_cache == [{"entity": "OldData", "mentions": 5}]
```

### Step 2: Run tests to verify they fail

```bash
cd karma-core && python -m pytest tests/test_entity_relationship_context.py -v
```

Expected: `ImportError: cannot import name '_pattern_cache' from 'server'` (or AttributeError)

### Step 3: Add pattern cache to server.py

In `karma-core/server.py`, after line 337 (`_falkor_client = None`), add:

```python
# ─── Pattern Cache (recurring topics, 30min refresh) ──────────────────────────
_pattern_cache: list[dict] = []  # [{"entity": str, "mentions": int}]


def _refresh_pattern_cache() -> None:
    """Query FalkorDB for top-10 most-mentioned entities. Updates module-level cache.
    Non-fatal: on FalkorDB error, existing cache is preserved."""
    global _pattern_cache
    try:
        r = get_falkor()
        cypher = (
            "MATCH (ep:Episodic)-[:MENTIONS]->(e:Entity) "
            "RETURN e.name AS entity, count(ep) AS mentions "
            "ORDER BY mentions DESC LIMIT 10"
        )
        result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
        if len(result) >= 2 and result[1]:
            _pattern_cache = [{"entity": row[0], "mentions": row[1]} for row in result[1]]
        else:
            _pattern_cache = []
    except Exception as e:
        print(f"[PATTERN] cache refresh failed (non-fatal): {e}")
        # Intentionally preserve existing cache on error
```

### Step 4: Run tests to verify they pass

```bash
cd karma-core && python -m pytest tests/test_entity_relationship_context.py::test_pattern_cache_starts_empty tests/test_entity_relationship_context.py::test_refresh_pattern_cache_populates_cache tests/test_entity_relationship_context.py::test_refresh_pattern_cache_graceful_on_error -v
```

Expected: all 3 PASS

### Step 5: Commit

```bash
git add karma-core/tests/test_entity_relationship_context.py karma-core/server.py
git commit -m "feat: add pattern cache for recurring topics in entity context"
```

---

## Task 2: Bulk Relationship Query Function + Tests (TDD)

**Files:**
- Modify: `karma-core/tests/test_entity_relationship_context.py` (add tests)
- Modify: `karma-core/server.py` (add after line 527)

### Step 1: Add failing tests

Append to `karma-core/tests/test_entity_relationship_context.py`:

```python
def test_query_relevant_relationships_empty_list():
    """query_relevant_relationships([]) returns [] without hitting FalkorDB."""
    import server
    with patch.object(server, "get_falkor") as mock_get_falkor:
        result = server.query_relevant_relationships([])
    mock_get_falkor.assert_not_called()
    assert result == []


def test_query_relevant_relationships_returns_facts():
    """query_relevant_relationships returns from/relationship/to dicts using r.fact."""
    import server

    mock_result = [
        ["header"],
        [["Karma", "uses for memory storage", "FalkorDB"],
         ["Colby", "is building", "Karma"]]
    ]

    with patch.object(server, "get_falkor") as mock_get_falkor:
        mock_r = MagicMock()
        mock_r.execute_command.return_value = mock_result
        mock_get_falkor.return_value = mock_r

        result = server.query_relevant_relationships(["Karma", "Colby"])

    assert len(result) == 2
    assert result[0] == {"from": "Karma", "relationship": "uses for memory storage", "to": "FalkorDB"}
    assert result[1] == {"from": "Colby", "relationship": "is building", "to": "Karma"}


def test_query_relevant_relationships_graceful_on_error():
    """query_relevant_relationships returns [] on FalkorDB failure."""
    import server
    with patch.object(server, "get_falkor") as mock_get_falkor:
        mock_get_falkor.side_effect = Exception("timeout")
        result = server.query_relevant_relationships(["Karma"])
    assert result == []
```

### Step 2: Run tests to verify they fail

```bash
cd karma-core && python -m pytest tests/test_entity_relationship_context.py::test_query_relevant_relationships_empty_list tests/test_entity_relationship_context.py::test_query_relevant_relationships_returns_facts tests/test_entity_relationship_context.py::test_query_relevant_relationships_graceful_on_error -v
```

Expected: `AttributeError: module 'server' has no attribute 'query_relevant_relationships'`

### Step 3: Add the function to server.py

In `karma-core/server.py`, after line 527 (after the closing of `query_entity_relationships`), add:

```python
def query_relevant_relationships(entity_names: list[str]) -> list[dict]:
    """Query RELATES_TO edges for a list of entity names in one FalkorDB call.
    Uses r.fact (the meaningful relationship description from Graphiti).
    Returns [{"from": str, "relationship": str, "to": str}].
    Returns [] on empty input or FalkorDB failure (non-fatal)."""
    if not entity_names:
        return []
    try:
        r = get_falkor()
        safe_names = [n.replace("'", "") for n in entity_names]
        names_str = ", ".join(f"'{n}'" for n in safe_names)
        cypher = (
            f"MATCH (e1:Entity)-[r:RELATES_TO]->(e2:Entity) "
            f"WHERE e1.name IN [{names_str}] "
            "RETURN e1.name AS from, r.fact AS relationship, e2.name AS to "
            "LIMIT 20"
        )
        result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
        if len(result) >= 2 and result[1]:
            return [
                {"from": row[0], "relationship": row[1], "to": row[2]}
                for row in result[1]
                if row[0] and row[1] and row[2]  # skip rows with None fact
            ]
        return []
    except Exception as e:
        print(f"[RELATIONSHIPS] edge query failed (non-fatal): {e}")
        return []
```

### Step 4: Run tests to verify they pass

```bash
cd karma-core && python -m pytest tests/test_entity_relationship_context.py -v
```

Expected: all 6 tests PASS

### Step 5: Commit

```bash
git add karma-core/tests/test_entity_relationship_context.py karma-core/server.py
git commit -m "feat: add query_relevant_relationships bulk edge query using r.fact"
```

---

## Task 3: Wire Into build_karma_context() + startup() + Tests (TDD)

**Files:**
- Modify: `karma-core/tests/test_entity_relationship_context.py` (add integration tests)
- Modify: `karma-core/server.py` (lines 820-824 and 2618-2620)

### Step 1: Add failing tests

Append to `karma-core/tests/test_entity_relationship_context.py`:

```python
def test_build_karma_context_includes_relationship_section():
    """build_karma_context includes Entity Relationships section when edges exist."""
    import server

    # Mock entity query to return known entities
    mock_entities = [{"name": "Karma", "summary": "AI system"}, {"name": "FalkorDB", "summary": "graph DB"}]
    # Mock relationship query to return edges
    mock_rels = [{"from": "Karma", "relationship": "stores data in", "to": "FalkorDB"}]

    with patch.object(server, "query_knowledge_graph", return_value=mock_entities), \
         patch.object(server, "query_relevant_relationships", return_value=mock_rels), \
         patch.object(server, "_pattern_cache", []), \
         patch.object(server, "query_identity_facts", return_value=""), \
         patch.object(server, "query_recent_episodes", return_value=[]), \
         patch.object(server, "query_recent_ingest_episodes", return_value=[]), \
         patch.object(server, "query_pending_cc_proposals", return_value=[]), \
         patch.object(server, "query_preferences", return_value=[]):
        ctx = server.build_karma_context("test message")

    assert "## Entity Relationships" in ctx
    assert "Karma → stores data in → FalkorDB" in ctx


def test_build_karma_context_includes_recurring_topics():
    """build_karma_context includes Recurring Topics section when pattern cache has data."""
    import server

    mock_entities = [{"name": "Karma", "summary": "AI system"}]
    mock_pattern = [{"entity": "Karma", "mentions": 47}, {"entity": "FalkorDB", "mentions": 31}]

    with patch.object(server, "query_knowledge_graph", return_value=mock_entities), \
         patch.object(server, "query_relevant_relationships", return_value=[]), \
         patch.object(server, "_pattern_cache", mock_pattern), \
         patch.object(server, "query_identity_facts", return_value=""), \
         patch.object(server, "query_recent_episodes", return_value=[]), \
         patch.object(server, "query_recent_ingest_episodes", return_value=[]), \
         patch.object(server, "query_pending_cc_proposals", return_value=[]), \
         patch.object(server, "query_preferences", return_value=[]):
        ctx = server.build_karma_context("test message")

    assert "## Recurring Topics" in ctx
    assert "1. Karma (47 episodes)" in ctx
    assert "2. FalkorDB (31 episodes)" in ctx


def test_build_karma_context_omits_sections_when_empty():
    """build_karma_context omits both sections when no data available."""
    import server

    with patch.object(server, "query_knowledge_graph", return_value=[]), \
         patch.object(server, "query_relevant_relationships", return_value=[]), \
         patch.object(server, "_pattern_cache", []), \
         patch.object(server, "query_identity_facts", return_value=""), \
         patch.object(server, "query_recent_episodes", return_value=[]), \
         patch.object(server, "query_recent_ingest_episodes", return_value=[]), \
         patch.object(server, "query_pending_cc_proposals", return_value=[]), \
         patch.object(server, "query_preferences", return_value=[]):
        ctx = server.build_karma_context("test message")

    assert "## Entity Relationships" not in ctx
    assert "## Recurring Topics" not in ctx
```

### Step 2: Run tests to verify they fail

```bash
cd karma-core && python -m pytest tests/test_entity_relationship_context.py::test_build_karma_context_includes_relationship_section tests/test_entity_relationship_context.py::test_build_karma_context_includes_recurring_topics tests/test_entity_relationship_context.py::test_build_karma_context_omits_sections_when_empty -v
```

Expected: FAIL (sections not in context yet)

### Step 3: Wire into build_karma_context()

In `karma-core/server.py`, in `build_karma_context()`, **replace** lines 817-823 (the entity block):

```python
    # Current (lines 817-823):
    # entities = query_knowledge_graph(user_message, limit=5)
    # if entities:
    #     parts.append("\n## Relevant Knowledge")
    #     for e in entities:
    #         summary = (e["summary"] or "")[:200]
    #         parts.append(f"- **{e['name']}**: {summary}")
```

**With** this expanded block:

```python
    # Get relevant entities from knowledge graph based on message keywords
    entities = query_knowledge_graph(user_message, limit=5)
    if entities:
        parts.append("\n## Relevant Knowledge")
        for e in entities:
            summary = (e["summary"] or "")[:200]
            parts.append(f"- **{e['name']}**: {summary}")

        # Entity relationships — RELATES_TO edges between relevant entities
        entity_names = [e["name"] for e in entities]
        relationships = query_relevant_relationships(entity_names)
        if relationships:
            parts.append("\n## Entity Relationships")
            for rel in relationships:
                parts.append(f"- {rel['from']} → {rel['relationship']} → {rel['to']}")

    # Recurring topics — top entities by episode count (cached, 30min refresh)
    if _pattern_cache:
        parts.append("\n## Recurring Topics")
        for i, entry in enumerate(_pattern_cache, 1):
            parts.append(f"{i}. {entry['entity']} ({entry['mentions']} episodes)")
```

### Step 4: Wire into startup()

In `karma-core/server.py`, in `startup()` at line ~2618, **before** the final `print("=" * 50)`, add:

```python
    # Start pattern cache refresh loop (recurring topics for entity context)
    _refresh_pattern_cache()

    async def _pattern_refresh_loop():
        while True:
            await asyncio.sleep(1800)  # 30 minutes
            _refresh_pattern_cache()

    asyncio.create_task(_pattern_refresh_loop())
    print("  Pattern cache: ACTIVE (30min refresh, recurring topics)")
```

### Step 5: Run all tests

```bash
cd karma-core && python -m pytest tests/test_entity_relationship_context.py -v
```

Expected: all 9 tests PASS

### Step 6: Run full test suite to verify no regressions

```bash
cd karma-core && python -m pytest tests/ -v
```

Expected: all existing tests still PASS

### Step 7: Commit

```bash
git add karma-core/tests/test_entity_relationship_context.py karma-core/server.py
git commit -m "feat: wire entity relationships + recurring topics into build_karma_context"
```

---

## Task 4: Deploy to vault-neo

### Step 1: Push to GitHub

```bash
git push origin main
```

### Step 2: Pull on vault-neo

```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"
```

Expected output: shows files updated

### Step 3: Sync to build context

```bash
ssh vault-neo "cp /home/neo/karma-sade/karma-core/server.py /opt/seed-vault/memory_v1/karma-core/server.py"
```

Verify:
```bash
ssh vault-neo "diff /home/neo/karma-sade/karma-core/server.py /opt/seed-vault/memory_v1/karma-core/server.py && echo 'IN SYNC'"
```

Expected: `IN SYNC`

### Step 4: Rebuild karma-server image

```bash
ssh vault-neo "cd /opt/seed-vault/memory_v1/compose && docker compose build --no-cache karma-server 2>&1 | tail -5"
```

Expected: `Image compose-karma-server Built` (takes ~60-120s)

### Step 5: Restart karma-server

```bash
ssh vault-neo "cd /opt/seed-vault/memory_v1/compose && docker compose up -d karma-server"
```

### Step 6: Verify startup (RestartCount=0 + pattern cache active)

```bash
ssh vault-neo "docker inspect karma-server --format '{{.RestartCount}}' && docker logs karma-server --tail=20 2>&1 | grep -E 'Pattern|ACTIVE|ERROR'"
```

Expected:
- `0` (RestartCount)
- `Pattern cache: ACTIVE (30min refresh, recurring topics)` in logs

### Step 7: Smoke test /raw-context

```bash
ssh vault-neo "curl -s 'http://localhost:8340/raw-context?q=Karma' | python3 -c \"import sys,json; ctx=json.load(sys.stdin)['context']; print('Recurring Topics' in ctx, 'Entity Relationships' in ctx or 'no edges yet')\""
```

Expected: `True True` (or `True no edges yet` if graph still sparse — both are correct)

### Step 8: Commit STATE.md + MEMORY.md updates

Update `.gsd/STATE.md` Session 64 Accomplishments and `MEMORY.md` Active Task, then:

```bash
git add .gsd/STATE.md MEMORY.md
git commit -m "session-64: entity relationship context deployed"
git push origin main
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"
```

---

## Notes for Implementer

- **`_pattern_cache` is module-level** — must be declared with `global _pattern_cache` inside `_refresh_pattern_cache()` to write to it
- **`asyncio.create_task()` requires a running event loop** — calling it inside `@app.on_event("startup")` is correct; do NOT call it at module level
- **FalkorDB `:MENTIONS` edges** — these are created by Graphiti during entity extraction. They may not exist yet for the 571 legacy entities (Graphiti may have used different edge labels). If the pattern query returns empty, the section is silently omitted — that's correct behavior.
- **`r.fact` on RELATES_TO edges** — if Graphiti stored the fact differently (e.g., as `fact` vs `description`), the relationship column will be None. The `if row[0] and row[1] and row[2]` guard in `query_relevant_relationships` handles this.
- **Do NOT use heredoc to write JS files on vault-neo** — not applicable here (Python file), but remember this for hub-bridge changes in other sessions
