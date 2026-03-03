#!/usr/bin/env python3
"""Fix _fetch_ambient_context to read ledger directly instead of HTTP call.
karma-server has /ledger/memory.jsonl mounted but no hub-bridge auth token."""

SERVER_PY = "/app/consciousness.py"

OLD = r'''    def _fetch_ambient_context(self) -> list:
        """Query hub-bridge /v1/context for recent ambient entries.
        Returns list of ambient events (git commits, CC sessions, etc.)
        Non-blocking: returns empty list on any failure."""
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
            return []'''

NEW = r'''    def _fetch_ambient_context(self) -> list:
        """Read recent ambient entries directly from the vault ledger.
        Looks for entries with content.source in (git, claude-code, ambient)
        that were captured in the last hour.
        Non-blocking: returns empty list on any failure."""
        try:
            ledger_path = "/ledger/memory.jsonl"
            cutoff = time.time() - 3600  # 1 hour ago
            cutoff_iso = datetime.fromtimestamp(cutoff, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            ambient_sources = {"git", "claude-code", "ambient", "screen"}

            # Read last 200 lines (reverse scan would be ideal but this is simple)
            import os
            with open(ledger_path, "r") as f:
                lines = f.readlines()
            recent = lines[-200:] if len(lines) > 200 else lines

            entries = []
            for line in reversed(recent):
                try:
                    rec = json.loads(line.strip())
                    content = rec.get("content", {})
                    captured_at = content.get("captured_at", "")
                    if not captured_at:
                        continue
                    if captured_at < cutoff_iso:
                        break
                    src = content.get("source", "")
                    if src not in ambient_sources:
                        continue
                    entries.append({
                        "id": rec.get("id", ""),
                        "source": src,
                        "source_node": content.get("source_node", ""),
                        "summary": content.get("summary", ""),
                    })
                    if len(entries) >= 5:
                        break
                except (json.JSONDecodeError, KeyError):
                    continue

            # Filter out entries we've already seen
            if not hasattr(self, '_last_ambient_ids'):
                self._last_ambient_ids = set()
            new_entries = [e for e in entries if e.get("id") not in self._last_ambient_ids]
            self._last_ambient_ids = {e.get("id") for e in entries}
            return new_entries
        except Exception as e:
            logger.debug(f"Ambient context read failed (non-fatal): {e}")
            return []'''

with open(SERVER_PY, "r") as f:
    content = f.read()

if OLD not in content:
    print("ERROR: Could not find _fetch_ambient_context to replace")
    # Try to show what's there
    idx = content.find("_fetch_ambient_context")
    if idx >= 0:
        print(f"Found at position {idx}, showing context:")
        print(repr(content[idx:idx+200]))
    raise SystemExit(1)

content = content.replace(OLD, NEW)

# Also remove the urllib import since we no longer need it
content = content.replace("import urllib.request\n", "")

with open(SERVER_PY, "w") as f:
    f.write(content)

print("OK: Replaced HTTP-based ambient fetch with direct ledger read")
