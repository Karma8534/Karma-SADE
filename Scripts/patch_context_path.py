#!/usr/bin/env python3
"""Fix /v1/context endpoint: use container path for ledger."""

SERVER_JS = "/opt/seed-vault/memory_v1/hub_bridge/app/server.js"

OLD = '      const LEDGER_PATH = "/opt/seed-vault/memory_v1/ledger/memory.jsonl";'
NEW = '      const LEDGER_PATH = "/karma/ledger/memory.jsonl";'

with open(SERVER_JS, "r") as f:
    content = f.read()

if OLD not in content:
    print("ERROR: Could not find the line to patch")
    raise SystemExit(1)

patched = content.replace(OLD, NEW)

with open(SERVER_JS, "w") as f:
    f.write(patched)

print("OK: Fixed ledger path to container mount /karma/ledger/memory.jsonl")
