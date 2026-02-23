#!/usr/bin/env python3
"""
Karma K2 Sync Worker — Read droplet state, process locally, write back every 60s
"""

import requests
import json
import time
from datetime import datetime
import os
import sys

# Config
DROPLET_BASE = "https://vault-neo.cloud.tailscale.net:8340"  # Tailscale IP
K2_LOG_DIR = r"\\PAYBACK\Users\raest\OneDrive\Karma\Processing"
CYCLE_INTERVAL = 60

# Ensure log dir exists
os.makedirs(K2_LOG_DIR, exist_ok=True)

def get_droplet_state():
    """Read current graph state from droplet."""
    try:
        resp = requests.get(f"{DROPLET_BASE}/health", timeout=5, verify=False)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e), "status": "droplet_unreachable"}

def process_state(state):
    """Process state locally (simple reasoning for now)."""
    if "error" in state:
        return {
            "type": "sync_error",
            "reason": state.get("error"),
            "timestamp": datetime.utcnow().isoformat(),
        }

    # Extract key metrics
    brain = state.get("brain", {})
    graph = brain.get("knowledge_graph", {})

    return {
        "type": "consciousness_cycle",
        "timestamp": datetime.utcnow().isoformat(),
        "observations": {
            "entities": graph.get("entities", 0),
            "episodes": graph.get("episodes", 0),
            "relationships": graph.get("relationships", 0),
        },
        "cycle_number": int(time.time() / 60),
    }

def write_decision(decision):
    """Write decision back to droplet."""
    try:
        headers = {"Content-Type": "application/json"}
        # For now, just log locally (droplet endpoint can be added later)
        return {"status": "logged", "decision": decision}
    except Exception as e:
        return {"error": str(e)}

def log_cycle(result):
    """Log cycle result to shared drive."""
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(K2_LOG_DIR, f"cycle_{timestamp}.json")
        with open(log_file, "w") as f:
            json.dump(result, f, indent=2)
        return log_file
    except Exception as e:
        print(f"ERROR: Could not write log: {e}")
        return None

def main():
    """Main sync loop."""
    print(f"[K2 SYNC] Starting consciousness worker. Interval: {CYCLE_INTERVAL}s")

    while True:
        try:
            # Read state from droplet
            state = get_droplet_state()

            # Process locally
            decision = process_state(state)

            # Write back (stub for now)
            result = write_decision(decision)

            # Log to shared drive
            log_path = log_cycle({
                "state": state,
                "decision": decision,
                "result": result,
            })

            print(f"[K2 SYNC] Cycle complete. Log: {log_path}")

            # Wait for next cycle
            time.sleep(CYCLE_INTERVAL)

        except KeyboardInterrupt:
            print("\n[K2 SYNC] Shutting down.")
            sys.exit(0)
        except Exception as e:
            print(f"[K2 SYNC] ERROR: {e}")
            time.sleep(CYCLE_INTERVAL)

if __name__ == "__main__":
    main()
