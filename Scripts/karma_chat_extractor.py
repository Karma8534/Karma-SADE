"""Karma Chat Extractor

Reads recent chats from the Open WebUI SQLite database, sends them
to a local Ollama model for fact extraction, and merges new facts
into 05-user-facts.json.

Bugs fixed 2026-02-11:
  - updated_at is Unix epoch (int), not a datetime string
  - Track per-chat updated_at so edited chats are re-processed
  - Use qwen2.5-coder:3b (lighter, faster on 4GB VRAM)
  - Robust JSON parsing of LLM output
"""
import sqlite3, json, os, re, requests, time
from datetime import datetime, timezone

# --------------- config ---------------
DB_PATH = r"C:\openwebui\venv\Lib\site-packages\open_webui\data\webui.db"
FACTS_FILE = r"C:\Users\raest\Documents\Karma_SADE\Memory\05-user-facts.json"
STATE_FILE = r"C:\Users\raest\Documents\Karma_SADE\Memory\.chat_extraction_state.json"
OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = os.environ.get("KARMA_EXTRACT_MODEL", "qwen2.5-coder:3b")
LOOKBACK_DAYS = 14

# --------------- helpers ---------------
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default.copy()

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --------------- DB query ---------------
def get_recent_chats():
    """Return chats updated within LOOKBACK_DAYS (epoch-based comparison)."""
    cutoff_epoch = int(time.time()) - (LOOKBACK_DAYS * 86400)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, user_id, chat, updated_at, created_at "
        "FROM chat "
        "WHERE updated_at > ? "
        "ORDER BY updated_at DESC "
        "LIMIT 50",
        (cutoff_epoch,),
    )
    rows = c.fetchall()
    conn.close()
    chats = []
    for row in rows:
        try:
            chat_data = json.loads(row[2])
            chats.append({
                "id": row[0],
                "user_id": row[1],
                "messages": chat_data.get("messages", []),
                "updated_at": row[3],  # epoch int
                "created_at": row[4],
            })
        except (json.JSONDecodeError, TypeError):
            continue
    return chats

# --------------- LLM extraction ---------------
EXTRACTION_PROMPT = """\
You are analyzing a conversation between a user called Neo and an AI called Karma.
Your job is to extract PERSISTENT facts, preferences, or context about Neo.

Rules:
- Only extract information that is worth remembering long-term.
- Ignore greetings, temporary tasks, and transient questions.
- Use snake_case keys (e.g. favorite_editor, preferred_language).
- If no new facts exist, return empty arrays.

Return ONLY valid JSON (no markdown, no commentary) in this schema:
{"facts":[{"key":"","value":""}], "preferences":[{"key":"","value":""}], "context":[{"key":"","value":""}]}

Conversation:
"""

def extract_facts(messages):
    """Send recent messages to the LLM for fact extraction."""
    msgs = messages[-12:] if len(messages) > 12 else messages
    formatted = []
    for msg in msgs:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role and content:
            # Truncate very long messages to save context
            if len(content) > 600:
                content = content[:600] + "..."
            formatted.append(f"{role.upper()}: {content}")
    if not formatted:
        return None

    prompt = EXTRACTION_PROMPT + "\n".join(formatted)
    try:
        response = requests.post(
            OLLAMA_API,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2, "top_p": 0.9},
            },
            timeout=90,
        )
        response.raise_for_status()
        text = response.json().get("response", "")
        return parse_llm_json(text)
    except requests.exceptions.ConnectionError:
        print("  [ERROR] Cannot connect to Ollama. Is it running?")
        return None
    except Exception as exc:
        print(f"  [ERROR] LLM extraction failed: {exc}")
        return None

def parse_llm_json(text):
    """Robustly extract JSON from LLM output (handles fences, preamble)."""
    # Strip markdown code fences
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = text.strip()
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try to find JSON object in the text
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    print(f"  [WARN] Could not parse LLM output as JSON: {text[:120]}...")
    return None

