"""
Auto-Promote — Phase 5
Automatically promotes high-confidence episodes to canonical when corroborated.

Promotion criteria (ALL must be true):
  1. Episode is in 'candidate' lane (not conflict, not raw)
  2. Confidence >= AUTO_PROMOTE_THRESHOLD (default 0.90)
  3. Episode has been corroborated: at least N other episodes reference
     overlapping entities/topics (evidence of repeated mention)
  4. Episode is at least MIN_AGE_MINUTES old (avoids premature promotion)

Runs on a timer from consciousness loop (every N cycles) or can be called
manually via /auto-promote endpoint.

Zero LLM calls. All decisions are rule-based.
"""
import json
import os
import re
import traceback
from datetime import datetime, timezone, timedelta
import config

# ── Config ─────────────────────────────────────────────────────────────────────────

AUTO_PROMOTE_THRESHOLD = float(os.getenv("AUTO_PROMOTE_THRESHOLD", "0.90"))
AUTO_PROMOTE_MIN_CORROBORATION = int(os.getenv("AUTO_PROMOTE_MIN_CORROBORATION", "2"))
AUTO_PROMOTE_MIN_AGE_MINUTES = int(os.getenv("AUTO_PROMOTE_MIN_AGE_MINUTES", "30"))
CANDIDATES_JSONL = os.getenv("CANDIDATES_JSONL", "/ledger/candidates.jsonl")


def _extract_key_tokens(text: str) -> set:
    """Extract significant tokens from episode content for corroboration matching."""
    stop_words = {
        'the', 'is', 'are', 'was', 'were', 'has', 'have', 'had', 'will',
        'can', 'could', 'would', 'should', 'does', 'did', 'not', 'but',
        'and', 'for', 'from', 'with', 'this', 'that', 'user', 'assistant',
        'you', 'your', 'my', 'me', 'about', 'just', 'like', 'also',
        'some', 'any', 'all', 'other', 'than', 'then', 'there', 'here',
        'karma', 'terminal', 'chat', 'ingest',
    }
    words = re.findall(r'[a-z]{3,}', text.lower())
    return {w for w in words if w not in stop_words}


def _count_corroboration(candidate_uuid: str, candidate_content: str,
                         get_falkor_fn) -> int:
    """Count how many OTHER episodes share significant topic overlap with this candidate.
    Returns count of corroborating episodes."""
    try:
        r = get_falkor_fn()
        if r is None:
            return 0

        tokens = _extract_key_tokens(candidate_content)
        if len(tokens) < 3:
            return 0

        key_tokens = sorted(tokens, key=len, reverse=True)[:5]

        conditions = []
        for token in key_tokens:
            safe = token.replace("'", "\\'")
            conditions.append(
                f"toLower(COALESCE(e.content, e.episode_body, '')) CONTAINS '{safe}'"
            )

        where_clause = " OR ".join(conditions)
        cypher = (
            f"MATCH (e:Episodic) "
            f"WHERE ({where_clause}) "
            f"AND e.uuid <> '{candidate_uuid}' "
            f"RETURN count(e) AS cnt"
        )

        result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
        if len(result) >= 2 and result[1]:
            count = result[1][0][0]
            if isinstance(count, bytes):
                count = int(count.decode())
            return int(count)
        return 0

    except Exception as e:
        print(f"[AUTO-PROMOTE] Corroboration check failed (non-fatal): {e}")
        return 0


def run_auto_promote(get_falkor_fn) -> dict:
    """Scan candidates.jsonl for episodes eligible for auto-promotion.

    Returns summary dict with promoted count, checked count, reasons.
    """
    try:
        if not os.path.exists(CANDIDATES_JSONL):
            return {"status": "ok", "checked": 0, "promoted": 0, "message": "no candidates file"}

        entries = []
        with open(CANDIDATES_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        if not entries:
            return {"status": "ok", "checked": 0, "promoted": 0, "message": "empty"}

        now = datetime.now(timezone.utc)
        checked = 0
        promoted = 0
        promoted_names = []
        skipped_reasons = {"already_promoted": 0, "wrong_lane": 0, "low_confidence": 0,
                           "too_young": 0, "insufficient_corroboration": 0}

        import falkordb as fdb
        fdb_r = fdb.FalkorDB(host=config.FALKORDB_HOST, port=config.FALKORDB_PORT)
        g = fdb_r.select_graph(config.GRAPHITI_GROUP_ID)

        for entry in entries:
            if entry.get("promoted"):
                skipped_reasons["already_promoted"] += 1
                continue

            checked += 1
            uuid_val = entry.get("uuid", "")
            lane = entry.get("lane", "")
            confidence = float(entry.get("confidence", 0))
            created_at_str = entry.get("created_at", "")

            if lane != "candidate":
                skipped_reasons["wrong_lane"] += 1
                continue

            if confidence < AUTO_PROMOTE_THRESHOLD:
                skipped_reasons["low_confidence"] += 1
                continue

            try:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                age_minutes = (now - created_at).total_seconds() / 60
                if age_minutes < AUTO_PROMOTE_MIN_AGE_MINUTES:
                    skipped_reasons["too_young"] += 1
                    continue
            except (ValueError, TypeError):
                pass

            try:
                content_result = g.query(
                    "MATCH (e:Episodic {uuid: $uuid}) RETURN COALESCE(e.content, '') AS content",
                    {"uuid": uuid_val}
                )
                if not content_result.result_set:
                    continue
                content = str(content_result.result_set[0][0])
            except Exception:
                continue

            corr_count = _count_corroboration(uuid_val, content, get_falkor_fn)
            if corr_count < AUTO_PROMOTE_MIN_CORROBORATION:
                skipped_reasons["insufficient_corroboration"] += 1
                continue

            try:
                promoted_at = now.isoformat()
                g.query(
                    "MATCH (e:Episodic {uuid: $uuid}) "
                    "SET e.lane = 'canonical', "
                    "e.promoted_by = 'auto-promote', "
                    "e.promoted_at = $at, "
                    "e.promotion_reason = $reason",
                    {
                        "uuid": uuid_val,
                        "at": promoted_at,
                        "reason": f"auto: conf={confidence:.2f}, corroboration={corr_count}",
                    }
                )
                entry["promoted"] = True
                entry["promoted_by"] = "auto-promote"
                entry["promoted_at"] = promoted_at
                entry["promotion_reason"] = f"auto: conf={confidence:.2f}, corroboration={corr_count}"
                promoted += 1
                promoted_names.append(entry.get("name", uuid_val[:8]))
                print(f"[AUTO-PROMOTE] {entry.get('name', uuid_val[:8])} → canonical "
                      f"(conf={confidence:.2f}, corr={corr_count})")
            except Exception as pe:
                print(f"[AUTO-PROMOTE] Promote failed for {uuid_val[:8]}: {pe}")

        if promoted > 0:
            with open(CANDIDATES_JSONL, "w", encoding="utf-8") as f:
                for entry in entries:
                    f.write(json.dumps(entry) + "\n")

        return {
            "status": "ok",
            "checked": checked,
            "promoted": promoted,
            "promoted_names": promoted_names,
            "skipped": skipped_reasons,
        }

    except Exception as e:
        print(f"[AUTO-PROMOTE] Error: {e}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}
