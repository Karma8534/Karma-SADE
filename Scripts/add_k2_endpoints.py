#!/usr/bin/env python3
"""
Add K2 polling endpoints to karma-server/server.py

Inserts /v1/k2-proposals (GET) and /v1/k2-feedback (POST) endpoints
before the startup section to avoid SSH heredoc escaping issues.
"""

import re

# The new endpoints code
ENDPOINTS_CODE = '''

# ─── K2 Polling Interface ─────────────────────────────────────────────────

@app.get("/v1/k2-proposals")
async def k2_get_proposals(request: Request):
    """
    Get pending proposals from K2 consciousness loop for Claude Code review.

    Returns proposals from collab.jsonl where:
    - status == "pending"
    - to == "claude-code"

    Response: {proposals: [...], count: int}
    """
    import json
    from pathlib import Path

    COLLAB_FILE = "/opt/seed-vault/memory_v1/ledger/collab.jsonl"
    proposals = []

    try:
        path = Path(COLLAB_FILE)
        if not path.exists():
            return {"proposals": [], "count": 0, "error": f"Collab file not found: {COLLAB_FILE}"}

        with open(path, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if (entry.get("status") == "pending" and
                        entry.get("to") == "claude-code" and
                        entry.get("type") == "autonomous_proposal"):
                        proposals.append(entry)
                except json.JSONDecodeError:
                    continue

        # Sort by timestamp (newest first)
        proposals.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return {
            "proposals": proposals,
            "count": len(proposals),
            "status": "ok"
        }
    except Exception as e:
        return {
            "proposals": [],
            "count": 0,
            "error": str(e),
            "status": "error"
        }


@app.post("/v1/k2-feedback")
async def k2_send_feedback(request: Request):
    """
    Send feedback on K2 proposals back to consciousness loop.

    Request body: {
        proposal_id: str,
        decision: "accept" | "reject" | "defer" | "revise",
        reasoning: str,
        action_taken?: str
    }

    Appends feedback to collab.jsonl with status=resolved
    """
    import json
    from pathlib import Path
    from datetime import datetime, timezone
    import uuid

    COLLAB_FILE = "/opt/seed-vault/memory_v1/ledger/collab.jsonl"

    try:
        body = await request.json()
        proposal_id = body.get("proposal_id")
        decision = body.get("decision")  # accept, reject, defer, revise
        reasoning = body.get("reasoning", "")
        action_taken = body.get("action_taken", "")

        if not proposal_id or not decision:
            return {
                "status": "error",
                "error": "Missing required fields: proposal_id, decision"
            }

        if decision not in ["accept", "reject", "defer", "revise"]:
            return {
                "status": "error",
                "error": f"Invalid decision: {decision}. Must be: accept, reject, defer, revise"
            }

        # Create feedback entry
        feedback_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "id": f"feedback_{uuid.uuid4().hex[:12]}",
            "from": "claude-code",
            "to": "karma-consciousness",
            "type": "proposal_feedback",
            "proposal_id": proposal_id,
            "decision": decision,
            "reasoning": reasoning,
            "action_taken": action_taken,
            "status": "resolved"
        }

        # Append to collab.jsonl
        path = Path(COLLAB_FILE)
        with open(path, "a") as f:
            f.write(json.dumps(feedback_entry) + "\\n")

        return {
            "status": "ok",
            "feedback_id": feedback_entry["id"],
            "proposal_id": proposal_id,
            "decision": decision,
            "message": "Feedback recorded and sent to consciousness loop"
        }

    except json.JSONDecodeError:
        return {
            "status": "error",
            "error": "Invalid JSON in request body"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

'''

def add_endpoints():
    """Read server.py, insert endpoints before startup section."""

    server_file = "/opt/seed-vault/memory_v1/karma-core/server.py"

    # Read the file
    with open(server_file, "r") as f:
        content = f.read()

    # Find the startup section marker
    startup_marker = '@app.on_event("startup")'
    if startup_marker not in content:
        print("ERROR: Could not find startup section marker")
        return False

    # Insert endpoints before startup
    insert_pos = content.find(startup_marker)

    # Check if endpoints already exist
    if "/v1/k2-proposals" in content:
        print("INFO: Endpoints already exist in server.py")
        return True

    # Insert the new code
    new_content = content[:insert_pos] + ENDPOINTS_CODE + "\n" + content[insert_pos:]

    # Write back
    with open(server_file, "w") as f:
        f.write(new_content)

    print("✓ K2 polling endpoints added to server.py")
    return True


if __name__ == "__main__":
    success = add_endpoints()
    exit(0 if success else 1)
