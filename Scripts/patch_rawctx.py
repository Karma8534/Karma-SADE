"""
Patch karma-core/server.py to add Recent Approvals block.
Closes retrieval drift window for newly-promoted ingest episodes.
"""
import sys

path = "/opt/seed-vault/memory_v1/karma-core/server.py"
src = open(path).read()

# ── 1. Add query_recent_ingest_episodes after query_recent_episodes ────────
NEW_FUNC = '''
def query_recent_ingest_episodes(limit: int = 5) -> list:
    """Get the most recently promoted ingest episodes (images, PDFs, text, chat signals).
    Returned regardless of query match to close the retrieval-drift window:
    in the session immediately after promotion, semantic queries may not yet
    activate these memories. Ordered by created_at DESC as proxy for promoted_at."""
    try:
        r = get_falkor()
        cypher = (
            "MATCH (e:Episodic) "
            "WHERE e.lane = 'canonical' AND e.content STARTS WITH '[karma-ingest]' "
            "RETURN e.uuid AS uuid, e.name AS name, e.content AS content "
            f"ORDER BY e.created_at DESC LIMIT {limit}"
        )
        result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
        if len(result) >= 2 and result[1]:
            return [{"uuid": row[0], "name": row[1], "content": (row[2] or "")[:400]} for row in result[1]]
        return []
    except Exception as e:
        print(f"[WARN] Recent ingest episodes query failed: {e}")
        return []

'''

MARKER = "def query_identity_facts() -> str:"
if MARKER not in src:
    print("ERROR: query_identity_facts marker not found")
    sys.exit(1)
src = src.replace(MARKER, NEW_FUNC + MARKER, 1)

# ── 2. Replace the Recent Memories block to add dedup + Recent Approvals ──
OLD_BLOCK = (
    "    # Get recent conversation memories for continuity\n"
    "    recent = query_recent_episodes(limit=3, lane=episode_lane)\n"
    "    if recent:\n"
    "        parts.append(\"\\n## Recent Memories\")\n"
    "        for ep in recent:\n"
    "            content = ep[\"content\"][:200] if ep[\"content\"] else \"\"\n"
    "            if content:\n"
    "                parts.append(f\"- {content}\")"
)

NEW_BLOCK = (
    "    # Get recent conversation memories for continuity\n"
    "    recent = query_recent_episodes(limit=3, lane=episode_lane)\n"
    "    recent_names = {ep[\"name\"] for ep in recent}\n"
    "    if recent:\n"
    "        parts.append(\"\\n## Recent Memories\")\n"
    "        for ep in recent:\n"
    "            content = ep[\"content\"][:200] if ep[\"content\"] else \"\"\n"
    "            if content:\n"
    "                parts.append(f\"- {content}\")\n"
    "\n"
    "    # Recent Approvals: last N canonical ingest episodes, always surfaced.\n"
    "    # Closes retrieval-drift window: newly-promoted memories appear in the\n"
    "    # very next session without requiring a matching query to activate them.\n"
    "    # Deduplicates against Recent Memories to avoid showing the same entry twice.\n"
    "    recent_ingest = query_recent_ingest_episodes(limit=5)\n"
    "    if recent_ingest:\n"
    "        unique_ingest = [ep for ep in recent_ingest if ep.get(\"name\") not in recent_names]\n"
    "        if unique_ingest:\n"
    "            parts.append(\"\\n## Recently Learned (Approved)\")\n"
    "            for ep in unique_ingest:\n"
    "                content = ep[\"content\"][:300] if ep[\"content\"] else \"\"\n"
    "                if content:\n"
    "                    parts.append(f\"- {content}\")"
)

if OLD_BLOCK not in src:
    print("ERROR: Recent Memories block not found in source. Snippet to match:")
    print(repr(OLD_BLOCK))
    # Show surrounding context to help debug
    idx = src.find("query_recent_episodes")
    print("Context around query_recent_episodes:")
    print(repr(src[idx-20:idx+300]))
    sys.exit(1)

src = src.replace(OLD_BLOCK, NEW_BLOCK, 1)

open(path, "w").write(src)
print("Patch applied OK")
print(f"File size: {len(src)} bytes")
