"""
Insert /write-primitive endpoint into karma-server/server.py.
Run on vault-neo: python3 /tmp/insert_write_primitive.py
"""
import re

path = '/opt/seed-vault/memory_v1/karma-core/server.py'

with open(path, 'r') as f:
    content = f.read()

# Check if already inserted
if '/write-primitive' in content:
    print("SKIP: /write-primitive already present in server.py")
    exit(0)

# Insert point: right after the /raw-context endpoint's return statement
insert_marker = '    return JSONResponse({"ok": True, "context": ctx, "query": q})\n'

new_endpoint = '''
@app.post("/write-primitive")
async def write_primitive(request: Request):
    """Write Karma's synthesized insight to FalkorDB as an Episodic node.
    Called by hub-bridge when Karma signals ASSIMILATE or DEFER during document evaluation."""
    try:
        body = await request.json()
        content_text = body.get("content", "").strip()
        verdict = body.get("verdict", "assimilate")
        source_file = body.get("source_file", "unknown")
        topic = body.get("topic", "")

        if not content_text:
            return JSONResponse({"ok": False, "error": "content required"}, status_code=400)

        episode_text = (
            f"[karma-ingest][{verdict}] Source: {source_file}\\n"
            f"Topic: {topic}\\n"
            f"Karma's synthesis: {content_text}"
        )

        graphiti = await get_graphiti()
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
        return JSONResponse({"ok": True, "verdict": verdict, "source": source_file})
    except Exception as e:
        print(f"[ERROR] /write-primitive failed: {e}")
        traceback.print_exc()
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

'''

idx = content.find(insert_marker)
if idx == -1:
    print("ERROR: insertion point not found — looking for:")
    print(repr(insert_marker))
    # Try to find approximate location
    for line in content.split('\n'):
        if 'raw-context' in line or 'context": ctx' in line:
            print("  Found nearby:", repr(line))
    exit(1)

idx += len(insert_marker)
new_content = content[:idx] + new_endpoint + content[idx:]

with open(path, 'w') as f:
    f.write(new_content)

print(f"OK: /write-primitive endpoint inserted at position {idx}")
print(f"New file size: {len(new_content)} chars")
