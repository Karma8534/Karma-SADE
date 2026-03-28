#!/usr/bin/env python3
"""
Task 7-6: File Restriction Enforcement.
PreToolUse hook for Write/Edit — checks file paths against restriction patterns.
KO/KFH doctrine: Codex skills cannot write k2/aria/*.py, etc.

Reads restrictions from .claude/file-restrictions.json:
{
  "restrictions": [
    { "pattern": "k2/aria/*.py", "reason": "K2 agent code is CC-only", "allow": ["cc"] },
    { "pattern": "Memory/00-*.md", "reason": "System prompt is Sovereign-only", "allow": ["colby"] }
  ]
}
"""
import json
import sys
import os
import fnmatch

def main():
    hook_input = json.loads(sys.stdin.read())
    tool_name = hook_input.get("tool_name", "")

    # Only gate Write and Edit tools
    if tool_name not in ("Write", "Edit"):
        print(json.dumps({"decision": "approve"}))
        return

    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path:
        print(json.dumps({"decision": "approve"}))
        return

    # Normalize path
    file_path = file_path.replace("\\", "/")

    # Load restrictions
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    restrictions_file = os.path.join(project_dir, ".claude", "file-restrictions.json")

    try:
        with open(restrictions_file, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # No restrictions file = no restrictions
        print(json.dumps({"decision": "approve"}))
        return

    # Current agent is always CC (this hook runs in Claude Code context)
    current_agent = "cc"

    for rule in config.get("restrictions", []):
        pattern = rule.get("pattern", "")
        allowed = rule.get("allow", [])
        reason = rule.get("reason", "restricted")

        # Check if file_path matches the restriction pattern
        if fnmatch.fnmatch(file_path, f"*{pattern}") or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            if current_agent not in allowed:
                print(json.dumps({
                    "decision": "block",
                    "reason": f"FILE RESTRICTION: {reason} (pattern: {pattern}, allowed: {allowed})"
                }))
                return

    print(json.dumps({"decision": "approve"}))

if __name__ == "__main__":
    main()
