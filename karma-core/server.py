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
