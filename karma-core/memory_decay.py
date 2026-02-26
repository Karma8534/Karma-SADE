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
        falkor = get_falkor_fn()
        if falkor is None:
            return {"status": "skipped", "reason": "FalkorDB not available"}

        # Find episodes that haven't been retrieved recently
        # FalkorDB uses Cypher — query for Episodic nodes with last_retrieved_at
        # If last_retrieved_at doesn't exist, use created_at as baseline
        cutoff_days = 7  # Start decaying after 7 days unretrieved
        decay_rate = config.MEMORY_DECAY_RATE
        decay_floor = config.MEMORY_DECAY_FLOOR

        # Query: find all Episodic nodes, check their age
        # Note: FalkorDB graph name comes from config.GRAPHITI_GROUP_ID
        graph_name = config.GRAPHITI_GROUP_ID
        result = falkor.graph(graph_name).query(
            """
            MATCH (e:Episodic)
            WHERE e.created_at IS NOT NULL
            RETURN e.uuid AS uuid,
                   e.name AS name,
                   e.created_at AS created_at,
                   COALESCE(e.confidence, 1.0) AS confidence,
                   COALESCE(e.last_retrieved_at, e.created_at) AS last_accessed
            """
        )

        decayed_count = 0
        total_checked = 0
        now = datetime.now(timezone.utc)

        for record in result.result_set:
            total_checked += 1
            uuid = record[0]
            confidence = float(record[3])
            last_accessed_str = str(record[4])

            # Parse last access time
            try:
                last_accessed = datetime.fromisoformat(last_accessed_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                continue  # Skip unparseable dates

            days_since_access = (now - last_accessed).days
            if days_since_access < cutoff_days:
                continue  # Recently accessed, skip

            # Apply decay: confidence -= decay_rate * (days_over_cutoff / cutoff_days)
            days_over = days_since_access - cutoff_days
            decay_amount = decay_rate * (days_over / cutoff_days)
            new_confidence = max(decay_floor, confidence - decay_amount)

            if new_confidence < confidence:
                # Update in graph
                falkor.graph(graph_name).query(
                    """
                    MATCH (e:Episodic {uuid: $uuid})
                    SET e.confidence = $new_confidence,
                        e.last_decayed_at = $now
                    """,
                    params={
                        "uuid": uuid,
                        "new_confidence": round(new_confidence, 4),
                        "now": now.isoformat(),
                    }
                )
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
