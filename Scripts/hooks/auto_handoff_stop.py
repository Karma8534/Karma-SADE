"""auto_handoff_stop.py — Stop event handler.
Writes a YAML handoff document on every agent stop for session continuity.
"""
import json, sys, os, yaml
from datetime import datetime, timezone

HANDOFF_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "tmp", "handoffs")


def handle(context: dict) -> dict:
    """Generate YAML handoff from session context."""
    os.makedirs(HANDOFF_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session_id = context.get("session_id", "unknown")

    handoff = {
        "timestamp": ts,
        "session_id": session_id,
        "goal": context.get("goal", ""),
        "now": context.get("current_task", ""),
        "done_this_session": context.get("completed_tasks", []),
        "blockers": context.get("blockers", []),
        "decisions": context.get("decisions", []),
        "findings": context.get("findings", []),
        "next": context.get("next_steps", []),
        "files_changed": context.get("files_changed", []),
    }

    filename = f"handoff-{ts}.yaml"
    filepath = os.path.join(HANDOFF_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(handoff, f, default_flow_style=False, allow_unicode=True)

    return {"systemMessage": f"Session handoff saved: {filename}", "handoff_path": filepath}


# ── Stdin/stdout protocol for hooks engine ───────────────────────────────────
if __name__ == "__main__":
    if "--test" in sys.argv:
        result = handle({"session_id": "test-123", "goal": "test handoff", "current_task": "testing"})
        assert "handoff_path" in result
        assert os.path.exists(result["handoff_path"])
        os.remove(result["handoff_path"])
        print("PASS")
        sys.exit(0)

    ctx = json.loads(sys.stdin.read())
    output = handle(ctx)
    print(json.dumps(output))
