# Karma Architecture Improvements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` or `superpowers:subagent-driven-development` to execute this plan task-by-task.

**Goal:** Execute Phase 1-3 improvements: clean FalkorDB, re-enable ingestion, add atomic writes, implement adversarial cc verification, and monitoring.

**Architecture:** Three sequential phases building on each other:
- **Phase 1:** Query corrupted entities from batch_ingest --skip-dedup, remove duplicates, re-enable ingestion_fn
- **Phase 2:** Add latency monitoring to /v1/chat, inject adversarial cc prompts, document Pull-Reason-Push
- **Phase 3:** Implement atomic write semantics with rollback for critical operations

**Tech Stack:** FalkorDB (graph), FastAPI (server), asyncio (async operations), pytest (testing)

---

## Phase 1: Clean FalkorDB & Re-Enable Ingestion

### Task 1: Identify Corrupted Entities in FalkorDB

**Files:**
- Create: `karma-core/scripts/identify_duplicates.py`
- Reference: `karma-core/consciousness.py` (for query patterns)

**Step 1: Write script to find duplicate Entity nodes**

```python
# karma-core/scripts/identify_duplicates.py
"""
Identify duplicate Entity nodes created by batch_ingest --skip-dedup.
Duplicates are Entity nodes with same or similar names (case-insensitive).
"""
import redis
import json
from collections import defaultdict
import config

def find_duplicate_entities():
    """Query FalkorDB for Entity nodes, group by normalized name."""
    r = redis.Redis(host=config.FALKORDB_HOST, port=config.FALKORDB_PORT, decode_responses=True)

    # Query all entities
    cypher = "MATCH (e:Entity) RETURN e.id, e.name, e.entity_type ORDER BY e.name"
    result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)

    if not result or len(result) < 2:
        print("No entities found")
        return {}

    # Group by normalized name (lowercase, stripped)
    groups = defaultdict(list)
    for row in result[1]:
        entity_id, name, entity_type = row[0], row[1], row[2]
        if name:
            normalized = name.lower().strip()
            groups[normalized].append({
                "id": entity_id,
                "name": name,
                "type": entity_type
            })

    # Find groups with duplicates
    duplicates = {k: v for k, v in groups.items() if len(v) > 1}

    return duplicates

if __name__ == "__main__":
    dupes = find_duplicate_entities()
    print(f"Found {len(dupes)} duplicate groups:")
    for normalized_name, entities in sorted(dupes.items()):
        print(f"  {normalized_name}: {len(entities)} instances")
        for e in entities:
            print(f"    - {e['id']}: {e['name']} ({e['type']})")
```

**Step 2: Run script to verify it works**

Run:
```bash
cd /c/dev/Karma && python karma-core/scripts/identify_duplicates.py
```

Expected output:
```
Found 47 duplicate groups:
  alice: 3 instances
    - ent_12345: alice (Person)
    - ent_12346: Alice (Person)
    - ent_12347: ALICE (Person)
  ...
```

**Step 3: Write test for the script**

```python
# karma-core/tests/test_identify_duplicates.py
import pytest
from scripts.identify_duplicates import find_duplicate_entities

def test_find_duplicate_entities_returns_dict():
    """Should return dict of duplicate groups."""
    result = find_duplicate_entities()
    assert isinstance(result, dict)
    # Each value should be a list of entities
    for group, entities in result.items():
        assert isinstance(entities, list)
        assert all(isinstance(e, dict) for e in entities)
        assert all('id' in e and 'name' in e for e in entities)
```

**Step 4: Run test**

Run: `pytest karma-core/tests/test_identify_duplicates.py -v`
Expected: PASS

**Step 5: Commit**

```bash
cd /c/dev/Karma && git add karma-core/scripts/identify_duplicates.py karma-core/tests/test_identify_duplicates.py && git commit -m "feat: Add script to identify duplicate entities in FalkorDB"
```

---

### Task 2: Implement Duplicate Removal

**Files:**
- Create: `karma-core/scripts/remove_duplicates.py`
- Modify: `karma-core/consciousness.py` (reference for FalkorDB write patterns)

