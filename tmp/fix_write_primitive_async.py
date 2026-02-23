"""
Patch /write-primitive in karma-server/server.py to use background task
so it returns immediately (Graphiti add_episode takes several seconds due to OpenAI calls).
"""

path = '/opt/seed-vault/memory_v1/karma-core/server.py'

with open(path, 'r') as f:
    content = f.read()

# Check current state
if 'ingest_primitive_episode' in content:
    print("SKIP: already patched with background task")
    exit(0)

if '/write-primitive' not in content:
    print("ERROR: /write-primitive endpoint not found — run insert script first")
    exit(1)

# The helper function to add before @app.post("/write-primitive")
HELPER_FN = '''
async def ingest_primitive_episode(name: str, body: str, source: str):
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
        print(f"[INGEST] {name} failed: {e}")


'''

# Replace the blocking await graphiti.add_episode section
# Find the block we need to replace inside /write-primitive
OLD_BLOCK = '''        graphiti = await get_graphiti()
        if graphiti is None:
            return JSONResponse({"ok": False, "error": "graphiti_unavailable"}, status_code=503)

        ref_time = datetime.now(timezone.utc)
        episode_name = f"karma_primitive_{int(ref_time.timestamp())}"

        await graphiti.add_episode(
            name=episode_name,
            episode_body=episode_text,
            source_description=f"karma-ingest from {source_file}",
            reference_time=ref_time,
            group_id=config.GRAPHITI_GROUP_ID,
        )

        print(f"[INGEST] {verdict} from '{source_file}' written to {config.GRAPHITI_GROUP_ID}")
        return JSONResponse({"ok": True, "verdict": verdict, "source": source_file})'''

NEW_BLOCK = '''        import time as _time
        episode_name = f"karma_primitive_{int(_time.time())}"

        # Fire-and-forget: add_episode calls OpenAI internally (~10s).
        # Return immediately; Graphiti writes in background.
        asyncio.create_task(ingest_primitive_episode(episode_name, episode_text, source_file))

        print(f"[INGEST] {verdict} from '{source_file}' queued")
        return JSONResponse({"ok": True, "verdict": verdict, "source": source_file})'''

if OLD_BLOCK not in content:
    print("WARNING: exact block not found — trying partial match")
    # Check what's in the write-primitive endpoint
    idx = content.find('@app.post("/write-primitive")')
    if idx >= 0:
        print("Found endpoint at index", idx)
        print("Context around it:")
        print(content[idx:idx+1500])
    exit(1)

# Apply both changes
content = content.replace(OLD_BLOCK, NEW_BLOCK, 1)
insert_before = '@app.post("/write-primitive")'
content = content.replace(insert_before, HELPER_FN + insert_before, 1)

with open(path, 'w') as f:
    f.write(content)

print("OK: /write-primitive patched to use background task")
print(f"New file size: {len(content)} chars")
