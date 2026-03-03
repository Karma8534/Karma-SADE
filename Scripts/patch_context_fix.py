#!/usr/bin/env python3
"""Fix /v1/context endpoint: skip entries with no captured_at instead of breaking."""

SERVER_JS = "/opt/seed-vault/memory_v1/hub_bridge/app/server.js"

OLD = '            if (capturedAt < cutoff) break; // Past the time window, stop'
NEW = '            if (!capturedAt) continue; // Skip entries without timestamp\n            if (capturedAt < cutoff) break; // Past the time window, stop'

with open(SERVER_JS, "r") as f:
    content = f.read()

if OLD not in content:
    print("ERROR: Could not find the line to patch")
    raise SystemExit(1)

patched = content.replace(OLD, NEW)

with open(SERVER_JS, "w") as f:
    f.write(patched)

print("OK: Fixed capturedAt empty-string break bug")