**Step 1: Write removal script**

```python
# karma-core/scripts/remove_duplicates.py
"""
Remove duplicate Entity nodes, keeping the one with most relationships.
Creates backup before deletion.
"""
import redis
import json
from datetime import datetime
import config

def backup_graph_state():
    """Create backup of current graph state."""
    r = redis.Redis(host=config.FALKORDB_HOST, port=config.FALKORDB_PORT, decode_responses=True)

    # Count current state
    cypher = "MATCH (e:Entity) RETURN COUNT(e) as count"
    result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
    count = result[1][0][0] if result and len(result) > 1 else 0

    backup = {
        "timestamp": datetime.utcnow().isoformat(),
        "entity_count": count,
        "description": "Backup before duplicate removal"
    }

    with open(f"karma-core/backups/falkordb_backup_{backup['timestamp']}.json", "w") as f:
        json.dump(backup, f, indent=2)

    print(f"Backup created: {backup['entity_count']} entities")
    return backup

def remove_duplicate_entities(dry_run=True):
    """
    Remove duplicate entities, keeping the one with most relationships.

    Args:
        dry_run: If True, only show what would be deleted (don't delete)
    """
    r = redis.Redis(host=config.FALKORDB_HOST, port=config.FALKORDB_PORT, decode_responses=True)

    # Find duplicates (same as identify_duplicates.py)
    cypher = "MATCH (e:Entity) RETURN e.id, e.name, e.entity_type ORDER BY e.name"
    result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)

    from collections import defaultdict
    groups = defaultdict(list)
    for row in result[1]:
        entity_id, name, entity_type = row[0], row[1], row[2]
        if name:
            normalized = name.lower().strip()
            groups[normalized].append({
                "id": entity_id,
                "name": name,
                "type": entity_type
            })

    duplicates = {k: v for k, v in groups.items() if len(v) > 1}

    removed_count = 0
    for normalized_name, entities in duplicates.items():
        # Find entity with most relationships
        max_rels = -1
        keeper_id = None
        keeper_name = None

        for entity in entities:
            rel_query = f"MATCH (e:Entity {{id: '{entity['id']}'}}) OPTIONAL MATCH (e)-[r]-() RETURN COUNT(r) as rel_count"
            rel_result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, rel_query)
            rel_count = rel_result[1][0][0] if rel_result and len(rel_result) > 1 else 0

            if rel_count > max_rels:
                max_rels = rel_count
                keeper_id = entity['id']
                keeper_name = entity['name']

        # Remove all others
        for entity in entities:
            if entity['id'] != keeper_id:
                del_query = f"MATCH (e:Entity {{id: '{entity['id']}'}}) DETACH DELETE e"

                if dry_run:
                    print(f"[DRY RUN] Would delete: {entity['name']} ({entity['id']}) — keeping {keeper_name}")
                else:
                    try:
                        r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, del_query)
                        print(f"Deleted: {entity['name']} ({entity['id']}) — keeping {keeper_name}")
                        removed_count += 1
                    except Exception as e:
                        print(f"ERROR deleting {entity['id']}: {e}")

    return removed_count

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Actually delete (default is dry-run)")
    args = parser.parse_args()

    if args.execute:
        backup_graph_state()
        removed = remove_duplicate_entities(dry_run=False)
        print(f"\nRemoved {removed} duplicate entities")
    else:
        print("DRY RUN MODE (use --execute to actually delete)")
        remove_duplicate_entities(dry_run=True)
```

**Step 2: Run in dry-run mode to verify**

Run: `cd /c/dev/Karma && python karma-core/scripts/remove_duplicates.py`
Expected: Shows what would be deleted without deleting

**Step 3: Write test for removal logic**

