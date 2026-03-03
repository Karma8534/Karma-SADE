"""
Memory Decay — Decision #5
Time-decay: unretrieved memories lose confidence over time.
Runs daily as part of the consciousness cycle.
"""
import time
import traceback
from datetime import datetime, timezone, timedelta
import config


def run_decay(get_falkor_fn) -> dict:
    """Apply time-decay to unretrieved episodic memories in FalkorDB.
    Reduces confidence of episodes not retrieved in the last N days.
    Returns summary of what was decayed."""
    try:
        r = get_falkor_fn()
        if r is None:
            return {"status": "skipped", "reason": "FalkorDB not available"}

        cutoff_days = 7
        decay_rate = config.MEMORY_DECAY_RATE
        decay_floor = config.MEMORY_DECAY_FLOOR
        graph_name = config.GRAPHITI_GROUP_ID

        # Query all Episodic nodes with created_at
        query = (
            "MATCH (e:Episodic) "
            "WHERE e.created_at IS NOT NULL "
            "RETURN e.uuid, e.name, e.created_at, "
            "COALESCE(e.confidence, 1.0), "
            "COALESCE(e.last_retrieved_at, e.created_at)"
        )
        result = r.execute_command("GRAPH.QUERY", graph_name, query)

        decayed_count = 0
        total_checked = 0
        now = datetime.now(timezone.utc)

        # FalkorDB returns [header, [rows...], stats]
        if not isinstance(result, list) or len(result) < 2:
            return {"status": "completed", "total_checked": 0, "decayed": 0}

        rows = result[1] if isinstance(result[1], list) else []

        for record in rows:
            if not isinstance(record, list) or len(record) < 5:
                continue
            total_checked += 1
            uuid = str(record[0])
            confidence = float(record[3])
            last_accessed_str = str(record[4])

            try:
                last_accessed = datetime.fromisoformat(last_accessed_str.replace("Z", "+00:00"))
                # Ensure timezone-aware for comparison with now (UTC)
                if last_accessed.tzinfo is None:
                    last_accessed = last_accessed.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                continue

            days_since_access = (now - last_accessed).days
            if days_since_access < cutoff_days:
                continue

            days_over = days_since_access - cutoff_days
            decay_amount = decay_rate * (days_over / cutoff_days)
            new_confidence = max(decay_floor, confidence - decay_amount)

            if new_confidence < confidence:
                safe_uuid = uuid.replace("\\", "\\\\").replace('"', '\\"')
                update_q = (
                    f'MATCH (e:Episodic) WHERE e.uuid = "{safe_uuid}" '
                    f'SET e.confidence = {round(new_confidence, 4)}, '
                    f'e.last_decayed_at = "{now.isoformat()}" '
                    f'RETURN e.uuid'
                )
                r.execute_command("GRAPH.QUERY", graph_name, update_q)
                decayed_count += 1

        return {
            "status": "completed",
            "total_checked": total_checked,
            "decayed": decayed_count,
            "decay_rate": decay_rate,
            "decay_floor": decay_floor,
            "cutoff_days": cutoff_days,
            "timestamp": now.isoformat(),
        }
    except Exception as e:
        print(f"[MEMORY_DECAY] Error: {e}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}
