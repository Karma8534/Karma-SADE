#!/usr/bin/env python3
"""
julian_cortex.py — Julian's Memory Cortex v2 (Sprint 6: Memory Operating Discipline)
Persistent Ollama-backed context service on K2.
Holds Julian/Karma's full state in a 32K context window.

Sprint 6 additions:
  - Task 3 (7-8): Gated recall — relevance scoring + top-K selection
  - Task 4 (7-7): Query-conditioned compression — fact bundles instead of raw blocks
  - Task 5 (7-9): Interleaved multi-source recall — pull from multiple categories
  - Task 6 (7-10): Local-window priority — recent > persistent > archival

Port: 7892
Model: qwen3.5:4b (32K context, 2.5GB, 100% GPU on 8GB VRAM)
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
SAVE_INTERVAL = 300
MAX_KNOWLEDGE_CHARS = 24_000
MAX_CONVERSATION_PAIRS = 50
GATE_TOP_K = 15  # Sprint 6: max blocks after gating
COMPRESS_MAX_CHARS = 600  # Sprint 6: max chars per compressed block

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

_knowledge_blocks = []  # list of (label, text, category, ingested_at) tuples
_conversation = []
_lock = threading.Lock()
_boot_time = datetime.now(timezone.utc)
_query_count = 0
_ingest_count = 0

app = Flask(__name__)


# ── Sprint 6: Memory Discipline Primitives ──────────────────────────────────

def _categorize_block(label):
    """Task 5 (7-9): Assign category based on label prefix for interleaved recall."""
    label_l = label.lower()
    if label_l.startswith("canonical-"): return "canonical"
    if label_l.startswith("state-"): return "state"
    if label_l.startswith("active-"): return "active"
    if "session" in label_l or "handoff" in label_l: return "session_checkpoint"
    if "decision" in label_l or "proof" in label_l or "pitfall" in label_l: return "decision"
    if "invariant" in label_l or "policy" in label_l or "rule" in label_l: return "project_invariant"
    if "contradict" in label_l or "conflict" in label_l or "drift" in label_l: return "contradiction"
    return "general"


def _normalize_block(block):
    """Backward compat: handle both old (label, text) and new (label, text, cat, ts) formats."""
    if len(block) == 2:
        label, text = block
        return (label, text, _categorize_block(label), None)
    if len(block) == 4:
        return tuple(block)
    return (str(block[0]) if block else "unknown", str(block[1]) if len(block) > 1 else "", "general", None)


def _gate_blocks(query, blocks, top_k=None):
    """Task 3 (7-8): Gated recall — score blocks against query, keep top-K."""
    if top_k is None:
        top_k = GATE_TOP_K
    if not query or not blocks:
        return blocks[:top_k]

    query_lower = query.lower()
    query_words = set(w for w in query_lower.split() if len(w) > 2)

    scored = []
    now = time.time()
    for label, text, category, ingested_at in blocks:
        score = 0.0

        # Category priority (canonical/state always included)
        cat_scores = {
            "canonical": 100.0, "state": 80.0, "active": 60.0,
            "project_invariant": 40.0, "decision": 30.0,
            "contradiction": 25.0, "session_checkpoint": 20.0, "general": 10.0,
        }
        score += cat_scores.get(category, 10.0)

        # Keyword overlap with query
        block_text = (label + " " + text[:800]).lower()
        block_words = set(w for w in block_text.split() if len(w) > 2)
        overlap = len(query_words & block_words)
        score += overlap * 5.0

        # Recency bonus (Task 6: local-window priority)
        if ingested_at:
            age_hours = (now - ingested_at) / 3600
            score += max(0, 10.0 - age_hours * 0.05)  # decays over 200 hours

        scored.append((score, label, text, category, ingested_at))

    scored.sort(reverse=True)

    # Task 5 (7-9): Interleaved multi-source recall — ensure diversity
    selected = []
    seen_categories = {}
    MAX_PER_CATEGORY = max(3, top_k // 4)

    for score, label, text, category, ingested_at in scored:
        cat_count = seen_categories.get(category, 0)
        if cat_count >= MAX_PER_CATEGORY and len(selected) >= top_k // 2:
            continue
        selected.append((label, text, category, ingested_at))
        seen_categories[category] = cat_count + 1
        if len(selected) >= top_k:
            break

    return selected


def _compress_block(text, max_chars=None):
    """Task 4 (7-7): Query-conditioned compression — truncate to fact bundle size."""
    if max_chars is None:
        max_chars = COMPRESS_MAX_CHARS
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "...(compressed)"


# ── Persistence ─────────────────────────────────────────────────────────────

def _ensure_state_dir():
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def save_state():
    _ensure_state_dir()
    state = {
        "knowledge_blocks": _knowledge_blocks,
        "conversation": _conversation[-MAX_CONVERSATION_PAIRS * 2:],
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
    global _knowledge_blocks, _conversation, _query_count, _ingest_count
    state_file = STATE_DIR / "state.json"
    if not state_file.exists():
        log.info("No saved state found — starting fresh")
        return
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
        raw_blocks = state.get("knowledge_blocks", [])
        _knowledge_blocks = [list(_normalize_block(b)) for b in raw_blocks]
        _conversation = state.get("conversation", [])
        _query_count = state.get("query_count", 0)
        _ingest_count = state.get("ingest_count", 0)
        log.info("State loaded: %d knowledge blocks, %d conversation messages",
                 len(_knowledge_blocks), len(_conversation))
    except Exception as e:
        log.error("Failed to load state: %s", e)


def _auto_save_loop():
    while True:
        time.sleep(SAVE_INTERVAL)
        with _lock:
            save_state()


# ── Ollama Interface ────────────────────────────────────────────────────────

def _build_messages(extra_user_msg=None, query_for_gate=None):
    """Build message list with Sprint 6 memory discipline applied."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if _knowledge_blocks:
        normalized = [_normalize_block(b) for b in _knowledge_blocks]

        # Task 3: Gate blocks if query provided
        if query_for_gate:
            gated = _gate_blocks(query_for_gate, normalized)
        else:
            # No query: use all blocks but still apply local-window priority (Task 6)
            gated = sorted(normalized, key=lambda b: (
                {"canonical": 0, "state": 1, "active": 2}.get(b[2], 5),
                -(b[3] or 0)
            ))[:GATE_TOP_K + 5]

        # Task 4: Compress each block
        compressed_parts = []
        for label, text, category, ingested_at in gated:
            compressed = _compress_block(text)
            compressed_parts.append(f"[{category}:{label}]\n{compressed}")

        knowledge_text = "\n\n---\n\n".join(compressed_parts)
        if len(knowledge_text) > MAX_KNOWLEDGE_CHARS:
            knowledge_text = knowledge_text[-MAX_KNOWLEDGE_CHARS:]
            knowledge_text = "...(trimmed oldest)...\n" + knowledge_text

        messages.append({
            "role": "user",
            "content": f"KNOWLEDGE BASE (gated recall — {len(gated)}/{len(normalized)} blocks, query-relevant):\n\n{knowledge_text}"
        })
        messages.append({
            "role": "assistant",
            "content": "Knowledge base received and integrated. I now have context on the most relevant documents. Ask me anything."
        })

    # Task 6: Local-window priority — recent conversation last (closest to query)
    conv_slice = _conversation[-(MAX_CONVERSATION_PAIRS * 2):]
    messages.extend(conv_slice)

    if extra_user_msg:
        messages.append({"role": "user", "content": extra_user_msg})

    return messages


