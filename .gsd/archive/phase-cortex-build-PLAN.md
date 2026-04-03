# Phase: Build the Brain (K2 Memory Cortex) — PLAN

## Task 1: Build julian_cortex.py
**What:** Python Flask service on K2 that wraps Ollama persistent session with HTTP API.
**Method:**
- Flask app on port TBD (suggest 7892 to avoid conflicts with aria:7890, kiki:1387)
- POST /context — returns current state summary from cortex
- POST /ingest — feed new knowledge (text, file content, bus post)
- POST /query — ask cortex a specific question
- GET /health — liveness check
- Uses Ollama Python client to maintain persistent chat session with Nemotron 9B v2
- System prompt = identity + invariants + current state summary
**Verify:** `curl K2:7892/health` returns ok. `curl K2:7892/context` returns coherent state.
**Done:** Service starts, responds to all 4 endpoints.

## Task 2: Initial Knowledge Load
**What:** Build ingestion script that feeds core files into cortex at startup.
**Method:**
- Read: MEMORY.md, STATE.md, PLAN.md, karma_contract_policy.md, all Karma2/map/* files
- Chunk into cortex-friendly blocks (each < 4K tokens)
- POST each to /ingest in order
- Verify with /query "what is the active task?"
**Verify:** Cortex answers "what's the active task?" correctly.
**Done:** All core files ingested, cortex answers accurately.

## Task 3: Research Ingestion
**What:** Feed summarized PDFs from docs/wip/ into cortex.
**Method:**
- Extract key primitives from each PDF (already done for 4 repos in SESSION-143-AUDIT)
- POST summaries to /ingest
- Verify with /query about specific research topics
**Verify:** Cortex answers "what did we learn from autoresearch?" accurately.
**Done:** Research knowledge accessible via cortex.

## Task 4: Session History Load
**What:** Feed last 20 session summaries from claude-mem.
**Method:**
- Search claude-mem for recent session summaries
- POST each to /ingest
- Verify with /query "what happened in Session 143?"
**Verify:** Cortex knows recent session history.
**Done:** Session history accessible.

## Task 5: Systemd Service
**What:** Register julian-cortex as systemd service on K2.
**Method:**
- Write julian-cortex.service unit file
- Enable + start
- Verify auto-restart on crash
**Verify:** `systemctl status julian-cortex` → active. Kill process → auto-restarts.
**Done:** Service persists across K2 reboots.

## Gate
Cortex answers "what is the current state of Julian's Resurrection?" with accurate, current info including: active task, recent decisions, hardware config, and research findings.
