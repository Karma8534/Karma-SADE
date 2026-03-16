#!/usr/bin/env python3
"""Patch cc_ascendant_watchdog.py to add bus-response (acknowledge pending messages)."""
import sys

WATCHDOG_PATH = "/mnt/c/dev/Karma/k2/aria/tools/cc_ascendant_watchdog.py"

with open(WATCHDOG_PATH) as f:
    content = f.read()

if "acknowledge_pending_messages" in content:
    print("SKIP: already patched")
    sys.exit(0)

# New function to insert
NEW_FUNC = '''

def acknowledge_pending_messages(token: str, pending_result: dict) -> int:
    """Auto-acknowledge CC-addressed bus messages with triage response.

    Posts acknowledgment so senders know watchdog received it.
    Complex messages queued for next CC session. Zero Anthropic tokens.
    """
    if pending_result.get("count", 0) == 0:
        return 0
    data = _bus_get("/v1/coordination/recent?limit=100", token)
    entries = data.get("entries", [])
    pending = [e for e in entries if e.get("to") == "cc" and e.get("status") == "pending"]
    acknowledged = 0
    for msg in pending[:3]:  # Max 3 per cycle to avoid spam
        sender = msg.get("from", "unknown")
        preview = str(msg.get("content", ""))[:100]
        ack_msg = (
            f"CC WATCHDOG ACK [auto]: Received from {sender}. "
            f"Queued for CC session review. Preview: {preview}..."
        )
        _bus_post(token, sender, ack_msg, urgency="informational")
        acknowledged += 1
    return acknowledged


'''

# Insert before evolution capture section
MARKER = "# --- Evolution capture: extract CC events from bus ---"
content = content.replace(MARKER, NEW_FUNC + MARKER)

# Add call in run() after pending = check_pending_cc(token)
RUN_MARKER = "    pending = check_pending_cc(token)"
RUN_PATCH = """    pending = check_pending_cc(token)

    # --- Auto-acknowledge pending messages ---
    acked = acknowledge_pending_messages(token, pending)
    if acked:
        print(f"[{ts}] auto-ack: {acked} messages acknowledged")"""
content = content.replace(RUN_MARKER, RUN_PATCH, 1)

with open(WATCHDOG_PATH, "w") as f:
    f.write(content)

print("PATCHED OK")
