# K2 Kiki Bridge — Design

**Date:** 2026-03-13
**Status:** Approved
**Scope:** Extend `fetchK2WorkingMemory()` to include kiki state in Karma's context

## Problem

Kiki v5 autonomous loop runs on K2 (devstral/Ollama). Karma's chat brain (Haiku/hub-bridge) has no visibility into what kiki is doing. Karma can't see her own autonomous evolution — backlog, results, failures.

## Design

Extend the existing `fetchK2WorkingMemory()` shell command (server.js line 322) to also read:
- `kiki_state.json` — cycle counts, success/failure rate
- `tail -20 kiki_journal.jsonl` — full JSON entries (issue, action, result, verification)
- `kiki_issues.jsonl` — current backlog

All files live at `/mnt/c/dev/Karma/k2/cache/` on K2.

## Changes

1. **server.js `fetchK2WorkingMemory()` shell command** — append reads for 3 kiki files
2. **`K2_WORKING_MEM_MAX_CHARS`** — bump 4000 → 6000
3. **Section header** — update to reflect kiki inclusion

## What Karma Sees

```
=== SCRATCHPAD ===
(existing structured notes)
=== SHADOW ===
(existing raw session capture)
=== KIKI STATE ===
{"cycles": 3, "actions_succeeded": 1, ...}
=== KIKI JOURNAL (last 20) ===
{"ts":"...","cycle":1,"type":"failure","issue":"...","summary":"...","result":"...","ok":false}
{"ts":"...","cycle":3,"type":"action","issue":"...","summary":"...","result":"...","ok":true}
=== KIKI BACKLOG ===
{"issue":"...","details":"..."}
```

Journal entries are full JSON — not summaries. Karma reads the causal chain: what issue → what fix → what verification → pass/fail.

## What Doesn't Change

- Cache TTL (5min via `K2_MEM_CACHE_TTL_MS`)
- Fetch mechanism (Aria `/api/exec`)
- Error handling (non-blocking, null if K2 unreachable)
- `Promise.all` parallel fetch pattern
- `buildSystemText()` signature (k2WorkingMemCtx param already exists)

## Deploy

1. Edit server.js locally
2. git commit + push
3. ssh vault-neo: git pull → cp to build context → `docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d`
4. Verify via `docker logs anr-hub-bridge` for `[K2-WORK]` log line
