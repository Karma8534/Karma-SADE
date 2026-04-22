#!/usr/bin/env python3
"""arknexus-focus-gate.py — PreToolUse hook.

When a focus lock is engaged on an active ArkNexus phase, block
Write/Edit/NotebookEdit tool calls that touch paths outside the
phase's allowed_paths list.

Lock modes:
    soft   => warn on stderr (exit 0, tool still runs)
    strict => hard block (exit 2, tool rejected)

Hook input (stdin JSON):
    {"tool_name": "Write", "tool_input": {"file_path": "..."} }

Exit codes:
    0 => allow
    2 => block (strict mode only)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent.parent
LOCK = Path(__file__).resolve().parent / ".arknexus-focus-lock.json"
DRIFT_LOG = Path(__file__).resolve().parent / ".arknexus-drift.log"

BLOCKING_TOOLS = {"Write", "Edit", "NotebookEdit"}


def load_lock() -> dict | None:
    if not LOCK.exists():
        return None
    try:
        return json.loads(LOCK.read_text(encoding="utf-8"))
    except Exception:
        return None


def path_in_scope(target: str, allowed: list[str]) -> bool:
    norm = target.replace("\\", "/")
    root_str = str(ROOT).replace("\\", "/")
    if norm.startswith(root_str):
        rel = norm[len(root_str):].lstrip("/")
    else:
        rel = norm
    for prefix in allowed:
        p = prefix.replace("\\", "/")
        if rel.startswith(p) or p in rel:
            return True
    return False


def extract_target(tool_name: str, tool_input: dict) -> str:
    return (
        tool_input.get("file_path")
        or tool_input.get("path")
        or tool_input.get("notebook_path")
        or ""
    )


def log_drift(phase: int, tool: str, target: str, mode: str, blocked: bool) -> None:
    try:
        entry = (
            f"{datetime.utcnow().isoformat()}Z  phase={phase}  mode={mode}  "
            f"blocked={blocked}  tool={tool}  target={target}\n"
        )
        with DRIFT_LOG.open("a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


def main() -> int:
    lock = load_lock()
    if not lock:
        return 0

    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return 0

    tool_name = payload.get("tool_name") or payload.get("tool") or ""
    tool_input = payload.get("tool_input") or payload.get("input") or {}

    if tool_name not in BLOCKING_TOOLS:
        return 0

    target = extract_target(tool_name, tool_input)
    if not target:
        return 0

    allowed = lock.get("allowed_paths", [])
    if path_in_scope(target, allowed):
        return 0

    phase = lock.get("phase", "?")
    name = lock.get("name", "?")
    mode = lock.get("mode", "soft")
    task = lock.get("task", "")

    log_drift(phase, tool_name, target, mode, mode == "strict")

    msg_lines = [
        "=" * 66,
        f"ARKNEXUS FOCUS GATE — Phase {phase} ({name}) LOCKED",
        "=" * 66,
        f"  Tool:       {tool_name}",
        f"  Target:     {target}",
        f"  Mode:       {mode}",
    ]
    if task:
        msg_lines.append(f"  Active task: {task}")
    msg_lines += [
        f"  Allowed:    {allowed}",
        "",
        "  This write falls OUTSIDE the active phase scope.",
        "  To proceed:",
        "    - complete the write within scope, OR",
        "    - `python .claude/hooks/arknexus-focus.py unlock` (Sovereign authority), OR",
        "    - `python .claude/hooks/arknexus-focus.py soft` to downgrade to warn-only",
        "=" * 66,
    ]
    message = "\n".join(msg_lines)

    if mode == "strict":
        print(message, file=sys.stderr)
        return 2
    else:
        print(f"[focus-gate WARN] {tool_name} -> {target} outside Phase {phase} scope", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
