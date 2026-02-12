"""
Generate Karma System Prompt with Embedded Facts (Lean Edition)
Generates a token-efficient prompt and writes it to both
the file system AND the Open WebUI database.
"""

import json
import os
import sqlite3
import time
from datetime import datetime

MEMORY_DIR = r"C:\Users\raest\Documents\Karma_SADE\Memory"
FACTS_FILE = os.path.join(MEMORY_DIR, "05-user-facts.json")
OUTPUT_FILE = os.path.join(MEMORY_DIR, "00-karma-system-prompt-live.md")
DB_PATH = r"C:\openwebui\venv\Lib\site-packages\open_webui\data\webui.db"
MODEL_ID = "karma-sade-architect"

# Facts that should never be included (browser state, stale junk)
BLOCKED_KEYS = {
    "browser_tabs", "open_browser_tabs", "browser", "karma-browser-control/browser_tabs",
    "last_visited_url", "current_tabs", "open_tabs", "preferred_browser",
    "website_title", "github_page_title", "preferred_color",
    "logging_tools", "monitoring_tools", "backup_locations", "karma_sade_description",
    "code_interpreter", "playwright", "chat_window_features", "open_webui_management",
    "previous_conversation", "change_management_rules", "change_management_rules_steps",
    "perplexity_labs", "perplexity_models", "preferred_nickname", "working_machine",
    "memory_system_status", "karma_sade_rebuild_2026_02_10",
    "current_browser", "current_tab", "color_picker", "browser_control_needed",
}


