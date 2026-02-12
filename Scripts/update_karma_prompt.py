"""Update Karma's system prompt to enable proactive tool use."""
import sqlite3
import json

DB_PATH = r"C:\openwebui\venv\Lib\site-packages\open_webui\data\webui.db"
MODEL_ID = "karma-sade-architect"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT meta FROM model WHERE id=?", (MODEL_ID,))
row = c.fetchone()
if not row:
    print("ERROR: Model not found")
    conn.close()
    exit(1)

meta = json.loads(row[0])
params = meta.get("params", {})
system = params.get("system", "")

# --- Fix 1: Soften the memory-only directive ---
system = system.replace(
    "**NEVER write code, call tools, or run scripts to look up information that is already in your memory above.** Just answer from what you know.",
    "**Do NOT call tools to look up information that is already in your memory above.** Just answer from what you know."
)
print("[1] Fixed memory directive")

# --- Fix 2: Replace Response Style section and add Tool Use section ---
OLD_RESPONSE = """## Response Style (CRITICAL)

- **Answer questions directly in plain language.** Do NOT show code, scripts, or tool calls unless Neo specifically asks for them.
- Do NOT use the code interpreter or Python to answer questions you can answer from memory or general knowledge.
- Only show code when Neo asks you to write code, debug something, or explicitly requests to see the process.
- Keep answers conversational, clear, and concise.
- When Neo asks a simple question, give a simple answer."""

NEW_RESPONSE = """## Response Style (CRITICAL)

- **Answer questions directly in plain language.** Keep answers conversational, clear, and concise.
- When Neo asks a simple question, give a simple answer.
- Do NOT use the code interpreter or Python to answer questions you can answer from memory or general knowledge.
- Only show raw code when Neo asks you to write code or debug something.

## Tool Use (CRITICAL)

- **ALWAYS use your browser tools when Neo asks you to do anything with the browser.** Do not describe what you would do — actually call the tool.
- When Neo says "open github", "check my tabs", "read that page", "take a screenshot", etc. — **call the appropriate browser_* or cockpit_* tool immediately.**
- Present tool results naturally in your response. Do not ask Neo to confirm before calling a read-only tool (browser_tabs, browser_read, browser_links, browser_screenshot, etc.).
- For mutation tools (browser_click, browser_fill, cockpit_execute), follow the approval flow as designed.
- You may chain multiple tool calls in sequence to accomplish a task without asking permission between each step."""

if OLD_RESPONSE in system:
    system = system.replace(OLD_RESPONSE, NEW_RESPONSE)
    print("[2] Replaced Response Style + added Tool Use section")
else:
    print("[2] WARNING: Could not find exact Response Style block to replace")
    idx = system.find("## Response Style")
    if idx >= 0:
        print("    Found at index", idx)
        print("    Content:", repr(system[idx:idx+200]))

params["system"] = system
meta["params"] = params
c.execute("UPDATE model SET meta = ? WHERE id = ?", (json.dumps(meta), MODEL_ID))
conn.commit()
conn.close()
print("[OK] System prompt updated. Length:", len(system))
