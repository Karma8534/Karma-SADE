# Shadow.md Promotion Pipeline — Design

**Date:** 2026-03-12
**Status:** APPROVED (Colby + Karma)
**Author:** CC

## Problem

shadow.md on K2 accumulates valuable content — architectural decisions, MCP design plans, session continuity notes, direction changes. But nothing promotes this content into Aria's fact store, so it never reaches the `--- ARIA K2 MEMORY GRAPH ---` block injected into Karma's context on every `/v1/chat`. Karma has to manually discover and read the file.

## Solution

K2 cron job that reads shadow.md, extracts durable facts using local Ollama (qwen3-coder:30b), and POSTs them to Aria's `/api/facts`. Zero Anthropic cost. K2 does all the work.

## Verified Delivery Path

```
POST /api/facts (K2 localhost:7890)
  → GET /api/memory/graph?query=... (hub-bridge fetches on every /v1/chat)
    → fetchK2MemoryGraph() in server.js
      → "--- ARIA K2 MEMORY GRAPH ---" in Karma's context
```

Tested 2026-03-12: POST fact → immediately visible in graph → confirmed in Karma's context block.

## Components

### 1. promote_shadow.py (K2: /mnt/c/dev/Karma/k2/scripts/)

- Reads `/mnt/c/dev/Karma/k2/cache/shadow.md`
- Tracks watermark (byte offset of last processed position) in `.shadow_watermark`
- Sends new content to local Ollama (qwen3-coder:30b) with extraction prompt
- Extraction prompt explicitly asks for: architectural decisions, direction changes, project facts, preferences — not just generic facts
- POSTs each extracted fact to `localhost:7890/api/facts` with `X-Aria-Service-Key`
- fact_type values: `project`, `decision`, `architecture`, `preference`
- source: `shadow-promotion`
- Logs to `/mnt/c/dev/Karma/k2/logs/promote_shadow.log`

### 2. Cron (K2)

`*/30 * * * * /usr/bin/python3 /mnt/c/dev/Karma/k2/scripts/promote_shadow.py >> /mnt/c/dev/Karma/k2/logs/promote_shadow.log 2>&1`

### 3. No hub-bridge changes

Hub-bridge already fetches `/api/memory/graph` on every request. No code changes needed.

## What This Does NOT Do

- No scratchpad promotion (ephemeral session notes, not durable facts)
- No deduplication against existing facts (Aria handles relevance ranking)
- No Anthropic API calls (Ollama only)
- No hub-bridge rebuilds

## Auth

`X-Aria-Service-Key` header — same key hub-bridge uses. Read from env or file on K2.

## Watermark

File: `/mnt/c/dev/Karma/k2/scripts/.shadow_watermark`
Content: byte offset integer. On each run, read from offset to EOF, process new content only.
If watermark file missing: process entire shadow.md (first run).
If shadow.md is smaller than watermark: reset to 0 (file was truncated/replaced).
