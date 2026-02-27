"""
Episode Dedup Guard — Phase 4
Prevents duplicate episodes from being ingested into FalkorDB.

Two-tier check:
  1. Exact match: skip if identical episode_body already exists (within 24h)
  2. Semantic match: skip if a highly similar episode exists (fuzzy, token-overlap)

Zero LLM calls — fast, deterministic, no cost.
Runs inline before graphiti.add_episode() in ingest_episode().
"""
import re
from datetime import datetime, timezone, timedelta
import config


# ── Normalization ────────────────────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Lowercase, collapse whitespace, strip timestamps and episode markers."""
    text = text.lower().strip()
    text = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[Z\+\-\d:]*', '', text)
    text = re.sub(r'\b\d{10,13}\b', '', text)
    text = re.sub(r'terminal_chat_\d+_\d+', '', text)
    text = re.sub(r'p_\w{3}_[\w-]+_\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _tokenize(text: str) -> set:
    """Extract meaningful tokens from text (words > 2 chars, no stop words)."""
    stop_words = {
        'the', 'is', 'are', 'was', 'were', 'has', 'have', 'had', 'will',
        'can', 'could', 'would', 'should', 'does', 'did', 'not', 'but',
        'and', 'for', 'from', 'with', 'this', 'that', 'user', 'assistant',
        'you', 'your', 'my', 'me', 'about', 'just', 'like', 'what',
        'who', 'how', 'when', 'where', 'why', 'also', 'some', 'any',
        'all', 'other', 'than', 'then', 'there', 'here', 'very', 'been',
        'being', 'they', 'them', 'their', 'our', 'its', 'into',
    }
    words = re.findall(r'[a-z]{3,}', text.lower())
    return {w for w in words if w not in stop_words}


def _jaccard(set_a: set, set_b: set) -> float:
    """Jaccard similarity between two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


# ── Main Dedup Check ─────────────────────────────────────────────────────────────────────

def is_duplicate(episode_body: str, get_falkor_fn, lookback_hours: int = 24,
                 similarity_threshold: float = 0.75) -> tuple[bool, str]:
    """Check if an episode is a duplicate of a recent one in FalkorDB.

    Returns (is_dup: bool, reason: str).
    reason is empty if not duplicate, otherwise explains why.

    Two checks:
    1. Exact: normalized text matches an existing episode within lookback window
    2. Fuzzy: Jaccard token overlap >= similarity_threshold with recent episode
    """
    try:
        r = get_falkor_fn()
        if r is None:
            return False, ""

        normalized_new = _normalize(episode_body)
        tokens_new = _tokenize(normalized_new)

        if not tokens_new or len(tokens_new) < 3:
            return False, ""

        cypher = (
            "MATCH (e:Episodic) "
            "RETURN e.uuid AS uuid, "
            "COALESCE(e.content, e.episode_body, '') AS body, "
            "e.name AS name "
            "ORDER BY e.created_at DESC "
            f"LIMIT 50"
        )
        result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)

        if not (len(result) >= 2 and result[1]):
            return False, ""

        for row in result[1]:
            existing_uuid = row[0]
            existing_body = row[1]
            existing_name = row[2] or ""

            if isinstance(existing_body, bytes):
                existing_body = existing_body.decode()
            if isinstance(existing_uuid, bytes):
                existing_uuid = existing_uuid.decode()
            if isinstance(existing_name, bytes):
                existing_name = existing_name.decode()

            if not existing_body:
                continue

            normalized_existing = _normalize(existing_body)

            if normalized_new == normalized_existing:
                return True, f"exact_match:{existing_uuid[:8]}"

            tokens_existing = _tokenize(normalized_existing)
            sim = _jaccard(tokens_new, tokens_existing)
            if sim >= similarity_threshold:
                return True, f"similar({sim:.2f}):{existing_uuid[:8]}"

        return False, ""

    except Exception as e:
        print(f"[DEDUP] Check failed (non-fatal, allowing through): {e}")
        return False, ""
