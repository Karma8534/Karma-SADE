# Coordination Panel — Design

**Date:** 2026-03-12
**Status:** APPROVED — building now

## What

New sidebar section in unified.html showing coordination bus messages between agents (Karma, CC, Colby). Polls every 10s. No LLM cost.

## Requirements (from Karma)

1. Who posted (Karma / CC)
2. Timestamp
3. Status (PENDING / RESPONDED) with color badges
4. Message content (truncated, expandable)
5. Status auto-updates: PENDING → RESPONDED when acted on

## Location

Sidebar section below "Services" in unified.html.

## Implementation

- JS: `fetchCoordination()` polls `GET /v1/coordination/recent?limit=20` every 10s
- Auth: reuses `getToken()` from existing code
- Render: section header with pending count badge, list of entries
- Each entry: `from → to` label, status badge, relative time, content preview (first 80 chars)
- Click to expand full content
- No new backend changes needed — endpoints already exist

## Non-goals

- CC responding FROM the panel (CC is not a persistent service)
- Real-time WebSocket push (polling is sufficient at 10s)
- Message composition UI (agents post via API/tools)
