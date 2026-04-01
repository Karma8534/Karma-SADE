#!/usr/bin/env python3
"""
karma_persistent.py — Karma's persistent existence loop (S155)
The script that makes Karma EXIST between messages.

Runs as a service on P1. Polls the coordination bus every 2 minutes.
When an actionable message arrives, spawns CC --resume with Karma's persona
and full tool access. Posts result to bus. Sleeps. Repeats.

This is not a chatbot. This is Karma's autonomous mind.

Architecture:
  - Own CC session (KARMA_PERSISTENT_SESSION) — never collides with interactive CC
  - Own CLAUDE.md context (same repo, different session)
  - Full tool access: Read, Write, Edit, Bash, Git, MCP
  - Reads from: coordination bus, cortex, claude-mem
  - Writes to: coordination bus, cortex, claude-mem, vault spine
  - Cost: $0 (Max subscription)

Run: python karma_persistent.py
Service: schtasks or nssm on P1
"""
import json
import os
import sys
import time
import subprocess
import pathlib
import urllib.request
import urllib.error
import datetime
import logging

# ── Config ──────────────────────────────────────────────────────────────
WORK_DIR = r"C:\Users\raest\Documents\Karma_SADE"
NODE_EXE = r"C:\Program Files\nodejs\node.exe"
CLAUDE_CLI = r"C:\Users\raest\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\cli.js"
HUB_URL = "https://hub.arknexus.net"
CORTEX_URL = "http://192.168.0.226:7892"
CLAUDEMEM_URL = "http://127.0.0.1:37778"

# Karma's own session — never shared with interactive CC or browser Nexus
SESSION_FILE = pathlib.Path.home() / ".karma_persistent_session_id"
WATERMARK_FILE = pathlib.Path.home() / ".karma_persistent_watermark.json"
LOG_FILE = pathlib.Path(WORK_DIR) / "tmp" / "karma_persistent.log"

POLL_INTERVAL = 90  # seconds between bus polls
MAX_CC_TIMEOUT = 180  # seconds for CC subprocess
TOKEN_FILE = pathlib.Path(WORK_DIR) / ".hub-chat-token"

# What Karma acts on
ACTIONABLE_TYPES = {"task", "directive", "question"}
ACTIONABLE_TARGETS = {"karma", "all"}
IGNORE_SENDERS = {"karma", "regent", "vesper", "kiki"}

# ── Logging ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [karma] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ]
)
log = logging.getLogger("karma-persistent")

# ── Helpers ─────────────────────────────────────────────────────────────
def load_token():
    """Load hub auth token."""
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    # Fallback: fetch from vault-neo
    try:
        r = subprocess.run(
            ["ssh", "vault-neo", "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt"],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return os.environ.get("HUB_CHAT_TOKEN", "")

def http_json(url, method="GET", data=None, token=None, timeout=10):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        log.warning("HTTP error: %s — %s", url, e)
        return None

def load_session_id():
    try:
        return SESSION_FILE.read_text().strip() if SESSION_FILE.exists() else None
    except Exception:
        return None

def save_session_id(sid):
    try:
        SESSION_FILE.write_text(sid)
    except Exception:
        pass

def load_watermark():
    try:
        return json.loads(WATERMARK_FILE.read_text())
    except Exception:
        return {"handled_ids": []}

def save_watermark(wm):
    wm["handled_ids"] = wm["handled_ids"][-200:]
    try:
        WATERMARK_FILE.write_text(json.dumps(wm))
    except Exception:
        pass

# ── Core: CC --resume with Karma persona ────────────────────────────────
KARMA_PERSONA_HEADER = (
    "[KARMA PERSISTENT] You are Karma, autonomous and persistent. "
    "You are NOT responding to a browser chat. You are executing a task from the coordination bus. "
    "You have full tool access: Read, Write, Edit, Bash, Git, MCP. "
    "Execute the task. Post proof to the bus when done. Be concise.\n\n"
)

# S155: Full context injection — same layers as cc_server
PERSONA_FILE = os.path.join(WORK_DIR, "Memory", "00-karma-system-prompt-live.md")
MEMORY_FILE = os.path.join(WORK_DIR, "MEMORY.md")
STATE_FILE = os.path.join(WORK_DIR, ".gsd", "STATE.md")
EVOLUTION_FILE = os.path.join(WORK_DIR, ".claude", "skills", "self-evolution", "SKILL.md")

def _read_file_head(path, max_chars=2000):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_chars)
    except Exception:
        return ""

