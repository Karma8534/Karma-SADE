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
                cypher = f"MATCH (e:Entity) WHERE e.id = '{entity['id']}' DELETE e"
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
