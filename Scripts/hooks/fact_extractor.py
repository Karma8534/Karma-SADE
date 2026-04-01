"""fact_extractor.py — PostToolUse handler (Sprint 4b).
Auto-extracts key facts from tool results and saves to claude-mem.
Triggered after: WebSearch, WebFetch, Read, Grep, Glob, graph_query.
Cap: 2KB per extraction, 50 per session.
"""
import json, sys, os, re, threading, urllib.request, urllib.error

CLAUDEMEM_URL = os.environ.get("CLAUDEMEM_URL", "http://localhost:37777")
FACT_WORTHY_TOOLS = {"WebSearch", "WebFetch", "Read", "Grep", "Glob", "graph_query", "k2_file_read"}

_session_count = 0
MAX_PER_SESSION = 50
MAX_BYTES = 2048


def reset():
    """Reset session counter."""
    global _session_count
    _session_count = 0


def _save_to_claudemem(title: str, text: str):
    """Fire-and-forget save to claude-mem."""
    def _do():
        try:
            payload = json.dumps({
                "title": title,
                "text": text[:MAX_BYTES],
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
    threading.Thread(target=_do, daemon=True).start()


def _extract_facts(tool_name: str, output: str) -> str:
    """Extract key facts from tool output. Returns condensed text."""
    if not output:
        return ""

    # Truncate long outputs
    text = output[:4000]

    # For Read: extract first meaningful lines (skip blank/comment-only)
    if tool_name == "Read":
        lines = text.splitlines()
        meaningful = [l for l in lines[:20] if l.strip() and not l.strip().startswith('#')]
        if meaningful:
            return f"File content excerpt: {' | '.join(meaningful[:5])}"
        return ""

    # For Grep/Glob: extract matched patterns
    if tool_name in ("Grep", "Glob"):
        lines = text.splitlines()
        if len(lines) > 5:
            return f"Search results ({len(lines)} matches): {' | '.join(lines[:5])}..."
        return f"Search results: {' | '.join(lines)}"

    # For WebSearch/WebFetch: extract key sentences
    if tool_name in ("WebSearch", "WebFetch"):
        sentences = re.split(r'[.!?]\s+', text)
        key = [s for s in sentences[:10] if len(s) > 20][:3]
        return f"Web content: {'. '.join(key)}"

    # For graph_query: return as-is (usually structured)
    if tool_name == "graph_query":
        return f"Graph query result: {text[:500]}"

    return text[:500]


def extract(context: dict) -> dict | None:
    """Extract facts from a tool result context.

    Args:
        context: {tool_name, output, input?}

    Returns:
        {title, text} or None if nothing worth saving.
    """
    global _session_count

    tool_name = context.get("tool_name", "")
    output = context.get("output", "")

    if tool_name not in FACT_WORTHY_TOOLS:
        return None
    if _session_count >= MAX_PER_SESSION:
        return None
    if not output or len(output.strip()) < 20:
        return None

    facts = _extract_facts(tool_name, output)
    if not facts or len(facts) < 10:
        return None

    _session_count += 1
    title = f"auto-extracted: {tool_name} result"
    return {"title": title, "text": facts, "tool_name": tool_name}


def handle(context: dict) -> dict:
    """Hook handler interface for hooks engine."""
    result = extract(context)
    if result:
        _save_to_claudemem(result["title"], result["text"])
        return {"systemMessage": f"Fact extracted from {result['tool_name']} ({_session_count}/{MAX_PER_SESSION})"}
    return {}


if __name__ == "__main__":
    if "--test" in sys.argv:
        reset()

        # Fact-worthy tool with content
        result = extract({
            "tool_name": "Read",
            "output": "# MEMORY.md\nCurrent state: Sprint 3 in progress\nActive task: Building hooks engine",
        })
        assert result is not None, "Expected extraction from Read"
        assert "Sprint 3" in result["text"], f"Expected 'Sprint 3' in text, got: {result['text']}"

        # Non-fact-worthy tool
        result = extract({"tool_name": "Edit", "output": "file edited"})
        assert result is None, "Edit should not trigger extraction"

        # Too short output
        result = extract({"tool_name": "Read", "output": "ok"})
        assert result is None, "Short output should not trigger extraction"

        # Session cap
        reset()
        for i in range(50):
            extract({"tool_name": "Read", "output": f"Line {i} of important content that is long enough"})
        capped = extract({"tool_name": "Read", "output": "This should be capped"})
        assert capped is None, f"Expected None after cap, got: {capped}"

        print("PASS")
        sys.exit(0)

    ctx = json.loads(sys.stdin.read())
    output = handle(ctx)
    print(json.dumps(output))
