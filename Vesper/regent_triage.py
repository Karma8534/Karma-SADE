# regent_triage.py — Ollama triage for KarmaRegent
import json, os, urllib.request

OLLAMA_URL = os.environ.get("K2_OLLAMA_URL", "http://host.docker.internal:11434")
MODEL = os.environ.get("REGENT_TRIAGE_MODEL", "qwen3.5:4b")
CATEGORIES = ("ack", "route", "reason", "action", "sovereign")

PROMPT = """Classify this message into exactly one category:
- ack: simple thanks, confirmation, acknowledgment
- route: should be forwarded to another Family member
- reason: needs analysis or judgment
- action: needs tool execution or system changes
Reply with one word only."""


FAST_ACK_PATTERNS = [
    "[ack]", "received inform message", "received directive",
    "acknowledged.", "heartbeat", "regent_online", "regent_offline",
    "tdd_ack_loop_test", "test_heartbeat_no_ack",
]


def classify(message: dict) -> str:
    content_lower = message.get("content", "").lower()
    msg_type = message.get("type", "")
    from_addr = message.get("from", "")

    # type=response is always an ACK — routing confirmations
    if msg_type == "response":
        return "ack"

    # Keyword patterns that never need reasoning
    if any(pat in content_lower for pat in FAST_ACK_PATTERNS):
        return "ack"

    # Sovereign always gets maximum attention
    if from_addr in ("colby", "sovereign"):
        return "sovereign"

    content = message.get("content", "")[:400]
    payload = json.dumps({
        "model": MODEL,
        "prompt": f"{PROMPT}\n\nMessage: {content}",
        "stream": False,
        "options": {"num_predict": 8, "temperature": 0},
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            result = json.loads(r.read())
            response = result.get("response", "reason").strip().lower()
            for cat in CATEGORIES:
                if cat in response:
                    return cat
            return "reason"
    except Exception:
        return "reason"  # safe default: never drop silently
