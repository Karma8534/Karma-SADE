"""
Step 2.3: Append-Only Observation Block (P3)
Builds a stable prefix of observations for prompt cache hits.
Format: dated event-log entries (event_type + description + outcome).
Stable across turns within a session → 4-10x cost reduction via prompt caching.

The observation block is APPEND-ONLY within a session.
New observations are added at the end; existing entries never change.
This makes the prefix identical across consecutive turns → cache hit.
"""

import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.getenv("MEMORY_DB_PATH", "/opt/seed-vault/memory_v1/memory.db")

# Cache the block within process lifetime to guarantee stability
_CACHED_BLOCK = None
_CACHED_SESSION_ID = None
_CACHED_OBS_COUNT = 0


def build_observation_block(session_id: str = None, max_observations: int = 50) -> str:
    """
    Build a stable, append-only observation block for prompt injection.

    Returns a formatted text block like:
    --- OBSERVATIONS (since last session) ---
    [2026-02-27T14:30:00Z] entity_delta: New entity 'FalkorDB' detected → added to graph
    [2026-02-27T14:31:00Z] episode_delta: 3 new episodes since last check → processed
    ...
    --- END OBSERVATIONS ---

    The block is cached per session_id. New observations are APPENDED only.
    """
    global _CACHED_BLOCK, _CACHED_SESSION_ID, _CACHED_OBS_COUNT

    db = sqlite3.connect(DB_PATH)
    try:
        # Determine the cutoff: observations since last session end
        since = 0
        if session_id:
            row = db.execute(
                "SELECT ended_at FROM sessions WHERE session_id=? ORDER BY ended_at DESC LIMIT 1",
                (session_id,)
            ).fetchone()
            if row and row[0]:
                since = row[0]
        else:
            # Use most recent session
            row = db.execute(
                "SELECT ended_at FROM sessions ORDER BY ended_at DESC LIMIT 1"
            ).fetchone()
            if row and row[0]:
                since = row[0]

        observations = db.execute("""
            SELECT observed_at, event_type, description, outcome
            FROM observations
            WHERE observed_at > ?
            ORDER BY observed_at ASC
            LIMIT ?
        """, (since, max_observations)).fetchall()

        if not observations:
            return ""

        current_count = len(observations)

        # Check if we can use cached version (append-only guarantee)
        if (_CACHED_BLOCK and _CACHED_SESSION_ID == session_id
                and current_count >= _CACHED_OBS_COUNT):
            # Only rebuild if new observations appeared
            if current_count == _CACHED_OBS_COUNT:
                return _CACHED_BLOCK

        # Build the block
        lines = ["--- OBSERVATIONS (since last session) ---"]
        for obs_at, event_type, description, outcome in observations:
            ts = datetime.fromtimestamp(obs_at, tz=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ) if isinstance(obs_at, (int, float)) else str(obs_at)

            line = f"[{ts}] {event_type}: {description}"
            if outcome:
                line += f" → {outcome}"
            lines.append(line)
        lines.append("--- END OBSERVATIONS ---")

        block = "\n".join(lines)

        # Cache it
        _CACHED_BLOCK = block
        _CACHED_SESSION_ID = session_id
        _CACHED_OBS_COUNT = current_count

        return block

    finally:
        db.close()


def reset_observation_cache():
    """Reset cache when session changes."""
    global _CACHED_BLOCK, _CACHED_SESSION_ID, _CACHED_OBS_COUNT
    _CACHED_BLOCK = None
    _CACHED_SESSION_ID = None
    _CACHED_OBS_COUNT = 0


def get_observation_stats() -> dict:
    """Return stats about the current observation block."""
    db = sqlite3.connect(DB_PATH)
    try:
        total = db.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        unreflected = db.execute(
            "SELECT COUNT(*) FROM observations WHERE reflected=0"
        ).fetchone()[0]
        return {
            "total_observations": total,
            "unreflected": unreflected,
            "cache_active": _CACHED_BLOCK is not None,
            "cached_count": _CACHED_OBS_COUNT,
        }
    finally:
        db.close()
