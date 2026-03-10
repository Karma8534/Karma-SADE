#!/usr/bin/env python3
"""Ingest files to hub.arknexus.net /v1/ingest endpoint."""
import base64, json, subprocess, sys, os

TOKEN_PATH = "/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt"
HUB = "https://hub.arknexus.net"

with open(TOKEN_PATH) as f:
    token = f.read().strip()

files = [
    ("/tmp/LocalAIFortress.PDF", "LocalAIFortress.PDF",
     "LocalAIFortress: self-hosted AI deployment patterns, security boundaries, local model routing"),
    ("/tmp/CCintoanOS.txt", "CCintoanOS.txt",
     "CCintoanOS: Claude Code OS architecture, confidence levels, anti-hallucination patterns, Context7 MCP, PostToolUseFailure hooks"),
    ("/tmp/PiMonoCoder.PDF", "PiMonoCoder.PDF",
     "PiMonoCoder: pi-mono 4-tool coding philosophy, self-as-subagent, minimal system prompt discipline"),
]

for filepath, filename, hint in files:
    if not os.path.exists(filepath):
        print(f"{filename} -> SKIP (not found)")
        continue
    print(f"{filename} -> ", end="", flush=True)
    with open(filepath, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    payload = {"file_b64": b64, "filename": filename, "hint": hint}
    payload_path = "/tmp/_ingest_payload.json"
    with open(payload_path, "w") as f:
        json.dump(payload, f)
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", f"{HUB}/v1/ingest",
         "-H", f"Authorization: Bearer {token}",
         "-H", "Content-Type: application/json",
         "-d", f"@{payload_path}"],
        capture_output=True, text=True
    )
    try:
        d = json.loads(result.stdout)
        if d.get("ok"):
            print("ok")
        else:
            print(f"ERROR: {d}")
    except Exception:
        print(f"RAW: {result.stdout[:200]}")
