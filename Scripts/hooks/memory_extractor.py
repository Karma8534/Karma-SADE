"""memory_extractor.py — Stop + SessionEnd handler.
Extracts DECISION/PROOF/PITFALL/DIRECTION/INSIGHT events from recent context,
saves to claude-mem via HTTP.
"""
import json, sys, os, re, urllib.request, urllib.error

CLAUDEMEM_URL = os.environ.get("CLAUDEMEM_URL", "http://localhost:37777")


def _save_to_claudemem(title: str, text: str, project: str = "Karma_SADE") -> bool:
    """Save observation to claude-mem (fire-and-forget)."""
    try:
        payload = json.dumps({"title": title, "text": text, "project": project}).encode()
        req = urllib.request.Request(
            f"{CLAUDEMEM_URL}/api/memory/save",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status == 200
    except Exception:
        return False


def _extract_events(text: str) -> list[dict]:
    """Extract DECISION/PROOF/PITFALL/DIRECTION/INSIGHT markers from text."""
    events = []
    patterns = [
        (r'\b(DECISION)[:\s]+(.+?)(?:\n|$)', "DECISION"),
        (r'\b(PROOF)[:\s]+(.+?)(?:\n|$)', "PROOF"),
        (r'\b(PITFALL)[:\s]+(.+?)(?:\n|$)', "PITFALL"),
        (r'\b(DIRECTION)[:\s]+(.+?)(?:\n|$)', "DIRECTION"),
        (r'\b(INSIGHT)[:\s]+(.+?)(?:\n|$)', "INSIGHT"),
    ]
    for pattern, event_type in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            events.append({"type": event_type, "content": match.group(2).strip()[:500]})
    return events


def handle(context: dict) -> dict:
    """Extract memory events from session context and save to claude-mem."""
    # Gather text from various context sources
    sources = []
    if context.get("assistant_text"):
        sources.append(context["assistant_text"])
    if context.get("tool_results"):
        for tr in context["tool_results"]:
            if isinstance(tr, str):
                sources.append(tr[:2000])
    if context.get("session_summary"):
        sources.append(context["session_summary"])

    full_text = "\n".join(sources)
    if not full_text:
        return {}

    events = _extract_events(full_text)
    if not events:
        return {}

    saved = 0
    for event in events[:10]:  # Cap at 10 per invocation
        title = f"{event['type']}: {event['content'][:80]}"
        text = f"[{event['type']}] {event['content']}"
        if _save_to_claudemem(title, text):
            saved += 1

    return {"systemMessage": f"Extracted {len(events)} memory events, saved {saved} to claude-mem."}


if __name__ == "__main__":
    if "--test" in sys.argv:
        events = _extract_events(
            "DECISION: Use Option A for foundations.\n"
            "PROOF: hooks engine fires correctly.\n"
            "PITFALL: partial document updates cause stale data.\n"
        )
        assert len(events) == 3, f"Expected 3 events, got {len(events)}"
        assert events[0]["type"] == "DECISION"
        assert events[1]["type"] == "PROOF"
        assert events[2]["type"] == "PITFALL"
        print("PASS")
        sys.exit(0)

    ctx = json.loads(sys.stdin.read())
    output = handle(ctx)
    print(json.dumps(output))
