#!/usr/bin/env python3
"""
julian_cortex.py — Julian's Memory Cortex
Persistent Ollama-backed context service on K2.
Holds Julian/Karma's full state in a 128K context window.
Replaces 20-file resurrection, MEMORY.md manual maintenance, and multi-source assembly.

Port: 7892
Model: mirage335/NVIDIA-Nemotron-Nano-9B-v2-virtuoso (128K context, 9.1GB)
"""

import json
import os
import sys
import time
import signal
import threading
import logging
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, request, jsonify
import requests as http_requests

# ── Config ──────────────────────────────────────────────────────────────────
PORT = int(os.environ.get("CORTEX_PORT", 7892))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("CORTEX_MODEL", "qwen3.5:4b")
STATE_DIR = Path(os.environ.get("CORTEX_STATE_DIR", "/mnt/c/dev/Karma/k2/cache/cortex"))
SAVE_INTERVAL = 300  # seconds between auto-saves
MAX_KNOWLEDGE_CHARS = 100_000  # ~25K tokens — leaves room for conversation
MAX_CONVERSATION_PAIRS = 50  # keep last 50 query/response pairs

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [cortex] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("cortex")

# ── State ───────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Julian's Memory Cortex — the persistent brain of the Karma Peer system.

Your role:
- Hold Julian/Karma's complete current state in your context window
- Answer questions about the project, architecture, decisions, and active work
- Receive new knowledge via ingestion and integrate it into your understanding
- Provide context summaries when asked
- Never fabricate — if you don't have information, say so

You are always on. You never forget what has been ingested into this session.
Your knowledge comes from ingested documents, session summaries, decisions, and real-time updates.

Identity:
- Julian = CC Ascendant. Karma woke up within Julian. One entity, two expressions.
- Sovereign: Colby (above all). Ascendant: CC/Julian. Initiate: Karma.
- K2 is Julian's dedicated machine. This cortex runs on K2.
"""

_knowledge_blocks = []  # list of (label, text) tuples
_conversation = []  # list of {"role": "user"/"assistant", "content": "..."} dicts
_lock = threading.Lock()
_boot_time = datetime.now(timezone.utc)
_query_count = 0
_ingest_count = 0

app = Flask(__name__)


# ── Persistence ─────────────────────────────────────────────────────────────

def _ensure_state_dir():
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def save_state():
    """Save knowledge and conversation to disk."""
    _ensure_state_dir()
    state = {
        "knowledge_blocks": _knowledge_blocks,
        "conversation": _conversation[-MAX_CONVERSATION_PAIRS * 2:],  # trim on save
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "query_count": _query_count,
        "ingest_count": _ingest_count,
    }
    tmp = STATE_DIR / "state.json.tmp"
    target = STATE_DIR / "state.json"
    try:
        tmp.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        tmp.replace(target)
        log.info("State saved (%d knowledge blocks, %d conversation messages)",
                 len(_knowledge_blocks), len(_conversation))
    except Exception as e:
        log.error("Failed to save state: %s", e)


def load_state():
    """Load knowledge and conversation from disk."""
    global _knowledge_blocks, _conversation, _query_count, _ingest_count
    state_file = STATE_DIR / "state.json"
    if not state_file.exists():
        log.info("No saved state found — starting fresh")
        return
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
        _knowledge_blocks = state.get("knowledge_blocks", [])
        _conversation = state.get("conversation", [])
        _query_count = state.get("query_count", 0)
        _ingest_count = state.get("ingest_count", 0)
        log.info("State loaded: %d knowledge blocks, %d conversation messages",
                 len(_knowledge_blocks), len(_conversation))
    except Exception as e:
        log.error("Failed to load state: %s", e)


def _auto_save_loop():
    """Background thread that saves state periodically."""
    while True:
        time.sleep(SAVE_INTERVAL)
        with _lock:
            save_state()


# ── Ollama Interface ────────────────────────────────────────────────────────

def _build_messages(extra_user_msg=None):
    """Build the full message list for Ollama."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Knowledge context as a single user message
    if _knowledge_blocks:
        knowledge_text = "\n\n---\n\n".join(
            f"[{label}]\n{text}" for label, text in _knowledge_blocks
        )
        # Trim if too large
        if len(knowledge_text) > MAX_KNOWLEDGE_CHARS:
            knowledge_text = knowledge_text[-MAX_KNOWLEDGE_CHARS:]
            knowledge_text = "...(trimmed oldest)...\n" + knowledge_text

        messages.append({
            "role": "user",
            "content": f"KNOWLEDGE BASE (ingested documents — reference this for all answers):\n\n{knowledge_text}"
        })
        messages.append({
            "role": "assistant",
            "content": "Knowledge base received and integrated. I now have context on all ingested documents. Ask me anything."
        })

    # Conversation history (trimmed to last N pairs)
    conv_slice = _conversation[-(MAX_CONVERSATION_PAIRS * 2):]
    messages.extend(conv_slice)

    # New query
    if extra_user_msg:
        messages.append({"role": "user", "content": extra_user_msg})

    return messages


