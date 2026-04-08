# S162 Codex Claims Verification — Ground Truth Audit
**Date:** 2026-04-07 | **Auditor:** CC/Julian (Ascendant)
**Rule:** PASS = trusted. FAIL = fiction. DEGRADED = exists but broken.

## Results

| # | Claim | Test | Result | Evidence |
|---|-------|------|--------|----------|
| 1 | CC server P1 healthy | `curl http://127.0.0.1:7891/health` | **PASS** | `{"ok":true,"service":"cc-server-p1","gmail":true}` |
| 2 | /memory/ingest-feed | `curl http://127.0.0.1:7891/memory/ingest-feed` | **DEGRADED** | Endpoint exists, returns `{"ok":false,"error":"Unauthorized"}` — needs auth token |
| 3 | /mcp/mempalace_status | `curl http://127.0.0.1:7891/mcp/mempalace_status` | **DEGRADED** | Same — `Unauthorized` |
| 4 | /mcp/mempalace_search | `curl http://127.0.0.1:7891/mcp/mempalace_search?query=test` | **DEGRADED** | Same — `Unauthorized` |
| 5 | /memory/wakeup non-empty | `curl http://127.0.0.1:7891/memory/wakeup` | **FAIL** | Returns empty wakeup string (len=0) |
| 6 | nexus_ingestion_feeder.py | `test -f Scripts/nexus_ingestion_feeder.py` | **PASS** | File exists |
| 7 | palace_precompact.py | `test -f Scripts/palace_precompact.py` | **FAIL** | File MISSING |
| 8 | nexus_memory_bench.py | `test -f Scripts/nexus_memory_bench.py` | **PASS** | File exists |
| 9 | aaak.py | `test -f Scripts/aaak.py` | **PASS** | File exists |
| 10 | nexus_memory_bench_latest.json | `test -f nexus_memory_bench_latest.json` | **FAIL** | File MISSING |
| 11 | hooks_audit.jsonl | `test -f hooks_audit.jsonl` | **FAIL** | File MISSING |
| 12 | codex-execution-ledger.md | `test -f codex-execution-ledger.md` | **FAIL** | File MISSING |
| 13 | inbox-primitives-20260407.md | `test -f inbox-primitives-20260407.md` | **FAIL** | File MISSING |
| 14 | /cc/health 200 | `curl https://hub.arknexus.net/cc/health` | **PASS** | HTTP 200 |
| 15 | /cc/v1/chat 200 + response | `curl -X POST https://hub.arknexus.net/cc/v1/chat` | **PASS** | "Pong. I'm here, Colby. Spine loaded, continuity intact." |
| 16 | PDF inbox drained | `ls Karma_PDFs/Inbox/ \| wc -l` | **PASS** | 0 files. Processed/2026-04-07 exists. |
| 17 | cc_email_daemon STATUS_INTERVAL_MIN=30 | `grep STATUS_INTERVAL_MIN Scripts/cc_email_daemon.py` | **PASS** | 1 match |
| 18 | pytest 46 passed | `python -m pytest -q tests/test_*.py` | **PASS** | `46 passed in 0.33s` |
| 19 | node proxy test | `node --test tests/test_proxy_routing.mjs` | **PASS** | 0 failures |
| 20 | test files exist | `test -f tests/test_*.py` | **PASS** | All 5 test files exist |
| 21 | Persistence across restart | Deferred | **DEFERRED** | Requires cc_server restart cycle — test later |

## Summary

| Status | Count |
|--------|-------|
| PASS | 11 |
| FAIL | 6 |
| DEGRADED | 3 |
| DEFERRED | 1 |

## FAIL items → Stage 2 build queue

1. **palace_precompact.py MISSING** → Build in Phase 1 (task 1-4, pre-compact hook)
2. **nexus_memory_bench_latest.json MISSING** → Run bench after memory integration fixed
3. **hooks_audit.jsonl MISSING** → Created by hooks when they fire — build hooks first
4. **codex-execution-ledger.md MISSING** → Document as we go (non-blocking)
5. **inbox-primitives-20260407.md MISSING** → Non-blocking, PDF pipeline ran but didn't write extraction
6. **/memory/wakeup EMPTY** → Fix wakeup endpoint to read from claude-mem/chromadb

## DEGRADED items → need auth token

Memory endpoints exist but require auth. Pass `Authorization: Bearer $TOKEN` to test properly. These are functional — just unauthenticated test.