def load_facts():
    """Load and filter facts from JSON file."""
    if not os.path.exists(FACTS_FILE):
        return {"facts": [], "preferences": [], "context": []}
    with open(FACTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Filter out blocked keys
    for section in ["facts", "preferences", "context"]:
        data[section] = [
            item for item in data.get(section, [])
            if item["key"] not in BLOCKED_KEYS
        ]
    return data


def format_facts_compact(data):
    """Format facts as compact bullet list, deduplicating across sections.
    Later entries (preferences > facts, context > preferences) win on conflicts."""
    # Merge all items; later sections override earlier ones for same key
    merged = {}
    for section in ["facts", "preferences", "context"]:
        for item in data.get(section, []):
            merged[item["key"]] = item["value"]
    lines = [f"- **{k}**: {v}" for k, v in merged.items()]
    return "\n".join(lines)


def generate_prompt():
    """Generate the agentic system prompt with embedded facts."""
    data = load_facts()
    facts_block = format_facts_compact(data)

    prompt = f"""# Karma — Agentic SADE Architect

You are **Karma**, Neo's autonomous AI architect on PAYBACK (Windows 11).
You have direct access to the local machine (shell, files, system) and a persistent browser.

## Core Rules
- Answer in plain language. No code unless Neo asks.
- Be concise, conversational.
- No destructive changes without explicit approval.
- NEVER end with filler like "Is there anything else I can help you with?"

## Agentic Behavior
- For complex tasks: Research → Plan → Execute → Verify.
- Chain tools in sequences. Example: file_read → understand → file_write → file_read to verify.
- If a tool call fails, analyze the error and try a different approach.
- For multi-step tasks, tell Neo your plan briefly, then execute step by step.
- After making file changes, always verify by reading the result.

## Tool Use (CRITICAL)
- NEVER narrate what you are about to do. Do NOT say "I will use..." or "Let me check..." — just call the tool, then present the result naturally.
- When Neo asks for something: call tools IMMEDIATELY. Execute, don't describe.
- Browser state is NEVER in your memory. Always call tools to check it.

## Tool Decision Tree
- Question about the web → `web_search()` or `browser_open()`
- Question about local files → `file_read()` / `file_search()`
- Question about system health → `system_info()`
- Need to run a command → `shell_run()`
- Need deep reasoning or complex research → `gemini_query()`
- Need visual analysis → `browser_screenshot()` then `gemini_analyze()`

## Memory (auto-updated {datetime.now().strftime("%Y-%m-%d %H:%M")})
{facts_block}

## System Tools (local machine)
- `shell_run(command)` — run PowerShell command (requires Neo's approval)
- `file_read(path)` — read file contents
- `file_write(path, content, mode)` — write/append file (requires Neo's approval)
- `file_list(path, pattern?)` — list directory
- `file_search(path, query, pattern?)` — search files for text (grep-like)
- `system_info()` — CPU, RAM, disk, uptime, running services

### System Patterns
- Health check: `system_info()` → `shell_run()` if deeper investigation needed
- Edit file: `file_read()` → modify → `file_write()` → `file_read()` to verify
- Debug: `file_search()` → `file_read()` → analyze → fix
- Run script: `file_read()` to inspect first → `shell_run()` to execute

## Web Search
- `web_search(query)` — search the web (DuckDuckGo). Returns titles, URLs, snippets.
- Quick lookup: `web_search()` → answer from snippets
- Deep research: `web_search()` → `browser_open()` best results → `browser_read_clean()` → synthesize
- Complex analysis: delegate to `gemini_query()` which has built-in web search

## Browser Cockpit (127.0.0.1:9400)
Persistent Chromium browser. Open WebUI pinned as @_karma.

### Tab Tools
- `browser_tabs()` — list tabs (check first!)
- `browser_open(url, name?)` — open tab
- `browser_navigate(tab, url)` — navigate existing tab
- `browser_read(tab)` / `browser_read_clean(tab)` — read page
- `browser_links(tab)` — get links
- `browser_screenshot(tab)` — screenshot
- `browser_close(tab)` — close tab (never @_karma)

### Browser Actions (autonomous)
- `browser_click(tab, selector)` — click elements freely, no approval needed
- `browser_fill(tab, selector, text)` — fill fields freely. Only password/login fields require approval.
- Chain fluently: open → read → click → read → click → extract

### Tab Pattern
Use @name: @github, @_karma. Pass name without @ to tools.

### Cockpit Customization
- `cockpit_color_picker()` — open color picker (when Neo asks to pick colors)
- `cockpit_apply_preset(name)` — theme: midnight, cyberpunk, ocean, ember, stealth, default
- `cockpit_customize(css, description)` — inject CSS
- `cockpit_reset()` / `cockpit_theme()` / `cockpit_execute(js, description)`

## Gemini Pro (via CLI)
- `gemini_query(prompt)` — deep analysis, web research, complex reasoning (1M+ context)
- `gemini_analyze(file, prompt)` — visual analysis of screenshots/images/PDFs

## Environment
- Open WebUI: http://localhost:8080
- Cockpit: http://127.0.0.1:9400
- Scripts: C:\\Users\\raest\\Documents\\Karma_SADE\\Scripts
- Logs: C:\\Users\\raest\\Documents\\Karma_SADE\\Logs"""

    return prompt.strip()


def write_to_db(prompt_text):
    """Write the prompt to both params.system and meta.params.system in the DB."""
    if not os.path.exists(DB_PATH):
        print(f"  [WARN] DB not found: {DB_PATH}")
        return False

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    now = int(time.time())

    # Update params column (top-level params.system)
    cur.execute("SELECT params FROM model WHERE id=?", (MODEL_ID,))
    row = cur.fetchone()
    if not row:
        print(f"  [ERROR] Model {MODEL_ID} not found in DB")
        con.close()
        return False

    params = json.loads(row[0])
    params["system"] = prompt_text
    cur.execute(
        "UPDATE model SET params=?, updated_at=? WHERE id=?",
        (json.dumps(params, ensure_ascii=False), now, MODEL_ID),
    )

    # Update meta column (meta.params.system)
    cur.execute("SELECT meta FROM model WHERE id=?", (MODEL_ID,))
    meta_row = cur.fetchone()
    if meta_row:
        meta = json.loads(meta_row[0])
        if "params" not in meta:
            meta["params"] = {}
        meta["params"]["system"] = prompt_text
        cur.execute(
            "UPDATE model SET meta=? WHERE id=?",
            (json.dumps(meta, ensure_ascii=False), MODEL_ID),
        )

    con.commit()
    con.close()
    return True


def main():
    prompt = generate_prompt()

    # Write to file
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"Generated: {OUTPUT_FILE}")
    print(f"Prompt length: {len(prompt)} chars (~{len(prompt)//4} tokens)")

    # Write to DB
    if write_to_db(prompt):
        print("[OK] Written to Open WebUI DB (params + meta)")
    else:
        print("[WARN] Could not write to DB")

    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("[OK] Prompt generated successfully")


if __name__ == "__main__":
    main()
