#!/usr/bin/env python3
"""
agent_diary.py — Per-agent diary using claude-mem project namespacing.
MemPalace pattern (nexus 5.6.0, obs #25022): each agent gets its own diary wing.

Convention: project = "Karma_SADE_diary_{agent_name}"
Entries written in AAAK format for compression.
Read at session start for agent-specific continuity.

Usage:
    python agent_diary.py write julian "SESSION:2026-04-07|built.hooks|★★★"
    python agent_diary.py read julian 5
    python agent_diary.py read karma 10
"""
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

CLAUDE_MEM_BASE = "http://127.0.0.1:37778"


def _project(agent: str) -> str:
    return f"Karma_SADE_diary_{agent.lower().strip()}"


def diary_write(agent: str, entry: str, title: str = None) -> dict:
    """Write a diary entry for an agent via claude-mem MCP save_observation."""
    project = _project(agent)
    ts = datetime.now(tz=None).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not title:
        title = f"DIARY: {agent} {ts[:10]}"

    # claude-mem MCP uses JSONRPC stdio protocol, but we can use the HTTP API
    # The /api/save endpoint accepts {text, title, project}
    payload = json.dumps({
        "text": entry,
        "title": title,
        "project": project,
    }).encode("utf-8")

    # Try the MCP-compatible save endpoint
    for endpoint in ["/api/save", "/api/observations"]:
        try:
            req = urllib.request.Request(
                f"{CLAUDE_MEM_BASE}{endpoint}",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                return {"ok": True, "id": result.get("id"), "agent": agent, "project": project}
        except urllib.error.HTTPError:
            continue
        except Exception as e:
            return {"ok": False, "error": str(e)}

    return {"ok": False, "error": "No working save endpoint found"}


def diary_read(agent: str, last_n: int = 5) -> dict:
    """Read an agent's recent diary entries via claude-mem search."""
    project = _project(agent)
    params = urllib.parse.urlencode({
        "query": f"DIARY {agent}",
        "project": project,
        "limit": last_n,
        "orderBy": "recent",
    })
    try:
        req = urllib.request.Request(f"{CLAUDE_MEM_BASE}/api/search?{params}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = json.loads(resp.read())
            # claude-mem returns MCP-formatted content
            text = ""
            if isinstance(raw, dict) and "content" in raw:
                for block in raw["content"]:
                    if block.get("type") == "text":
                        text += block["text"]
            return {"ok": True, "agent": agent, "raw": text[:2000], "count": text.count("|")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def format_diary_entry(agent: str, entry: str) -> dict:
    """Format a diary entry for CC to save via MCP save_observation.
    Returns the args CC should pass to mcp save_observation."""
    project = _project(agent)
    ts = datetime.now(tz=None).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "text": entry,
        "title": f"DIARY: {agent} {ts[:10]}",
        "project": project,
    }


def format_diary_search(agent: str) -> dict:
    """Format a diary search query for CC to use via MCP search.
    Returns the args CC should pass to mcp search."""
    return {
        "query": f"DIARY {agent}",
        "project": _project(agent),
        "limit": 5,
        "orderBy": "recent",
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python agent_diary.py write <agent> <entry>   — format entry for MCP save")
        print("  python agent_diary.py read <agent> [last_n]   — search via claude-mem HTTP")
        print()
        print("NOTE: 'write' outputs MCP args for CC to call save_observation.")
        print("      'read' queries claude-mem HTTP search API directly.")
        sys.exit(0)

    cmd = sys.argv[1]
    agent = sys.argv[2]

    if cmd == "write":
        entry = sys.argv[3] if len(sys.argv) > 3 else "no entry"
        args = format_diary_entry(agent, entry)
        print(json.dumps(args, indent=2))
        print(f"\nCC should call: mcp save_observation(text='{args['text'][:50]}...', title='{args['title']}', project='{args['project']}')")
    elif cmd == "read":
        last_n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        result = diary_read(agent, last_n)
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
