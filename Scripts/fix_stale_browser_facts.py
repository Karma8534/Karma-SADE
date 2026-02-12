"""Remove stale browser-state facts from Karma's system prompt
and add a directive to always use browser tools for live state."""
import sqlite3
import json

DB_PATH = r"C:\openwebui\venv\Lib\site-packages\open_webui\data\webui.db"
MODEL_ID = "karma-sade-architect"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT meta FROM model WHERE id=?", (MODEL_ID,))
row = c.fetchone()
meta = json.loads(row[0])
params = meta.get("params", {})
system = params.get("system", "")

# --- Remove stale browser-state lines from memory section ---
stale_prefixes = [
    "- **browser_tabs**:",
    "- **open_browser_tabs**:",
    "- **karma-browser-control/browser_tabs**:",
    "- **last_visited_url**:",
    "- **browser**:",
]

lines = system.split("\n")
removed = []
kept = []
for line in lines:
    stripped = line.strip()
    if any(stripped.startswith(prefix) for prefix in stale_prefixes):
        removed.append(stripped)
    else:
        kept.append(line)

system = "\n".join(kept)
print(f"[1] Removed {len(removed)} stale browser-state lines:")
for r in removed:
    print(f"    - {r[:80]}")

# --- Add directive that browser state must come from tools ---
OLD_TOOL_HEADER = "## Tool Use (CRITICAL)"
NEW_TOOL_HEADER = """## Tool Use (CRITICAL)

- **Browser state (open tabs, URLs, page content) is NEVER in your memory. ALWAYS call browser_tabs() or the appropriate tool to get live data.**"""

if OLD_TOOL_HEADER in system and "Browser state" not in system:
    system = system.replace(OLD_TOOL_HEADER, NEW_TOOL_HEADER, 1)
    print("[2] Added 'browser state is never in memory' directive")
else:
    print("[2] Directive already present or section not found")

params["system"] = system
meta["params"] = params
c.execute("UPDATE model SET meta = ? WHERE id = ?", (json.dumps(meta), MODEL_ID))
conn.commit()
conn.close()
print(f"[OK] Done. Prompt length: {len(system)}")
