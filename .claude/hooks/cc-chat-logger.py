#!/usr/bin/env python3
"""
cc-chat-logger.py -- Stop hook
Captures the last CC turn (user message + assistant response) from the
session .jsonl file and appends to nexus-chat.jsonl on vault-neo.
Runs silently -- never blocks the Stop hook.
"""
import json, sys, os, pathlib, subprocess, datetime


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

    # Build project folder key: both : and \ become -
    # e.g. C:\Users\raest\Documents\Karma_SADE -> C--Users-raest-Documents-Karma-SADE
    project_key = cwd.replace("\\", "-").replace("/", "-").replace(":", "-")

    home = pathlib.Path.home()
    session_file = home / ".claude" / "projects" / project_key / f"{session_id}.jsonl"

    if not session_file.exists():
        sys.exit(0)

    # Parse entries
    entries = []
    for line in session_file.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except Exception:
            continue

    # Walk backwards: find last assistant text + last user text before it
    last_assistant = ""
    last_user = ""

    for entry in reversed(entries):
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

        if role == "assistant" and not last_assistant:
            last_assistant = text
        elif role == "user" and last_assistant and not last_user:
            last_user = text

        if last_user and last_assistant:
            break

    if not last_assistant:
        sys.exit(0)

    log_entry = json.dumps({
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "user": last_user[:600],
        "assistant": last_assistant[:1200],
        "session_id": session_id,
        "source": "cc-code-tab"
    }, ensure_ascii=True)

    # Append to vault-neo nexus-chat.jsonl via SSH (stdin pipe -- no quoting issues)
    try:
        subprocess.run(
            ["ssh", "vault-neo",
             "cat >> /opt/seed-vault/memory_v1/session/state/nexus-chat.jsonl"],
            input=(log_entry + "\n").encode("ascii", errors="replace"),
            timeout=10,
            capture_output=True
        )
    except Exception:
        pass  # Never block the Stop hook


if __name__ == "__main__":
    main()