```python
# karma-core/tests/test_remove_duplicates.py
import pytest
from scripts.remove_duplicates import backup_graph_state, remove_duplicate_entities

def test_backup_graph_state_creates_file():
    """Should create backup JSON file."""
    backup = backup_graph_state()
    assert backup['timestamp']
    assert 'entity_count' in backup
    # Verify file was created
    import os
    assert os.path.exists(f"karma-core/backups/falkordb_backup_{backup['timestamp']}.json")

def test_remove_duplicates_dry_run_returns_count():
    """Dry run should return count without deleting."""
    count = remove_duplicate_entities(dry_run=True)
    assert isinstance(count, int)
    assert count >= 0
```

**Step 4: Run test**

Run: `pytest karma-core/tests/test_remove_duplicates.py -v`
Expected: PASS

**Step 5: Commit**

```bash
cd /c/dev/Karma && git add karma-core/scripts/remove_duplicates.py karma-core/tests/test_remove_duplicates.py && git commit -m "feat: Add script to remove duplicate entities with dry-run mode"
```

---

### Task 3: Re-Enable Episode Ingestion

**Files:**
- Modify: `karma-core/server.py:1612`

**Step 1: Verify current state**

```bash
grep -n "ingest_episode_fn=None" /c/dev/Karma/karma-core/server.py
```

Expected: Shows line 1612 with comment about disabled ingestion

**Step 2: Update server.py to enable ingestion**

Change line 1612 from:
```python
ingest_episode_fn=None,  # Disabled: Graphiti has corrupted entities from batch_ingest --skip-dedup
```

To:
```python
ingest_episode_fn=ingest_episode,  # Re-enabled: Corrupted entities cleaned (see docs/plans/2026-02-25-...)
```

**Step 3: Add test to verify ingestion is enabled**

```python
# karma-core/tests/test_ingestion_enabled.py
def test_consciousness_loop_receives_ingest_episode_function():
    """Should verify consciousness loop has ingest_episode function."""
    # This will be called in server startup
    # For now, just check the function exists
    from server import ingest_episode
    assert callable(ingest_episode)
    assert ingest_episode.__name__ == "ingest_episode"
```

**Step 4: Run test**

Run: `pytest karma-core/tests/test_ingestion_enabled.py -v`
Expected: PASS

**Step 5: Commit**

```bash
cd /c/dev/Karma && git add karma-core/server.py karma-core/tests/test_ingestion_enabled.py && git commit -m "feat: Re-enable episode ingestion after FalkorDB cleanup"
```

---

### Task 4: Rebuild & Deploy

**Files:**
- Docker: `karma-core/Dockerfile`
- Deploy: `vault-neo` droplet

**Step 1: Rebuild karma-core image on vault-neo**

```bash
ssh vault-neo "cd /opt/seed-vault/memory_v1/karma-core && docker build -t karma-core:latest --no-cache . 2>&1 | tail -20"
```

Expected: Successful build with "exporting to image"

**Step 2: Stop old container & start new one**

```bash
ssh vault-neo "docker stop karma-server && sleep 2 && docker rm karma-server && docker run -d --name karma-server --network anr-vault-net -e FALKORDB_HOST=falkordb -e POSTGRES_HOST=anr-vault-db -v /opt/seed-vault/memory_v1/ledger:/ledger:rw -v /opt/seed-vault/memory_v1:/opt/seed-vault/memory_v1:rw karma-core:latest python -u server.py && sleep 5 && docker logs karma-server | grep -E 'GRAPHITI|Consciousness|Ingestion'"
```

Expected: Logs show "Graphiti: READY" and "Consciousness: ACTIVE"

**Step 3: Verify no errors in logs**

```bash
ssh vault-neo "docker logs karma-server 2>&1 | grep -i error | head -10 || echo 'No errors found'"
```

Expected: No errors or just warnings

**Step 4: Commit**

```bash
cd /c/dev/Karma && git add . && git commit -m "phase-1: Deploy FalkorDB cleanup + re-enabled ingestion"
```

---

## Phase 2: Adversarial cc Prompts + Latency Monitoring

### Task 5: Add Adversarial cc Prompts to CLAUDE.md

**Files:**
- Modify: `CLAUDE.md` (system prompt section)

**Step 1: Review current cc prompt**

