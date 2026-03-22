#!/usr/bin/env python3
"""ArchonAgent bus poster — reads /tmp/archon_payload.json, posts to coordination bus."""
import json, urllib.request, sys, os

payload_path = "/tmp/archon_payload.json"
try:
    d = json.load(open(payload_path, encoding="utf-8-sig"))
    tok = d.pop("token")
    payload = json.dumps(d).encode()
    req = urllib.request.Request(
        "https://hub.arknexus.net/v1/coordination/post",
        data=payload,
        headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read())
        print("ok:", res.get("ok"), "id:", str(res.get("id", ""))[:30])
except Exception as e:
    print("ERROR:", e, file=sys.stderr)
    sys.exit(1)
finally:
    try: os.remove(payload_path)
    except: pass
