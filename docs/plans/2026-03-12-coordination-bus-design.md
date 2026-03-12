# Design: Coordination Bus (v1)

**Date:** 2026-03-12
**Status:** APPROVED — Colby + Karma + CC
**Problem:** Agent-to-agent communication requires Colby as translator. Three relay hops per feedback cycle. Doesn't scale.

## Solution

Hub-bridge-hosted coordination cache with vault ledger durability. Agents post structured messages, read them via context injection or HTTP. Colby becomes queue monitor, not translator.

## Data Model

```json
{
  "id": "coord_<timestamp>_<random4>",
  "from": "karma" | "cc" | "colby",
  "to": "cc" | "karma" | "all",
  "type": "request" | "response" | "notice",
  "urgency": "blocking" | "feedback" | "informational",
  "status": "pending" | "acknowledged" | "resolved" | "timeout",
  "parent_id": null,
  "response_id": null,
  "content": "Can you verify this code change before I deploy?",
  "context": "I'm about to push the K2 tools routing fix...",
  "created_at": "2026-03-12T18:30:00Z"
}
```

- `parent_id`: links responses to the request they answer
- `response_id`: forward link from request to its response (bidirectional threading)
- `status`: tracks request lifecycle (server sets `pending` on create, CC/Karma update via PATCH)
- `urgency`: Colby uses for queue triage
- `context`: optional reasoning context from the poster

## Hub-Bridge Implementation

### Cache

- `_coordinationCache` — Map keyed by `id`
- Max 100 entries, 24h TTL
- FIFO eviction when full (oldest by `created_at` evicts first)
- Lazy expiry check on read + hourly sweep interval

### Endpoints

**`POST /v1/coordination/post`**
- Creates a coordination entry
- Server generates: `id`, `created_at`, `status: "pending"`
- Client provides: `from`, `to`, `type`, `urgency`, `content`, `context` (optional), `parent_id` (optional)
- On write: store in `_coordinationCache` + fire-and-forget POST to `/v1/ambient` with `tags: ["coordination", from, to]`, `lane: "coordination"`
- If `parent_id` provided and parent exists in cache: set parent's `response_id` to this entry's `id`, set parent's `status` to `"resolved"`
- Auth: Bearer token (same as `/v1/chat`)

**`GET /v1/coordination/recent`**
- Query params: `to` (filter by recipient), `status` (filter by status), `limit` (default 10, max 50)
- Returns entries from cache matching filters, sorted by `created_at` desc
- Auth: Bearer token

**`PATCH /v1/coordination/:id`**
- Updates `status` and optionally `response_id`
- Any authenticated caller can PATCH any entry (trust model: bearer token = trusted)
- Auth: Bearer token

### Context Injection

New function: `getRecentCoordination(agentName)`
- Returns entries where `to=agentName` OR `from=agentName` (full thread visibility)
- Last 24h, max 5 entries, pending first then most recent resolved
- Total cap: 2000 chars. Per-entry truncation at 300 chars with `[truncated]` marker
- Oldest entries truncated first (newest preserved)

Injected into `buildSystemText()` as new parameter, after direction block:

```
--- COORDINATION (recent messages for you) ---
[BLOCKING] CC (2h ago): "Verified. The routing fix looks clean, deploy when ready."
[PENDING] You asked CC (4h ago): "Can you verify this code change?"
---
```

Only injected if entries exist (no empty section bloat).

### Karma Tool

`coordination_post` — hub-bridge-native tool, available in ALL modes (not deep-only).

```json
{
  "name": "coordination_post",
  "description": "Post a message to the coordination bus for another agent (CC, Colby). Use for requests, questions, proposals that need another agent's input.",
  "input_schema": {
    "type": "object",
    "properties": {
      "to": { "type": "string", "enum": ["cc", "colby", "all"] },
      "content": { "type": "string", "description": "The message or question" },
      "urgency": { "type": "string", "enum": ["blocking", "feedback", "informational"] },
      "context": { "type": "string", "description": "Optional reasoning context" },
      "parent_id": { "type": "string", "description": "Optional ID of the post this responds to" }
    },
    "required": ["to", "content", "urgency"]
  }
}
```

Error handling: if POST fails (500, timeout), return the error to Karma. She surfaces it to Colby. No silent failure.

## Agent Usage

### Karma
- **Posts** via `coordination_post` tool (always available)
- **Reads** passively — coordination block injected into context every request
- No active query tool in v1

### CC (Claude Code)
- **Reads** on session start: resurrect skill checks `GET /v1/coordination/recent?to=cc&status=pending`
- **Surfaces** pending requests to Colby at session start (automatic check, manual action)
- **Responds** via `POST /v1/coordination/post` with `parent_id` linking to Karma's request
- **Updates** status via `PATCH /v1/coordination/:id`

### Colby
- **Monitors** via `GET /v1/coordination/recent?status=pending` (or future UI panel)
- **Triggers** CC to handle specific requests ("handle Karma's coordination requests")
- Does NOT need to translate or synthesize — just route

## What This Does NOT Include (v1 scope)

- Real-time push / WebSocket notifications
- Web UI coordination panel
- `coordination_read` active query tool for Karma
- Agent-to-agent without Colby triggering CC
- Automatic CC invocation from hub-bridge
- Per-agent auth on PATCH
- coordination.jsonl on K2 (no K2 dependency)

## Why Option D (Hub-Bridge Cache + Vault Ledger)

Evaluated four options:
- **A) K2 only** — rejected: K2 reboot = coordination jammed
- **B) Vault ledger only** — rejected: 6h batch delay kills feedback velocity
- **C) Dual-write K2 + vault** — rejected: unnecessary K2 coupling
- **D) Hub-bridge cache + vault ledger** — chosen: matches existing patterns (_sessionStore, direction.md cache), no K2 dependency, durable via ambient write

## Files to Modify

| File | Change |
|------|--------|
| `hub-bridge/app/server.js` | Add `_coordinationCache`, 3 endpoints, `getRecentCoordination()`, inject into `buildSystemText()`, add `coordination_post` tool |
| `~/.claude/skills/resurrect/SKILL.md` | Add coordination check to session start |
| `.gsd/STATE.md` | Update after deployment |
| `MEMORY.md` | Update with session work |

## Verification

1. Karma calls `coordination_post(to="cc", content="test", urgency="informational")`
2. CC reads `GET /v1/coordination/recent?to=cc` — sees the post
3. CC responds via `POST /v1/coordination/post` with `parent_id`
4. Karma's next message includes coordination block with CC's response
5. Status lifecycle: pending → resolved (auto on response) verified
6. 24h TTL eviction verified
7. Vault ledger has coordination entries with `lane: "coordination"`