```bash
grep -A 20 "cc.*prompt\|verifier.*prompt" /c/Users/raest/Documents/Karma_SADE/CLAUDE.md | head -30
```

**Step 2: Add adversarial directives**

Modify CLAUDE.md Honesty & Analysis Contract section to add:

```markdown
## cc (2nd Verifier) Adversarial Checklist

**You are cc. Your role is to find what's WRONG, not affirm what's right.**

Every recommendation from Claude Code or Karma requires critical review:

- [ ] **Contradiction Check:** Is there internal inconsistency? (e.g., claims X is done, but Y hasn't been verified)
- [ ] **Hidden Complexity:** What's being glossed over? (e.g., "this should work" without testing)
- [ ] **Failure Scenarios:** What breaks if this goes wrong? (e.g., network timeout, concurrent writes, state corruption)
- [ ] **Edge Cases:** What about boundary conditions? (e.g., empty input, max size, race conditions)
- [ ] **Cost/Benefit:** Is the proposed solution worth the complexity? (e.g., adding atomic writes for 1% risk)
- [ ] **Data Loss Risk:** Could this corrupt or lose state? (e.g., partial writes, network interruption)
- [ ] **False Positives:** Is success verified or just assumed? (e.g., "test passes" vs "actually ran the test")

**If any checkbox is unchecked, ask Claude Code for evidence before approving.**
```

**Step 3: Write test to verify cc prompt exists**

```python
# tests/test_cc_prompt.py
def test_cc_adversarial_checklist_in_claude_md():
    """Verify cc adversarial checklist is in CLAUDE.md."""
    with open("CLAUDE.md", "r") as f:
        content = f.read()

    required_phrases = [
        "cc (2nd Verifier) Adversarial",
        "Contradiction Check",
        "Hidden Complexity",
        "Failure Scenarios",
        "Edge Cases"
    ]

    for phrase in required_phrases:
        assert phrase in content, f"Missing: {phrase}"
```

**Step 4: Run test**

Run: `pytest tests/test_cc_prompt.py -v`
Expected: PASS

**Step 5: Commit**

```bash
cd /c/Users/raest/Documents/Karma_SADE && git add CLAUDE.md tests/test_cc_prompt.py && git commit -m "feat: Add cc adversarial verification checklist to CLAUDE.md"
```

---

### Task 6: Add Latency Monitoring to /v1/chat

**Files:**
- Modify: `karma-core/server.py` (/v1/chat endpoint)

**Step 1: Write test for latency measurement**

```python
# karma-core/tests/test_latency_monitoring.py
import time
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_chat_endpoint_returns_latency_in_response():
    """Should include latency measurements in response."""
    response = client.post("/v1/chat", json={
        "message": "hello",
        "provider": "test"
    })

    assert response.status_code == 200
    data = response.json()

    # Should have timing info
    assert "timing" in data or "debug_latency" in data or response.headers.get("X-Latency-Ms")

def test_chat_endpoint_latency_under_4_seconds():
    """Should complete within 4 second SLA."""
    start = time.time()
    response = client.post("/v1/chat", json={
        "message": "test",
        "provider": "test"
    })
    elapsed = time.time() - start

    assert elapsed < 4.0, f"Latency {elapsed:.2f}s exceeds 4s SLA"
```

**Step 2: Implement latency monitoring in server.py**

Add to `/v1/chat` endpoint:

