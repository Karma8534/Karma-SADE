import sys

path = "/opt/seed-vault/memory_v1/hub_bridge/app/server.js"

with open(path, "r") as f:
    content = f.read()

# Add debug logging before JSON.parse in the /v1/ingest handler
old = '''      const raw = await parseBody(req, 20000000);
      let body;
      try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }'''

new = '''      const raw = await parseBody(req, 20000000);
      console.log(`[INGEST-DEBUG] content-type: ${req.headers['content-type']}, body length: ${(raw||'').length}, first 200 chars: ${(raw||'').slice(0,200)}`);
      let body;
      try { body = JSON.parse(raw || "{}"); } catch (e) { console.error(`[INGEST-DEBUG] JSON parse error: ${e.message}, raw starts with: ${(raw||'').slice(0,100)}`); return json(res, 400, { ok: false, error: "invalid_json" }); }'''

if old not in content:
    # Also try to add debug to /v1/chat endpoint
    old_chat = '''      const raw = await parseBody(req);
      let body; try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }'''

    new_chat = '''      const raw = await parseBody(req);
      console.log(`[CHAT-DEBUG] content-type: ${req.headers['content-type']}, body length: ${(raw||'').length}, first 200 chars: ${(raw||'').slice(0,200)}`);
      let body; try { body = JSON.parse(raw || "{}"); } catch (e) { console.error(`[CHAT-DEBUG] JSON parse error: ${e.message}, raw starts with: ${(raw||'').slice(0,100)}`); return json(res, 400, { ok: false, error: "invalid_json" }); }'''

    if old_chat in content:
        content = content.replace(old_chat, new_chat)
        print("OK - debug logging added to /v1/chat")
    else:
        print("ERROR: could not find target strings in server.js")
        sys.exit(1)
else:
    content = content.replace(old, new)
    print("OK - debug logging added to /v1/ingest")

# Also add debug to /v1/chat if not already done
old_chat = '''      const raw = await parseBody(req);
      let body; try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }'''

new_chat = '''      const raw = await parseBody(req);
      if (req.headers['content-type'] && !req.headers['content-type'].includes('application/json')) { console.log(`[CHAT-DEBUG] non-JSON content-type: ${req.headers['content-type']}, body length: ${(raw||'').length}`); }
      let body; try { body = JSON.parse(raw || "{}"); } catch (e) { console.error(`[CHAT-DEBUG] JSON parse error: ${e.message}, content-type: ${req.headers['content-type']}, body first 200: ${(raw||'').slice(0,200)}`); return json(res, 400, { ok: false, error: "invalid_json" }); }'''

if old_chat in content:
    content = content.replace(old_chat, new_chat, 1)
    print("OK - debug logging added to /v1/chat too")

with open(path, "w") as f:
    f.write(content)
