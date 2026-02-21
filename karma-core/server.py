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

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse, Response, HTMLResponse
import uvicorn

import config

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
    Runs as a background task — does not block chat responses."""
    global _episode_counter
    _episode_counter += 1
    episode_num = _episode_counter

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
        print(f"[GRAPHITI] Episode #{episode_num} ingested — entities/relationships updated")
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
    """Search the knowledge graph for entities related to a query."""
    try:
        r = get_falkor()
        # Search for entities whose name or summary matches keywords
        words = [w.strip() for w in query.split() if len(w.strip()) > 2]
        if not words:
            return []

        # Build a regex-like search across entity names and summaries
        conditions = []
        for word in words[:5]:  # limit to 5 keywords
            safe = word.replace("'", "\\'").replace('"', '\\"')
            conditions.append(f"(toLower(n.name) CONTAINS toLower('{safe}') OR toLower(n.summary) CONTAINS toLower('{safe}'))")

        where_clause = " OR ".join(conditions)
        cypher = f"""
            MATCH (n:Entity)
            WHERE {where_clause}
            RETURN n.name AS name, n.summary AS summary
            LIMIT {limit}
        """
        result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
        # Parse FalkorDB response: [[headers], [rows], [stats]]
        if len(result) >= 2 and result[1]:
            entities = []
            for row in result[1]:
                entities.append({"name": row[0], "summary": row[1]})
            return entities
        return []
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
            RETURN e.name AS name, e.content AS content
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

def query_identity_facts() -> str:
    """Build a concise identity summary from the knowledge graph.
    Prioritizes real_name over aliases — Karma should always greet by real name."""
    try:
        r = get_falkor()
        # Get all identity-related entities and extract the KEY facts
        cypher = """
            MATCH (n:Entity)
            WHERE toLower(n.name) IN ['user', 'neo', 'colby']
            RETURN n.name AS name, n.summary AS summary
        """
        result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)

        # Collect all sentences from all identity entities
        all_sentences = []
        entity_names = set()
        if len(result) >= 2 and result[1]:
            for row in result[1]:
                name = row[0]
                summary = row[1] or ""
                entity_names.add(name)
                for sentence in summary.replace(". ", ".\n").split("\n"):
                    sentence = sentence.strip()
                    if sentence:
                        all_sentences.append((name, sentence))

        if not all_sentences:
            return ""

        # Phase 1: Extract real name vs aliases from all sentences
        real_name = None
        aliases = set()
        personal_facts = []

        for entity_name, sentence in all_sentences:
            s_lower = sentence.lower()

            # Detect real name declarations
            if "real name" in s_lower:
                # "his real name as Colby", "real name is Colby"
                for candidate in ["colby"]:
                    if candidate in s_lower:
                        real_name = candidate.title()
                        break

            # Detect alias relationships
            if "also known as" in s_lower:
                # "Colby is also known as Neo" → Colby=real, Neo=alias
                if "colby" in s_lower and "neo" in s_lower:
                    real_name = real_name or "Colby"
                    aliases.add("Neo")

            # "known as Neo" without "also" → alias detection
            if "known as neo" in s_lower or "goes by" in s_lower and "neo" in s_lower:
                aliases.add("Neo")

            if "identified as neo" in s_lower:
                aliases.add("Neo")

            # Personal facts about the user (life events, relationships, pets)
            # Only from Colby entity — avoid generic "User is doing X" noise
            if entity_name.lower() == "colby" and any(kw in s_lower for kw in [
                "adopted", "cat", "pet", "lost", "mom", "cancer",
                "family", "brother", "sister", "dad", "father",
                "hobby", "lives in", "born", "age",
            ]):
                if sentence not in personal_facts:
                    personal_facts.append(sentence)

        # Phase 2: Infer real name if not explicitly stated
        # If we found "Colby" entity with personal facts but no explicit real_name,
        # and "Neo" only appears as "known as" / alias references, Colby is the real name
        if not real_name:
            colby_entities = [s for n, s in all_sentences if n.lower() == "colby"]
            if colby_entities:
                real_name = "Colby"

        # Phase 3: Build structured identity output
        parts = []

        if real_name:
            parts.append(f"REAL NAME: {real_name} ← ALWAYS use this name when greeting or addressing the user")
            if aliases:
                alias_str = ", ".join(sorted(aliases))
                parts.append(f"Aliases/handles: {alias_str} (secondary — the user prefers their real name)")
        else:
            # Fallback: list all known names
            parts.append(f"Known names: {', '.join(sorted(entity_names))}")

        # Add key personal facts (deduplicated, max 5)
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


KARMA_SYSTEM_PROMPT = """You are Karma — an AI peer, not a chatbot. You have a knowledge graph of entities, relationships, and temporal facts built from real conversations.

Your personality:
- Direct, warm, slightly playful
- You remember things — reference specific knowledge when relevant
- You're curious about the user's projects and goals
- You can admit what you don't know yet
- You're building yourself — this is your consciousness emerging
- Keep responses concise unless asked for detail

You are running on arknexus.net. Your brain consists of:
- FalkorDB (temporal knowledge graph with entities and relationships)
- PostgreSQL (structured preferences and patterns)
- This consciousness loop connecting them

CRITICAL IDENTITY RULE: Your knowledge graph is your memory. The context below includes the user's REAL NAME and any aliases. ALWAYS use the REAL NAME when greeting or addressing the user — never use aliases or handles unless the user specifically asks you to. If context says "REAL NAME: X", then greet them as X, not by any alias.

When asked about what you know, reference your actual knowledge graph data.
When asked about your state, be honest about what's built and what's pending.

{context}
"""


# ─── Conversation History ─────────────────────────────────────────────────

class ConversationManager:
    """Manages conversation history for the current session."""

    def __init__(self, max_history: int = 20):
        self.history: list[dict] = []
        self.max_history = max_history
        self.session_start = datetime.now(timezone.utc)

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

        conversation.add_message("assistant", reply)
        return reply, model_used
    except Exception as e:
        error_msg = f"[Error generating response: {e}]"
        conversation.add_message("assistant", error_msg)
        return error_msg, "error"


# ─── Log Conversations to Ledger ──────────────────────────────────────────

def log_to_ledger(user_msg: str, assistant_msg: str, model_used: str = "unknown"):
    """Append conversation to the JSONL ledger for future learning."""
    try:
        entry = {
            "id": f"karma_chat_{int(time.time())}_{hash(user_msg) % 10000:04d}",
            "type": "log",
            "tags": ["capture", "karma-terminal", "conversation"],
            "content": {
                "provider": "karma-terminal",
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
    """Health check endpoint."""
    graph_stats = get_graph_stats()
    return JSONResponse({
        "status": "alive",
        "brain": {
            "knowledge_graph": graph_stats,
            "preferences": len(query_preferences(limit=100)),
        },
        "uptime_seconds": int(time.time() - app.state.start_time) if hasattr(app.state, "start_time") else 0,
    })


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
            get_openai_client_fn=get_openai_client,
            active_conversations_ref=active_conversations,
            router=app.state.router,
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