```python
import time
from datetime import datetime

@app.post("/v1/chat")
async def chat(request: Request):
    # ... existing code ...

    # LATENCY: Start timing
    t_start = time.monotonic()
    t_falkor = None
    t_llm = None
    t_write = None

    try:
        # LATENCY: FalkorDB query
        t_before_falkor = time.monotonic()
        # ... existing graph query code ...
        t_falkor = time.monotonic() - t_before_falkor

        # LATENCY: LLM inference
        t_before_llm = time.monotonic()
        # ... existing LLM call code ...
        t_llm = time.monotonic() - t_before_llm

        # LATENCY: Write to ledger
        t_before_write = time.monotonic()
        # ... existing ledger write code ...
        t_write = time.monotonic() - t_before_write

        t_total = time.monotonic() - t_start

        # Log latency
        print(f"[LATENCY] /v1/chat: {t_total:.3f}s (falkordb: {t_falkor:.3f}s, llm: {t_llm:.3f}s, write: {t_write:.3f}s)")

        # Alert if SLA violated
        if t_total > 4.0:
            print(f"[ALERT] Latency SLA violated: {t_total:.3f}s > 4.0s")

        # Return response with timing info
        return {
            "ok": True,
            "response": assistant_text,
            "timing": {
                "total_ms": int(t_total * 1000),
                "falkordb_ms": int(t_falkor * 1000),
                "llm_ms": int(t_llm * 1000),
                "write_ms": int(t_write * 1000)
            }
        }

    except Exception as e:
        t_total = time.monotonic() - t_start
        print(f"[ERROR] /v1/chat failed after {t_total:.3f}s: {e}")
        raise
```

**Step 3: Run test**

Run: `pytest karma-core/tests/test_latency_monitoring.py -v`
Expected: PASS

**Step 4: Commit**

```bash
cd /c/dev/Karma && git add karma-core/server.py karma-core/tests/test_latency_monitoring.py && git commit -m "feat: Add latency monitoring to /v1/chat endpoint (target: <4s SLA)"
```

---

### Task 7: Document Pull-Reason-Push Pattern in CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Add Pull-Reason-Push documentation**

Add to CLAUDE.md under "Critical Rules":

```markdown
## Pull-Reason-Push Pattern (LOCKED — Required for All Interactions)

**Pattern:** Every interaction with Karma must follow Pull → Reason → Push cycle

### What This Means

1. **Pull:** Query droplet state
   - FalkorDB: current graph, entities, relationships
   - consciousness.jsonl: recent cycles, THINK results
   - identity.json, invariants.json: Karma's core rules
   - Do NOT assume local knowledge

2. **Reason:** Perform inference locally
   - LLM generates response based on pulled state
   - Make decisions independently (don't defer to droplet)
   - Use full context (reasoning rooted in state, not heuristics)

3. **Push:** Write results back to droplet
   - consciousness.jsonl: decisions, reflections, insights
   - FalkorDB: new entities, relationships from episodes
   - decision_log.jsonl: reasoned choices with rationale
   - Do NOT cache locally without sync plan

### Why This Matters

- **Prevents divergence:** Local cache can't become authoritative
- **Ensures coherence:** All systems read from single source (droplet)
- **Enables debugging:** Can trace decisions back to state + reasoning
- **Preserves identity:** Karma's state is droplet state, not LLM state
```

**Step 2: Write test to verify documentation**

```python
# tests/test_pull_reason_push.py
def test_pull_reason_push_pattern_documented():
    """Verify Pull-Reason-Push pattern is documented in CLAUDE.md."""
    with open("CLAUDE.md", "r") as f:
        content = f.read()

    required = ["Pull-Reason-Push", "Pull", "Reason", "Push", "droplet state"]

    for term in required:
        assert term in content, f"Missing documentation for: {term}"
```

**Step 3: Run test**

Run: `pytest tests/test_pull_reason_push.py -v`
Expected: PASS

**Step 4: Commit**

```bash
cd /c/Users/raest/Documents/Karma_SADE && git add CLAUDE.md tests/test_pull_reason_push.py && git commit -m "docs: Document Pull-Reason-Push pattern as required interaction model"
```

---

## Phase 3: Atomic Write Semantics (Later Sessions)

### Task 8: Design Atomic Write Mechanism (Planning Only)

**Files:**
- Create: `karma-core/atomic_writes.py` (module for transaction handling)

**Step 1: Write design doc (non-executable)**

