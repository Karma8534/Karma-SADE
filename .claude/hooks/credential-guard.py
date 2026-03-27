#!/usr/bin/env python3
"""
credential-guard.py — PreToolUse hook that blocks reading credential files.
P060 prevention: credentials must never appear in chat output.
Reference files by path only.
"""
import json, sys, os, re

BLOCKED_PATTERNS = [
    r'\.gmail-cc-creds',
    r'mylocks1\.txt',
    r'api[_-]key\.txt',
    r'token\.txt',
    r'\.secrets/',
    r'hub\.chat\.token',
    r'hub\.capture\.token',
    r'openai\.api_key',
    r'anthropic.*key',
    r'\.env\.secrets',
    r'id_rsa',
    r'id_ed25519',
    r'\.pem$',
    r'\.key$',
]

def check():
    tool_input = os.environ.get("CLAUDE_TOOL_INPUT", "{}")
    tool_name = os.environ.get("CLAUDE_TOOL_NAME", "")

    try:
        data = json.loads(tool_input)
    except Exception:
        return

    # Check file paths in Read, Bash(cat/head/tail), file_path args
    paths_to_check = []

    if tool_name == "Read":
        paths_to_check.append(data.get("file_path", ""))
    elif tool_name == "Bash":
        cmd = data.get("command", "")
        # Check if command reads a sensitive file
        paths_to_check.append(cmd)
    elif tool_name in ("mcp__k2__file_read",):
        paths_to_check.append(data.get("path", ""))

    for path in paths_to_check:
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                result = {
                    "decision": "block",
                    "reason": f"P060: Credential file detected ({pattern}). Reference by path only — never display contents."
                }
                print(json.dumps(result))
                sys.exit(0)

if __name__ == "__main__":
    check()
