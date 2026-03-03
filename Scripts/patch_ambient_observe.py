#!/usr/bin/env python3
"""Patch consciousness.py to query /v1/context in the OBSERVE phase.

Adds ambient context awareness: Karma's consciousness loop now sees git commits,
CC session events, and any other ambient entries flowing through the vault.
"""

SERVER_PY = "/app/consciousness.py"

# 1. Add urllib import at the top (after existing imports)
OLD_IMPORTS = "from decision_logger import DecisionLogger"
NEW_IMPORTS = """from decision_logger import DecisionLogger
import urllib.request"""

# 2. Add _fetch_ambient_context method after _observe
OLD_OBSERVE_END = """        # Return delta observation
        return {
            'new_episodes': episodes,
            'time_delta_seconds': time_delta,
            'episode_count': len(episodes)
        }"""

NEW_OBSERVE_END = """        # Fetch ambient context (git commits, CC sessions, etc.)
        ambient_events = self._fetch_ambient_context()

        # If nothing changed in graph AND no ambient events, return None (idle)
        if (not episodes or len(episodes) == 0) and not ambient_events:
            return None

        # Return delta observation
        return {
            'new_episodes': episodes,
            'time_delta_seconds': time_delta,
            'episode_count': len(episodes),
            'ambient_events': ambient_events,
        }

    def _fetch_ambient_context(self) -> list:
        \"\"\"Query hub-bridge /v1/context for recent ambient entries.
        Returns list of ambient events (git commits, CC sessions, etc.)
        Non-blocking: returns empty list on any failure.\"\"\"
        try:
            token_path = "/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt"
            with open(token_path) as f:
                token = f.read().strip()
            url = "http://127.0.0.1:18090/v1/context?hours=1&limit=5"
            req = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {token}",
            })
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
            entries = data.get("entries", [])
            # Filter out entries we've already seen (by tracking last seen ID)
            if not hasattr(self, '_last_ambient_ids'):
                self._last_ambient_ids = set()
            new_entries = [e for e in entries if e.get("id") not in self._last_ambient_ids]
            # Update seen set (keep bounded)
            self._last_ambient_ids = {e.get("id") for e in entries}
            return new_entries
        except Exception as e:
            logger.debug(f"Ambient context fetch failed (non-fatal): {e}")
            return []"""

# 3. Update _decide_rule_based to handle ambient events
OLD_DECIDE_START = '        episode_count = observations.get("episode_count", 0)\n\n        # No activity \u2192 no action\n        if episode_count == 0:\n            return Action.NO_ACTION, "No new activity"'

NEW_DECIDE_START = '        episode_count = observations.get("episode_count", 0)\n        ambient_events = observations.get("ambient_events", [])\n\n        # Ambient events detected (git commits, CC sessions, etc.)\n        if ambient_events and episode_count == 0:\n            sources = set(e.get("source", "?") for e in ambient_events)\n            summaries = [e.get("summary", "")[:60] for e in ambient_events[:3]]\n            return Action.LOG_DISCOVERY, f"Ambient: {len(ambient_events)} events from {\', \'.join(sources)} | {\'; \'.join(summaries)}"\n\n        # No activity \u2192 no action\n        if episode_count == 0 and not ambient_events:\n            return Action.NO_ACTION, "No new activity"'

import sys

with open(SERVER_PY, "r") as f:
    content = f.read()

# Apply patches in order
patches = [
    ("imports", OLD_IMPORTS, NEW_IMPORTS),
    ("observe_end", OLD_OBSERVE_END, NEW_OBSERVE_END),
    ("decide_start", OLD_DECIDE_START, NEW_DECIDE_START),
]

for name, old, new in patches:
    if old not in content:
        print(f"ERROR: Could not find patch target '{name}'")
        print(f"  Looking for: {repr(old[:80])}...")
        sys.exit(1)
    content = content.replace(old, new)
    print(f"OK: Patched '{name}'")

with open(SERVER_PY, "w") as f:
    f.write(content)

print(f"\nDone. consciousness.py patched with ambient context awareness.")
