"""
Step 3.3: Session-Start Briefing (Option C — Tiered Consciousness)
OBSERVE ran while Colby was away. Now Karma reasons WITH Colby's context.

Generates a plain-text briefing from observations accumulated since last session.
No LLM call — pure data aggregation.
"""

import sqlite3
import os
from datetime import datetime, timezone
from collections import Counter

DB_PATH = os.getenv("MEMORY_DB_PATH", "/opt/seed-vault/memory_v1/memory.db")


def generate_session_briefing() -> str:
    """
    Option C: Tiered consciousness briefing.
    Aggregates observations since last session into a human-readable summary.
    Zero LLM cost — pure data.
    """
    db = sqlite3.connect(DB_PATH)
    try:
        # Find last session end time
        last_session = db.execute(
            "SELECT ended_at FROM sessions ORDER BY ended_at DESC LIMIT 1"
        ).fetchone()
        since = last_session[0] if last_session else 0

        observations = db.execute("""
            SELECT event_type, description, outcome, observed_at
            FROM observations
            WHERE observed_at > ? AND reflected = 0
            ORDER BY observed_at
        """, (since,)).fetchall()

        if not observations:
            return "No significant changes since your last session."

        # Categorize observations
        by_type = Counter()
        alerts = []
        episode_count = 0
        entity_changes = []
        tool_uses = []
        other = []

        for event_type, description, outcome, obs_at in observations:
            by_type[event_type] += 1

            if event_type == "episode_delta":
                # Try to extract count from description
                try:
                    parts = description.split(":")
                    if len(parts) > 1:
                        num = int("".join(c for c in parts[1].split()[0] if c.isdigit()) or "0")
                        episode_count += num
                except (ValueError, IndexError):
                    episode_count += 1
            elif event_type == "entity_delta":
                entity_changes.append(description[:100])
            elif event_type == "alert":
                alerts.append(description[:150])
            elif event_type.startswith("tool_"):
                tool_uses.append(f"{event_type}: {description[:80]}")
            else:
                other.append(f"{event_type}: {description[:80]}")

        # Build briefing
        lines = ["Since your last session:"]

        if episode_count > 0:
            lines.append(f"- {episode_count} new episodes captured in the knowledge graph")

        if entity_changes:
            lines.append(f"- {len(entity_changes)} entity changes detected:")
            for ec in entity_changes[:5]:  # Cap at 5 for brevity
                lines.append(f"  - {ec}")
            if len(entity_changes) > 5:
                lines.append(f"  - ...and {len(entity_changes) - 5} more")

        if alerts:
            lines.append(f"- {len(alerts)} alerts:")
            for a in alerts:
                lines.append(f"  ⚠ {a}")

        if tool_uses:
            lines.append(f"- {len(tool_uses)} tool executions logged")

        if other:
            lines.append(f"- {len(other)} other observations")

        # Overall stats
        total_obs = len(observations)
        first_ts = observations[0][3]
        last_ts = observations[-1][3]
        span_hours = (last_ts - first_ts) / 3600 if last_ts > first_ts else 0

        lines.append(f"")
        lines.append(f"Total: {total_obs} observations over {span_hours:.1f} hours")

        # Memory stats
        try:
            mem_count = db.execute(
                "SELECT COUNT(*) FROM mem_cells WHERE archived=0"
            ).fetchone()[0]
            lines.append(f"Active memory cells: {mem_count}")
        except Exception:
            pass

        return "\n".join(lines)

    finally:
        db.close()


def get_briefing_data() -> dict:
    """Return structured briefing data (for API responses)."""
    db = sqlite3.connect(DB_PATH)
    try:
        last_session = db.execute(
            "SELECT session_id, ended_at FROM sessions ORDER BY ended_at DESC LIMIT 1"
        ).fetchone()

        obs_count = db.execute(
            "SELECT COUNT(*) FROM observations WHERE reflected=0"
        ).fetchone()[0]

        mem_count = db.execute(
            "SELECT COUNT(*) FROM mem_cells WHERE archived=0"
        ).fetchone()[0]

        return {
            "last_session_id": last_session[0] if last_session else None,
            "last_session_ended": last_session[1] if last_session else None,
            "pending_observations": obs_count,
            "active_memory_cells": mem_count,
            "briefing_text": generate_session_briefing(),
        }
    finally:
        db.close()
