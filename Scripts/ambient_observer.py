"""
ambient_observer.py — K-3 Echo Integration
Observes coordination bus signals and generates behavioral insights via Ollama.
Called from aria_consciousness.py Echo step as: observe(cycle_id) -> list[dict]
"""
import json
import os
import datetime
import urllib.request
import urllib.error
from pathlib import Path

# From K2 WSL: bus is on vault-neo public endpoint; Ollama is Windows-side via host.docker.internal
COORDINATION_BUS_URL = "https://hub.arknexus.net/v1/coordination/recent?limit=50"
OLLAMA_URL = "http://host.docker.internal:11434/v1/chat/completions"
OLLAMA_MODEL = "nemotron-mini:optimized"
HUB_AUTH_TOKEN = os.environ.get("HUB_AUTH_TOKEN", "")
EVOLUTION_LOG = Path("/mnt/c/dev/Karma/k2/cache/regent_evolution.jsonl")
DEDUP_HOURS = 6
MIN_SIGNAL_MESSAGES = 3  # K-3 Task 9: require at least 3 non-noise messages

# K-3 Task 9: prefixes that identify heartbeat/noise messages — skip before analysis
NOISE_CONTENT_PREFIXES = (
    "HEARTBEAT:",
    "SESSION WRAP",
    "SESSION CHECKPOINT",
    "SESSION START",
    "CC SESSION",
    "INSIGHT: CC WATCHDOG",
)

STOPWORDS = {
    "the", "a", "an", "is", "in", "it", "of", "to", "and", "for", "on",
    "at", "be", "by", "as", "or", "from", "with", "that", "this", "are",
    "was", "has", "not", "but", "have", "had", "its", "can", "will", "all",
    "i", "you", "we", "they", "he", "she", "my", "your", "our", "their",
    "no", "so", "do", "if", "up", "out", "me", "him", "us", "them",
    "cc", "karma", "colby", "regent", "aria", "vesper",  # project-specific noise
    # K-3 Task 9: heartbeat-specific noise words
    "heartbeat", "online", "processed", "messages", "evolve", "continue",
    "aliases", "runtime", "89831", "status", "complete",
}


def _is_noise_message(msg: dict) -> bool:
    """Return True if this message is a heartbeat or system log — not a behavioral signal."""
    content = (msg.get("content", "") or "").strip()
    return any(content.startswith(prefix) for prefix in NOISE_CONTENT_PREFIXES)


def _get_last_ambient_ts() -> datetime.datetime | None:
    """Return timestamp of most recent ambient_observer entry, or None."""
    if not EVOLUTION_LOG.exists():
        return None
    last_ts = None
    try:
        with open(EVOLUTION_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("source") == "ambient_observer":
                        ts_str = entry.get("ts", "")
                        if ts_str:
                            ts = datetime.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                            if last_ts is None or ts > last_ts:
                                last_ts = ts
                except (json.JSONDecodeError, ValueError):
                    continue
    except OSError:
        return None
    return last_ts


def _fetch_bus_signals() -> list[dict]:
    """Fetch recent coordination bus messages."""
    try:
        headers = {}
        if HUB_AUTH_TOKEN:
            headers["Authorization"] = f"Bearer {HUB_AUTH_TOKEN}"
        req = urllib.request.Request(COORDINATION_BUS_URL, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return data.get("entries", data.get("messages", data.get("items", [])))
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return []
    return []


def _extract_signal_batch(messages: list[dict]) -> dict:
    """Extract unique senders, frequency, and top topic words from messages."""
    senders = set()
    word_counts: dict[str, int] = {}

    for msg in messages:
        sender = msg.get("from", "")
        if sender:
            senders.add(sender)
        content = msg.get("content", "") or ""
        for word in content.lower().split():
            clean = word.strip(".,!?;:\"'()[]{}").lower()
            if len(clean) > 3 and clean not in STOPWORDS:
                word_counts[clean] = word_counts.get(clean, 0) + 1

    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "senders": sorted(senders),
        "message_count": len(messages),
        "top_words": [w for w, _ in top_words],
    }


def _call_ollama(prompt: str) -> str:
    """Call Ollama nemotron-mini and return the response text."""
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 120,
        "stream": False,
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            OLLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
            return data["choices"][0]["message"]["content"].strip()
    except (urllib.error.URLError, json.JSONDecodeError, KeyError, OSError):
        return ""


def _write_entry(entry: dict) -> None:
    """Append entry to regent_evolution.jsonl."""
    EVOLUTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(EVOLUTION_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def observe(cycle_id: str) -> list[dict]:
    """
    Main entry point called from aria_consciousness.py Echo step.
    Returns list of entries written (empty = nothing new this cycle).
    """
    # Dedup: skip if last ambient entry was < DEDUP_HOURS ago
    last_ts = _get_last_ambient_ts()
    if last_ts is not None:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        if last_ts.tzinfo is None:
            last_ts = last_ts.replace(tzinfo=datetime.timezone.utc)
        age_hours = (now_utc - last_ts).total_seconds() / 3600
        if age_hours < DEDUP_HOURS:
            return []

    # Fetch signals
    all_messages = _fetch_bus_signals()
    if not all_messages:
        return []

    # K-3 Task 9: filter noise (heartbeats, session logs) before analysis
    signal_messages = [m for m in all_messages if not _is_noise_message(m)]
    if len(signal_messages) < MIN_SIGNAL_MESSAGES:
        return []  # Not enough meaningful signal — skip this cycle

    batch = _extract_signal_batch(signal_messages)
    if not batch["senders"] and not batch["top_words"]:
        return []

    # Build Ollama prompt
    prompt = (
        f"Given these coordination bus signals from the last hour: "
        f"senders={batch['senders']}, message_count={batch['message_count']}, "
        f"top_topics={batch['top_words']}. "
        f"What is one specific behavioral pattern or insight you observe about the work context? "
        f"One sentence, factual, specific."
    )
    insight = _call_ollama(prompt)
    if not insight:
        return []

    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = {
        "ts": ts,
        "source": "ambient_observer",
        "cycle_id": cycle_id,
        "insight": insight,
        "signal_count": batch["message_count"],
        "signal_messages": len(signal_messages),
        "senders": batch["senders"],
        "top_words": batch["top_words"],
    }
    _write_entry(entry)
    return [entry]
