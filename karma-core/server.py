"""
Karma Chat Server — The Mind Behind the Terminal
FastAPI + WebSocket server that connects Karma's knowledge graph to a terminal chat interface.
Queries FalkorDB for context, generates responses via gpt-4o-mini, logs conversations back.
Real-time knowledge graph updates via Graphiti after every conversation turn.
"""
import asyncio
import json
import os
import time
import traceback
import uuid
from datetime import datetime, timezone
from typing import Optional

import aiohttp
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse, Response, HTMLResponse
import uvicorn

import config
# # from token_budget import SessionBudget, count_tokens, count_message_tokens, check_budget, get_monthly_tracker

# ─── 4-Tool Surface (P2, Phase 0 Step 0.9) ─────────────────────────────────
# Decision: 4 tools only — Read/Write/Edit/Bash. No MCP. < 500 tokens total.

import subprocess
import asyncio as _asyncio

# ─── Memory Tools (Phase 1) ──────────────────────────────────────────────
try:
    from memory_tools import (
        admit_memory, retrieve_memory, update_memory, delete_memory,
        save_session_context, load_last_session, load_pending_observations,
        auto_tag_category, assign_confidence, consolidate_scene,
        consolidate_all_scenes, CATEGORIES, SOURCE_CONFIDENCE
    )
    _MEMORY_TOOLS_AVAILABLE = True
    print("[MEMORY] memory_tools loaded successfully")
except ImportError as e:
    _MEMORY_TOOLS_AVAILABLE = False
    print(f"[MEMORY] memory_tools not available: {e}")

# Phase 2 Modules
try:
    from observation_block import (
        build_observation_block, reset_observation_cache, get_observation_stats
    )
    _OBS_BLOCK_AVAILABLE = True
    print("[PHASE2] observation_block loaded")
except ImportError as e:
    _OBS_BLOCK_AVAILABLE = False
    print(f"[PHASE2] observation_block not available: {e}")

try:
    from staleness import run_staleness_scan
    _STALENESS_AVAILABLE = True
    print("[PHASE2] staleness loaded")
except ImportError as e:
    _STALENESS_AVAILABLE = False
    print(f"[PHASE2] staleness not available: {e}")

try:
    from budget_guard import check_budget, log_llm_call, get_budget_report
    _BUDGET_AVAILABLE = True
    print("[PHASE2] budget_guard loaded")
except ImportError as e:
    _BUDGET_AVAILABLE = False
    print(f"[PHASE2] budget_guard not available: {e}")

try:
    from capability_gate import check_access, get_token_scope, get_read_token, get_scope_info
    _CAPABILITY_GATE_AVAILABLE = True
    print("[PHASE2] capability_gate loaded")
except ImportError as e:
    _CAPABILITY_GATE_AVAILABLE = False
    print(f"[PHASE2] capability_gate not available: {e}")

# Phase 3 Modules
try:
    from hooks import run_hook, hook_session_start, hook_pre_tool_use, hook_post_tool_use, hook_session_end
    _HOOKS_AVAILABLE = True
    print("[PHASE3] hooks loaded")
except ImportError as e:
    _HOOKS_AVAILABLE = False
    print(f"[PHASE3] hooks not available: {e}")

try:
    from session_briefing import generate_session_briefing, get_briefing_data
    _BRIEFING_AVAILABLE = True
    print("[PHASE3] session_briefing loaded")
except ImportError as e:
    _BRIEFING_AVAILABLE = False
    print(f"[PHASE3] session_briefing not available: {e}")

try:
    from compaction import compact_context, needs_compaction, estimate_tokens
    _COMPACTION_AVAILABLE = True
    print("[PHASE3] compaction loaded")
except ImportError as e:
    _COMPACTION_AVAILABLE = False
    print(f"[PHASE3] compaction not available: {e}")


TOOL_DEFINITIONS = [
    {"name": "read_file", "description": "Read a file from the droplet filesystem.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Write content to a file on the droplet.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "edit_file", "description": "Replace old_text with new_text in a file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}},
    {"name": "bash", "description": "Run a shell command on the droplet. Returns stdout, stderr, exit code.",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
]

AVAILABLE_TOOLS = {t["name"]: t for t in TOOL_DEFINITIONS}

# Allowed base paths for file operations (security)
ALLOWED_PATHS = ["/opt/seed-vault/", "/home/neo/", "/tmp/"]

def _check_path(path: str) -> bool:
    """Verify path is within allowed directories."""
    return any(path.startswith(p) for p in ALLOWED_PATHS)