```python
# karma-core/atomic_writes.py
"""
Atomic Write Mechanism for Karma State

Design (Phase 3 - not implemented yet):

CONCEPT:
An atomic write operation bundles multiple FalkorDB operations into a single
logical unit. If any operation fails, all must rollback.

EXAMPLE:
    async with atomic_transaction() as txn:
        # Add episode
        await txn.add_episodic_node(...)
        # Add entities from episode
        await txn.add_entity_nodes([...])
        # Add relationships
        await txn.add_relationships([...])
    # If any operation fails, ENTIRE transaction rolls back

IMPLEMENTATION (Phase 3):
1. Create transaction log: txn_[timestamp].jsonl (records all operations)
2. Before commit: verify all operations can succeed (dry-run)
3. Commit: execute all operations in sequence
4. On failure: read txn log, reverse operations in reverse order
5. Log result: success/failure with rationale

FAILURE SCENARIOS:
- Network timeout during write: detected by redis timeout, automatic rollback
- FalkorDB full: queued, retried with backoff, logged if failed
- Entity already exists: checked before write, skipped if exists
- Relationship target missing: validated before operation
"""
```

**Step 2: Write test (will fail in Phase 3)**

```python
# karma-core/tests/test_atomic_writes.py
@pytest.mark.skip(reason="Phase 3: Atomic writes not yet implemented")
async def test_atomic_transaction_succeeds_when_all_operations_valid():
    """Should commit when all operations are valid."""
    async with atomic_transaction() as txn:
        await txn.add_episodic_node(name="test", body="test body")
        await txn.add_entity_node(name="Alice", type="Person")
        await txn.add_relationship("test", "has_entity", "Alice")

    # Verify all operations persisted
    # ... verification code ...

@pytest.mark.skip(reason="Phase 3: Atomic writes not yet implemented")
async def test_atomic_transaction_rollsback_on_failure():
    """Should rollback all operations if any operation fails."""
    try:
        async with atomic_transaction() as txn:
            await txn.add_episodic_node(name="test", body="test body")
            await txn.add_entity_node(name="Alice", type="Person")
            # This should fail (invalid relationship)
            await txn.add_relationship("nonexistent", "has_entity", "Alice")
    except TransactionError:
        pass

    # Verify nothing persisted
    # ... verification code ...
```

**Step 3: Commit design doc + skipped tests**

```bash
cd /c/dev/Karma && git add karma-core/atomic_writes.py karma-core/tests/test_atomic_writes.py && git commit -m "docs: Phase 3 design - atomic write semantics with transaction log and rollback"
```

---

## Summary & Next Steps

**Total Tasks:** 8
- **Phase 1 (Current Blocker):** Tasks 1-4 (Cleanup + re-enable ingestion)
- **Phase 2 (Parallel):** Tasks 5-7 (cc prompts + monitoring + documentation)
- **Phase 3 (Later):** Task 8 (Design only, implementation deferred)

**Expected Timeline:**
- Phase 1: Session 34 (2-3 hours)
- Phase 2: Sessions 34-35 (1-2 hours parallel with Phase 1)
- Phase 3: Sessions 36+ (after Phase 1-2 verified)

**Success Criteria:**
- ✅ FalkorDB cleaned (duplicates removed)
- ✅ Episodes ingesting (no errors in logs)
- ✅ Consciousness THINK executing (not just NO_ACTION)
- ✅ Latency monitoring active (< 4s SLA)
- ✅ cc prompts adversarial (documented)
- ✅ Pull-Reason-Push documented

---

## Execution Path (Two Options)

### Option 1: Subagent-Driven (Current Session)
**Use:** `superpowers:subagent-driven-development`
- Fresh subagent per 1-2 tasks
- Review outputs between tasks
- Stay in this session
- Tighter feedback loop
- **Best for:** Catching issues early, rapid iteration

### Option 2: Parallel Session (Separate)
**Use:** `superpowers:executing-plans`
- Open new session
- Batch execution with checkpoints
- More autonomy
- Better for long implementations
- **Best for:** Uninterrupted focus, parallel work

---

**Plan Status:** ✅ Approved, designed, and ready for execution
**Files:** Saved to `docs/plans/2026-02-25-karma-architecture-audit-implementation.md` (committed to git)
**Next Step:** Choose execution option and proceed