# --------------- merge ---------------
# Keys that represent volatile/live state and must never be stored as facts.
# Browser state should always come from live tool calls, not memory.
# Keep in sync with generate_karma_prompt.py BLOCKED_KEYS.
BLOCKED_KEYS = {
    "browser_tabs", "open_browser_tabs", "browser", "karma-browser-control/browser_tabs",
    "last_visited_url", "current_tabs", "open_tabs", "preferred_browser", "browser_state",
    "website_title", "github_page_title", "preferred_color",
    "logging_tools", "monitoring_tools", "backup_locations", "karma_sade_description",
    "code_interpreter", "playwright", "chat_window_features", "open_webui_management",
    "previous_conversation", "change_management_rules", "change_management_rules_steps",
    "perplexity_labs", "perplexity_models", "preferred_nickname", "working_machine",
    "memory_system_status", "karma_sade_rebuild_2026_02_10",
    "current_browser", "current_tab", "color_picker", "browser_control_needed",
}

def merge(existing, extracted):
    """Merge extracted facts into existing facts file. Returns count of changes."""
    if not extracted:
        return 0
    updated = 0
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    for section in ("facts", "preferences", "context"):
        for item in extracted.get(section, []):
            key = str(item.get("key", "")).strip()
            value = str(item.get("value", "")).strip()
            if not key or not value or len(key) > 80:
                continue
            if key.lower() in BLOCKED_KEYS or any(b in key.lower() for b in ("browser_tab", "visited_url")):
                print(f"  [SKIP] Blocked volatile key: {key}")
                continue
            collection = existing.setdefault(section, [])
            match = next((x for x in collection if x.get("key") == key), None)
            if not match:
                collection.append({"key": key, "value": value, "updated": timestamp})
                print(f"  [+] {section[:-1]}: {key} = {value}")
                updated += 1
            elif match.get("value") != value:
                match["value"] = value
                match["updated"] = timestamp
                print(f"  [~] {section[:-1]}: {key} = {value}")
                updated += 1
    return updated

# --------------- main ---------------
def needs_processing(chat, state):
    """Check if a chat needs (re-)processing based on its updated_at epoch."""
    chat_id = chat["id"]
    chat_epoch = chat["updated_at"]
    seen = state.get("seen_epochs", {})
    last_epoch = seen.get(chat_id, 0)
    return chat_epoch > last_epoch

def main():
    print("=" * 60)
    print("Karma Chat Extractor")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: {MODEL}")
    print("=" * 60)

    facts = load_json(FACTS_FILE, {"facts": [], "preferences": [], "context": []})
    state = load_json(STATE_FILE, {"seen_epochs": {}, "last_extraction": None})

    # Migrate old state format (list of IDs) → new format (dict of epochs)
    if "processed_messages" in state and "seen_epochs" not in state:
        state["seen_epochs"] = {cid: 0 for cid in state.pop("processed_messages")}

    chats = get_recent_chats()
    print(f"\nFound {len(chats)} recent chats (within {LOOKBACK_DAYS} days)")

    total = 0
    processed = 0
    for chat in chats:
        if not needs_processing(chat, state):
            continue
        processed += 1
        print(f"\nProcessing chat {chat['id'][:8]}... "
              f"({len(chat['messages'])} messages)")
        extracted = extract_facts(chat["messages"])
        total += merge(facts, extracted)
        state.setdefault("seen_epochs", {})[chat["id"]] = chat["updated_at"]

    if total:
        save_json(FACTS_FILE, facts)
        print(f"\n[OK] Added/updated {total} items in 05-user-facts.json")
    else:
        if processed:
            print(f"\n[OK] Processed {processed} chats, no new facts found")
        else:
            print("\n[OK] All chats already up-to-date")

    state["last_extraction"] = datetime.now(timezone.utc).isoformat()
    save_json(STATE_FILE, state)
    print(f"\nExtraction complete ({processed} chats processed)")
    print("=" * 60)

if __name__ == "__main__":
    main()
