#!/usr/bin/env python3
"""
Locked Invariant Guard — PreToolUse hook (CCTrustVerify P3-D)
Blocks Edit/Write to governance-critical files without SOVEREIGN_APPROVED=1.
Exit code 2 = HARD BLOCK. This is not a suggestion.

JSON stdin: {tool_name, tool_input.file_path, hook_event_name, session_id, cwd}
"""
import json, sys, os
# Force UTF-8 stdout/stderr to handle all chars on Windows cp1252 consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


LOCKED_PATTERNS = [
    "karma_contract_policy",   # SovereignPeer policy v1.1
    "vesper_governor",         # Contains SAFE_EXEC_WHITELIST constant
    "SAFE_EXEC_WHITELIST",     # Shouldn't appear standalone but just in case
]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Edit", "Write", "NotebookEdit"):
        sys.exit(0)

    file_path = (tool_input.get("file_path") or tool_input.get("path") or "")

    for pattern in LOCKED_PATTERNS:
        if pattern in file_path:
            if os.environ.get("SOVEREIGN_APPROVED") == "1":
                print(f"[INVARIANT GUARD] Sovereign-approved edit: {file_path}", file=sys.stderr)
                sys.exit(0)
            print(f"\n{'='*60}")
            print(f"🔒  LOCKED INVARIANT GUARD — HARD BLOCK")
            print(f"{'='*60}")
            print(f"  File: {file_path}")
            print(f"  Matched pattern: '{pattern}'")
            print(f"")
            print(f"  This file is a Locked Invariant per Karma2/PLAN.md §Locked Invariants.")
            print(f"  Self-improvement pipeline CANNOT modify it.")
            print(f"  Structural changes require:")
            print(f"    1. Explicit Sovereign (Colby) approval in chat FIRST")
            print(f"    2. Set SOVEREIGN_APPROVED=1 in this session's environment")
            print(f"    3. Then retry the edit")
            print(f"")
            print(f"  (CCTrustVerify P3-D hook — exit 2 = hard block)")
            print(f"{'='*60}")
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
