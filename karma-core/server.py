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
import tempfile
from pathlib import Path

# Phase 2 imports
from observation_block import build_observation_block, reset_observation_cache, get_observation_stats
from staleness import run_staleness_scan
from budget_guard import check_budget, log_llm_call, get_budget_report
from capability_gate import check_access, get_scope_info, get_read_token
from memory_tools import (
    admit_memory, retrieve_memory, update_memory, delete_memory,
    save_session_context, load_last_session, consolidate_scene,
    get_scene_context, load_pending_observations
)

# ─── Configuration ──────────────────────────────────────────────────────────
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")
GPT_API_KEY = os.getenv("OPENAI_API_KEY", "")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")
DB_PATH = os.getenv("MEMORY_DB_PATH", "/opt/seed-vault/memory_v1/memory.db")

app = FastAPI(title="Karma Memory Server", version="2.0.0")


# ─── Phase 2 Middleware: Capability Gate ────────────────────────────────────

@app.middleware("http")
async def capability_gate_middleware(request: Request, call_next):
    """
    Step 2.6: Enforce read vs write token scoping on all requests.
    Public paths (/, /v1/health) bypass the gate.
    """
    # Always-public paths
    public_paths = {"/", "/v1/health", "/docs", "/openapi.json", "/redoc"}
    if request.url.path in public_paths or request.method == "OPTIONS":
        return await call_next(request)

    # Extract bearer token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        return JSONResponse(
            status_code=401,
            content={"error": "Missing Authorization header"}
        )

    # Check access
    result = check_access(auth_header, request.url.path, request.method)
    if not result["allowed"]:
        return JSONResponse(
            status_code=403,
            content={"error": result["reason"], "scope": result["scope"]}
        )

    return await call_next(request)


# ─── Health Check ────────────────────────────────────────────────────────────

@app.get("/v1/health")
async def health():
    """Phase 2 health check with scope info."""
    budget = get_budget_report()
    obs_stats = get_observation_stats()
    scope_info = get_scope_info()
    return {
        "status": "ok",
        "version": "2.0.0",
        "phase": 2,
        "budget": {
            "daily_spend": budget["daily_spend"],
            "daily_remaining": budget["daily_remaining"],
            "monthly_spend": budget["monthly_spend"],
            "monthly_remaining": budget["monthly_remaining"],
        },
        "observations": obs_stats,
        "capability_gate": scope_info,
        "read_token_preview": get_read_token()[:12] + "...",
    }


# ─── Step 1.1: Memory Admission ──────────────────────────────────────────────

@app.post("/v1/admit")
async def admit(request: Request):
    """
    Admit a memory through the quality gate.
    Phase 2: auto-tags category (2.1), assigns confidence (2.2).
    """
    body = await request.json()
    content = body.get("content", "")
    if not content:
        return JSONResponse(status_code=400, content={"error": "content required"})

    result = admit_memory(
        content=content,
        category=body.get("category"),
        source=body.get("source", "api"),
        confidence=body.get("confidence"),
        pinned=body.get("pinned", False),
    )
    return result


# ─── Step 1.2: Memory Retrieval ──────────────────────────────────────────────

@app.post("/v1/retrieve")
async def retrieve(request: Request):
    """Hybrid memory retrieval: FTS5 + embedding + RRF fusion."""
    body = await request.json()
    query = body.get("query", "")
    if not query:
        return JSONResponse(status_code=400, content={"error": "query required"})

    results = retrieve_memory(
        query=query,
        top_k=body.get("top_k", 5),
        category_filter=body.get("category_filter"),
    )
    return {"results": results, "count": len(results)}


# ─── Step 1.3: Memory Update / Delete ────────────────────────────────────────

@app.post("/v1/memory/update")
async def memory_update(request: Request):
    """Update memory content (Decision #6: newer wins)."""
    body = await request.json()
    memory_id = body.get("memory_id", "")
    new_content = body.get("new_content", "")
    reason = body.get("reason", "api_update")

    if not memory_id or not new_content:
        return JSONResponse(
            status_code=400,
            content={"error": "memory_id and new_content required"}
        )

    return update_memory(memory_id, new_content, reason)


@app.post("/v1/memory/delete")
async def memory_delete(request: Request):
    """Soft-delete a memory (set archived=1)."""
    body = await request.json()
    memory_id = body.get("memory_id", "")
    reason = body.get("reason", "api_delete")

    if not memory_id:
        return JSONResponse(status_code=400, content={"error": "memory_id required"})

    return delete_memory(memory_id, reason)


# ─── Step 1.4: Session Context ────────────────────────────────────────────────

@app.post("/v1/session/save")
async def session_save(request: Request):
    """Save session context for resume (P5)."""
    body = await request.json()
    session_id = body.get("session_id", "")
    if not session_id:
        return JSONResponse(status_code=400, content={"error": "session_id required"})

    return save_session_context(
        session_id=session_id,
        task=body.get("task", ""),
        goal=body.get("goal", ""),
        approaches=body.get("approaches", ""),
        decisions=body.get("decisions", ""),
        state=body.get("state", ""),
        token_count=body.get("token_count", 0),
    )


