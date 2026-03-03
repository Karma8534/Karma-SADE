"""
Step 2.4: Staleness Cron (Decision #5)
Weekly scan: flag last_accessed > 90 days, archive > 180 days.
Exceptions: identity + decision categories NEVER go stale. Pinned cells NEVER go stale.

Designed to run as: python staleness.py
Or called from server.py via run_staleness_scan().
"""

import sqlite3
import os
import json
from datetime import datetime, timezone

DB_PATH = os.getenv("MEMORY_DB_PATH", "/opt/seed-vault/memory_v1/memory.db")
LEDGER_DIR = os.getenv("LEDGER_DIR", "/opt/seed-vault/memory_v1/ledger")
STALENESS_LOG = os.path.join(LEDGER_DIR, "staleness_log.jsonl")

# Thresholds in seconds
DAYS_90 = 90 * 86400
DAYS_180 = 180 * 86400

# Categories exempt from staleness
EXEMPT_CATEGORIES = {"identity", "decision"}


def run_staleness_scan() -> dict:
    """
    Scan all non-archived mem_cells.
    - Flag cells with last_accessed > 90 days ago as 'stale'
    - Archive cells with last_accessed > 180 days ago
    - Skip: pinned=1, category in {identity, decision}

    Returns: {flagged: int, archived: int, exempt: int, scanned: int}
    """
    now = datetime.now(timezone.utc).timestamp()
    cutoff_90 = now - DAYS_90
    cutoff_180 = now - DAYS_180

    db = sqlite3.connect(DB_PATH)
    try:
        cells = db.execute("""
            SELECT id, cell_type, pinned, last_accessed, content
            FROM mem_cells WHERE archived=0
        """).fetchall()

        flagged = 0
        archived = 0
        exempt = 0
        scanned = len(cells)
        report_entries = []

        for cell_id, cell_type, pinned, last_accessed, content in cells:
            # Exempt checks
            if pinned:
                exempt += 1
                continue
            if cell_type in EXEMPT_CATEGORIES:
                exempt += 1
                continue

            if last_accessed < cutoff_180:
                # Archive: >180 days stale
                db.execute(
                    "UPDATE mem_cells SET archived=1 WHERE id=?", (cell_id,)
                )
                archived += 1
                report_entries.append({
                    "action": "archived",
                    "id": cell_id,
                    "cell_type": cell_type,
                    "days_stale": round((now - last_accessed) / 86400, 1),
                    "preview": content[:80] if content else "",
                })
            elif last_accessed < cutoff_90:
                # Flag as stale (soft warning)
                flagged += 1
                report_entries.append({
                    "action": "flagged_stale",
                    "id": cell_id,
                    "cell_type": cell_type,
                    "days_stale": round((now - last_accessed) / 86400, 1),
                    "preview": content[:80] if content else "",
                })

        db.commit()

        # Write staleness report
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scanned": scanned,
            "flagged": flagged,
            "archived": archived,
            "exempt": exempt,
            "entries": report_entries,
        }
        try:
            os.makedirs(os.path.dirname(STALENESS_LOG), exist_ok=True)
            with open(STALENESS_LOG, "a") as f:
                f.write(json.dumps(report) + "\n")
        except Exception as e:
            print(f"[STALENESS] Log write failed: {e}")

        return {
            "scanned": scanned,
            "flagged": flagged,
            "archived": archived,
            "exempt": exempt,
        }

    finally:
        db.close()


if __name__ == "__main__":
    result = run_staleness_scan()
    print(f"[STALENESS] Scan complete: {json.dumps(result)}")