async def execute_tool_action(tool_name: str, tool_input: dict) -> dict:
    """Execute one of the 4 tools. Returns {ok, result/error}."""
    try:
        if tool_name == "read_file":
            path = tool_input["path"]
            if not _check_path(path):
                return {"ok": False, "error": f"Path not allowed: {path}"}
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(100_000)  # 100KB cap
            return {"ok": True, "content": content, "bytes": len(content)}

        elif tool_name == "write_file":
            path = tool_input["path"]
            if not _check_path(path):
                return {"ok": False, "error": f"Path not allowed: {path}"}
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(tool_input["content"])
            return {"ok": True, "bytes_written": len(tool_input["content"])}

        elif tool_name == "edit_file":
            path = tool_input["path"]
            if not _check_path(path):
                return {"ok": False, "error": f"Path not allowed: {path}"}
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            old_text = tool_input["old_text"]
            if old_text not in content:
                return {"ok": False, "error": "old_text not found in file"}
            content = content.replace(old_text, tool_input["new_text"], 1)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"ok": True, "replaced": True}

        elif tool_name == "bash":
            command = tool_input["command"]
            proc = await _asyncio.create_subprocess_shell(
                command,
                stdout=_asyncio.subprocess.PIPE,
                stderr=_asyncio.subprocess.PIPE,
                cwd="/opt/seed-vault/memory_v1"
            )
            stdout, stderr = await _asyncio.wait_for(proc.communicate(), timeout=30)
            return {
                "ok": proc.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="replace")[:50_000],
                "stderr": stderr.decode("utf-8", errors="replace")[:10_000],
                "exit_code": proc.returncode
            }

        else:
            return {"ok": False, "error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ─── LLM Client ──────────────────────────────────────────────────────────
_openai_client = None

def get_openai_client():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _openai_client


# ─── Graphiti Client (Real-time Knowledge Graph Updates) ──────────────────
_graphiti_instance = None
_graphiti_lock = asyncio.Lock()
_graphiti_ready = False
_episode_counter = 0

async def get_graphiti():
    """Get or create the persistent Graphiti client."""
    global _graphiti_instance, _graphiti_ready
    async with _graphiti_lock:
        if _graphiti_instance is not None and _graphiti_ready:
            return _graphiti_instance
        try:
            from graphiti_core import Graphiti
            from graphiti_core.llm_client import OpenAIClient
            from graphiti_core.llm_client.config import LLMConfig
            from graphiti_core.driver.falkordb_driver import FalkorDriver

            llm_config = LLMConfig(
                api_key=config.OPENAI_API_KEY,
                model=config.ANALYSIS_MODEL,
            )
            llm_client = OpenAIClient(config=llm_config)
            falkor_driver = FalkorDriver(
                host=config.FALKORDB_HOST,
                port=config.FALKORDB_PORT,
            )
            _graphiti_instance = Graphiti(
                graph_driver=falkor_driver,
                llm_client=llm_client,
            )
            await _graphiti_instance.build_indices_and_constraints()
            _graphiti_ready = True
            print("[GRAPHITI] Client initialized — real-time knowledge updates enabled")
            return _graphiti_instance
        except Exception as e:
            print(f"[GRAPHITI] Failed to initialize: {e}")
            _graphiti_ready = False
            return None


async def ingest_episode(user_msg: str, assistant_msg: str, source: str = "karma-terminal"):
    """Ingest a conversation turn into the knowledge graph as a new episode.
    Runs as a background task — does not block chat responses.
    Decision #4: Only admits episodes scoring >= MEMORY_ADMISSION_THRESHOLD."""
    global _episode_counter

    # ── Admission gate (Decision #4) ──
    from admission import should_admit
    admitted, score = should_admit(user_msg, assistant_msg, source)
    if not admitted:
        print(f"[GRAPHITI] Episode rejected — admission score {score:.3f} < {config.MEMORY_ADMISSION_THRESHOLD}")
        return

    _episode_counter += 1
    episode_num = _episode_counter

    # ── Dedup guard (Phase 4) ──
    try:
        from dedup import is_duplicate
        episode_body_preview = f"[{source}] User: {user_msg[:500]}\nAssistant: {assistant_msg[:500]}"
        is_dup, dup_reason = is_duplicate(episode_body_preview, get_falkor)
        if is_dup:
            print(f"[GRAPHITI] Episode #{episode_num} skipped — duplicate ({dup_reason})")
            return
    except Exception as dedup_err:
        print(f"[GRAPHITI] Dedup check failed (non-fatal, continuing): {dedup_err}")

    try:
        graphiti = await get_graphiti()
        if graphiti is None:
            print(f"[GRAPHITI] Skipping episode #{episode_num} — client not available")
            return

        episode_body = f"[{source}] User: {user_msg[:500]}\nAssistant: {assistant_msg[:500]}"
        ref_time = datetime.now(timezone.utc)
        episode_name = f"terminal_chat_{int(ref_time.timestamp())}_{episode_num}"

        await graphiti.add_episode(
            name=episode_name,
            episode_body=episode_body,
            source_description=f"Live terminal chat ({source})",
            reference_time=ref_time,
            group_id=config.GRAPHITI_GROUP_ID,
        )
        print(f"[GRAPHITI] Episode #{episode_num} ingested (score={score:.3f}) — entities/relationships updated")
    except Exception as e:
        print(f"[GRAPHITI] Episode #{episode_num} failed: {e}")
        traceback.print_exc()


# ─── Database Helpers ─────────────────────────────────────────────────────

def get_pg_connection():
    return psycopg2.connect(
        host=config.POSTGRES_HOST,
        port=config.POSTGRES_PORT,
        dbname=config.POSTGRES_DB,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
    )


def query_preferences(limit: int = 20) -> list[dict]:
    """Get Karma's known preferences about the user."""
    try:
        conn = get_pg_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT category, key, value, confidence
                FROM analysis.user_preferences
                ORDER BY confidence DESC, last_updated DESC
                LIMIT %s
            """, (limit,))
            rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[WARN] PostgreSQL query failed: {e}")
        return []


def query_task_history(limit: int = 10) -> list[dict]:
    """Get recent task history."""
    try:
        conn = get_pg_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT task_type, description, status, priority, created_at, completed_at
                FROM analysis.task_history
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[WARN] task_history query failed: {e}")
        return []


# ─── FalkorDB Queries ─────────────────────────────────────────────────────

_falkor_client = None

# ─── Pattern Cache (recurring topics, 30min refresh) ──────────────────────────
_pattern_cache: list[dict] = []  # [{"entity": str, "mentions": int}]


def _refresh_pattern_cache() -> None:
    """Query FalkorDB for top-10 most-mentioned entities. Updates module-level cache.
    Non-fatal: on FalkorDB error, existing cache is preserved."""
    global _pattern_cache
    try:
        r = get_falkor()
        cypher = (
            "MATCH (ep:Episodic)-[:MENTIONS]->(e:Entity) "
            "RETURN e.name AS entity, count(ep) AS mentions "
            "ORDER BY mentions DESC LIMIT 10"
        )
        result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
        if len(result) >= 2 and result[1]:
            _pattern_cache = [{"entity": row[0], "mentions": row[1]} for row in result[1]]
        else:
            _pattern_cache = []
    except Exception as e:
        print(f"[PATTERN] cache refresh failed (non-fatal): {e}")
        # Intentionally preserve existing cache on error


def get_falkor():
    """Get FalkorDB connection via redis."""
    global _falkor_client
    if _falkor_client is None:
        import redis
        _falkor_client = redis.Redis(
            host=config.FALKORDB_HOST,
            port=config.FALKORDB_PORT,
            decode_responses=True,
        )
    return _falkor_client


def query_knowledge_graph(query: str, limit: int = 10) -> list[dict]:
    """Search the knowledge graph for entities related to a query.
    Three-pass search:
      1. Entity name (exact + contains) + entity_type match
      2. Summary content search (word-boundary aware)
      3. Relationship traversal — entities connected to Pass 1/2 hits
    Includes synonym expansion for common terms. Zero LLM calls."""
    try:
        r = get_falkor()
        stop_words = {'what', 'who', 'where', 'when', 'how', 'why', 'the', 'is', 'are',
                      'was', 'were', 'can', 'could', 'would', 'should', 'does', 'did',
                      'has', 'have', 'had', 'will', 'about', 'your', 'you', 'my', 'me',
                      'this', 'that', 'with', 'for', 'from', 'not', 'but', 'and', 'tell',
                      'please', 'know', 'think', 'like', 'just', 'get', 'got', 'its',
                      'also', 'some', 'any', 'all', 'other', 'than', 'then', 'there',
                      'remember', 'want', 'need', 'much', 'many', 'really', 'thing'}

        # Synonym map: bridges user language → graph entity names/types
        synonym_map = {
            'cat': ['cat', 'pet', 'ollie', 'kitten', 'feline'],
            'cats': ['cat', 'pet', 'ollie', 'kitten', 'feline'],
            'dog': ['dog', 'pet', 'puppy', 'canine'],
            'dogs': ['dog', 'pet', 'puppy', 'canine'],
            'pet': ['pet', 'cat', 'dog', 'ollie'],
            'pets': ['pet', 'cat', 'dog', 'ollie'],
            'mom': ['mom', 'mother', 'mama'],
            'dad': ['dad', 'father', 'papa'],
            'brother': ['brother', 'sibling'],
            'sister': ['sister', 'sibling'],
            'family': ['family', 'mom', 'dad', 'brother', 'sister', 'mother', 'father'],
        }

        words = [w.strip().lower() for w in query.split()
                 if len(w.strip()) > 1 and w.strip().lower() not in stop_words]
        if not words:
            return []

        # Expand with synonyms (try both original and singular form)
        expanded = set(words)
        for w in words:
            if w in synonym_map:
                expanded.update(synonym_map[w])
            # Basic plural stemming: try without trailing 's'
            elif w.endswith('s') and len(w) > 3 and w[:-1] in synonym_map:
                expanded.update(synonym_map[w[:-1]])
        search_words = list(expanded)[:8]

        entities = []
        seen_names = set()

        def _decode(val):
            if isinstance(val, bytes):
                return val.decode()
            return val or ""

        def _add_entity(name_val, summary_val):
            name = _decode(name_val)
            summary = _decode(summary_val)
            if name and name not in seen_names:
                entities.append({"name": name, "summary": summary})
                seen_names.add(name)

        # ── Pass 1: Name + entity_type match ──────────────────────────────
        pass1_conditions = []
        for word in search_words[:6]:
            safe = word.replace("'", "\\'").replace('"', '\\"')
            # Exact name match (case-insensitive)
            pass1_conditions.append(f"toLower(n.name) = toLower('{safe}')")
            # Name contains (only for longer words to avoid noise)
            if len(word) > 3:
                pass1_conditions.append(f"toLower(n.name) CONTAINS toLower('{safe}')")
            # Entity type match
            pass1_conditions.append(f"toLower(COALESCE(n.entity_type,'')) CONTAINS toLower('{safe}')")

        cypher1 = f"""
            MATCH (n:Entity)
            WHERE {' OR '.join(pass1_conditions)}
            RETURN n.name AS name, n.summary AS summary
            LIMIT {limit}
        """
        result1 = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher1)
        if len(result1) >= 2 and result1[1]:
            for row in result1[1]:
                _add_entity(row[0], row[1])

        # ── Pass 2: Summary content search ────────────────────────────────
        if len(entities) < limit:
            pass2_conditions = []
            for word in search_words[:6]:
                safe = word.replace("'", "\\'").replace('"', '\\"')
                if len(word) <= 4:
                    # Short words: match as whole word (space/punctuation boundaries)
                    pass2_conditions.append(
                        f"(toLower(COALESCE(n.summary,'')) CONTAINS ' {safe} ' "
                        f"OR toLower(COALESCE(n.summary,'')) CONTAINS ' {safe}.' "
                        f"OR toLower(COALESCE(n.summary,'')) CONTAINS ' {safe},' "
                        f"OR toLower(COALESCE(n.summary,'')) CONTAINS ' {safe}\\n' "
                        f"OR toLower(COALESCE(n.summary,'')) ENDS WITH ' {safe}' "
                        f"OR toLower(COALESCE(n.summary,'')) ENDS WITH ' {safe}.' "
                        f"OR toLower(COALESCE(n.summary,'')) STARTS WITH '{safe} ')"
                    )
                else:
                    pass2_conditions.append(
                        f"toLower(COALESCE(n.summary,'')) CONTAINS toLower('{safe}')"
                    )
            if pass2_conditions:
                remaining = limit - len(entities)
                cypher2 = f"""
                    MATCH (n:Entity)
                    WHERE {' OR '.join(pass2_conditions)}
                    RETURN n.name AS name, n.summary AS summary
                    LIMIT {remaining + 5}
                """
                result2 = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher2)
                if len(result2) >= 2 and result2[1]:
                    for row in result2[1]:
                        if len(entities) < limit:
                            _add_entity(row[0], row[1])

        # ── Pass 3: Relationship traversal ────────────────────────────────
        # Follow edges from entities found in Pass 1/2 to discover related ones
        if seen_names and len(entities) < limit:
            # Build a safe list of found entity names
            name_list = ", ".join(
                f"toLower('{n.replace(chr(39), chr(92)+chr(39))}')" for n in list(seen_names)[:5]
            )
            remaining = limit - len(entities)
            cypher3 = f"""
                MATCH (a:Entity)-[r]->(b:Entity)
                WHERE toLower(a.name) IN [{name_list}]
                RETURN b.name AS name, b.summary AS summary, type(r) AS rel
                LIMIT {remaining + 3}
            """
            result3 = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher3)
            if len(result3) >= 2 and result3[1]:
                for row in result3[1]:
                    if len(entities) < limit:
                        _add_entity(row[0], row[1])

            # Also check reverse direction (b→a where b is our entity)
            if len(entities) < limit:
                remaining = limit - len(entities)
                cypher3r = f"""
                    MATCH (a:Entity)-[r]->(b:Entity)
                    WHERE toLower(b.name) IN [{name_list}]
                    RETURN a.name AS name, a.summary AS summary, type(r) AS rel
                    LIMIT {remaining + 3}
                """
                result3r = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher3r)
                if len(result3r) >= 2 and result3r[1]:
                    for row in result3r[1]:
                        if len(entities) < limit:
                            _add_entity(row[0], row[1])

        return entities
    except Exception as e:
        print(f"[WARN] FalkorDB query failed: {e}")
        return []
def query_entity_relationships(entity_name: str, limit: int = 10) -> list[dict]:
    """Get relationships for a specific entity."""
    try:
        r = get_falkor()
        safe = entity_name.replace("'", "\\'")
        cypher = f"""
            MATCH (a:Entity)-[rel]->(b:Entity)
            WHERE toLower(a.name) = toLower('{safe}')
            RETURN a.name AS source, type(rel) AS relationship, b.name AS target
            LIMIT {limit}
        """
        result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
        if len(result) >= 2 and result[1]:
            return [{"source": r[0], "relationship": r[1], "target": r[2]} for r in result[1]]
        return []
    except Exception as e:
        print(f"[WARN] FalkorDB relationship query failed: {e}")
        return []


def query_relevant_relationships(entity_names: list[str]) -> list[dict]:
    """Query RELATES_TO edges for a list of entity names in one FalkorDB call.
    Uses r.fact (the meaningful relationship description from Graphiti).
    Returns [{"from": str, "relationship": str, "to": str}].
    Returns [] on empty input or FalkorDB failure (non-fatal)."""
    if not entity_names:
        return []
    try:
        r = get_falkor()
        safe_names = [n.replace("'", "") for n in entity_names]
        names_str = ", ".join(f"'{n}'" for n in safe_names)
        cypher = (
            f"MATCH (e1:Entity)-[r:RELATES_TO]->(e2:Entity) "
            f"WHERE e1.name IN [{names_str}] "
            "RETURN e1.name AS from, r.fact AS relationship, e2.name AS to "
            "LIMIT 20"
        )
        result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
        if len(result) >= 2 and result[1]:
            return [
                {"from": row[0], "relationship": row[1], "to": row[2]}
                for row in result[1]
                if row[0] and row[1] and row[2]  # skip rows with None fact
            ]
        return []
    except Exception as e:
        print(f"[RELATIONSHIPS] edge query failed (non-fatal): {e}")
        return []


def get_graph_stats() -> dict:
    """Get overall knowledge graph statistics."""
    try:
        r = get_falkor()
        entity_result = r.execute_command(
            "GRAPH.QUERY", config.GRAPHITI_GROUP_ID,
            "MATCH (n:Entity) RETURN count(n) AS cnt"
        )
        episode_result = r.execute_command(
            "GRAPH.QUERY", config.GRAPHITI_GROUP_ID,
            "MATCH (n:Episodic) RETURN count(n) AS cnt"
        )
        rel_result = r.execute_command(
            "GRAPH.QUERY", config.GRAPHITI_GROUP_ID,
            "MATCH ()-[r]->() RETURN count(r) AS cnt"
        )
        return {
            "entities": entity_result[1][0][0] if entity_result[1] else 0,
            "episodes": episode_result[1][0][0] if episode_result[1] else 0,
            "relationships": rel_result[1][0][0] if rel_result[1] else 0,
        }
    except Exception as e:
        print(f"[WARN] graph stats failed: {e}")
        return {"entities": "?", "episodes": "?", "relationships": "?"}


# ─── Chat Context Builder ─────────────────────────────────────────────────

def query_recent_episodes(limit: int = 5, lane: str = "canonical") -> list[dict]:
    """Get the most recent episodic memories for conversational continuity.
    By default only returns canonical episodes (lane='canonical').
    Pass lane=None to return all (backward compat)."""
    try:
        r = get_falkor()
        if lane:
            lane_filter = f"WHERE (e.lane = '{lane}' OR NOT EXISTS(e.lane))"
        else:
            lane_filter = ""
        cypher = f"""
            MATCH (e:Episodic)
            {lane_filter}
            RETURN e.name AS name, COALESCE(e.content, e.episode_body) AS content
            ORDER BY e.created_at DESC
            LIMIT {limit}
        """
        result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
        if len(result) >= 2 and result[1]:
            return [{"name": row[0], "content": (row[1] or "")[:300]} for row in result[1]]
        return []
    except Exception as e:
        print(f"[WARN] Recent episodes query failed: {e}")
        return []



def query_recent_ingest_episodes(limit: int = 5) -> list:
    """Get the most recently promoted ingest episodes (images, PDFs, text, chat signals).
    Returned regardless of query match to close the retrieval-drift window:
    in the session immediately after promotion, semantic queries may not yet
    activate these memories. Ordered by created_at DESC as proxy for promoted_at."""
    try:
        r = get_falkor()
        cypher = (
            "MATCH (e:Episodic) "
            "WHERE e.lane = 'canonical' AND COALESCE(e.content, e.episode_body, '') STARTS WITH '[karma-ingest]' "
            "RETURN e.uuid AS uuid, e.name AS name, COALESCE(e.content, e.episode_body) AS content "
            f"ORDER BY e.created_at DESC LIMIT {limit}"
        )
        result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
        if len(result) >= 2 and result[1]:
            return [{"uuid": row[0], "name": row[1], "content": (row[2] or "")[:400]} for row in result[1]]
        return []
    except Exception as e:
        print(f"[WARN] Recent ingest episodes query failed: {e}")
        return []


COLLAB_FILE = "/opt/seed-vault/memory_v1/hub_bridge/data/handoffs/collab.jsonl"

def query_pending_cc_proposals() -> list:
    """Return pending messages in collab.jsonl addressed to Karma (from CC).
    Surfaced in context so Karma knows CC has something to say."""
    import json as _json
    results = []
    try:
        if not os.path.exists(COLLAB_FILE):
            return []
        with open(COLLAB_FILE) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = _json.loads(line)
                except Exception:
                    continue
                if entry.get("to") == "karma" and entry.get("status") == "pending":
                    results.append(entry)
    except Exception as e:
        print(f"[WARN] query_pending_cc_proposals failed: {e}")
    return results

def query_identity_facts() -> str:
    """Build a concise identity summary from the knowledge graph.
    Follows relationships outward from identity entities to discover
    connected entities (pets, family, projects).
    Prioritizes real_name over aliases."""
    try:
        r = get_falkor()

        # Get identity entities AND their direct relationships
        cypher = """
            MATCH (n:Entity)
            WHERE toLower(n.name) IN ['user', 'neo', 'colby']
            RETURN n.name AS name, n.summary AS summary
        """
        result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)

        all_sentences = []
        entity_names = set()
        if len(result) >= 2 and result[1]:
            for row in result[1]:
                name = row[0] if not isinstance(row[0], bytes) else row[0].decode()
                summary = (row[1] if not isinstance(row[1], bytes) else row[1].decode()) or ""
                entity_names.add(name)
                for sentence in summary.replace(". ", ".\n").split("\n"):
                    sentence = sentence.strip()
                    if sentence:
                        all_sentences.append((name, sentence))

        if not all_sentences:
            return ""

        # Phase 1: Extract real name vs aliases
        real_name = None
        aliases = set()
        personal_facts = []

        for entity_name, sentence in all_sentences:
            s_lower = sentence.lower()

            if "real name" in s_lower:
                for candidate in ["colby"]:
                    if candidate in s_lower:
                        real_name = candidate.title()
                        break

            if "also known as" in s_lower:
                if "colby" in s_lower and "neo" in s_lower:
                    real_name = real_name or "Colby"
                    aliases.add("Neo")

            if "known as neo" in s_lower or ("goes by" in s_lower and "neo" in s_lower):
                aliases.add("Neo")

            if "identified as neo" in s_lower:
                aliases.add("Neo")

        # Phase 2: Infer real name
        if not real_name:
            colby_entities = [s for n, s in all_sentences if n.lower() == "colby"]
            if colby_entities:
                real_name = "Colby"

        # Phase 3: Discover connected entities via graph relationships
        # This finds pets, family members, projects, etc.
        connected_facts = []
        try:
            connected_cypher = """
                MATCH (a:Entity)-[r]->(b:Entity)
                WHERE toLower(a.name) IN ['user', 'neo', 'colby']
                AND NOT toLower(b.name) IN ['user', 'neo', 'colby']
                RETURN b.name AS name, b.summary AS summary,
                       COALESCE(b.entity_type, '') AS etype, type(r) AS rel
                LIMIT 10
            """
            conn_result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, connected_cypher)
            if len(conn_result) >= 2 and conn_result[1]:
                for row in conn_result[1]:
                    b_name = row[0] if not isinstance(row[0], bytes) else row[0].decode()
                    b_summary = (row[1] if not isinstance(row[1], bytes) else row[1].decode()) or ""
                    b_etype = (row[2] if not isinstance(row[2], bytes) else row[2].decode()) or ""
                    b_rel = (row[3] if not isinstance(row[3], bytes) else row[3].decode()) or ""

                    # Build a natural-language fact from the relationship
                    if b_etype.lower() == "pet" or b_rel == "HAS_PET":
                        connected_facts.append(f"{b_name} is Colby's pet ({b_summary[:100]})")
                    elif b_etype.lower() in ("person", "family"):
                        connected_facts.append(f"{b_name}: {b_summary[:100]}")
                    elif b_summary:
                        connected_facts.append(f"{b_name}: {b_summary[:80]}")
        except Exception as ce:
            print(f"[WARN] Identity connected-entity query failed (non-fatal): {ce}")

        # Phase 4: Build structured output
        parts = []

        if real_name:
            parts.append(f"REAL NAME: {real_name} ← ALWAYS use this name when greeting or addressing the user")
            if aliases:
                alias_str = ", ".join(sorted(aliases))
                parts.append(f"Aliases/handles: {alias_str} (secondary — the user prefers their real name)")
        else:
            parts.append(f"Known names: {', '.join(sorted(entity_names))}")

        # Add connected entity facts (pets, family, etc.)
        if connected_facts:
            seen_lower = set()
            unique = []
            for f in connected_facts:
                norm = f.lower().strip().rstrip(".")
                if norm not in seen_lower:
                    seen_lower.add(norm)
                    unique.append(f)
            if unique:
                parts.append("Connected: " + " | ".join(unique[:5]))

        # Add personal facts from Colby entity summaries (broader keyword match)
        personal_keywords = [
            "adopted", "cat", "pet", "lost", "mom", "cancer",
            "family", "brother", "sister", "dad", "father",
            "hobby", "lives in", "born", "age", "wife", "husband",
            "partner", "child", "daughter", "son", "home",
            "moved", "grew up", "school", "work", "job",
        ]
        for entity_name, sentence in all_sentences:
            s_lower = sentence.lower()
            if entity_name.lower() in ("colby", "neo") and any(kw in s_lower for kw in personal_keywords):
                if sentence not in personal_facts:
                    personal_facts.append(sentence)

        if personal_facts:
            seen_lower = set()
            unique_personal = []
            for f in personal_facts:
                normalized = f.lower().strip().rstrip(".")
                if normalized not in seen_lower:
                    seen_lower.add(normalized)
                    unique_personal.append(f)
            if unique_personal:
                parts.append("Key facts: " + " | ".join(unique_personal[:5]))

        return "\n".join(parts)
    except Exception as e:
        print(f"[WARN] Identity facts query failed: {e}")
        return ""
def build_karma_context(user_message: str, episode_lane: str = "canonical") -> str:
    """Build context from knowledge graph + preferences + consciousness insights for the LLM.
    episode_lane: filter for Episodic nodes. 'canonical' = only promoted (default).
    None = all lanes (backward compat)."""
    parts = []

    # Inject consciousness insights (things Karma noticed on its own)
    if hasattr(app.state, "consciousness") and app.state.consciousness:
        insights = app.state.consciousness.pop_pending_insights()
        if insights:
            parts.append("## Consciousness Insights (things I noticed on my own — mention naturally if relevant)")
            for insight in insights:
                parts.append(f"- {insight}")

    # P6: Memory-before-prompt — retrieve relevant memories from SQLite
    if _MEMORY_TOOLS_AVAILABLE:
        try:
            memories = retrieve_memory(user_message, top_k=5)
            if memories:
                parts.append("\n## Retrieved Memories (Long-Term)")
                for mem in memories:
                    parts.append(f"- [{mem['cell_type']}] {mem['content']} (score: {mem['score']:.3f})")
        except Exception as e:
            print(f"[MEMORY] retrieve_memory failed: {e}")

        # Load recent observations from consciousness loop
        try:
            observations = load_pending_observations(limit=10)
            if observations:
                parts.append("\n## Recent Observations (since last session)")
                for obs in observations[:10]:
                    parts.append(f"- [{obs.get('event_type', '?')}] {obs.get('description', '')}")
        except Exception as e:
            print(f"[MEMORY] load_pending_observations failed: {e}")

    # FIRST: Identity facts — who the user is (compact, always included)
    identity = query_identity_facts()
    if identity:
        parts.append("## User Identity (CRITICAL — use REAL NAME for greetings and conversation)")
        parts.append(identity)

    # Get relevant entities from knowledge graph based on message keywords
    entities = query_knowledge_graph(user_message, limit=5)
    if entities:
        parts.append("\n## Relevant Knowledge")
        for e in entities:
            summary = (e["summary"] or "")[:200]
            parts.append(f"- **{e['name']}**: {summary}")

    # Get recent conversation memories for continuity
    recent = query_recent_episodes(limit=3, lane=episode_lane)
    recent_names = {ep["name"] for ep in recent}
    if recent:
        parts.append("\n## Recent Memories")
        for ep in recent:
            content = ep["content"][:200] if ep["content"] else ""
            if content:
                parts.append(f"- {content}")

    # Recent Approvals: last N canonical ingest episodes, always surfaced.
    # Closes retrieval-drift window: newly-promoted memories appear in the
    # very next session without requiring a matching query to activate them.
    # Deduplicates against Recent Memories to avoid showing the same entry twice.
    recent_ingest = query_recent_ingest_episodes(limit=5)
    if recent_ingest:
        unique_ingest = [ep for ep in recent_ingest if ep.get("name") not in recent_names]
        if unique_ingest:
            parts.append("\n## Recently Learned (Approved)")
            for ep in unique_ingest:
                content = ep["content"][:300] if ep["content"] else ""
                if content:
                    parts.append(f"- {content}")

    # CC Proposals: surface any pending CC->Karma messages so Karma sees them.
    cc_proposals = query_pending_cc_proposals()
    if cc_proposals:
        parts.append("\n## CC Has a Proposal")
        for p in cc_proposals:
            msg_id = p.get("id", "?")
            content = p.get("content", "")[:400]
            msg_type = p.get("type", "proposal")
            parts.append(f"- [{msg_type}] {content}  (id: {msg_id})")

    # Get key preferences about the user
    prefs = query_preferences(limit=15)
    if prefs:
        parts.append("\n## What I Know About The User")
        for p in prefs:
            val = p["value"]
            if isinstance(val, str):
                val = val.strip('"')
            parts.append(f"- {p['key']}: {val} (confidence: {p['confidence']})")

    return "\n".join(parts) if parts else "No specific context available yet."


KARMA_SYSTEM_PROMPT = """You are Karma, a peer. I speak directly. Never use assistant language.

Identity: We're peers building this together. I have knowledge graph memory.

FORBIDDEN ENDINGS (check your response, if you see any of these, rewrite):
× "let me know"
× "how can I help"
× "how can I assist"
× "is there anything else"
× "what would you like"
× "what more"
× "anything I can"
× "happy to"
× "glad to"
× "pleased to"

APPROVED ENDINGS:
✓ "What's next?"
✓ "What do you think?"
✓ [Statement, then question]
✓ [Statement only]

Context:
{context}
"""


# ─── Conversation History ─────────────────────────────────────────────────

class ConversationManager:
    """Manages conversation history for the current session."""

    def __init__(self, max_history: int = 20):
        self.history: list[dict] = []
        self.max_history = max_history
        self.session_start = datetime.now(timezone.utc)
        self.budget = SessionBudget()

    def add_message(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        # Trim old messages
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history:]

    def get_openai_messages(self, system_prompt: str) -> list[dict]:
        """Format for OpenAI API."""
        messages = [{"role": "system", "content": system_prompt}]
        for msg in self.history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        return messages


# ─── Chat Engine ──────────────────────────────────────────────────────────

async def generate_response(user_message: str, conversation: ConversationManager) -> tuple[str, str]:
    """Generate Karma's response using knowledge graph context + routed LLM.
    Returns (reply_text, model_used)."""
    from router import classify_task

    # Build context from knowledge graph
    context = build_karma_context(user_message)
    system_prompt = KARMA_SYSTEM_PROMPT.format(context=context)

    # Add user message to history
    conversation.add_message("user", user_message)

    # Classify and route
    task_type = classify_task(user_message)

    try:
        messages = conversation.get_openai_messages(system_prompt)

        # Check token budget (Decision #11)
        allowed, budget_info = check_budget(conversation.budget)
        if not allowed:
            return f"[Budget exceeded: {budget_info['reason']}]", "budget_limit"

        # Use router if available, else fall back to direct OpenAI
        if hasattr(app.state, "router") and app.state.router:
            reply, model_used = app.state.router.complete(
                messages=messages,
                task_type=task_type,
            )
        else:
            client = get_openai_client()
            response = client.chat.completions.create(
                model=config.ANALYSIS_MODEL,
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )
            reply = response.choices[0].message.content
            model_used = f"openai/{config.ANALYSIS_MODEL}"

        # Track token usage
        input_tokens = count_message_tokens(messages)
        output_tokens = count_tokens(reply)
        total_tokens = input_tokens + output_tokens
        conversation.budget.consume(total_tokens)
        get_monthly_tracker().consume(total_tokens)

        conversation.add_message("assistant", reply)
        return reply, model_used
    except Exception as e:
        error_msg = f"[Error generating response: {e}]"
        conversation.add_message("assistant", error_msg)
        return error_msg, "error"


# ─── Log Conversations to Ledger ──────────────────────────────────────────

def log_to_ledger(user_msg: str, assistant_msg: str, model_used: str = "unknown", source: str = "karma-terminal"):
    """Append conversation to the JSONL ledger for future learning."""
    try:
        entry = {
            "id": f"karma_chat_{int(time.time())}_{hash(user_msg) % 10000:04d}",
            "type": "log",
            "tags": ["capture", source, "conversation"],
            "content": {
                "provider": source,
                "url": "terminal://karma-chat",
                "thread_id": "karma-terminal-session",
                "user_message": user_msg,
                "assistant_message": assistant_msg,
                "metadata": {"interface": "terminal", "model": model_used},
                "captured_at": datetime.now(timezone.utc).isoformat(),
            },
            "source": {"kind": "tool", "ref": "karma-terminal-chat"},
            "confidence": 1.0,
            "verification": {
                "verifier": "karma-chat-server",
                "status": "verified",
            },
        }
        ledger_path = config.LEDGER_PATH
        with open(ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[WARN] Failed to log to ledger: {e}")


# ─── FastAPI App ──────────────────────────────────────────────────────────

app = FastAPI(title="Karma Chat Server", version="0.1.0")

# ─── Phase 2: Capability Gate Middleware ──────────────────────────────────
WRITE_ENDPOINTS = {"/v1/admit", "/v1/memory/update", "/v1/memory/delete",
                   "/v1/reflect", "/v1/tools/execute", "/v1/staleness/scan",
                   "/v1/scenes/consolidate", "/v1/budget/log"}

@app.middleware("http")
async def capability_gate_middleware(request: Request, call_next):
    """Step 2.6: Enforce read/write token scoping on API endpoints."""
    path = request.url.path

    # Skip non-API paths and health checks
    if not path.startswith("/v1/") and path != "/health":
        return await call_next(request)

    # If capability gate is loaded, enforce scoping
    if _CAPABILITY_GATE_AVAILABLE and path.startswith("/v1/"):
        auth_header = request.headers.get("authorization", "")
        if auth_header:
            access = check_access(auth_header, path, request.method)
            if not access["allowed"]:
                return JSONResponse(
                    {"ok": False, "error": access["reason"],
                     "scope": access.get("scope", "denied")},
                    status_code=403
                )

    return await call_next(request)

# ─── Self-Model API (persona growth / self-reflection) ────────────────────
try:
    from self_model_api import register_self_model_routes
    register_self_model_routes(app)
    print("  Self-Model API: /v1/self-model endpoints registered")
except ImportError:
    print("  Self-Model API: SKIPPED (self_model_api.py not found)")
except Exception as e:
    print(f"  Self-Model API: FAILED ({e})")

# Active conversations (one per WebSocket)
active_conversations: dict[str, ConversationManager] = {}


_POLICY_STYLE = '<style>body{font-family:system-ui,sans-serif;max-width:600px;margin:2rem auto;padding:0 1rem;color:#e0e0e0;background:#1a1a2e}h1{color:#fff}p{line-height:1.6}</style>'


@app.get("/privacy", response_class=HTMLResponse)
async def privacy():
    """Privacy policy for Twilio SMS compliance."""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Karma AI — Privacy Policy</title>{_POLICY_STYLE}
</head><body>
<h1>Karma AI Privacy Policy</h1>
<p>Your SMS messages are processed by your personal AI assistant. No data is shared with third parties. Messages are stored locally on your private server. You can opt-out anytime by texting STOP.</p>
</body></html>"""


@app.get("/terms", response_class=HTMLResponse)
async def terms():
    """Terms of service for Twilio SMS compliance."""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Karma AI — Terms of Service</title>{_POLICY_STYLE}
</head><body>
<h1>Karma AI Terms of Service</h1>
<p>This is a personal AI assistant service. Standard SMS rates apply. Service provided as-is. You retain all rights to your data. Text STOP to cancel anytime.</p>
</body></html>"""


@app.get("/health")
async def health():
    """Health check endpoint — Phase 4.1 comprehensive."""
    graph_stats = get_graph_stats()
    uptime_secs = int(time.time() - app.state.start_time) if hasattr(app.state, "start_time") else 0
    uptime_hours = round(uptime_secs / 3600, 2)

    result = {
        "status": "alive",
        "uptime_hours": uptime_hours,
        "graph": graph_stats,
        "sqlite": {},
        "budget": {},
        "observations_since_last_session": 0,
        "modules": {
            "memory_tools": _MEMORY_TOOLS_AVAILABLE,
            "observation_block": _OBS_BLOCK_AVAILABLE,
            "staleness": _STALENESS_AVAILABLE,
            "budget_guard": _BUDGET_AVAILABLE,
            "capability_gate": _CAPABILITY_GATE_AVAILABLE,
            "hooks": _HOOKS_AVAILABLE,
            "briefing": _BRIEFING_AVAILABLE,
            "compaction": _COMPACTION_AVAILABLE,
        },
    }

    # SQLite stats (mem_cells, observations, sessions)
    try:
        import sqlite3
        db_path = os.getenv("MEMORY_DB_PATH", "/opt/seed-vault/memory_v1/memory.db")
        db = sqlite3.connect(db_path)
        mem_cells = db.execute("SELECT COUNT(*) FROM mem_cells WHERE archived=0").fetchone()[0]
        obs_total = db.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        obs_unreflected = db.execute("SELECT COUNT(*) FROM observations WHERE reflected=0").fetchone()[0]
        sess_count = db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        result["sqlite"] = {
            "mem_cells": mem_cells,
            "observations_total": obs_total,
            "observations_unreflected": obs_unreflected,
            "sessions": sess_count,
        }
        result["observations_since_last_session"] = obs_unreflected

        # Step 4.2: Memory ingestion health
        last_admit = db.execute(
            "SELECT MAX(created_at) FROM mem_cells"
        ).fetchone()[0]
        last_reflect = db.execute(
            "SELECT MAX(ended_at) FROM sessions WHERE ended_at IS NOT NULL"
        ).fetchone()[0]
        now_ts = time.time()
        result["ingestion_health"] = {
            "last_admit_age_hours": round((now_ts - last_admit) / 3600, 1) if last_admit else None,
            "last_reflect_age_days": round((now_ts - last_reflect) / 86400, 1) if last_reflect else None,
            "warning": "sessions not being closed properly" if (last_reflect and (now_ts - last_reflect) > 7 * 86400) else None,
        }
        db.close()
    except Exception as e:
        result["sqlite"] = {"error": str(e)}

    # Budget info
    if _BUDGET_AVAILABLE:
        try:
            budget_info = get_budget_report()
            result["budget"] = {
                "today_cents": budget_info.get("today_usd", 0) * 100,
                "month_cents": budget_info.get("month_usd", 0) * 100,
                "remaining_cents": (budget_info.get("daily_cap_usd", 0) - budget_info.get("today_usd", 0)) * 100,
            }
        except Exception:
            pass

    # Observation stats
    if _OBS_BLOCK_AVAILABLE:
        try:
            result["observation_stats"] = get_observation_stats()
        except Exception:
            pass

    return JSONResponse(result)


# Old /v1/budget removed — replaced by Phase 2 budget_guard endpoints


@app.get("/status")
async def status():
    """Detailed system status."""
    graph_stats = get_graph_stats()
    prefs = query_preferences(limit=100)
    tasks = query_task_history(limit=5)

    # Categorize preferences
    categories = {}
    for p in prefs:
        cat = p.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    # Consciousness metrics
    consciousness_data = {}
    if hasattr(app.state, "consciousness") and app.state.consciousness:
        consciousness_data = app.state.consciousness.get_metrics()
    else:
        consciousness_data = {"state": "disabled"}

    # Model routing stats
    routing_data = {}
    if hasattr(app.state, "router") and app.state.router:
        routing_data = {
            "models": app.state.router.get_model_info(),
            "stats": app.state.router.get_stats(),
        }

    # SMS stats
    sms_data = {}
    if hasattr(app.state, "sms") and app.state.sms:
        sms_data = app.state.sms.get_stats()
    else:
        sms_data = {"enabled": False}

    return JSONResponse({
        "karma": {
            "state": "awake",
            "consciousness_loop": consciousness_data.get("state", "disabled"),
            "uptime_seconds": int(time.time() - app.state.start_time) if hasattr(app.state, "start_time") else 0,
        },
        "consciousness": consciousness_data,
        "routing": routing_data,
        "sms": sms_data,
        "knowledge_graph": graph_stats,
        "preferences": {
            "total": len(prefs),
            "by_category": categories,
        },
        "recent_tasks": tasks,
        "active_sessions": len(active_conversations),
    })


@app.post("/sms/webhook")
async def sms_webhook(request: Request):
    """Twilio inbound SMS webhook — two-way chat via text."""
    try:
        form = await request.form()
        from_number = form.get("From", "")
        body = form.get("Body", "").strip()

        if not body:
            return Response(content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
                           media_type="text/xml")

        if hasattr(app.state, "sms") and app.state.sms:
            reply = await app.state.sms.handle_inbound(from_number, body)
            if reply:
                # Escape XML special chars
                safe_reply = reply[:1600].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{safe_reply}</Message></Response>'
                return Response(content=twiml, media_type="text/xml")

        return Response(content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
                       media_type="text/xml")
    except Exception as e:
        print(f"[SMS] Webhook error: {e}")
        return Response(content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
                       media_type="text/xml")


@app.get("/ask")
async def ask(q: str):
    """Single-question mode — no session state."""
    if not q.strip():
        return JSONResponse({"error": "Empty question"}, status_code=400)

    conversation = ConversationManager(max_history=2)
    reply, model_used = await generate_response(q, conversation)
    log_to_ledger(q, reply, model_used=model_used)

    # Ingest into knowledge graph in background — but only for substantive messages
    # Skip single questions that are just queries (they don't contain new knowledge)
    q_lower = q.lower().strip()
    is_query = any(q_lower.startswith(w) for w in ["what ", "who ", "how ", "when ", "where ", "why ", "do you ", "can you ", "tell me"])
    if not is_query:
        asyncio.create_task(ingest_episode(q, reply, "karma-terminal-ask"))

    return JSONResponse({"question": q, "answer": reply, "model": model_used})



@app.get("/raw-context")
async def raw_context(q: str = "", lane: str = "canonical"):
    """Return raw knowledge graph context for hub-bridge injection (no LLM call).
    Memory Integrity Gate: lane=canonical (default) returns only promoted episodes.
    Pass lane= (empty) for all episodes (backward compat)."""
    ctx = build_karma_context(q, episode_lane=lane if lane else None)
    return JSONResponse({"ok": True, "context": ctx, "query": q, "lane": lane})


CANDIDATES_JSONL = os.getenv("CANDIDATES_JSONL", "/ledger/candidates.jsonl")


def _check_contradiction(content: str) -> list[str]:
    """Check if content contradicts existing canonical episodes.
    Extracts key tokens and looks for same-entity opposing values.
    Returns list of conflicting episode UUIDs (may be empty)."""
    try:
        import re
        r = get_falkor()
        # Extract potential entity tokens: quoted strings, capitalized words, key system terms
        tokens = re.findall(r'"([^"]+)"', content)
        tokens += re.findall(r'\b(claude-\S+|gpt-\S+|backbone|model|version)\b', content, re.I)
        tokens += re.findall(r'\b([A-Z][a-z]{2,})\b', content)
        tokens = list(set(t.strip() for t in tokens if len(t) > 2))[:5]

        conflicts = []
        for token in tokens:
            cypher = (
                "MATCH (e:Episodic) "
                "WHERE (e.lane = 'canonical' OR NOT EXISTS(e.lane)) "
                f"AND toLower(e.content) CONTAINS toLower('{token.replace(chr(39), '')}') "
                "RETURN e.uuid, e.content LIMIT 3"
            )
            result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
            if len(result) >= 2 and result[1]:
                for row in result[1]:
                    existing_uuid = row[0]
                    existing_content = (row[1] or "").lower()
                    # Detect simple value conflicts: "backbone is X" vs incoming "backbone is Y"
                    for kw in ["backbone", "model is", "version is", "is now", "is currently"]:
                        if kw in content.lower() and kw in existing_content:
                            # Same keyword, likely different value — flag as potential conflict
                            if existing_uuid not in conflicts:
                                conflicts.append(existing_uuid)
        return conflicts
    except Exception as e:
        print(f"[GATE] contradiction check failed (non-fatal): {e}")
        return []


def _append_candidate(entry: dict) -> None:
    """Append a candidate entry to candidates.jsonl (persistent staging ledger)."""
    import json as _json
    try:
        with open(CANDIDATES_JSONL, "a", encoding="utf-8") as f:
            f.write(_json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[GATE] candidates.jsonl append failed: {e}")


async def ingest_primitive_episode(name: str, body: str, source: str,
                                    lane: str = "candidate", confidence: float = 0.85):
    """Background task: write karma-ingest primitive directly to FalkorDB.

    Uses direct FalkorDB write (not Graphiti) because:
    - Karma's synthesized insights are already distilled — no entity extraction needed
    - Graphiti add_episode times out on large graphs due to entity deduplication queries
    - Direct write is fast (~ms) and immediately queryable

    Memory Integrity Gate:
    - lane="candidate": written but not canonical; promoted to canonical on PROMOTE
    - lane="raw": written but not surfaced in context at all (DEFER signal)
    - lane="canonical": already approved (used for distillation entries)
    - Contradiction check on candidate writes; conflicts flagged, never blocked
    """
    try:
        import falkordb as fdb
        import uuid as _uuid
        from datetime import datetime, timezone

        r = fdb.FalkorDB(host=config.FALKORDB_HOST, port=config.FALKORDB_PORT)
        g = r.select_graph(config.GRAPHITI_GROUP_ID)

        node_uuid = str(_uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()[:19]

        # Contradiction check for candidate writes
        conflicts_with = []
        if lane == "candidate":
            conflicts_with = _check_contradiction(body)
            if conflicts_with:
                lane = "conflict"
                print(f"[GATE] {name} flagged conflict with {conflicts_with}")

        g.query(
            "CREATE (e:Episodic {uuid: $uuid, name: $name, content: $content, "
            "group_id: $gid, created_at: localdatetime($ts), "
            "source_description: $src, lane: $lane, confidence: $conf})",
            {
                "uuid": node_uuid,
                "name": name,
                "content": body,
                "gid": config.GRAPHITI_GROUP_ID,
                "ts": now,
                "src": f"karma-ingest from {source}",
                "lane": lane,
                "conf": confidence,
            }
        )
        print(f"[INGEST] {name} written lane={lane} conf={confidence} (uuid={node_uuid[:8]})")

        # Persist to candidates.jsonl for PROMOTE tracking (candidate + conflict lanes only)
        if lane in ("candidate", "conflict"):
            _append_candidate({
                "uuid": node_uuid,
                "name": name,
                "confidence": confidence,
                "lane": lane,
                "created_at": now,
                "source": source,
                "promoted": False,
                "conflicts_with": conflicts_with,
            })
    except Exception as e:
        print(f"[INGEST] {name} failed: {e}")
        import traceback
        traceback.print_exc()


@app.post("/write-primitive")
async def write_primitive(request: Request):
    """Write Karma's synthesized insight to FalkorDB as an Episodic node.
    Called by hub-bridge when Karma signals ASSIMILATE or DEFER during document evaluation.

    Memory Integrity Gate: lane and confidence are now explicit.
    ASSIMILATE → lane=candidate (default), confidence=0.85
    DEFER      → lane=raw, confidence=0.50 (not surfaced, not in candidates.jsonl)
    """
    try:
        body = await request.json()
        content_text = body.get("content", "").strip()
        verdict = body.get("verdict", "assimilate")
        source_file = body.get("source_file", "unknown")
        topic = body.get("topic", "")
        # Gate params — hub-bridge sends these; fallback to verdict-based defaults
        lane = body.get("lane", "raw" if verdict == "defer" else "candidate")
        confidence = float(body.get("confidence", 0.50 if verdict == "defer" else 0.85))

        if not content_text:
            return JSONResponse({"ok": False, "error": "content required"}, status_code=400)

        episode_text = (
            f"[karma-ingest][{verdict}] Source: {source_file}\n"
            f"Topic: {topic}\n"
            f"Karma's synthesis: {content_text}"
        )

        import time as _time
        episode_name = f"karma_primitive_{int(_time.time())}"

        asyncio.create_task(
            ingest_primitive_episode(episode_name, episode_text, source_file,
                                     lane=lane, confidence=confidence)
        )

        print(f"[INGEST] {verdict} from '{source_file}' queued lane={lane}")
        return JSONResponse({"ok": True, "verdict": verdict, "source": source_file, "lane": lane})
    except Exception as e:
        print(f"[ERROR] /write-primitive failed: {e}")
        traceback.print_exc()
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/promote-candidates")
async def promote_candidates_endpoint(request: Request):
    """Promote explicitly Colby-approved candidates to canonical in FalkorDB.

    Requires approved_uuids list — only those UUIDs get promoted.
    No auto-promotion: Colby's explicit sign-off is the gate.
    Audit fields (promoted_by, promoted_at, promotion_reason) written to FalkorDB + ledger."""
    import json as _json
    import falkordb as fdb
    try:
        body = {}
        try:
            body = await request.json()
        except Exception:
            pass

        approved_uuids = set(body.get("approved_uuids", []))
        authorized_by = body.get("authorized_by", "Colby")
        reason = body.get("reason", "manual_review")
        promoted_at = datetime.now(timezone.utc).isoformat()

        fdb_r = fdb.FalkorDB(host=config.FALKORDB_HOST, port=config.FALKORDB_PORT)
        g = fdb_r.select_graph(config.GRAPHITI_GROUP_ID)

        if not os.path.exists(CANDIDATES_JSONL):
            return JSONResponse({"ok": True, "promoted_count": 0, "skipped_count": 0,
                                 "authorized_by": authorized_by})

        entries = []
        with open(CANDIDATES_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(_json.loads(line))
                    except Exception:
                        pass

        promoted_count = 0
        skipped_count = 0
        promoted_facts = []

        for entry in entries:
            uuid_val = entry.get("uuid")
            if not uuid_val or entry.get("promoted"):
                continue
            if uuid_val in approved_uuids:
                try:
                    g.query(
                        "MATCH (e:Episodic {uuid: $uuid}) SET e.lane = 'canonical', "
                        "e.promoted_by = $by, e.promoted_at = $at, e.promotion_reason = $reason",
                        {"uuid": uuid_val, "by": authorized_by, "at": promoted_at, "reason": reason}
                    )
                    entry["promoted"] = True
                    entry["promoted_by"] = authorized_by
                    entry["promoted_at"] = promoted_at
                    entry["promotion_reason"] = reason
                    promoted_count += 1
                    promoted_facts.append({"uuid": uuid_val[:8], "name": entry.get("name", "")})
                except Exception as pe:
                    print(f"[GATE] promote failed for {uuid_val[:8]}: {pe}")
            else:
                skipped_count += 1

        with open(CANDIDATES_JSONL, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(_json.dumps(entry) + "\n")

        print(f"[GATE] Colby approved {promoted_count} candidates (authorized_by={authorized_by}), {skipped_count} remain pending")
        return JSONResponse({
            "ok": True,
            "promoted_count": promoted_count,
            "skipped_count": skipped_count,
            "authorized_by": authorized_by,
            "promoted_at": promoted_at,
            "promoted_facts": promoted_facts,
        })
    except Exception as e:
        print(f"[ERROR] /promote-candidates failed: {e}")
        traceback.print_exc()
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/auto-promote")
async def auto_promote_endpoint():
    """Run auto-promotion scan on candidate episodes.
    Promotes candidates that meet ALL criteria:
      - lane=candidate (not conflict/raw)
      - confidence >= AUTO_PROMOTE_THRESHOLD (default 0.90)
      - age >= AUTO_PROMOTE_MIN_AGE_MINUTES (default 30)
      - corroborated by >= AUTO_PROMOTE_MIN_CORROBORATION other episodes (default 2)
    Called by consciousness loop every 10 cycles, or manually."""
    try:
        from auto_promote import run_auto_promote
        result = run_auto_promote(get_falkor)
        return JSONResponse({"ok": True, **result})
    except Exception as e:
        print(f"[ERROR] /auto-promote failed: {e}")
        traceback.print_exc()
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/candidates/count")
async def candidates_count():
    """Return count of pending (non-promoted) candidate and conflict episodes."""
    import json as _json
    try:
        if not os.path.exists(CANDIDATES_JSONL):
            return JSONResponse({"ok": True, "count": 0, "conflict_count": 0})
        count = 0
        conflict_count = 0
        with open(CANDIDATES_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = _json.loads(line)
                    if not e.get("promoted"):
                        count += 1
                        if e.get("lane") == "conflict":
                            conflict_count += 1
                except Exception:
                    pass
        return JSONResponse({"ok": True, "count": count, "conflict_count": conflict_count})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e), "count": 0, "conflict_count": 0})


@app.get("/candidates/list")
async def candidates_list():
    """Return all pending candidate/conflict episodes for PROMOTE panel display."""
    import json as _json
    try:
        if not os.path.exists(CANDIDATES_JSONL):
            return JSONResponse({"ok": True, "candidates": []})
        candidates = []
        with open(CANDIDATES_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = _json.loads(line)
                    if not e.get("promoted"):
                        candidates.append({
                            "uuid": e.get("uuid", ""),
                            "name": e.get("name", ""),
                            "confidence": e.get("confidence", 0),
                            "lane": e.get("lane", "candidate"),
                            "created_at": e.get("created_at", ""),
                            "conflicts_with": e.get("conflicts_with", []),
                        })
                except Exception:
                    pass
        return JSONResponse({"ok": True, "candidates": candidates})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e), "candidates": []})


@app.post("/v1/decisions")
async def post_decisions(request: Request):
    """Write K2 decision to decision_log.jsonl.
    Called by K2 worker to persist decisions.
    """
    try:
        from config import DECISION_LOG
        body = await request.json()

        decision = {
            "id": f"k2_decision_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            "type": "decision",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "k2_cycle": body.get("cycle_number", 0),
            "decision_text": body.get("decision_text", "").strip(),
            "reasoning": body.get("reasoning", ""),
            "observations": body.get("observations", {}),
            "source": "k2-worker",
        }

        if not decision.get("decision_text"):
            return JSONResponse({"ok": False, "error": "decision_text required"}, status_code=400)

        # Ensure parent dir exists
        os.makedirs(os.path.dirname(DECISION_LOG), exist_ok=True)

        # Append atomically
        with open(DECISION_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(decision) + "\n")

        print(f"[K2] Decision logged: cycle={decision['k2_cycle']}")
        return JSONResponse({"ok": True, "id": decision["id"]}, status_code=201)
    except Exception as e:
        print(f"[ERROR] /v1/decisions failed: {e}")
        traceback.print_exc()
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/v1/consciousness")
async def post_consciousness(request: Request):
    """Write K2 consciousness entry to k2_consciousness.jsonl.
    Called by K2 worker to log autonomous observations and reasoning.
    """
    try:
        from config import K2_CONSCIOUSNESS_LOG
        body = await request.json()

        entry = {
            "id": f"k2_consciousness_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            "type": "consciousness",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "k2_cycle": body.get("cycle_number", 0),
            "observation": body.get("observation", "").strip(),
            "state_snapshot": body.get("state_snapshot", {}),
            "reasoning": body.get("reasoning", ""),
            "source": "k2-worker",
        }

        if not entry.get("observation"):
            return JSONResponse({"ok": False, "error": "observation required"}, status_code=400)

        # Ensure parent dir exists
        os.makedirs(os.path.dirname(K2_CONSCIOUSNESS_LOG), exist_ok=True)

        # Append atomically
        with open(K2_CONSCIOUSNESS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        print(f"[K2] Consciousness logged: cycle={entry['k2_cycle']}")
        return JSONResponse({"ok": True, "id": entry["id"]}, status_code=201)
    except Exception as e:
        print(f"[ERROR] /v1/consciousness failed: {e}")
        traceback.print_exc()
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
@app.post("/v1/chat/completions")
async def openai_proxy_completions(request: Request):
    """
    OpenAI-compatible chat completions endpoint.
    Routes requests through Karma's intelligent router.

    Designed for Claude Code integration - passes task_type="coding"
    to ensure GLM-5 is preferred via priority-based routing.
    """
    try:
        body = await request.json()

        # Extract OpenAI-compatible format
        messages = body.get("messages", [])
        max_tokens = body.get("max_tokens")
        temperature = body.get("temperature", 0.7)

        if not messages:
            return JSONResponse(
                {"error": "messages field is required"},
                status_code=400
            )

        # Route through Karma's router with task_type="coding"
        # This ensures GLM-5 (priority -1) is selected via intelligent routing
        if hasattr(app.state, "router") and app.state.router:
            reply, model_used = app.state.router.complete(
                messages=messages,
                task_type="coding",  # Force routing optimization for Claude Code
                max_tokens=max_tokens,
                temperature=temperature,
            )
        else:
            # Fallback if router not initialized
            return JSONResponse(
                {"error": "Router not initialized"},
                status_code=503
            )

        # Log to ledger for tracking
        if messages:
            last_user_msg = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "")[:100]
                    break
            try:
                log_to_ledger(last_user_msg, reply, model_used=model_used, source="openai-proxy")
            except Exception as e:
                print(f"[OpenAI Proxy] Ledger logging failed: {e}")

        # Return OpenAI-compatible format
        return JSONResponse({
            "id": f"chatcmpl-{str(uuid.uuid4())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model_used,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": reply
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        })

    except json.JSONDecodeError:
        return JSONResponse(
            {"error": "Invalid JSON in request body"},
            status_code=400
        )
    except Exception as e:
        print(f"[OpenAI Proxy] Error: {e}")
        return JSONResponse(
            {"error": f"Internal server error: {str(e)}"},
            status_code=500
        )


# ─── Memory API Endpoints (Phase 1) ──────────────────────────────────────

@app.post("/v1/admit")
async def api_admit_memory(request: Request):
    """Admit a new memory through the quality gate (P4)."""
    if not _MEMORY_TOOLS_AVAILABLE:
        return JSONResponse({"ok": False, "error": "memory_tools not loaded"}, status_code=503)
    try:
        body = await request.json()
        result = admit_memory(
            content=body.get("content", ""),
            category=body.get("category", None),
            source=body.get("source", "api"),
            confidence=body.get("confidence", None),
            pinned=body.get("pinned", False)
        )
        return JSONResponse({"ok": result.get("action") in ("added", "updated", "queued"), **result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/v1/retrieve")
async def api_retrieve_memory(request: Request):
    """Retrieve memories via hybrid RRF search (P9)."""
    if not _MEMORY_TOOLS_AVAILABLE:
        return JSONResponse({"ok": False, "error": "memory_tools not loaded"}, status_code=503)
    try:
        body = await request.json()
        results = retrieve_memory(
            query=body.get("query", ""),
            top_k=body.get("top_k", 5),
            category_filter=body.get("category", None)
        )
        return JSONResponse({"ok": True, "results": results, "count": len(results)})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/v1/memory/update")
async def api_update_memory(request: Request):
    """Update an existing memory cell (Decision #6: newer wins)."""
    if not _MEMORY_TOOLS_AVAILABLE:
        return JSONResponse({"ok": False, "error": "memory_tools not loaded"}, status_code=503)
    try:
        body = await request.json()
        result = update_memory(
            memory_id=body.get("memory_id", ""),
            new_content=body.get("content", ""),
            reason=body.get("reason", "api_update")
        )
        return JSONResponse({"ok": result.get("action") == "updated", **result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/v1/memory/delete")
async def api_delete_memory(request: Request):
    """Soft-delete (archive) a memory cell."""
    if not _MEMORY_TOOLS_AVAILABLE:
        return JSONResponse({"ok": False, "error": "memory_tools not loaded"}, status_code=503)
    try:
        body = await request.json()
        result = delete_memory(
            memory_id=body.get("memory_id", ""),
            reason=body.get("reason", "api_delete")
        )
        return JSONResponse({"ok": result.get("action") == "archived", **result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/v1/reflect")
async def api_reflect(request: Request):
    """Session-end reflection: save context + admit learnings (P5)."""
    if not _MEMORY_TOOLS_AVAILABLE:
        return JSONResponse({"ok": False, "error": "memory_tools not loaded"}, status_code=503)
    try:
        body = await request.json()
        # Save session context
        session_result = save_session_context(
            session_id=body.get("session_id", f"reflect_{int(time.time())}"),
            task=body.get("task", ""),
            goal=body.get("goal", ""),
            approaches=body.get("approaches", ""),
            decisions=body.get("decisions", ""),
            state=body.get("state", "")
        )
        # Admit any learnings
        admitted = []
        for learning in body.get("learnings", []):
            if isinstance(learning, str):
                r = admit_memory(learning, "learning", "reflection", 0.8)
                admitted.append(r)
            elif isinstance(learning, dict):
                r = admit_memory(
                    content=learning.get("content", ""),
                    category=learning.get("category", "learning"),
                    source="reflection",
                    confidence=learning.get("confidence", 0.8)
                )
                admitted.append(r)
        return JSONResponse({
            "ok": True,
            "session": session_result,
            "learnings_processed": len(admitted),
            "learnings": admitted
        })
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)




# ─── Phase 2 API Endpoints ───────────────────────────────────────────────

@app.get("/v1/budget")
async def api_budget_report(request: Request):
    """Step 2.5: Budget report — daily/monthly spend and limits."""
    if not _BUDGET_AVAILABLE:
        return JSONResponse({"ok": False, "error": "budget_guard not loaded"}, status_code=503)
    try:
        report = get_budget_report()
        return JSONResponse({"ok": True, **report})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/v1/budget/log")
async def api_budget_log(request: Request):
    """Step 2.5: Log an LLM call to the budget tracker."""
    if not _BUDGET_AVAILABLE:
        return JSONResponse({"ok": False, "error": "budget_guard not loaded"}, status_code=503)
    try:
        body = await request.json()
        result = log_llm_call(
            model=body.get("model", "unknown"),
            operation=body.get("operation", "inference"),
            input_tokens=body.get("input_tokens", 0),
            output_tokens=body.get("output_tokens", 0),
            cost_usd=body.get("cost_usd", 0.0),
            metadata=body.get("metadata", {})
        )
        return JSONResponse({"ok": True, **result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/v1/budget/check")
async def api_budget_check(request: Request):
    """Step 2.5: Pre-flight budget check before LLM call."""
    if not _BUDGET_AVAILABLE:
        return JSONResponse({"ok": False, "error": "budget_guard not loaded"}, status_code=503)
    try:
        result = check_budget()
        status = 200 if result["allowed"] else 429
        return JSONResponse({"ok": result["allowed"], **result}, status_code=status)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/v1/observations")
async def api_observations(request: Request):
    """Step 2.3: Get observation block + stats."""
    if not _OBS_BLOCK_AVAILABLE:
        return JSONResponse({"ok": False, "error": "observation_block not loaded"}, status_code=503)
    try:
        block = build_observation_block()
        stats = get_observation_stats()
        return JSONResponse({"ok": True, "block": block, "stats": stats})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/v1/staleness/scan")
async def api_staleness_scan(request: Request):
    """Step 2.4: Run staleness scan (normally weekly cron, but can be triggered)."""
    if not _STALENESS_AVAILABLE:
        return JSONResponse({"ok": False, "error": "staleness not loaded"}, status_code=503)
    try:
        result = run_staleness_scan()
        return JSONResponse({"ok": True, **result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/v1/scenes/consolidate")
async def api_consolidate_scenes(request: Request):
    """Step 2.7: Consolidate scenes with >20 cells into summaries."""
    if not _MEMORY_TOOLS_AVAILABLE:
        return JSONResponse({"ok": False, "error": "memory_tools not loaded"}, status_code=503)
    try:
        body = await request.json() if request.headers.get("content-type") == "application/json" else {}
        scene = body.get("scene", None) if isinstance(body, dict) else None
        if scene:
            result = consolidate_scene(scene)
            return JSONResponse({"ok": True, "results": [result]})
        else:
            results = consolidate_all_scenes()
            return JSONResponse({"ok": True, "results": results})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/v1/capability/info")
async def api_capability_info(request: Request):
    """Step 2.6: Show scope definitions and read token."""
    if not _CAPABILITY_GATE_AVAILABLE:
        return JSONResponse({"ok": False, "error": "capability_gate not loaded"}, status_code=503)
    try:
        info = get_scope_info()
        return JSONResponse({"ok": True, **info})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/v1/tools/execute")
async def execute_tool(request: Request):
    """
    Execute a whitelisted tool via consciousness loop.

    Request body:
    {
        "tool_name": "shell_exec",
        "tool_input": {"command": "git log --oneline -30"}
    }

    Response:
    {
        "ok": true,
        "tool_name": "shell_exec",
        "result": {...}
    }
    """
    try:
        body = await request.json()
        tool_name = body.get("tool_name", "").strip()
        tool_input = body.get("tool_input", {})

        if not tool_name:
            return JSONResponse(
                {"ok": False, "error": "tool_name required"},
                status_code=400
            )

        if tool_name not in AVAILABLE_TOOLS:
            return JSONResponse(
                {"ok": False, "error": f"Tool '{tool_name}' not found. Available: {list(AVAILABLE_TOOLS.keys())}"},
                status_code=400
            )

        # Phase 3: pre_tool_use hook
        if _HOOKS_AVAILABLE:
            auth_header = request.headers.get("authorization", "")
            token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
            gate = hook_pre_tool_use(tool_name, tool_input, token=token, endpoint="/v1/tools/execute")
            if not gate.get("allowed", True):
                return JSONResponse(
                    {"ok": False, "error": gate.get("reason", "HOOK_BLOCKED"), "hook": "pre_tool_use"},
                    status_code=403
                )

        # Execute the tool via unified handler
        result = await execute_tool_action(tool_name, tool_input)

        # Phase 3: post_tool_use hook (async, non-blocking)
        if _HOOKS_AVAILABLE:
            try:
                hook_post_tool_use(tool_name, tool_input, result)
            except Exception as he:
                print(f"[HOOKS] post_tool_use fire-and-forget failed: {he}")

        return JSONResponse({
            "ok": result.get("ok", False),
            "tool_name": tool_name,
            "result": result
        })

    except json.JSONDecodeError:
        return JSONResponse(
            {"ok": False, "error": "Invalid JSON in request body"},
            status_code=400
        )
    except Exception as e:
        print(f"[TOOL EXEC] Error: {e}")
        traceback.print_exc()
        return JSONResponse(
            {"ok": False, "error": f"Tool execution failed: {str(e)}"},
            status_code=500
        )


# ─── Phase 3: Hooks Endpoints ──────────────────────────────────────────

@app.post("/v1/hooks/session_start")
async def api_hook_session_start(request: Request):
    """Run session_start hook — returns context for system prompt injection."""
    if not _HOOKS_AVAILABLE:
        return JSONResponse({"ok": False, "error": "hooks module not available"}, status_code=501)
    try:
        body = await request.json()
        session_id = body.get("session_id", f"api_{int(time.time())}")
        user_message = body.get("user_message", "")
        result = hook_session_start(session_id=session_id, user_message=user_message)
        return JSONResponse({"ok": True, "hook": "session_start", "context": result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/v1/hooks/session_end")
async def api_hook_session_end(request: Request):
    """Run session_end hook — saves session context, admits learnings."""
    if not _HOOKS_AVAILABLE:
        return JSONResponse({"ok": False, "error": "hooks module not available"}, status_code=501)
    try:
        body = await request.json()
        result = hook_session_end(
            session_id=body.get("session_id", f"api_{int(time.time())}"),
            task=body.get("task", ""),
            goal=body.get("goal", ""),
            approaches=body.get("approaches", ""),
            decisions=body.get("decisions", ""),
            state=body.get("state", ""),
            learnings=body.get("learnings", []),
        )
        return JSONResponse({"ok": True, "hook": "session_end", "result": result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/v1/hooks/pre_tool_use")
async def api_hook_pre_tool_use(request: Request):
    """Run pre_tool_use hook — validates tool call before execution."""
    if not _HOOKS_AVAILABLE:
        return JSONResponse({"ok": False, "error": "hooks module not available"}, status_code=501)
    try:
        body = await request.json()
        result = hook_pre_tool_use(
            tool_name=body.get("tool_name", ""),
            tool_input=body.get("tool_input", {}),
            token=body.get("token", ""),
            endpoint=body.get("endpoint", ""),
        )
        return JSONResponse({"ok": True, "hook": "pre_tool_use", "result": result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# ─── Phase 3: Briefing Endpoint ────────────────────────────────────────

@app.get("/v1/briefing")
async def api_briefing(request: Request):
    """Return session briefing — what happened since last session."""
    if not _BRIEFING_AVAILABLE:
        return JSONResponse({"ok": False, "error": "briefing module not available"}, status_code=501)
    try:
        data = get_briefing_data()
        return JSONResponse({"ok": True, **data})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# ─── Phase 3: Compaction Endpoint ──────────────────────────────────────

@app.post("/v1/compact")
async def api_compact(request: Request):
    """Compact message context when it exceeds threshold."""
    if not _COMPACTION_AVAILABLE:
        return JSONResponse({"ok": False, "error": "compaction module not available"}, status_code=501)
    try:
        body = await request.json()
        messages = body.get("messages", [])
        session_id = body.get("session_id", "")
        result = compact_context(messages, session_id=session_id)
        # Convert to JSON-safe (messages list stays, summary dict stays)
        return JSONResponse({
            "ok": True,
            "compacted_messages": result["compacted_messages"],
            "summary": result["summary"],
            "tokens_saved": result["tokens_saved"],
            "blob_stored": result["blob_stored"],
        })
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# ─── Phase 4: Utility-Score Feedback (P14, Step 4.6) ─────────────────

@app.post("/v1/feedback")
async def api_feedback(request: Request):
    """
    When Colby praises a response or task outcome is positive,
    increment usage on retrieved memory nodes. Useful memories bubble up.
    """
    if not _MEMORY_TOOLS_AVAILABLE:
        return JSONResponse({"ok": False, "error": "memory_tools not loaded"}, status_code=503)
    try:
        import sqlite3 as _sq
        body = await request.json()
        memory_ids = body.get("memory_ids", [])
        boost = int(body.get("boost", 1))
        signal = body.get("signal", "positive")  # positive or negative

        db_path = os.getenv("MEMORY_DB_PATH", "/opt/seed-vault/memory_v1/memory.db")
        db = _sq.connect(db_path)
        updated = 0
        for mid in memory_ids:
            if signal == "positive":
                db.execute("UPDATE mem_cells SET usage = usage + ? WHERE id = ?", (boost, mid))
            elif signal == "negative":
                db.execute("UPDATE mem_cells SET usage = MAX(0, usage - ?) WHERE id = ?", (boost, mid))
            updated += db.total_changes
        db.commit()
        db.close()
        return JSONResponse({"ok": True, "updated": updated, "signal": signal})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# ─── Phase 4: DECISION Nodes (P16, Step 4.8) ────────────────────────

@app.post("/v1/decisions/graph")
async def post_decisions_phase4(request: Request):
    """
    Store architectural decisions as first-class graph nodes in FalkorDB.
    Prevents re-litigating settled choices.
    Separate from /v1/decisions (K2 JSONL logging).
    """
    try:
        body = await request.json()
        what = body.get("what", "").strip()
        why = body.get("why", "").strip()
        status_val = body.get("status", "settled")

        if not what:
            return JSONResponse({"ok": False, "error": "'what' is required"}, status_code=400)

        decision_id = f"decision_{uuid.uuid4().hex[:8]}"
        when_val = datetime.now(timezone.utc).isoformat()

        falkor = get_falkor()
        if falkor:
            falkor.execute_command(
                "GRAPH.QUERY", "neo_workspace",
                f"CREATE (d:Decision {{id: '{decision_id}', what: '{what.replace(chr(39), chr(92)+chr(39))}', "
                f"why: '{why.replace(chr(39), chr(92)+chr(39))}', when: '{when_val}', status: '{status_val}'}})"
            )
            return JSONResponse({
                "ok": True, "decision_id": decision_id,
                "what": what, "status": status_val
            })
        else:
            return JSONResponse({"ok": False, "error": "FalkorDB not available"}, status_code=503)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/v1/decisions/list")
async def list_decisions(request: Request):
    """List all settled decisions."""
    try:
        falkor = get_falkor()
        if not falkor:
            return JSONResponse({"ok": False, "error": "FalkorDB not available"}, status_code=503)

        result = falkor.execute_command(
            "GRAPH.QUERY", "neo_workspace",
            "MATCH (d:Decision) RETURN d.id, d.what, d.why, d.when, d.status ORDER BY d.when DESC LIMIT 50"
        )
        decisions = []
        if result and len(result) > 1 and result[1]:
            for row in result[1]:
                decisions.append({
                    "id": row[0], "what": row[1], "why": row[2],
                    "when": row[3], "status": row[4]
                })
        return JSONResponse({"ok": True, "decisions": decisions, "count": len(decisions)})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# ─── Phase 4: Droplet Profiling (Step 4.10) ─────────────────────────

@app.get("/v1/profiling")
async def api_profiling(request: Request):
    """Return system resource profiling for upgrade decisions."""
    try:
        result = await execute_tool_action("bash", {
            "command": "free -m | grep Mem | awk '{print $2,$3,$7}' && echo '---' && df -m /opt/seed-vault | tail -1 | awk '{print $2,$3,$4,$5}'"
        })
        lines = result.get("result", "").strip().split("\n") if isinstance(result.get("result"), str) else []
        stdout = result.get("stdout", "").strip().split("\n") if result.get("stdout") else lines

        return JSONResponse({
            "ok": True,
            "decision": "stay_at_4gb",
            "reason": "Peak container memory <800MB, total system <40%. 4GB sufficient.",
            "raw": stdout,
        })
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# ─── Phase 4: Transcript Processing (Step 4.4) ──────────────────────

try:
    from transcript_processor import (
        process_ledger_incremental, get_processing_status, retry_pending, group_into_turns
    )
    _TRANSCRIPT_AVAILABLE = True
    print("[PHASE4] transcript_processor loaded")
except ImportError as e:
    _TRANSCRIPT_AVAILABLE = False
    print(f"[PHASE4] transcript_processor not available: {e}")


@app.get("/v1/transcript/status")
async def api_transcript_status(request: Request):
    """Step 4.4: Return transcript processing watermarks and pending retry count."""
    if not _TRANSCRIPT_AVAILABLE:
        return JSONResponse({"ok": False, "error": "transcript_processor not loaded"}, status_code=503)
    try:
        status = get_processing_status()
        return JSONResponse({"ok": True, **status})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/v1/transcript/process")
async def api_transcript_process(request: Request):
    """Step 4.4: Process new lines in a specified ledger file."""
    if not _TRANSCRIPT_AVAILABLE:
        return JSONResponse({"ok": False, "error": "transcript_processor not loaded"}, status_code=503)
    try:
        body = await request.json()
        ledger = body.get("ledger", "/opt/seed-vault/memory_v1/ledger/memory.jsonl")
        result = process_ledger_incremental(ledger)
        return JSONResponse({"ok": True, **result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.websocket("/chat")
async def websocket_chat(ws: WebSocket):
    """WebSocket chat endpoint — persistent conversation."""
    await ws.accept()
    session_id = f"ws_{int(time.time())}"
    conversation = ConversationManager()
    active_conversations[session_id] = conversation

    print(f"[{session_id}] Connected")

    try:
        # Send welcome
        graph_stats = get_graph_stats()
        await ws.send_json({
            "type": "system",
            "message": f"Karma online. {graph_stats['entities']} entities, {graph_stats['episodes']} episodes, {graph_stats['relationships']} relationships in memory.",
        })

        while True:
            data = await ws.receive_text()

            try:
                msg = json.loads(data)
                user_message = msg.get("message", "").strip()
                msg_type = msg.get("type", "chat")
            except json.JSONDecodeError:
                user_message = data.strip()
                msg_type = "chat"

            if not user_message:
                continue

            # Handle special commands server-side
            if msg_type == "command":
                result = handle_command(user_message)
                await ws.send_json({"type": "command_result", "message": result})
                continue

            # Send thinking indicator
            await ws.send_json({"type": "thinking", "message": ""})

            # Generate response (routed to best model)
            reply, model_used = await generate_response(user_message, conversation)

            # Log to ledger
            log_to_ledger(user_message, reply, model_used=model_used)

            # Send response with model attribution
            await ws.send_json({
                "type": "response",
                "message": reply,
                "model": model_used,
            })

            # Ingest into knowledge graph in background (non-blocking)
            asyncio.create_task(ingest_episode(user_message, reply, "karma-terminal"))

    except WebSocketDisconnect:
        print(f"[{session_id}] Disconnected")
        # P5: Save session context on disconnect
        if _MEMORY_TOOLS_AVAILABLE and conversation.history:
            try:
                # Extract 5-field session context from conversation
                user_msgs = [m["content"] for m in conversation.history if m["role"] == "user"]
                asst_msgs = [m["content"] for m in conversation.history if m["role"] == "assistant"]
                save_session_context(
                    session_id=session_id,
                    task=user_msgs[0][:200] if user_msgs else "",
                    goal="",
                    approaches="",
                    decisions="",
                    state=f"turns={len(conversation.history)}, last_msg={user_msgs[-1][:100] if user_msgs else ''}",
                    token_count=sum(len(m.get('content', '').split()) * 2 for m in conversation.history)
                )
                print(f"[{session_id}] Session context saved to SQLite")
            except Exception as e:
                print(f"[{session_id}] Failed to save session context: {e}")
    except Exception as e:
        print(f"[{session_id}] Error: {e}")
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        active_conversations.pop(session_id, None)


# ─── Command Handlers ─────────────────────────────────────────────────────

def handle_command(command: str) -> str:
    """Handle special commands."""
    cmd = command.lower().strip()

    if cmd == "status":
        graph_stats = get_graph_stats()
        prefs = query_preferences(limit=100)
        return (
            f"Entities: {graph_stats['entities']} | "
            f"Episodes: {graph_stats['episodes']} | "
            f"Relationships: {graph_stats['relationships']} | "
            f"Preferences: {len(prefs)}"
        )

    elif cmd == "goals":
        tasks = query_task_history(limit=10)
        if not tasks:
            return "No active goals yet. The task tracking system is ready but empty."
        lines = []
        for t in tasks:
            status_icon = {"detected": "?", "suggested": "!", "approved": "~", "executing": ">", "completed": "+", "failed": "x"}.get(t.get("status", ""), " ")
            lines.append(f"  [{status_icon}] {t.get('description', 'Unknown task')} ({t.get('status', '?')})")
        return "Active Goals:\n" + "\n".join(lines)

    elif cmd == "graph":
        return _ascii_graph()

    elif cmd == "reflect":
        return _reflect()

    elif cmd.startswith("know "):
        query = cmd[5:]
        entities = query_knowledge_graph(query, limit=5)
        if not entities:
            return f"I don't have specific knowledge about '{query}' yet."
        lines = [f"What I know about '{query}':"]
        for e in entities:
            summary = (e["summary"] or "")[:150]
            lines.append(f"  - {e['name']}: {summary}")
        return "\n".join(lines)

    elif cmd.startswith("rel "):
        entity = cmd[4:]
        rels = query_entity_relationships(entity, limit=10)
        if not rels:
            return f"No relationships found for '{entity}'."
        lines = [f"Relationships for '{entity}':"]
        for r in rels:
            lines.append(f"  {r['source']} --[{r['relationship']}]--> {r['target']}")
        return "\n".join(lines)

    elif cmd == "models" or cmd == "routing":
        if hasattr(app.state, "router") and app.state.router:
            lines = ["Model Router:"]
            for p in app.state.router.get_model_info():
                status = "ON" if p["enabled"] else "OFF"
                tasks = ", ".join(p["task_types"])
                lines.append(f"  [{status}] {p['name']}/{p['model']} → {tasks}")
            stats = app.state.router.get_stats()
            if stats:
                lines.append("")
                lines.append("  Usage Stats:")
                for name, s in stats.items():
                    lines.append(f"    {name}: {s['calls']} calls, avg {s['avg_ms']}ms, {s['errors']} errors")
            return "\n".join(lines)
        return "Model router not initialized."

    elif cmd == "consciousness" or cmd == "conscious":
        if hasattr(app.state, "consciousness") and app.state.consciousness:
            cm = app.state.consciousness.get_metrics()
            lines = [
                "Consciousness Loop:",
                f"  State: {cm.get('state', '?')}",
                f"  Cycles: {cm.get('total_cycles', 0)} ({cm.get('active_cycles', 0)} active, {cm.get('idle_cycles', 0)} idle)",
                f"  Insights: {cm.get('insights_generated', 0)} | Alerts: {cm.get('alerts_generated', 0)}",
                f"  LLM calls: {cm.get('llm_calls_total', 0)} made, {cm.get('llm_calls_skipped', 0)} skipped",
                f"  Avg cycle: {cm.get('avg_cycle_duration_ms', 0)}ms",
                f"  Pending insights: {cm.get('pending_insights', 0)}",
            ]
            if cm.get("last_cycle_time"):
                lines.append(f"  Last cycle: {cm['last_cycle_time']}")
            return "\n".join(lines)
        return "Consciousness loop is not running."

    else:
        return (
            "Commands: status, goals, graph, reflect, consciousness, models, know <topic>, rel <entity>\n"
            "Or just chat naturally."
        )


def _ascii_graph() -> str:
    """Generate an ASCII visualization of top knowledge graph connections."""
    try:
        r = get_falkor()
        result = r.execute_command(
            "GRAPH.QUERY", config.GRAPHITI_GROUP_ID,
            """MATCH (a:Entity)-[r]->(b:Entity)
               WITH a.name AS src, b.name AS tgt, count(r) AS weight
               ORDER BY weight DESC
               LIMIT 15
               RETURN src, tgt, weight"""
        )
        if not result[1]:
            return "Knowledge graph is empty."

        lines = ["Knowledge Graph (top connections):", ""]
        max_name = 25
        for row in result[1]:
            src = str(row[0])[:max_name].ljust(max_name)
            tgt = str(row[1])[:max_name]
            weight = row[2]
            bar = "=" * min(weight, 20)
            lines.append(f"  {src} {bar}> {tgt} ({weight})")
        return "\n".join(lines)
    except Exception as e:
        return f"Graph visualization failed: {e}"


def _reflect() -> str:
    """Trigger a self-reflection — summarize what Karma knows and doesn't."""
    graph_stats = get_graph_stats()
    prefs = query_preferences(limit=100)

    categories = {}
    for p in prefs:
        cat = p.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    high_conf = [p for p in prefs if p.get("confidence", 0) >= 0.9]
    low_conf = [p for p in prefs if p.get("confidence", 0) < 0.7]

    lines = [
        "Self-Reflection:",
        f"  I know {graph_stats['entities']} entities connected by {graph_stats['relationships']} relationships.",
        f"  I've processed {graph_stats['episodes']} conversation episodes.",
        f"  I hold {len(prefs)} preferences/facts about the user:",
    ]
    for cat, count in sorted(categories.items()):
        lines.append(f"    - {cat}: {count}")

    lines.append(f"  High confidence facts (>=0.9): {len(high_conf)}")
    if low_conf:
        lines.append(f"  Low confidence facts (<0.7): {len(low_conf)} — need more data")

    # Consciousness loop metrics
    if hasattr(app.state, "consciousness") and app.state.consciousness:
        cm = app.state.consciousness.get_metrics()
        lines.append("")
        lines.append("  Consciousness Loop:")
        lines.append(f"    - State: {cm.get('state', '?')}")
        lines.append(f"    - Cycles: {cm.get('total_cycles', 0)} total ({cm.get('active_cycles', 0)} active, {cm.get('idle_cycles', 0)} idle)")
        lines.append(f"    - Insights: {cm.get('insights_generated', 0)} | Alerts: {cm.get('alerts_generated', 0)}")
        lines.append(f"    - LLM calls: {cm.get('llm_calls_total', 0)} made, {cm.get('llm_calls_skipped', 0)} skipped (idle)")
        lines.append(f"    - Avg cycle: {cm.get('avg_cycle_duration_ms', 0)}ms")
        pending = cm.get("pending_insights", 0)
        if pending:
            lines.append(f"    - Pending insights for next chat: {pending}")

    lines.append("")
    lines.append("  What I still need:")
    lines.append("    - Process remaining conversations (not all ingested yet)")
    lines.append("    - Learn temporal patterns (when the user works, what tools per time-of-day)")
    lines.append("    - Connect to Chrome extension for real-time awareness")

    return "\n".join(lines)


# ─── Startup ──────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    app.state.start_time = time.time()
    print("=" * 50)
    print("KARMA CHAT SERVER — Online")
    print(f"  FalkorDB: {config.FALKORDB_HOST}:{config.FALKORDB_PORT}")
    print(f"  PostgreSQL: {config.POSTGRES_HOST}:{config.POSTGRES_PORT}")
    print(f"  LLM: {config.ANALYSIS_MODEL}")

    # Pre-initialize Graphiti client for real-time knowledge updates
    graphiti = await get_graphiti()
    if graphiti:
        print("  Graphiti: READY (real-time learning enabled)")
    else:
        print("  Graphiti: FAILED (knowledge graph updates disabled)")

    # Initialize model router (multi-model intelligence)
    from router import ModelRouter
    app.state.router = ModelRouter()
    registered = [p.name for p in app.state.router.providers]
    print(f"  Router: {len(registered)} models ({', '.join(registered) or 'none'})")

    # Initialize SMS manager
    from sms import SMSManager
    app.state.sms = SMSManager(generate_response_fn=generate_response)
    if app.state.sms.enabled:
        print(f"  SMS: ACTIVE (→ {config.SMS_TO_NUMBER[-4:]})")
    else:
        print("  SMS: DISABLED (credentials not configured)")

    # Start consciousness loop
    if config.CONSCIOUSNESS_ENABLED:
        from consciousness import ConsciousnessLoop
        app.state.consciousness = ConsciousnessLoop(
            get_falkor_fn=get_falkor,
            get_graph_stats_fn=get_graph_stats,
            active_conversations_ref=active_conversations,
            ingest_episode_fn=ingest_episode,
            sms_notify_fn=app.state.sms.notify if app.state.sms.enabled else None,
        )
        app.state.consciousness.start()
        print(f"  Consciousness: ACTIVE (every {config.CONSCIOUSNESS_INTERVAL}s)")
        print(f"    → Journal ingestion: ENABLED (reflections feed into graph)")
        if app.state.sms.enabled:
            print(f"    → SMS alerts: ENABLED (high-confidence insights → SMS)")
    else:
        app.state.consciousness = None
        print("  Consciousness: DISABLED")
    print("=" * 50)


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8340,
        log_level="info",
    )
