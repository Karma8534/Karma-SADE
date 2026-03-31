# Plan — K2 Bridge: Fix Consciousness + Build Continuity Substrate

## Overview
K2 is a **continuity substrate** — not an agent, not an LLM runner. Karma is the only origin of thought. K2's job between sessions: **preserve, observe, sync**. Three things need building: fix the broken consciousness loop, create a K2 polling endpoint, and establish write-back rules.

## Requirements

### 1. Fix the Consciousness Loop (CRITICAL — the blocker)

The consciousness loop has been silently crashing since ~Feb 16. `_observe()` returns `{new_episodes, time_delta_seconds, episode_count}` but `_decide()` and `_act()` reference keys that don't exist: `new_entities`, `new_relationships`, `active_sessions`. Every active cycle throws `KeyError` → caught by the outer loop → increments `errors` → Karma observes but never thinks, decides, or acts.

**Fix `_observe()` to return all required keys:**
- Query FalkorDB for new entity count and new relationship count since `last_cycle_time` (delta queries, same pattern as the episode delta query)
- Count active sessions from `self._active_conversations` dict
- Return dict must include: `new_episodes` (list), `episode_count` (int), `new_entities` (int), `new_relationships` (int), `active_sessions` (int), `time_delta_seconds` (float)

**Fix `_decide()` comparison bug:**
- Line `if analysis is None and observations["new_episodes"] > 0` compares a list to an int → TypeError
- Change to `observations["episode_count"] > 0`

**Fix `_observe()` timestamp type mismatch (finding 2.2):**
- `self.last_cycle_time` is a Unix epoch float (e.g. `1740000000.0`)
- `ingest_primitive_episode()` writes `created_at: localdatetime($ts)` — a FalkorDB `localdatetime` type
- The Cypher `WHERE e.created_at > {self.last_cycle_time}` compares `localdatetime` against a raw float → silently returns empty
- Fix: store `last_cycle_time` as ISO string (e.g. `2026-02-16T00:00:00`) and use `WHERE e.created_at > localdatetime('{self.last_cycle_time}')` in the Cypher query
- Also handle episodes created via Graphiti's `add_episode()` which may use a different timestamp format — add a fallback numeric comparison with `OR`

**Fix `_act()` journal entry to use correct keys:**
- The `observations` dict written to the journal and collab entries references `new_entities`, `new_relationships`, `active_sessions` — use the same keys from the fixed `_observe()` return

**Wrap synchronous calls in `asyncio.to_thread()` (finding 2.3):**
- `_observe()` calls `falkor.execute_command()` (synchronous Redis) — blocks the FastAPI event loop
- `_think()` calls `self._router.complete()` (synchronous HTTP to LLM providers) — blocks the event loop
- `_distillation_cycle()` has multiple `falkor.execute_command()` calls + `self._router.complete()`
- Wrap all synchronous FalkorDB and router calls in `await asyncio.to_thread(...)`
- `_observe()` and `_decide()` must become `async def` methods (they are currently sync)

### 2. K2 Polling Endpoint

New `GET /v1/graph/sync` endpoint on karma-server (droplet) that returns a bounded snapshot of recent graph changes for K2 to mirror.

**Request:** `GET /v1/graph/sync?since=<ISO-timestamp>&limit=100`

**Response:**
```json
{
  "ok": true,
  "sync_at": "<ISO timestamp of this snapshot>",
  "graph_stats": { "entities": N, "episodes": N, "relationships": N },
  "new_episodes": [ { "uuid": "...", "name": "...", "content": "(truncated)", "lane": "canonical", "created_at": "...", "source": "..." } ],
  "consciousness": { "last_cycle": "<ISO>", "state": "running|stopped", "pending_insights": N },
  "checkpoint_summary": "<latest karma_brief if available>"
}
```

