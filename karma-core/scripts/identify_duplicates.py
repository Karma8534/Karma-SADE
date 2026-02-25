"""
Identify duplicate Entity nodes created by batch_ingest --skip-dedup.
Duplicates are Entity nodes with same or similar names (case-insensitive).
"""
import redis
import json
from collections import defaultdict
import sys
import os

# Add parent directory to path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
