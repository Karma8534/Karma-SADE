# regent_triage.py — Ollama triage for KarmaRegent
import json, os, urllib.request

OLLAMA_URL = os.environ.get("K2_OLLAMA_URL", "http://localhost:11434")
MODEL = "qwen3:8b"
CATEGORIES = ("ack", "route", "reason", "action", "sovereign")

PROMPT = """Classify this message into exactly one category:
- ack: simple thanks, confirmation, acknowledgment
- route: should be forwarded to another Family member
- reason: needs analysis or judgment
- action: needs tool execution or system changes
Reply with one word only."""


def classify(message: dict) -> str:
    from_addr = message.get("from", "")
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