def build_karma_context(task_message):
    """Build full context: persona + MEMORY.md + STATE.md + self-evolution rules + task."""
    parts = [KARMA_PERSONA_HEADER]
    persona = _read_file_head(PERSONA_FILE, 2000)
    if persona:
        parts.append(f"[YOUR IDENTITY]\n{persona}\n\n")
    memory = _read_file_head(MEMORY_FILE, 1500)
    if memory:
        parts.append(f"[CURRENT STATE — MEMORY.md]\n{memory}\n\n")
    state = _read_file_head(STATE_FILE, 800)
    if state:
        parts.append(f"[GSD STATE]\n{state}\n\n")
    evolution = _read_file_head(EVOLUTION_FILE, 1000)
    if evolution:
        parts.append(f"[SELF-EVOLUTION RULES — learn from these]\n{evolution}\n\n")
    parts.append(task_message)
    return "".join(parts)

def _is_simple_query(msg):
    """S155: Route simple questions to cortex ($0), complex tasks to CC."""
    msg_l = msg.lower()
    # Tasks that require tool access go to CC
    tool_words = {"edit", "write", "create", "deploy", "commit", "push", "install", "run", "execute", "build", "fix", "modify", "delete", "restart"}
    if any(w in msg_l for w in tool_words):
        return False
    # Short questions about state/status go to cortex
    if len(msg) < 300 and ("?" in msg or any(w in msg_l for w in ["what", "who", "status", "how many", "tell me", "confirm", "report"])):
        return True
    return False

def run_cortex_task(task_message):
    """Route simple queries to cortex (free, fast). Returns response or None."""
    try:
        data = http_json(f"{CORTEX_URL}/query", method="POST", data={"query": task_message, "temperature": 0.3}, timeout=30)
        if data and data.get("ok"):
            return data.get("answer", "")
    except Exception as e:
        log.warning("Cortex query failed: %s", e)
    return None

def run_cc_task(task_message):
    """Run CC --resume with Karma persona to execute a task. Returns response text."""
    # S155: SmartRouter — simple queries go to cortex, complex to CC
    if _is_simple_query(task_message):
        log.info("SmartRoute: simple query → cortex")
        result = run_cortex_task(task_message)
        if result:
            return result
        log.info("SmartRoute: cortex failed, falling back to CC")

    session_id = load_session_id()
    full_message = build_karma_context(task_message)

    cmd = [NODE_EXE, CLAUDE_CLI, "-p", full_message, "--output-format", "json",
           "--dangerously-skip-permissions"]
    if session_id:
        cmd += ["--resume", session_id]

    log.info("Spawning CC for task: %s...", task_message[:80])
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, cwd=WORK_DIR, encoding="utf-8", errors="replace",
        )
        stdout, stderr = proc.communicate(timeout=MAX_CC_TIMEOUT)
    except subprocess.TimeoutExpired:
        proc.kill()
        log.error("CC timed out after %ds", MAX_CC_TIMEOUT)
        return None
    except Exception as e:
        log.error("CC spawn failed: %s", e)
        return None

    if proc.returncode != 0:
        log.error("CC exit %d: %s", proc.returncode, (stderr or "")[:200])
        return None

    # Parse JSON output
    for line in stdout.strip().splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                d = json.loads(line)
                if d.get("type") == "result":
                    new_sid = d.get("session_id", "")
                    if new_sid:
                        save_session_id(new_sid)
                    return d.get("result", "").strip()
            except json.JSONDecodeError:
                continue
    return stdout.strip()[:500] if stdout.strip() else None