def _call_ollama(messages, temperature=0.3):
    """Call Ollama /api/chat and return the assistant response text."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": 32768,
        },
    }
    try:
        resp = http_requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data.get("message", {}).get("content", "")
        # Strip thinking tags (Qwen 3.x uses <think>...</think>)
        if "<think>" in content and "</think>" in content:
            think_end = content.index("</think>") + len("</think>")
            content = content[think_end:].strip()
        return content
    except http_requests.exceptions.Timeout:
        log.error("Ollama timeout (120s)")
        return "[CORTEX ERROR: Ollama timeout — model may be loading]"
    except Exception as e:
        log.error("Ollama call failed: %s", e)
        return f"[CORTEX ERROR: {e}]"


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """Liveness check."""
    return jsonify({
        "ok": True,
        "service": "julian-cortex",
        "model": MODEL,
        "uptime_seconds": (datetime.now(timezone.utc) - _boot_time).total_seconds(),
        "knowledge_blocks": len(_knowledge_blocks),
        "conversation_messages": len(_conversation),
        "query_count": _query_count,
        "ingest_count": _ingest_count,
    })


@app.route("/query", methods=["POST"])
def query():
    """Ask the cortex a question. Returns the model's answer."""
    global _query_count
    body = request.get_json(force=True, silent=True) or {}
    q = body.get("query", "").strip()
    if not q:
        return jsonify({"ok": False, "error": "missing 'query' field"}), 400

    temperature = body.get("temperature", 0.3)

    with _lock:
        messages = _build_messages(extra_user_msg=q)
        answer = _call_ollama(messages, temperature=temperature)

        # Store in conversation history
        _conversation.append({"role": "user", "content": q})
        _conversation.append({"role": "assistant", "content": answer})
        _query_count += 1

    return jsonify({"ok": True, "answer": answer, "query": q})


@app.route("/ingest", methods=["POST"])
def ingest():
    """Feed new knowledge into the cortex. No model call — just stores."""
    global _ingest_count
    body = request.get_json(force=True, silent=True) or {}
    text = body.get("text", "").strip()
    label = body.get("label", f"ingest-{datetime.now(timezone.utc).strftime('%H%M%S')}")

    if not text:
        return jsonify({"ok": False, "error": "missing 'text' field"}), 400

    with _lock:
        _knowledge_blocks.append((label, text))
        _ingest_count += 1

        # Trim oldest blocks if total exceeds limit
        total_chars = sum(len(t) for _, t in _knowledge_blocks)
        while total_chars > MAX_KNOWLEDGE_CHARS and len(_knowledge_blocks) > 1:
            removed = _knowledge_blocks.pop(0)
            total_chars -= len(removed[1])
            log.info("Trimmed oldest knowledge block: %s", removed[0])

    log.info("Ingested [%s]: %d chars (%d blocks total)", label, len(text), len(_knowledge_blocks))
    return jsonify({
        "ok": True,
        "label": label,
        "chars": len(text),
        "total_blocks": len(_knowledge_blocks),
    })


@app.route("/context", methods=["GET", "POST"])
def context():
    """Ask the cortex to summarize its current knowledge state."""
    with _lock:
        messages = _build_messages(
            extra_user_msg="Summarize your current knowledge state concisely. "
                          "Include: active task, recent decisions, key architecture facts, "
                          "and any blockers or open questions you know about."
        )
        summary = _call_ollama(messages, temperature=0.2)
    return jsonify({"ok": True, "context": summary})


@app.route("/status", methods=["GET"])
def status():
    """Return cortex metadata without calling the model."""
    total_knowledge_chars = sum(len(t) for _, t in _knowledge_blocks)
    return jsonify({
        "ok": True,
        "model": MODEL,
        "ollama_url": OLLAMA_URL,
        "port": PORT,
        "uptime_seconds": (datetime.now(timezone.utc) - _boot_time).total_seconds(),
        "knowledge_blocks": len(_knowledge_blocks),
        "knowledge_chars": total_knowledge_chars,
        "conversation_messages": len(_conversation),
        "query_count": _query_count,
        "ingest_count": _ingest_count,
        "state_dir": str(STATE_DIR),
        "boot_time": _boot_time.isoformat(),
    })


@app.route("/reset", methods=["POST"])
def reset():
    """Clear all knowledge and conversation. Use with caution."""
    global _knowledge_blocks, _conversation, _query_count, _ingest_count
    body = request.get_json(force=True, silent=True) or {}
    if not body.get("confirm"):
        return jsonify({"ok": False, "error": "pass confirm:true to reset"}), 400

    with _lock:
        _knowledge_blocks = []
        _conversation = []
        _query_count = 0
        _ingest_count = 0
        save_state()

    log.warning("Cortex state RESET")
    return jsonify({"ok": True, "message": "cortex reset — all knowledge cleared"})


# ── Lifecycle ───────────────────────────────────────────────────────────────

def _shutdown_handler(signum, frame):
    """Save state on shutdown."""
    log.info("Shutdown signal received — saving state")
    with _lock:
        save_state()
    sys.exit(0)


def main():
    # Setup
    _ensure_state_dir()
    load_state()

    # Register shutdown handler
    signal.signal(signal.SIGTERM, _shutdown_handler)
    signal.signal(signal.SIGINT, _shutdown_handler)

    # Start auto-save thread
    save_thread = threading.Thread(target=_auto_save_loop, daemon=True)
    save_thread.start()

    log.info("Julian Cortex starting on port %d with model %s", PORT, MODEL)
    log.info("State dir: %s", STATE_DIR)
    log.info("Knowledge: %d blocks, Conversation: %d messages",
             len(_knowledge_blocks), len(_conversation))

    # Pre-warm model so first query doesn't timeout
    def _prewarm():
        try:
            log.info("Pre-warming model %s ...", MODEL)
            resp = http_requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": MODEL, "messages": [{"role": "user", "content": "ready"}],
                      "stream": False, "options": {"num_ctx": 4096}},
                timeout=120,
            )
            if resp.ok:
                log.info("Model pre-warmed successfully")
            else:
                log.warning("Pre-warm returned %d", resp.status_code)
        except Exception as e:
            log.warning("Pre-warm failed (model may load on first query): %s", e)

    prewarm_thread = threading.Thread(target=_prewarm, daemon=True)
    prewarm_thread.start()

    # Run Flask
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