**Constraints:**
- Max 100 episodes per response, 1MB response cap
- Only returns `lane=canonical` episodes (K2 doesn't need to see candidates)
- Truncate episode content to 500 chars (K2 needs summaries, not full bodies)
- No authentication beyond network-level (Tailscale/VPN — K2 is a trusted peer)

**K2 side — `k2-worker/karma-k2-sync.py` rewrite:**
- Replace the current stub (health-check poller + `/v1/decisions` writer) with a real sync loop
- Poll `GET /v1/graph/sync?since=<last_sync_time>` every `K2_POLL_INTERVAL` seconds (default 120s)
- Store `last_sync_time` persistently (local file or sqlite) so K2 resumes from where it left off after restarts
- Log each sync: episodes received, graph stats delta, latency
- On network failure: log warning, exponential backoff (max 10 min), resume on reconnect
- K2 does NOT run an LLM, does NOT process episodes, does NOT make decisions — it only mirrors

### 3. Write-Back Rules (Observations Only)

K2 can write **observations** back to the graph via `POST /write-primitive`. Nothing else. No generated content, no LLM output, no decisions, no proposals.

**Allowed observation types:**
- Graph stats snapshots: `{ entity_count, episode_count, relationship_count, timestamp }` — written as `lane="raw"` Episodic nodes with source `"k2-observer"`
- Connectivity health: `{ droplet_reachable, latency_ms, last_sync_success, timestamp }`
- Sync lag measurements: `{ episodes_behind, time_since_last_sync }`

**Write-back constraints:**
- All writes go through `POST /write-primitive` with `lane="raw"` and `confidence=0.5` — never `candidate` or `canonical`
- Source field always `"k2-observer"` so writes are auditable
- Rate-limited: max 1 observation write per sync cycle (K2 should not flood the graph)
- Requires fixing **finding 3.2** first: `/write-primitive` must whitelist `lane` to `{"candidate", "raw"}` only, rejecting `lane="canonical"` from external callers

**What K2 NEVER does:**
- Call an LLM autonomously
- Write `lane="candidate"` or `lane="canonical"`
- Write generated content, decisions, or proposals
- Modify existing nodes (only CREATE, never SET/DELETE)

### 4. Atomic candidates.jsonl (CRITICAL — finding 3.1)

This must be fixed as a prerequisite for K2 write-back safety.

- Add a lock utility in `karma-core/server.py` using `fcntl.flock()` (or platform equivalent since this runs on Linux Docker)
- `_append_candidate()` acquires lock on `candidates.jsonl.lock` before appending
- `promote_candidates_endpoint()` acquires the same lock around the full read → modify → write-back cycle
- The lock is a file-level advisory lock, not a busy-wait spin

## Notes

- Fix #1 (consciousness loop) is the absolute blocker. Without it, Karma doesn't think between sessions regardless of K2.
- Fix #4 (atomic candidates) is a prerequisite for K2 write-back — without it, K2's observation writes could race with promotion.
- K2 polling endpoint should be bounded (max 100 episodes, 1MB cap) to prevent large payloads over Tailscale.
- `karma-k2-sync.py` must persist `last_sync_time` to survive K2 restarts — otherwise it re-syncs everything on every boot.
- The consciousness loop fix can be validated immediately by checking `/status` endpoint: `active_cycles` should start incrementing and `errors` should stop.
- K2 currently lives at `192.168.0.226` and connects to the droplet via Tailscale/public URL. The polling endpoint lives on the droplet at `:8340`.

## Relevant Files

| File | Changes |
|------|---------|
| `karma-core/consciousness.py` | Fix `_observe()`, `_decide()`, `_act()` key mismatches; fix timestamp type; wrap sync calls in `asyncio.to_thread()` |
| `karma-core/server.py` | Add `GET /v1/graph/sync` endpoint; add file lock utility; fix `_append_candidate()` and `promote_candidates_endpoint()` atomicity; whitelist `lane` in `/write-primitive` |
| `karma-core/config.py` | Add `K2_SYNC_EPISODE_LIMIT`, `K2_SYNC_MAX_BYTES` constants |
| `k2-worker/karma-k2-sync.py` | Rewrite from stub to real sync loop with persistent `last_sync_time` and observation write-back |
