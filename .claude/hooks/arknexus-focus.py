#!/usr/bin/env python3
"""arknexus-focus.py — CLI for phase focus lock.

Usage:
    python arknexus-focus.py lock <phase>  [--task "desc"]
    python arknexus-focus.py unlock
    python arknexus-focus.py status
    python arknexus-focus.py strict          (hard-block mode)
    python arknexus-focus.py soft            (warn-only)

Lock file: .claude/hooks/.arknexus-focus-lock.json

Engaged lock => PreToolUse gate blocks Write/Edit outside phase scope.
"""
from __future__ import annotations
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOCK = Path(__file__).resolve().parent / ".arknexus-focus-lock.json"

PHASE_SCOPES = {
    1: {
        "name": "Persona-on-Boot",
        "allowed_paths": [
            "Dashboard/",
            "frontend/src/store/karma.ts",
            "frontend/src/app/page.tsx",
            "nexus-tauri/",
            "Scripts/phase1-",
            "evidence/phase1-",
            ".gsd/phase-ascendance-1-",
            "MEMORY.md",
            "cc_scratchpad.md",
        ],
        "expected_evidence": [
            "evidence/phase1-first-frame.png",
            "evidence/phase1-timing.json",
            "evidence/phase1-history-diff.txt",
            "evidence/phase1-canonical-trace.txt",
        ],
    },
    2: {
        "name": "Cross-Surface Parity",
        "allowed_paths": [
            "Dashboard/",
            "nexus-tauri/",
            "hub-bridge/",
            "Scripts/cc_server_p1.py",
            "evidence/phase2-",
            ".gsd/phase-ascendance-2-",
            "MEMORY.md",
            "cc_scratchpad.md",
        ],
        "expected_evidence": [
            "evidence/phase2-parity.png",
            "evidence/phase2-roundtrip.json",
            "evidence/phase2-session-equality.txt",
        ],
    },
    3: {
        "name": "TRUE FAMILY Enforcement",
        "allowed_paths": [
            "Dashboard/",
            "nexus-tauri/",
            "frontend/",
            "evidence/phase3-",
            ".gsd/phase-ascendance-3-",
            "MEMORY.md",
            "cc_scratchpad.md",
        ],
        "expected_evidence": [
            "evidence/phase3-agents-sections.png",
            "evidence/phase3-whoami.png",
            "evidence/phase3-family-grep.txt",
        ],
    },
}


def load_lock() -> dict | None:
    if LOCK.exists():
        try:
            return json.loads(LOCK.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def save_lock(data: dict) -> None:
    LOCK.write_text(json.dumps(data, indent=2), encoding="utf-8")


def clear_lock() -> None:
    if LOCK.exists():
        LOCK.unlink()


def cmd_lock(args: list[str]) -> int:
    if not args:
        print("Usage: lock <phase> [--task \"desc\"]", file=sys.stderr)
        return 2
    try:
        phase = int(args[0])
    except ValueError:
        print(f"Invalid phase: {args[0]}", file=sys.stderr)
        return 2
    if phase not in PHASE_SCOPES:
        print(f"Phase must be 1, 2, or 3 (got {phase})", file=sys.stderr)
        return 2
    task = ""
    if "--task" in args:
        idx = args.index("--task")
        if idx + 1 < len(args):
            task = args[idx + 1]

    prior = load_lock()
    mode = prior.get("mode", "soft") if prior else "soft"
    data = {
        "phase": phase,
        "name": PHASE_SCOPES[phase]["name"],
        "task": task,
        "mode": mode,
        "allowed_paths": PHASE_SCOPES[phase]["allowed_paths"],
        "expected_evidence": PHASE_SCOPES[phase]["expected_evidence"],
        "locked_at": datetime.utcnow().isoformat() + "Z",
    }
    save_lock(data)
    print(f"LOCKED Phase {phase} — {data['name']} (mode={mode})")
    if task:
        print(f"  task: {task}")
    print(f"  allowed paths: {data['allowed_paths']}")
    return 0


def cmd_unlock(args: list[str]) -> int:
    if not LOCK.exists():
        print("No lock engaged.")
        return 0
    prior = load_lock()
    clear_lock()
    print(f"UNLOCKED (was Phase {prior.get('phase', '?')} — {prior.get('name', '?')})")
    return 0


def cmd_status(args: list[str]) -> int:
    lock = load_lock()
    if not lock:
        print("No lock engaged. Focus-gate inactive.")
        return 0
    print(f"LOCKED Phase {lock['phase']} — {lock['name']}")
    print(f"  mode:        {lock.get('mode', 'soft')}")
    print(f"  task:        {lock.get('task', '(none)')}")
    print(f"  locked_at:   {lock.get('locked_at', '?')}")
    print(f"  allowed:     {lock['allowed_paths']}")
    print(f"  evidence:    {lock['expected_evidence']}")
    return 0


def cmd_strict(args: list[str]) -> int:
    lock = load_lock()
    if not lock:
        print("No lock engaged. Run `lock <phase>` first.", file=sys.stderr)
        return 2
    lock["mode"] = "strict"
    save_lock(lock)
    print(f"STRICT mode ON — writes outside phase scope will be HARD-BLOCKED (exit 2)")
    return 0


def cmd_soft(args: list[str]) -> int:
    lock = load_lock()
    if not lock:
        print("No lock engaged.", file=sys.stderr)
        return 2
    lock["mode"] = "soft"
    save_lock(lock)
    print(f"SOFT mode ON — writes outside phase scope will WARN only")
    return 0


COMMANDS = {
    "lock": cmd_lock,
    "unlock": cmd_unlock,
    "status": cmd_status,
    "strict": cmd_strict,
    "soft": cmd_soft,
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__, file=sys.stderr)
        return 2
    return COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
