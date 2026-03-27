#!/usr/bin/env python3
"""
memory-reminder.py — PostToolUse hook that reminds CC to update MEMORY.md
when code files are modified. Proactive reminder before pre-commit gate catches it.
"""
import json, sys, os

CODE_EXTENSIONS = {'.js', '.py', '.ts', '.jsx', '.tsx', '.sh', '.ps1', '.yml', '.yaml'}

def check():
    tool_name = os.environ.get("CLAUDE_TOOL_NAME", "")
    tool_input = os.environ.get("CLAUDE_TOOL_INPUT", "{}")

    if tool_name not in ("Write", "Edit"):
        return

    try:
        data = json.loads(tool_input)
    except Exception:
        return

    file_path = data.get("file_path", "")
    ext = os.path.splitext(file_path)[1].lower()

    if ext in CODE_EXTENSIONS and "MEMORY.md" not in file_path:
        # Just a reminder, don't block
        print(json.dumps({
            "message": f"Code file modified ({os.path.basename(file_path)}). Remember to update MEMORY.md before committing."
        }))

if __name__ == "__main__":
    check()