@app.get("/v1/session/last")
async def session_last():
    """Load most recent session context (P5)."""
    result = load_last_session()
    if result is None:
        return {"session": None, "message": "No previous session found"}
    return {"session": result}


# ─── Step 2.3: Observation Block ──────────────────────────────────────────────

@app.get("/v1/observations")
async def get_observations(session_id: str = None, max_observations: int = 50):
    """
    Step 2.3: Get the append-only observation block.
    Returns the stable prefix for prompt cache injection.
    """
    block = build_observation_block(
        session_id=session_id,
        max_observations=max_observations
    )
    stats = get_observation_stats()
    return {
        "observation_block": block,
        "stats": stats,
        "cache_stable": True,  # Always true — append-only
    }


@app.post("/v1/observations/add")
async def add_observation(request: Request):
    """Add a new observation to the consciousness loop."""
    import sqlite3
    body = await request.json()

    event_type = body.get("event_type", "manual")
    description = body.get("description", "")
    outcome = body.get("outcome", "")

    if not description:
        return JSONResponse(status_code=400, content={"error": "description required"})

    db = sqlite3.connect(DB_PATH)
    try:
        now = datetime.now(timezone.utc).timestamp()
        db.execute("""
            INSERT INTO observations (observed_at, event_type, description, outcome, reflected)
            VALUES (?, ?, ?, ?, 0)
        """, (now, event_type, description, outcome))
        db.commit()
        row_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"action": "added", "id": row_id, "event_type": event_type}
    finally:
        db.close()


# ─── Step 2.4: Staleness Scan ────────────────────────────────────────────────

@app.post("/v1/staleness/scan")
async def staleness_scan():
    """
    Step 2.4: Trigger staleness cron manually.
    Also runs automatically on server startup and weekly via scheduler.
    """
    result = run_staleness_scan()
    return {"staleness_scan": result}


# ─── Step 2.5: Budget Endpoints ───────────────────────────────────────────────

@app.get("/v1/budget")
async def budget_status():
    """Step 2.5: Get current budget status."""
    return get_budget_report()


@app.post("/v1/budget/log")
async def budget_log_call(request: Request):
    """Step 2.5: Log an LLM call to budget tracking."""
    body = await request.json()
    return log_llm_call(
        model=body.get("model", "unknown"),
        operation=body.get("operation", "inference"),
        input_tokens=body.get("input_tokens", 0),
        output_tokens=body.get("output_tokens", 0),
        cost_usd=body.get("cost_usd", 0.0),
        metadata=body.get("metadata"),
    )


# ─── Step 2.7: Scene Consolidation ────────────────────────────────────────────

@app.post("/v1/scenes/consolidate")
async def scenes_consolidate(request: Request):
    """
    Step 2.7: Consolidate a scene with >20 cells into a ≤100-word summary.
    """
    body = await request.json()
    scene_name = body.get("scene_name", "")
    if not scene_name:
        return JSONResponse(status_code=400, content={"error": "scene_name required"})

    return consolidate_scene(scene_name, max_words=body.get("max_words", 100))


@app.get("/v1/scenes")
async def get_scenes(scenes: str = None, max_scenes: int = 5):
    """Get scene context for prompt injection."""
    scene_list = scenes.split(",") if scenes else None
    context = get_scene_context(scenes=scene_list, max_scenes=max_scenes)
    return {"context": context}


# ─── 4-Tool Surface (P2) ─────────────────────────────────────────────────────

@app.post("/v1/tools/execute")
async def tools_execute(request: Request):
    """
    4-tool surface: read, write, edit, bash.
    P2: Decision: 4 tools only. No MCP. <500 tokens total.
    Phase 2: Budget guard check before bash (may involve LLM calls).
    """
    body = await request.json()
    tool = body.get("tool", "")
    params = body.get("params", {})

    # Budget check for LLM-adjacent operations
    if tool in ("bash", "write", "edit"):
        budget = check_budget()
        if not budget["allowed"]:
            return JSONResponse(
                status_code=429,
                content={
                    "error": budget.get("reason", "BUDGET_EXHAUSTED"),
                    "budget": budget
                }
            )

    if tool == "read":
        path = params.get("path", "")
        if not path:
            return JSONResponse(status_code=400, content={"error": "path required"})
        try:
            p = Path(path)
            if not p.exists():
                return {"error": f"File not found: {path}"}
            content = p.read_text(errors="replace")
            lines = content.splitlines()
            offset = params.get("offset", 0)
            limit = params.get("limit", 2000)
            sliced = lines[offset:offset + limit]
            return {
                "content": "\n".join(sliced),
                "total_lines": len(lines),
                "returned_lines": len(sliced),
                "offset": offset
            }
        except Exception as e:
            return {"error": str(e)}

    elif tool == "write":
        path = params.get("path", "")
        content = params.get("content", "")
        if not path:
            return JSONResponse(status_code=400, content={"error": "path required"})
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            return {"written": True, "path": str(p), "bytes": len(content.encode())}
        except Exception as e:
            return {"error": str(e)}

    elif tool == "edit":
        path = params.get("path", "")
        old_string = params.get("old_string", "")
        new_string = params.get("new_string", "")
        if not path or not old_string:
            return JSONResponse(
                status_code=400,
                content={"error": "path and old_string required"}
            )
        try:
            p = Path(path)
            if not p.exists():
                return {"error": f"File not found: {path}"}
            content = p.read_text()
            if old_string not in content:
                return {"error": "old_string not found in file", "path": str(p)}
            new_content = content.replace(old_string, new_string, 1)
            p.write_text(new_content)
            return {"edited": True, "path": str(p)}
        except Exception as e:
            return {"error": str(e)}

    elif tool == "bash":
        cmd = params.get("command", "")
        if not cmd:
            return JSONResponse(status_code=400, content={"error": "command required"})
        try:
            timeout = params.get("timeout", 30)
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=timeout
            )
            return {
                "stdout": result.stdout[:8000],
                "stderr": result.stderr[:2000],
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout}s"}
        except Exception as e:
            return {"error": str(e)}

    else:
        return JSONResponse(
            status_code=400,
            content={"error": f"Unknown tool: {tool}. Valid: read, write, edit, bash"}
        )


