#!/bin/bash
# Task 3: Re-Enable Episode Ingestion
# Run on vault-neo (ssh root@arknexus.net 'bash task3_execute.sh')

set -e

echo "===== TASK 3: Re-Enable Episode Ingestion ====="
echo ""

# STEP 1: Create remove_duplicates.py if it doesn't exist
if [ ! -f /home/neo/karma-sade/karma-core/scripts/remove_duplicates.py ]; then
    echo "[STEP 1] Creating remove_duplicates.py..."
    cat > /home/neo/karma-sade/karma-core/scripts/remove_duplicates.py << 'EOFPYTHON'
"""
Remove duplicate Entity nodes created by batch_ingest --skip-dedup.
Keeps one canonical version per duplicate group (lowest ID).
Requires --confirm flag for actual deletion (dry-run mode by default).
"""
import redis
import json
from collections import defaultdict
import sys
import os

# Add parent directory to path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def get_canonical_entity(entities):
    """
    Select the canonical entity from a group of duplicates.
    Uses lowest ID (lexicographically) as the tiebreaker.

    Args:
        entities: List of entity dicts with 'id', 'name', 'type', 'created_at'

    Returns:
        The entity dict to keep (canonical)
    """
    if not entities:
        return None

    # Sort by ID (lexicographic) and return first
    sorted_entities = sorted(entities, key=lambda e: e['id'])
    return sorted_entities[0]


def find_and_mark_duplicates():
    """
    Query FalkorDB for Entity nodes, identify duplicates, mark for deletion.

    Returns:
        dict with 'keep' (canonical entities) and 'delete' (duplicates to remove)
    """
    r = redis.Redis(
        host=config.FALKORDB_HOST,
        port=config.FALKORDB_PORT,
        decode_responses=True
    )

    # Query all entities
    cypher = "MATCH (e:Entity) RETURN e.id, e.name, e.entity_type, e.created_at ORDER BY e.name"
    result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)

    if not result or len(result) < 2:
        # No entities found
        return {'keep': [], 'delete': []}

    # Group by normalized name (lowercase, stripped)
    groups = defaultdict(list)
    for row in result[1]:
        entity_id, name, entity_type, created_at = row[0], row[1], row[2], row[3]
        if name:
            normalized = name.lower().strip()
            groups[normalized].append({
                "id": entity_id,
                "name": name,
                "type": entity_type,
                "created_at": created_at
            })

    # Find groups with duplicates and mark for deletion
    keep = []
    delete = []

    for normalized_name, entities in groups.items():
        if len(entities) > 1:
            # This group has duplicates
            canonical = get_canonical_entity(entities)
            keep.append(canonical)

            # All others go to delete
            for entity in entities:
                if entity['id'] != canonical['id']:
                    delete.append(entity)
        else:
            # Single entity, no duplicate
            keep.append(entities[0])

    return {'keep': keep, 'delete': delete}


def delete_duplicates(marked):
    """
    Delete marked entities if --confirm flag is present.
    Prints dry-run output if --confirm is not present.

    Args:
        marked: dict with 'keep' and 'delete' entity lists
    """
    delete_list = marked['delete']
    keep_list = marked['keep']

    if '--confirm' in sys.argv:
        # Actually delete
        print(f"DELETING {len(delete_list)} duplicate entities...\n")

        r = redis.Redis(
            host=config.FALKORDB_HOST,
            port=config.FALKORDB_PORT,
            decode_responses=True
        )

        deleted_count = 0
        error_count = 0

        for entity in delete_list:
            try:
                # Delete entity by ID
                escaped_id = entity['id'].replace("'", "\\'")
                cypher = f"MATCH (e:Entity) WHERE e.id = '{escaped_id}' DELETE e"
                r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
                print(f"✓ Deleted: {entity['id']:<20} {entity['name']:<30} ({entity['type']})")
                deleted_count += 1
            except Exception as e:
                print(f"✗ Error deleting {entity['id']}: {str(e)}")
                error_count += 1

        print(f"\n{'='*80}")
        print(f"Summary: Deleted {deleted_count} entities, kept {len(keep_list)} canonical")
        if error_count > 0:
            print(f"Errors: {error_count}")
            sys.exit(1)
        else:
            sys.exit(0)

    else:
        # Dry-run mode
        print("DRY RUN MODE (no changes made)\n")

        if len(delete_list) == 0:
            print("No duplicates found. No entities to delete.")
        else:
            print(f"Would delete {len(delete_list)} duplicate entities:\n")
            for entity in delete_list:
                print(f"  Would delete: {entity['id']:<20} {entity['name']:<30} ({entity['type']})")

        print(f"\n{'='*80}")
        print(f"Summary: Would delete {len(delete_list)} entities, keep {len(keep_list)} canonical")
        print(f"\nRun with --confirm to execute deletion:")
        print(f"  python scripts/remove_duplicates.py --confirm")
        sys.exit(0)


if __name__ == "__main__":
    marked = find_and_mark_duplicates()
    delete_duplicates(marked)
EOFPYTHON
    echo "✓ remove_duplicates.py created"
