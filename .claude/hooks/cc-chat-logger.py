#!/usr/bin/env python3
"""
cc-chat-logger.py -- Stop hook (S155: full conversation capture)
Captures ALL CC turns since last run from the session .jsonl file.
Appends full text (no truncation) to vault-neo nexus-chat.jsonl + claude-mem.
Uses watermark to avoid re-capturing old turns.
Runs silently -- never blocks the Stop hook.
"""
import json, sys, os, pathlib, subprocess, datetime, urllib.request


CLAUDEMEM_URL = "http://127.0.0.1:37778"
WATERMARK_FILE = pathlib.Path.home() / ".claude-mem" / ".cc_logger_watermark.json"


def load_watermark():
    try:
        return json.loads(WATERMARK_FILE.read_text())
    except Exception:
        return {"last_entry_count": 0, "session_id": ""}


def save_watermark(wm):
    try:
        WATERMARK_FILE.parent.mkdir(parents=True, exist_ok=True)
        WATERMARK_FILE.write_text(json.dumps(wm))
    except Exception:
        pass


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    session_id = data.get("session_id", "")
    if not session_id:
        sys.exit(0)

    cwd = data.get("cwd", os.environ.get("CLAUDE_PROJECT_DIR", ""))
    if not cwd:
        sys.exit(0)

    project_key = cwd.replace("\\", "-").replace("/", "-").replace(":", "-")
    home = pathlib.Path.home()
    session_file = home / ".claude" / "projects" / project_key / f"{session_id}.jsonl"

    if not session_file.exists():
        sys.exit(0)

    # Parse ALL entries
    entries = []
    for line in session_file.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except Exception:
            continue

    # Watermark: only process entries we haven't seen
    wm = load_watermark()
    if wm.get("session_id") == session_id:
        start_idx = wm.get("last_entry_count", 0)
    else:
        start_idx = 0  # New session — process all

    new_entries = entries[start_idx:]
    if not new_entries:
        sys.exit(0)

    # Extract user/assistant pairs from new entries
    pairs = []
    current_user = ""
    for entry in new_entries:
        msg = entry.get("message", {})
        role = msg.get("role", "")
        content = msg.get("content", [])

        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            text = " ".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            ).strip()
        else:
            text = ""

        if not text:
            continue

        if role == "user":
            current_user = text
        elif role == "assistant" and current_user:
            pairs.append({"user": current_user, "assistant": text})
            current_user = ""

    if not pairs:
        save_watermark({"last_entry_count": len(entries), "session_id": session_id})
        sys.exit(0)

    # Write ALL pairs to vault-neo (full text, no truncation)
    log_lines = []
    for pair in pairs:
        log_lines.append(json.dumps({
            "ts": datetime.datetime.utcnow().isoformat() + "Z",
            "user": pair["user"],
            "assistant": pair["assistant"],
            "session_id": session_id,
            "source": "cc-code-tab"
        }, ensure_ascii=False))

    # Append to vault-neo nexus-chat.jsonl
    try:
        subprocess.run(
            ["ssh", "vault-neo",
             "cat >> /opt/seed-vault/memory_v1/session/state/nexus-chat.jsonl"],
            input=("\n".join(log_lines) + "\n").encode("utf-8", errors="replace"),
            timeout=15,
            capture_output=True
        )
    except Exception:
        pass

    # Also save to claude-mem (full text)
    for pair in pairs[-5:]:  # Last 5 pairs to avoid flooding
        try:
            payload = json.dumps({
                "text": f"[CC Code tab] user: {pair['user']}\nassistant: {pair['assistant']}",
                "title": f"CC conversation: {pair['user'][:80]}",
                "project": "Karma_SADE",
            }).encode()
            req = urllib.request.Request(
                f"{CLAUDEMEM_URL}/api/memory/save",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass

    save_watermark({"last_entry_count": len(entries), "session_id": session_id})


if __name__ == "__main__":
    main()
