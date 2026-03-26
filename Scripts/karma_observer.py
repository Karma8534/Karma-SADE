#!/usr/bin/env python3
"""Karma Observer — extracts behavioral rules from Karma's conversation history.

Polls vault-neo ledger (via FAISS search) for correction patterns,
extracts behavioral rules, writes to karma_behavioral_rules.jsonl,
and POSTs each new rule to /v1/ambient for FAISS indexing.

Run by systemd timer every 15 minutes on K2.
"""
import json, os, sys, hashlib, datetime, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# === Configuration ===
HUB_URL = os.environ.get("HUB_URL", "https://hub.arknexus.net")
TOKEN_PATH = os.environ.get("TOKEN_PATH", "/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")
# K2 local paths
CACHE_DIR = Path(os.environ.get("KARMA_OBSERVER_CACHE", "/mnt/c/dev/Karma/k2/cache"))
RULES_FILE = CACHE_DIR / "karma_behavioral_rules.jsonl"
WATERMARK_FILE = CACHE_DIR / "karma_observer_watermark.json"
MAX_RULES = 50  # cap total rules to prevent bloat

# Patterns that indicate a behavioral correction
CORRECTION_MARKERS = [
    "[karma-correction]",
    "[PITFALL]",
    "thumbs-down",
    "dpo-pair",
    "correction:",
    "don't do this",
    "stop doing",
    "wrong approach",
    "not what I asked",
    "too verbose",
    "too long",
    "hallucinating",
    "confabulating",
    "made up",
    "that's wrong",
    "incorrect",
]

# Search queries to find correction patterns in ledger
SEARCH_QUERIES = [
    "karma-correction behavioral rule",
    "thumbs-down karma response feedback",
    "PITFALL karma behavioral pattern",
    "Colby correction Karma wrong",
    "dpo-pair negative feedback",
]


def _load_token():
    """Load hub auth token. Try local file first, then SSH."""
    if os.path.exists(TOKEN_PATH):
        return open(TOKEN_PATH).read().strip()
    # Fallback: read from env
    return os.environ.get("HUB_CHAT_TOKEN", "")


def _http_post(url, data, token):
    """POST JSON to URL with Bearer auth."""
    payload = json.dumps(data).encode()
    req = Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except (URLError, HTTPError) as e:
        print(f"[karma-observer] HTTP error: {e}")
        return None


def _search_vault(query, token, limit=20):
    """Search vault via FAISS endpoint."""
    url = f"{HUB_URL}/v1/search"
    # Try the anr-vault-search endpoint via hub-bridge proxy or direct
    result = _http_post(url, {"query": query, "limit": limit}, token)
    if result and result.get("results"):
        return result["results"]
    # Fallback: try the hub-bridge semantic search path
    return []


def _search_claude_mem(query, token):
    """Search claude-mem via /memory/search on hub-bridge."""
    url = f"{HUB_URL}/memory/search"
    result = _http_post(url, {"query": query}, token)
    if result and result.get("ok"):
        return result.get("content", [])
    return []


def _load_watermark():
    """Load processing watermark."""
    if WATERMARK_FILE.exists():
        try:
            return json.loads(WATERMARK_FILE.read_text())
        except Exception:
            pass
    return {"last_run": None, "rule_hashes": []}


def _save_watermark(wm):
    """Save processing watermark."""
    WATERMARK_FILE.parent.mkdir(parents=True, exist_ok=True)
    WATERMARK_FILE.write_text(json.dumps(wm, indent=2))


def _load_existing_rules():
    """Load existing rules from JSONL."""
    rules = []
    if RULES_FILE.exists():
        for line in RULES_FILE.read_text().splitlines():
            if line.strip():
                try:
                    rules.append(json.loads(line))
                except Exception:
                    pass
    return rules


def _rule_hash(rule_text):
    """Fingerprint a rule for dedup."""
    return hashlib.sha256(rule_text.lower().strip().encode()).hexdigest()[:16]