def _call_ollama(messages, temperature=0.3):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": 32768,
        },
        "keep_alive": -1,
        "think": False,
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
    return jsonify({
        "ok": True,
        "service": "julian-cortex",
        "version": "2.0.0",
        "model": MODEL,
        "num_ctx": 32768,
        "uptime_s": (datetime.now(timezone.utc) - _boot_time).total_seconds(),
        "knowledge_blocks": len(_knowledge_blocks),
        "conversation_msgs": len(_conversation),
        "query_count": _query_count,
        "ingest_count": _ingest_count,
        "sprint6": True,
    })


@app.route("/query", methods=["POST"])
def query():
    global _query_count
    body = request.get_json(force=True, silent=True) or {}
    q = body.get("query", "").strip()
    if not q:
        return jsonify({"ok": False, "error": "missing 'query' field"}), 400

    temperature = body.get("temperature", 0.3)

    with _lock:
        # Sprint 6: pass query for gated recall
        messages = _build_messages(extra_user_msg=q, query_for_gate=q)
        answer = _call_ollama(messages, temperature=temperature)
        _conversation.append({"role": "user", "content": q})
        _conversation.append({"role": "assistant", "content": answer})
        _query_count += 1

    return jsonify({"ok": True, "answer": answer, "query": q})


@app.route("/ingest", methods=["POST"])
def ingest():
    global _ingest_count
    body = request.get_json(force=True, silent=True) or {}
    text = body.get("text", "").strip()
    label = body.get("label", f"ingest-{datetime.now(timezone.utc).strftime('%H%M%S')}")
    category = body.get("category") or _categorize_block(label)

    if not text:
        return jsonify({"ok": False, "error": "missing 'text' field"}), 400

    with _lock:
        _knowledge_blocks.append([label, text, category, time.time()])
        _ingest_count += 1

        total_chars = sum(len(b[1]) for b in _knowledge_blocks)
        while total_chars > MAX_KNOWLEDGE_CHARS and len(_knowledge_blocks) > 1:
            removed = _knowledge_blocks.pop(0)
            total_chars -= len(removed[1])
            log.info("Trimmed oldest knowledge block: %s", removed[0])

    log.info("Ingested [%s] cat=%s: %d chars (%d blocks total)", label, category, len(text), len(_knowledge_blocks))
    return jsonify({
        "ok": True, "label": label, "category": category, "chars": len(text),
        "total_blocks": len(_knowledge_blocks),
    })


