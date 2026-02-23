"""
Replace ingest_primitive_episode with a direct FalkorDB write.
Karma's synthesized insights don't need Graphiti's entity extraction —
they're already distilled knowledge. Direct write is fast and reliable.
"""
import uuid as uuid_lib, re

path = '/opt/seed-vault/memory_v1/karma-core/server.py'

with open(path, 'r') as f:
    content = f.read()

# Find and replace the existing ingest_primitive_episode function
OLD_FN = '''async def ingest_primitive_episode(name: str, body: str, source: str):
    """Background task: write karma-ingest primitive to FalkorDB via Graphiti."""
    try:
        g = await get_graphiti()
        if g is None:
            print(f"[INGEST] skipping {name} — Graphiti not available")
            return
        from datetime import datetime, timezone
        ref = datetime.now(timezone.utc)
        await g.add_episode(
            name=name,
            episode_body=body,
            source_description=f"karma-ingest from {source}",
            reference_time=ref,
            group_id=config.GRAPHITI_GROUP_ID,
        )
        print(f"[INGEST] {name} written to {config.GRAPHITI_GROUP_ID}")
    except Exception as e:
        print(f"[INGEST] {name} failed: {e}")'''

NEW_FN = '''async def ingest_primitive_episode(name: str, body: str, source: str):
    """Background task: write karma-ingest primitive directly to FalkorDB.

    Uses direct FalkorDB write (not Graphiti) because:
    - Karma's synthesized insights are already distilled — no entity extraction needed
    - Graphiti add_episode times out on large graphs due to entity deduplication queries
    - Direct write is fast (~ms) and immediately queryable
    """
    try:
        import falkordb as fdb
        import uuid as _uuid
        from datetime import datetime, timezone

        r = fdb.FalkorDB(host=config.FALKORDB_HOST, port=config.FALKORDB_PORT)
        g = r.select_graph(config.GRAPHITI_GROUP_ID)

        node_uuid = str(_uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()[:19]

        g.query(
            "CREATE (e:Episodic {uuid: $uuid, name: $name, content: $content, "
            "group_id: $gid, created_at: localdatetime($ts), "
            "source_description: $src})",
            {
                "uuid": node_uuid,
                "name": name,
                "content": body,
                "gid": config.GRAPHITI_GROUP_ID,
                "ts": now,
                "src": f"karma-ingest from {source}",
            }
        )
        print(f"[INGEST] {name} written to {config.GRAPHITI_GROUP_ID} (uuid={node_uuid[:8]})")
    except Exception as e:
        print(f"[INGEST] {name} failed: {e}")
        import traceback
        traceback.print_exc()'''

if OLD_FN not in content:
    print("ERROR: ingest_primitive_episode pattern not found")
    # Show what's there
    idx = content.find('ingest_primitive_episode')
    if idx >= 0:
        print("Current function context:")
        print(content[max(0,idx-20):idx+600])
    exit(1)

content = content.replace(OLD_FN, NEW_FN, 1)

with open(path, 'w') as f:
    f.write(content)

print("OK: ingest_primitive_episode now uses direct FalkorDB write")
print(f"New file size: {len(content)} chars")
