#!/usr/bin/env python3
"""arknexus-drift-logger.py — Stop hook.

Fires at end of every CC turn. If focus-lock engaged and the turn
made no progress on active phase (no writes to allowed paths, no
evidence file created/modified), log a drift event.

Accumulated drift events = signal Sovereign can audit.
Non-blocking.
"""
from __future__ import annotations
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parent.parent.parent
LOCK = Path(__file__).resolve().parent / ".arknexus-focus-lock.json"
DRIFT_LOG = Path(__file__).resolve().parent / ".arknexus-drift.log"
TURN_STATE = Path(__file__).resolve().parent / ".arknexus-turn-state.json"


def load_lock() -> dict | None:
    if not LOCK.exists():
        return None
    try:
        return json.loads(LOCK.read_text(encoding="utf-8"))
    except Exception:
        return None


def recent_phase_progress(lock: dict, window_seconds: int = 900) -> bool:
    """Check if any allowed-path file was modified in the last N seconds."""
    cutoff = datetime.utcnow().timestamp() - window_seconds
    allowed = lock.get("allowed_paths", [])
    for prefix in allowed:
        target = ROOT / prefix
        if target.is_file():
            if target.stat().st_mtime > cutoff:
                return True
        elif target.is_dir():
            for p in target.rglob("*"):
                if p.is_file() and p.stat().st_mtime > cutoff:
                    return True
        else:
            # prefix pattern — glob
            parent = (ROOT / prefix).parent
            pattern = (ROOT / prefix).name + "*"
            if parent.exists():
                for p in parent.glob(pattern):
                    if p.is_file() and p.stat().st_mtime > cutoff:
                        return True
    return False


def log_event(lock: dict, progress: bool) -> None:
    try:
        entry = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "phase": lock.get("phase"),
            "task": lock.get("task", ""),
            "progress": progress,
            "mode": lock.get("mode", "soft"),
        }
        line = f"{entry['ts']}  phase={entry['phase']}  progress={progress}  task={entry['task']}\n"
        with DRIFT_LOG.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def main() -> int:
    lock = load_lock()
    if not lock:
        return 0
    try:
        progress = recent_phase_progress(lock)
        log_event(lock, progress)
    except Exception as e:
        print(f"[drift-logger] non-fatal: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
