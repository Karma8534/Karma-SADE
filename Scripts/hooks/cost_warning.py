"""cost_warning.py — PostToolUse handler.
Tracks cumulative session cost, warns at $1/$5/$10 thresholds.
"""
import json, sys

# Session-scoped state (reset when cc_server restarts)
_session_cost = 0.0
_warned_thresholds = set()

THRESHOLDS = [
    (1.0, "Session cost exceeded $1. Consider using lower effort for simple queries."),
    (5.0, "Session cost exceeded $5. This is a high-cost session."),
    (10.0, "WARNING: Session cost exceeded $10. Review whether current task justifies this spend."),
]


def reset():
    """Reset session cost tracking (call on session start)."""
    global _session_cost, _warned_thresholds
    _session_cost = 0.0
    _warned_thresholds = set()


def handle(context: dict) -> dict:
    """Track cost from tool result metadata, warn at thresholds."""
    global _session_cost

    # Extract cost from context (CC reports cost in result events)
    cost_delta = context.get("cost_usd", 0)
    if isinstance(cost_delta, (int, float)) and cost_delta > 0:
        _session_cost += cost_delta

    # Also check total_cost_usd if provided
    total = context.get("total_cost_usd", 0)
    if isinstance(total, (int, float)) and total > _session_cost:
        _session_cost = total

    # Check thresholds
    for threshold, message in THRESHOLDS:
        if _session_cost >= threshold and threshold not in _warned_thresholds:
            _warned_thresholds.add(threshold)
            return {
                "systemMessage": f"[COST] {message} (current: ${_session_cost:.2f})",
            }

    return {}


if __name__ == "__main__":
    if "--test" in sys.argv:
        reset()
        # Below threshold — no warning
        result = handle({"cost_usd": 0.50})
        assert result == {}, f"Expected no warning at $0.50, got: {result}"
        # Hit $1 threshold
        result = handle({"cost_usd": 0.60})
        assert "COST" in result.get("systemMessage", ""), f"Expected warning at $1.10, got: {result}"
        # Same threshold shouldn't warn again
        result = handle({"cost_usd": 0.10})
        assert result == {}, f"Expected no re-warn, got: {result}"
        # Hit $5 threshold
        result = handle({"cost_usd": 4.00})
        assert "$5" in result.get("systemMessage", ""), f"Expected $5 warning, got: {result}"
        print("PASS")
        sys.exit(0)

    ctx = json.loads(sys.stdin.read())
    output = handle(ctx)
    print(json.dumps(output))