# ─── Reflect (P7, P8) ─────────────────────────────────────────────────────────

@app.post("/v1/reflect")
async def reflect(request: Request):
    """
    P7+P8: Reflection endpoint.
    Budget guard: checks before any LLM call.
    Returns structured insights from memory + pending observations.
    """
    body = await request.json()
    session_id = body.get("session_id")

    # Step 2.5: Check budget before reflection (uses LLM)
    budget = check_budget()
    if not budget["allowed"]:
        return JSONResponse(
            status_code=429,
            content={
                "error": budget.get("reason", "BUDGET_EXHAUSTED"),
                "budget": budget
            }
        )

    # Step 2.3: Get observation block
    obs_block = build_observation_block(session_id=session_id)

    # Get pending observations
    pending = load_pending_observations(since_session_id=session_id, limit=20)

    # Get top memories for context
    query = body.get("query", "recent activity")
    memories = retrieve_memory(query, top_k=5)

    return {
        "observation_block": obs_block,
        "pending_observations": pending,
        "relevant_memories": memories,
        "budget_status": {
            "daily_remaining": budget["daily_remaining"],
            "monthly_remaining": budget["monthly_remaining"],
        }
    }


# ─── Startup: Run Staleness Scan + Scene Consolidation ───────────────────────

@app.on_event("startup")
async def startup_tasks():
    """
    Phase 2 startup: run staleness scan + consolidate large scenes.
    Non-blocking — runs in background.
    """
    import asyncio

    async def _background_tasks():
        try:
            # Step 2.4: Staleness scan
            stale_result = run_staleness_scan()
            print(f"[STARTUP] Staleness scan: {stale_result}")

            # Step 2.7: Consolidate scenes with >20 cells
            import sqlite3
            db = sqlite3.connect(DB_PATH)
            try:
                scenes = db.execute(
                    "SELECT DISTINCT scene FROM mem_cells WHERE archived=0"
                ).fetchall()
            finally:
                db.close()

            for (scene_name,) in scenes:
                if scene_name:
                    result = consolidate_scene(scene_name)
                    if result.get("action") == "consolidated":
                        print(f"[STARTUP] Consolidated scene '{scene_name}': "
                              f"{result['cell_count']} cells → {result['summary_words']} words")

        except Exception as e:
            print(f"[STARTUP] Background tasks error: {e}")

    asyncio.create_task(_background_tasks())


# ─── Root ─────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "Karma Memory Server",
        "version": "2.0.0",
        "phase": 2,
        "endpoints": [
            "POST /v1/admit",
            "POST /v1/retrieve",
            "POST /v1/memory/update",
            "POST /v1/memory/delete",
            "POST /v1/session/save",
            "GET  /v1/session/last",
            "GET  /v1/observations",
            "POST /v1/observations/add",
            "POST /v1/staleness/scan",
            "GET  /v1/budget",
            "POST /v1/budget/log",
            "POST /v1/scenes/consolidate",
            "GET  /v1/scenes",
            "POST /v1/tools/execute",
            "POST /v1/reflect",
            "GET  /v1/health",
        ]
    }


if __name__ == "__main__":
    print("=" * 50)
    print("  Karma Memory Server v2.0 — Phase 2")
    print("  Quality Gates & Observations")
    print("  Steps 2.1-2.8 active")
    print(f"  Budget: $5/day, $80/month")
    print(f"  Capability Gate: read/write scoping")
    budget_info = get_budget_report()
    print(f"  Daily spend: ${budget_info['daily_spend']:.4f} / ${budget_info['daily_limit']}")
    print(f"  Monthly spend: ${budget_info['monthly_spend']:.4f} / ${budget_info['monthly_limit']}")
    print("=" * 50)
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8340,
        log_level="info",
    )