else
    echo "✓ remove_duplicates.py already exists"
fi
echo ""

# STEP 2: Run dry-run
echo "[STEP 2] Running dry-run to identify duplicates..."
cd /home/neo/karma-sade
python karma-core/scripts/remove_duplicates.py > /tmp/task3_dryrun.log 2>&1
DRY_RUN_EXIT=$?
echo "✓ Dry-run completed (exit code: $DRY_RUN_EXIT)"
cat /tmp/task3_dryrun.log | head -50
echo ""

# STEP 3: Run with --confirm
echo "[STEP 3] Running with --confirm to delete duplicates..."
python karma-core/scripts/remove_duplicates.py --confirm > /tmp/task3_confirm.log 2>&1
CONFIRM_EXIT=$?
echo "✓ Deletion completed (exit code: $CONFIRM_EXIT)"
cat /tmp/task3_confirm.log | head -50
echo ""

if [ $CONFIRM_EXIT -ne 0 ]; then
    echo "ERROR: Deletion failed with exit code $CONFIRM_EXIT"
    exit 1
fi

# STEP 4: Verify duplicates are gone
echo "[STEP 4] Verifying duplicates are removed..."
python karma-core/scripts/identify_duplicates.py > /tmp/task3_verify.log 2>&1
VERIFY_EXIT=$?
echo "✓ Verification completed (exit code: $VERIFY_EXIT)"
cat /tmp/task3_verify.log
echo ""

if grep -q "No duplicates found" /tmp/task3_verify.log; then
    echo "✓ Confirmed: No duplicates remain"
else
    echo "ERROR: Duplicates still exist after deletion"
    exit 1
fi
echo ""

# STEP 5: Update server.py
echo "[STEP 5] Updating server.py to re-enable ingestion..."
sed -i "s/ingest_episode_fn=None,.*Disabled: Graphiti has corrupted entities.*/ingest_episode_fn=ingest_episode,  # Re-enabled after duplicate cleanup (Task 3)/g" /opt/seed-vault/memory_v1/karma-core/server.py
echo "✓ server.py updated"
echo ""

# Verify the change
echo "[STEP 5-VERIFY] Verifying server.py change..."
sed -n '1610,1615p' /opt/seed-vault/memory_v1/karma-core/server.py
echo ""

# STEP 6: Rebuild Docker image
echo "[STEP 6] Rebuilding karma-core Docker image..."
cd /opt/seed-vault
docker build -t karma-core:latest /home/neo/karma-sade/karma-core/ > /tmp/task3_build.log 2>&1
BUILD_EXIT=$?

if [ $BUILD_EXIT -ne 0 ]; then
    echo "ERROR: Docker build failed"
    cat /tmp/task3_build.log | tail -30
    exit 1
fi

if grep -q "Successfully tagged karma-core:latest" /tmp/task3_build.log; then
    echo "✓ Docker image rebuilt successfully"
else
    echo "WARNING: Build output unclear, checking for image..."
    docker images karma-core:latest 2>&1 | head -2
fi
echo ""

# STEP 7: Stop and remove old container
echo "[STEP 7] Stopping old karma-server container..."
docker stop karma-server 2>&1 || echo "Container not running"
docker rm karma-server 2>&1 || echo "Container not found"
echo "✓ Old container removed"
echo ""

# STEP 8: Start new container
echo "[STEP 8] Starting new karma-server container..."
cd /opt/seed-vault
docker-compose up -d karma-server > /tmp/task3_start.log 2>&1
START_EXIT=$?

if [ $START_EXIT -ne 0 ]; then
    echo "ERROR: Failed to start container"
    cat /tmp/task3_start.log
    exit 1
fi

echo "✓ Container started"
sleep 5

echo ""
echo "[STEP 8-VERIFY] Checking container startup logs..."
docker logs karma-server 2>&1 | tail -30
echo ""

# STEP 9: Wait for consciousness cycle and verify THINK
echo "[STEP 9] Waiting for consciousness cycle (60 seconds)..."
sleep 60

echo ""
echo "[STEP 9-VERIFY] Checking consciousness.jsonl for THINK actions..."
tail -5 /opt/seed-vault/memory_v1/ledger/consciousness.jsonl | jq '.action' 2>/dev/null || echo "Cannot parse JSON"
echo ""

# STEP 10: Verify episode count
echo "[STEP 10] Verifying FalkorDB episode count..."
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
curl -s -H "Authorization: Bearer $TOKEN" https://hub.arknexus.net/v1/cypher -d '{"cypher": "MATCH (e:Episode) RETURN COUNT(e) as episodes"}' 2>&1 | jq '.data[0][0]' 2>/dev/null || echo "Query failed"
echo ""

echo "===== TASK 3 EXECUTION COMPLETE ====="
echo ""
echo "Next steps:"
echo "1. Commit changes to git: git add karma-core/server.py && git commit -m \"feat: Re-enable episode ingestion after duplicate cleanup (Task 3)\""
echo "2. Push to main: git push origin main"
echo "3. Monitor consciousness.jsonl for THINK entries"
echo ""
