#!/usr/bin/env python3
"""PreToolUse hook: BLOCK EnterWorktree calls.
Worktrees fragment state across sessions. All work must happen on main.
PITFALL #11813 (2026-03-25): 6 worktrees caused 5 sessions of invisible commits.
"""
import json, sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_name = data.get("tool_name", "")
if tool_name == "EnterWorktree":
    print("BLOCKED: EnterWorktree is permanently disabled for Karma SADE.", file=sys.stderr)
    print("All work must happen on main branch. See PITFALL #11813.", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
