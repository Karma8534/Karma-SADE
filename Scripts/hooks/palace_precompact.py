"""palace_precompact.py — retention compaction hook for observations.

Runs on SessionEnd/Stop to keep hall_events bounded.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path.home() / ".claude-mem" / "claude-mem.db"
KEEP_EVENTS = int(os.environ.get("NEXUS_KEEP_HALL_EVENTS", "7000"))


def _permission_ok() -> tuple[bool, str]:
    try:
        from Scripts.permission_engine import PermissionEngine
        eng = PermissionEngine()
        check = eng.check("Write", {"path": str(DB_PATH)})
        return bool(check.get("allowed")), str(check.get("reason", "permission engine denied"))
    except Exception as e:
        return False, f"permission engine unavailable: {e}"


def handle(context: dict) -> dict:
    allowed, reason = _permission_ok()
    if not allowed:
        return {"permissionDecision": "deny", "systemMessage": f"precompact blocked: {reason}"}
    if not DB_PATH.exists():
        return {}
    deleted = 0
    try:
        conn = sqlite3.connect(DB_PATH, timeout=8)
        cur = conn.execute(
            "SELECT id FROM observations WHERE hall='hall_events' ORDER BY created_at_epoch DESC LIMIT -1 OFFSET ?",
            (KEEP_EVENTS,),
        )
        ids = [row[0] for row in cur.fetchall()]
        if ids:
            placeholders = ",".join("?" for _ in ids)
            conn.execute(f"DELETE FROM observations WHERE id IN ({placeholders})", ids)
            deleted = len(ids)
            conn.commit()
        conn.close()
    except Exception as e:
        return {"permissionDecision": "deny", "systemMessage": f"precompact error: {e}"}
    if deleted:
        return {"systemMessage": f"precompact removed {deleted} hall_events rows"}
    return {}


if __name__ == "__main__":
    ctx = {}
    try:
        raw = sys.stdin.read().strip()
        if raw:
            ctx = json.loads(raw)
    except Exception:
        ctx = {}
    print(json.dumps(handle(ctx)))

