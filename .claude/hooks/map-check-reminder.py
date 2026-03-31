#!/usr/bin/env python3
"""
PreToolUse hook for Grep — reminds CC to check canonical maps before searching.

Fires on every Grep call. Returns a short reminder that gets injected into CC's context.
Does NOT block the tool call — just adds context CC cannot ignore.

P112 enforcement: CC has repeatedly grep-hunted for files instead of reading
data-map.md and file-structure.md first. This hook makes that impossible to forget.
"""
import json
import sys

def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        return

    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Only fire on Grep (the primary search tool CC uses to hunt for files)
    if tool != "Grep":
        return

    pattern = tool_input.get("pattern", "")
    path = tool_input.get("path", "")

    # If searching within a known file (not hunting), skip
    if path and ("/" in path or "\\" in path) and not path.endswith("/"):
        return  # Searching within a specific file — not a hunt

    # Inject reminder
    print(json.dumps({
        "message": (
            "MAP CHECK: Before grep-hunting, did you check "
            "Karma2/map/file-structure.md and .claude/rules/data-map.md? "
            "These are the canonical indexes of every file path in the system."
        )
    }))


if __name__ == "__main__":
    main()