def _extract_rules_from_text(text, source_id="unknown"):
    """Extract behavioral rules from a text block.

    Uses keyword matching + structural patterns. No LLM needed.
    Returns list of rule dicts.
    """
    rules = []
    lines = text.split("\n") if isinstance(text, str) else []

    for i, line in enumerate(lines):
        line_lower = line.lower().strip()

        # Direct correction markers
        for marker in CORRECTION_MARKERS:
            if marker.lower() in line_lower:
                # Extract the rule: use this line + context
                context_lines = lines[max(0, i-1):min(len(lines), i+3)]
                rule_text = " ".join(l.strip() for l in context_lines if l.strip())

                # Determine confidence from marker type
                confidence = 0.8
                if "[karma-correction]" in line_lower:
                    confidence = 0.95
                elif "[pitfall]" in line_lower:
                    confidence = 0.90
                elif "thumbs-down" in line_lower or "dpo-pair" in line_lower:
                    confidence = 0.85
                elif any(w in line_lower for w in ["wrong", "incorrect", "hallucinating"]):
                    confidence = 0.80
                elif any(w in line_lower for w in ["too verbose", "too long"]):
                    confidence = 0.75

                # Truncate long rules
                if len(rule_text) > 300:
                    rule_text = rule_text[:297] + "..."

                rules.append({
                    "rule": rule_text,
                    "confidence": confidence,
                    "source_episode": source_id,
                    "marker": marker,
                    "extracted_at": datetime.datetime.utcnow().isoformat() + "Z",
                    "applied": False,
                })
                break  # one rule per line

    return rules


def search_and_extract(token):
    """Main extraction loop: search vault, extract rules, deduplicate."""
    all_new_rules = []
    wm = _load_watermark()
    existing_hashes = set(wm.get("rule_hashes", []))

    # Search vault FAISS for correction patterns
    for query in SEARCH_QUERIES:
        results = _search_vault(query, token, limit=10)
        for result in results:
            content = result.get("content", "") or result.get("text", "")
            source_id = result.get("id", "vault-search")
            extracted = _extract_rules_from_text(content, source_id=str(source_id))

            for rule in extracted:
                h = _rule_hash(rule["rule"])
                if h not in existing_hashes:
                    rule["hash"] = h
                    all_new_rules.append(rule)
                    existing_hashes.add(h)

    # Also search claude-mem for corrections
    for query in ["karma-correction", "PITFALL behavioral", "thumbs-down karma"]:
        results = _search_claude_mem(query, token)
        for item in results:
            text = item.get("text", "") if isinstance(item, dict) else str(item)
            extracted = _extract_rules_from_text(text, source_id="claude-mem")

            for rule in extracted:
                h = _rule_hash(rule["rule"])
                if h not in existing_hashes:
                    rule["hash"] = h
                    all_new_rules.append(rule)
                    existing_hashes.add(h)

    return all_new_rules, existing_hashes


def persist_rules(new_rules, existing_hashes):
    """Write new rules to JSONL and POST to /v1/ambient."""
    if not new_rules:
        print("[karma-observer] no new rules extracted")
        return 0

    token = _load_token()

    # Append to JSONL
    RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RULES_FILE, "a") as f:
        for rule in new_rules:
            f.write(json.dumps(rule) + "\n")

    # POST each rule to /v1/ambient for FAISS indexing
    posted = 0
    for rule in new_rules:
        ambient_payload = {
            "content": f"[KARMA-BEHAVIORAL-RULE] {rule['rule']}",
            "tags": ["karma-behavioral-rule", "karma-observer", "auto-extracted"],
            "source": "karma-observer",
            "type": "behavioral_rule",
        }
        result = _http_post(f"{HUB_URL}/v1/ambient", ambient_payload, token)
        if result:
            posted += 1
        time.sleep(0.5)  # rate limit courtesy

    # Cap total rules
    existing = _load_existing_rules()
    if len(existing) > MAX_RULES:
        # Keep highest confidence rules
        existing.sort(key=lambda r: r.get("confidence", 0), reverse=True)
        existing = existing[:MAX_RULES]
        RULES_FILE.write_text("\n".join(json.dumps(r) for r in existing) + "\n")
        print(f"[karma-observer] capped rules to {MAX_RULES} (by confidence)")

    # Update watermark
    wm = _load_watermark()
    wm["last_run"] = datetime.datetime.utcnow().isoformat() + "Z"
    wm["rule_hashes"] = list(existing_hashes)
    wm["total_rules"] = len(_load_existing_rules())
    _save_watermark(wm)

    print(f"[karma-observer] {len(new_rules)} new rules extracted, {posted} posted to /v1/ambient")
    return len(new_rules)


def main():
    print(f"[karma-observer] {datetime.datetime.utcnow().isoformat()}Z — running")

    token = _load_token()
    if not token:
        print("[karma-observer] ERROR: no auth token found. Set HUB_CHAT_TOKEN env or check TOKEN_PATH.")
        sys.exit(1)

    new_rules, existing_hashes = search_and_extract(token)
    count = persist_rules(new_rules, existing_hashes)

    print(f"[karma-observer] done. {count} new rules. "
          f"Total: {len(_load_existing_rules())} rules in {RULES_FILE}")


if __name__ == "__main__":
    main()