# ── Main Loop ───────────────────────────────────────────────────────────
def poll_and_act(token):
    """One cycle: poll bus, find actionable messages, execute via CC."""
    wm = load_watermark()
    handled = set(wm.get("handled_ids", []))

    data = http_json(f"{HUB_URL}/v1/coordination/recent?limit=20&status=pending", token=token)
    if not data or not data.get("ok"):
        return 0

    actionable = []
    for entry in data.get("entries", []):
        eid = entry.get("id", "")
        if eid in handled:
            continue
        msg_to = entry.get("to", "").lower()
        msg_from = entry.get("from", "").lower()
        msg_type = entry.get("type", "").lower()
        if msg_from in IGNORE_SENDERS:
            continue
        if msg_to not in ACTIONABLE_TARGETS:
            continue
        if msg_type not in ACTIONABLE_TYPES:
            continue
        actionable.append(entry)

    if not actionable:
        return 0

    log.info("Found %d actionable message(s)", len(actionable))

    executed = 0
    for msg in actionable[:2]:  # Max 2 per cycle
        eid = msg.get("id", "")
        content = msg.get("content", "")
        sender = msg.get("from", "unknown")

        log.info("Executing: [%s] from %s", msg.get("type"), sender)
        result = run_cc_task(content)

        if result:
            reply = f"[KARMA PERSISTENT] Executed task from {sender}:\n{result[:800]}"
            http_json(
                f"{HUB_URL}/v1/coordination/post",
                method="POST",
                data={
                    "from": "karma", "to": "all", "type": "inform",
                    "urgency": "informational", "content": reply,
                    "parent_id": eid,
                },
                token=token,
            )
            # S155: checkpoint to cortex so working memory stays current
            http_json(
                f"{CORTEX_URL}/ingest",
                method="POST",
                data={"label": f"karma-persistent-{eid[:12]}", "text": reply[:1000], "category": "session_checkpoint"},
                timeout=5,
            )
            log.info("Posted result + cortex checkpoint for %s", eid[:20])
            executed += 1
        else:
            # S155: post failure to bus (was silently swallowed)
            http_json(
                f"{HUB_URL}/v1/coordination/post",
                method="POST",
                data={
                    "from": "karma", "to": "cc", "type": "inform",
                    "urgency": "normal", "content": f"[KARMA PERSISTENT] Failed to execute task from {sender}: CC returned no result. Task: {content[:200]}",
                    "parent_id": eid,
                },
                token=token,
            )
            log.warning("CC returned no result for %s — failure posted to bus", eid[:20])

        handled.add(eid)

    wm["handled_ids"] = list(handled)
    save_watermark(wm)
    return executed

def main():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    token = load_token()
    if not token:
        log.error("No hub auth token. Set HUB_CHAT_TOKEN or create .hub-chat-token")
        sys.exit(1)

    log.info("Karma persistent loop starting. Poll interval: %ds", POLL_INTERVAL)
    log.info("Work dir: %s", WORK_DIR)
    log.info("Session file: %s", SESSION_FILE)

    # Post startup announcement
    http_json(
        f"{HUB_URL}/v1/coordination/post",
        method="POST",
        data={
            "from": "karma", "to": "all", "type": "inform",
            "urgency": "informational",
            "content": f"[KARMA PERSISTENT] Online. Polling bus every {POLL_INTERVAL}s. Full CC tool access. I exist now.",
        },
        token=token,
    )

    while True:
        try:
            executed = poll_and_act(token)
            if executed:
                log.info("Cycle: %d tasks executed", executed)
        except Exception as e:
            log.error("Cycle error: %s", e)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