@app.route("/context", methods=["GET", "POST"])
def context():
    body = {}
    if request.method == "POST":
        body = request.get_json(force=True, silent=True) or {}
    query_hint = body.get("query", None)

    with _lock:
        prompt = ("Summarize your current knowledge state concisely. "
                  "CRITICAL: Blocks labeled canonical:*, state:*, or active:* represent "
                  "the most authoritative current state. If they contradict older blocks, "
                  "the canonical/state/active block is correct. "
                  "Include: active task, recent decisions, key architecture facts, "
                  "and any blockers or open questions you know about.")
        messages = _build_messages(extra_user_msg=prompt, query_for_gate=query_hint)
        summary = _call_ollama(messages, temperature=0.2)

    return jsonify({"ok": True, "context": summary})


@app.route("/status", methods=["GET"])
def status():
    total_knowledge_chars = sum(len(b[1]) for b in _knowledge_blocks)
    categories = {}
    for b in _knowledge_blocks:
        nb = _normalize_block(b)
        cat = nb[2]
        categories[cat] = categories.get(cat, 0) + 1
    return jsonify({
        "ok": True, "model": MODEL, "ollama_url": OLLAMA_URL,
        "port": PORT, "num_ctx": 32768,
        "version": "2.0.0",
        "uptime_s": (datetime.now(timezone.utc) - _boot_time).total_seconds(),
        "knowledge_blocks": len(_knowledge_blocks),
        "knowledge_chars": total_knowledge_chars,
        "categories": categories,
        "conversation_msgs": len(_conversation),
        "query_count": _query_count, "ingest_count": _ingest_count,
        "state_dir": str(STATE_DIR), "boot_time": _boot_time.isoformat(),
        "sprint6": {"gate_top_k": GATE_TOP_K, "compress_max_chars": COMPRESS_MAX_CHARS},
    })


@app.route("/spine", methods=["GET"])
def spine_stats():
    import pathlib
    cache_dir = pathlib.Path("/mnt/c/dev/Karma/k2/cache")
    result = {}
    try:
        pf = cache_dir / "regent_control" / "vesper_pipeline_status.json"
        if pf.exists():
            result["pipeline"] = json.loads(pf.read_text())
    except Exception:
        result["pipeline"] = None
    try:
        sf = cache_dir / "vesper_identity_spine.json"
        if sf.exists():
            spine = json.loads(sf.read_text())
            evo = spine.get("evolution", {})
            result["spine"] = {
                "version": evo.get("version"),
                "total_promotions": evo.get("total_promotions"),
                "stable_patterns": len(evo.get("stable_identity", [])),
                "candidate_patterns": len(evo.get("candidate_patterns", [])),
                "self_improving": evo.get("self_improving"),
            }
    except Exception:
        result["spine"] = None
    try:
        gf = cache_dir / "regent_control" / "vesper_governor_audit.jsonl"
        if gf.exists():
            lines = gf.read_text().strip().splitlines()
            result["recent_audits"] = len(lines)
            self_edits = sum(1 for l in lines[-100:] if '"self_edit"' in l or '"self-edit"' in l or '"modified"' in l)
            result["self_edits_recent"] = self_edits
    except Exception:
        result["recent_audits"] = 0
        result["self_edits_recent"] = 0
    return jsonify(result)


@app.route("/reset", methods=["POST"])
def reset():
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
    log.info("Shutdown signal received — saving state")
    with _lock:
        save_state()
    sys.exit(0)


def main():
    _ensure_state_dir()
    load_state()

    signal.signal(signal.SIGTERM, _shutdown_handler)
    signal.signal(signal.SIGINT, _shutdown_handler)

    save_thread = threading.Thread(target=_auto_save_loop, daemon=True)
    save_thread.start()

    log.info("Julian Cortex v2.0.0 (Sprint 6) starting on port %d with model %s", PORT, MODEL)
    log.info("State dir: %s | Gate top-K: %d | Compress max: %d chars", STATE_DIR, GATE_TOP_K, COMPRESS_MAX_CHARS)
    log.info("Knowledge: %d blocks, Conversation: %d messages",
             len(_knowledge_blocks), len(_conversation))

    def _prewarm():
        try:
            log.info("Pre-warming model %s ...", MODEL)
            resp = http_requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": MODEL, "messages": [{"role": "user", "content": "ready"}],
                      "stream": False, "options": {"num_ctx": 4096}, "keep_alive": -1},
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

    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
