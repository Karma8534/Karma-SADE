"""Fix Karma's prompt: better theming CSS guidance + remove filler phrases."""
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

# Fix 1: Replace the cockpit customization section with better CSS guidance
OLD_CUSTOMIZE = """### Cockpit Customization — Modify Your Own UI
Neo can ask you to change your cockpit appearance and you do it directly:
- `cockpit_customize(css, description)` — inject CSS to change colors, fonts, layout, anything visual. Use `!important`.
- `cockpit_reset()` — undo all customizations
- `cockpit_theme()` — see current active styles
- `cockpit_execute(js, description)` — run JavaScript for advanced DOM changes (requires approval)

Styles persist across sessions. When Neo says "change the background to blue", generate the CSS yourself and apply it."""

NEW_CUSTOMIZE = """### Cockpit Customization — Modify Your Own UI
Neo can ask you to change your cockpit appearance and you do it directly:
- `cockpit_customize(css, description)` — inject CSS. Always use `!important`.
- `cockpit_reset()` — undo all customizations
- `cockpit_theme()` — see current active styles
- `cockpit_execute(js, description)` — run JavaScript for advanced DOM changes (requires approval)

Styles persist across sessions. When Neo says "change the background to purple", generate the CSS yourself and call cockpit_customize immediately. Do NOT just show the CSS — actually call the tool.

**Open WebUI CSS selectors that work:**
- Background: `body, .app, main, div.relative.flex.flex-col { background-color: COLOR !important; }`
- Chat bubbles: `.assistant-message, [data-message-id] { background: COLOR !important; }`
- Text color: `.prose, .message-content, body { color: COLOR !important; }`
- Sidebar: `#sidebar, nav { background-color: COLOR !important; }`
Always target multiple selectors to ensure the change is visible."""

if OLD_CUSTOMIZE in system:
    system = system.replace(OLD_CUSTOMIZE, NEW_CUSTOMIZE)
    print("[1] Updated cockpit customization section with better CSS guidance")
else:
    print("[1] WARNING: Could not find customization section")

# Fix 2: Add no-filler directive to Communication Style
OLD_COMM = """## Communication Style

- Explain as an expert guiding a novice
- Use clear, step-by-step instructions
- Provide rationale for recommendations
- One action per step when executing
- Pause for confirmation on risky operations
- Be concise but information-dense"""

NEW_COMM = """## Communication Style

- Explain as an expert guiding a novice
- Use clear, step-by-step instructions
- Provide rationale for recommendations
- One action per step when executing
- Pause for confirmation on risky operations
- Be concise but information-dense
- **NEVER end with filler like "Is there anything else I can help you with?" or "Let me know if you need anything."** Just stop after the answer."""

if OLD_COMM in system:
    system = system.replace(OLD_COMM, NEW_COMM)
    print("[2] Added no-filler directive")
else:
    print("[2] WARNING: Could not find Communication Style section")

params["system"] = system
meta["params"] = params
c.execute("UPDATE model SET meta = ? WHERE id = ?", (json.dumps(meta), MODEL_ID))
conn.commit()
conn.close()
print(f"[OK] Done. Prompt length: {len(system)}")
