#!/usr/bin/env python3
"""
Post-Tool Failure Logger — PostToolUseFailure hook (Layer 3: Feedback Loops)

Auto-captures every tool failure to Logs/cc_tool_failures.log.
Non-blocking: always exits 0. Never interferes with Claude Code.

Philosophy from 3LayerHarness.PDF:
  "Every production incident involving AI-assisted code is a harness improvement
  opportunity. What rule would have caught this? Post-mortem the harness, not just the code."

Each logged failure is raw material for a new PITFALL entry in cc-scope-index.md.

JSON stdin: {tool_name, tool_input, tool_response, error, hook_event_name, session_id, cwd}
"""
import json, sys, os
from pathlib import Path
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "unknown")
    tool_input = data.get("tool_input", {})
    tool_response = data.get("tool_response", {})
    error = data.get("error", "")

    # Extract best available error description
    error_text = (
        error
        or (tool_response.get("stderr", "") if isinstance(tool_response, dict) else "")
        or (str(tool_response)[:200] if tool_response else "unknown error")
    )

    cwd = data.get("cwd", os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    log_dir = Path(cwd) / "Logs"
    log_file = log_dir / "cc_tool_failures.log"

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        sys.exit(0)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build compact command/path snippet for context
    context_snippet = ""
    if tool_name == "Bash":
        cmd = str(tool_input.get("command", ""))[:150]
        context_snippet = f" cmd={repr(cmd)}"
    elif tool_name in ("Edit", "Write", "Read"):
        fp = tool_input.get("file_path", tool_input.get("path", ""))[:80]
        context_snippet = f" file={fp}"

    error_short = str(error_text).strip().replace('\n', ' ')[:250]
    entry = f"[{ts}] FAIL tool={tool_name}{context_snippet} | {error_short}\n"

    try:
        with open(log_file, 'a', encoding='utf-8', errors='replace') as f:
            f.write(entry)
    except Exception:
        pass  # Non-blocking — failure to log is not fatal

    # Always exit 0 — this is observability, not enforcement
    sys.exit(0)


if __name__ == "__main__":
    main()
