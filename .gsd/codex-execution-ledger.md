# Codex Execution Ledger

Date: 2026-04-05T11:30:28.3019183-04:00
Host: P1
Mode: STEP-LOCK / master forensic build prompt
Authority: `docs/ForColby/CODEX MASTER FORENSIC BUILD PROMP.md`

## Current Phase

- Phase: Contradiction matrix for the single chosen failing path
- Status: IN PROGRESS
- Rule: only the Electron UI event-to-store/memory path is in scope until it is broken down, reproduced, and fixed

## Read Gate Status

### DONE

1. `docs/ForColby/CODEX MASTER FORENSIC BUILD PROMP.md`
2. `docs/ForColby/nexus.md`
3. `.gsd/codex-cascade-audit.md`
4. `.gsd/codex-final-directive.md`
5. `.gsd/codex-sovereign-directive.md`
6. `Karma2/cc-scope-index.md`
7. `docs/anthropic-docs/` authoritative entrypoints:
   - `inventory.md`
   - `agents-and-tools/tool-use-overview.md`
   - `agents-and-tools/implement-tool-use.md`
   - `agents-and-tools/fine-grained-tool-streaming.md`
   - `agent-sdk/agent-loop.md`
   - `agent-sdk/sessions.md`
   - `agent-sdk/permissions.md`
   - `agent-sdk/hooks.md`
   - `claude-code/how-claude-code-works.md`
   - `claude-code/cli-reference.md`
   - `claude-code/memory.md`
   - `claude-code/hooks.md`
8. `docs/claude-mem-docs/` authoritative entrypoints:
   - `README.md`
   - `CLAUDE.md`
   - `package.json`
   - `docs/SESSION_ID_ARCHITECTURE.md`
   - `src/services/worker/README.md`
   - `docs/public/architecture/overview.mdx`
   - `docs/public/architecture/worker-service.mdx`
   - `docs/public/progressive-disclosure.mdx`
   - `docs/public/usage/search-tools.mdx`
9. `docs/wip/preclaw1/preclaw1/src/` authoritative primitives:
   - full file inventory captured
   - `main.tsx`
   - `query.ts`
   - `QueryEngine.ts`
   - `Task.ts`
   - `Tool.ts`
   - `tools.ts`
   - `history.ts`
   - `context.ts`
   - `dialogLaunchers.tsx`
   - `utils/sessionStorage.ts`
   - `utils/permissions/permissions.ts`
   - `utils/hooks/sessionHooks.ts`
   - `bridge/replBridge.ts`
   - `bridge/sessionIdCompat.ts`
   - `bridge/remoteBridgeCore.ts`

### DONE

10. Current runtime code for the single chosen failing path
    - chosen failing path: Electron UI event-to-store/memory path
    - read from:
      - `electron/main.js` smoke runner and IPC path
      - `frontend/src/hooks/useKarmaStream.ts`
      - `frontend/src/components/MessageInput.tsx`
      - `frontend/src/components/ChatFeed.tsx`
      - `frontend/src/store/karma.ts`
      - `frontend/src/app/page.tsx`

## Ground Truth Notes From Reads

- Anthropic tool use requires a real tool loop: detect `tool_use`, execute locally, feed `tool_result`, repeat until assistant terminal output.
- Claude Code session persistence lives in `.jsonl` session files under `~/.claude/projects/...`, with `resume` / `continue` semantics distinct from a custom transcript layer.
- `claude-mem` architecture is hook-driven plus a worker service with HTTP API, search/progressive-disclosure retrieval, and a critical split between `contentSessionId` and internal `memorySessionId`.
- `preclaw1` core blueprint is a typed query engine around durable session storage, tool registry, permission pipeline, hooks, and bridge/session transports; it is not a separate “tabs” product model.
- Live runtime proof on the chosen failing path:
  - `http://localhost:37778/health` is healthy on the canonical `claude-mem` endpoint
  - Electron direct Claude path succeeds
  - Electron renderer `window.karma.chat(...)` path succeeds
  - Electron smoke UI path still fails with `ui smoke timed out`, `composerPresent: true`, `gatePresent: false`, `messageCount: 0`
- The first failing path is therefore not the Claude CLI engine itself; it is the UI-layer event-to-store/memory path or the smoke harness code that proves that path

## Active Pitfalls In Force

- `P106 [hard-gates-are-binary]`
- `P107 [no-phase-transition-without-itemized-closure]`
- `P108 [core-endpoint-must-be-proved-live]`
- `P109 [do-not-mitigate-user-owned-blockers]`
- `P110 [all-files-means-all-relevant-text-files]`
- `P111 [endpoint-cleanup-must-be-semantic]`
- `P112 [ledger-must-not-preserve-corrected-falsehoods]`

## Current Write Set

- `.gsd/codex-execution-ledger.md`

## Next Locked Step

- build the contradiction matrix for the Electron UI event-to-store/memory path
- identify the smallest reproducible failure inside that path
- write or identify the first RED test for that exact failure

## Completed Fix: Electron Token/Auth/Continuity Path

- Chosen failing path stayed locked to the Electron `cc-chat` + renderer/UI continuity path.
- Contradictions found and fixed in sequence:
  - external send-event listener readiness race
  - Electron loading the wrong static export directory
  - `file://` frontend calling relative `/v1/...` APIs without rewriting to local P1 server
  - local P1 server missing `/v1/chat` and `/v1/chat/stream` aliases expected by the merged workspace
  - Electron gate not auto-loading the existing hub token
  - exported Next assets using root-absolute `/_next/...` URLs, preventing hydration under `file://`
  - Electron `memory-search` returning raw worker payload instead of normalized `results`
- Files changed on this path:
  - `electron/main.js`
  - `electron/preload.js`
  - `frontend/src/components/MessageInput.tsx`
  - `frontend/src/app/page.tsx`
  - `frontend/src/components/Gate.tsx`
  - `frontend/next.config.js`
  - `Scripts/cc_server_p1.py`
  - `tests/test_electron_memory_autosave.py`
  - `tests/test_cc_server_harness.py`

## Proof

- `python -m pytest -q tests/test_electron_memory_autosave.py` -> `9 passed in 0.02s`
- `python -m pytest -q tests/test_electron_memory_autosave.py tests/test_cc_server_harness.py` -> `27 passed in 0.13s`
- `node --check electron/main.js` -> pass
- local P1 route proof:
  - `http://127.0.0.1:7891/v1/chat` with real token -> `200 {"ok": true, "response": "Pong."}`
- Electron full smoke proof:
  - output file: `tmp/electron-smoke-current.json`
  - `ok: true`
  - `isElectron: true`
  - `result.provider: "claude"`
  - `result.result: "UIREADY_20260405"`
  - `uiResult.ok: true`
  - `uiResult.lastKarma.content: "UI_MEM_mnlyjule"`
  - `uiResult.memory.ok: true`
  - `uiResult.memory.results[0].text` contains the saved token hit

## Closure

- The user-reported blocker “unable to enter the karma chat hub token into the electron harness” is fixed in runtime truth.
- The Electron merged-workspace path now:
  - hydrates correctly under `file://`
  - auto-loads the hub token
  - reaches the local P1 `/v1/chat` contract
  - uses Claude Max through the CLI path
  - auto-saves to `claude-mem`
  - retrieves the saved token through normalized memory search

## Next Locked Step

- chosen failing path: P1 sovereign email watcher/status loop
- reason: user explicitly requires recurring email checks plus status emails, and all email from `rae.steele76@gmail.com` must be treated as sovereign directive

## Contradiction Matrix: Email Loop

- Runtime truth:
  - `CC-Archon-Agent` already runs every 30 minutes on P1 via hidden scheduled task
  - `cc_email_daemon.py check` works live against Gmail
  - `cc_email_daemon.py status` can send email live
- Code contradiction found:
  - status cadence was still 8 hours
  - inbox check did not semantically recognize sovereign sender
  - no durable queue existed for inbound sovereign directives
  - no immediate acknowledgment existed for sovereign directive email

## Completed Fix: Sovereign Email Watcher/Status Slice

- Files changed on this path:
  - `Scripts/cc_email_daemon.py`
  - `Scripts/cc_archon_agent.ps1`
  - `tests/test_cc_email_daemon.py`
- New behavior:
  - status cadence reduced to 30 minutes
  - sovereign sender detection added for `rae.steele76@gmail.com`
  - inbound sovereign emails are queued to `tmp/sovereign_email_inbox/`
  - immediate acknowledgment email body is generated with explicit understanding
  - sovereign directive events are posted to the bus

## Proof

- `python -m pytest -q tests/test_cc_email_daemon.py tests/test_electron_memory_autosave.py tests/test_cc_server_harness.py` -> `31 passed in 0.15s`
- `python -m py_compile Scripts\cc_email_daemon.py` -> pass
- live watcher proof:
  - `py -3 Scripts\cc_email_daemon.py check` -> `no new messages (total=38)`
- live status proof:
  - first run -> `sent: [CC STATUS] 2026-04-05 16:14 UTC`
  - second run -> `skipped (0.6m since last, threshold=30m)`
- scheduler proof:
  - `schtasks /query /TN "CC-Archon-Agent" /V /FO LIST`
  - `Repeat: Every: 0 Hour(s), 30 Minute(s)`

## Live Sovereign Email Proof

- Real inbound sovereign email received:
  - subject: `Status update issues`
  - from: `rae.steele76@gmail.com`
  - queued file: `tmp/sovereign_email_inbox/20260405T185212.515638+0000_Status-update-issues.json`
- Archon log proof:
  - `Email check: new=1; sovereign=1: From: Rae Steele <rae.steele76@gmail.com> | Status update issues`
- Explicit clarification email sent via `send_to_colby(...)` and returned `{'ok': True}`
- Directive executed:
  - status email formatter cleaned
  - status body now emits digest + open blockers only
  - mojibake/raw-markdown artifacts removed from rendered body
- Completion email sent via `send_to_colby(...)` and returned `{'ok': True}`

## Additional Proof

- `python -m pytest -q tests/test_cc_email_daemon.py tests/test_electron_memory_autosave.py tests/test_cc_server_harness.py` -> `33 passed in 0.18s`
- live rendered status body now shows:
  - clean `CC Ascendant - Status Report`
  - clean `The One Thing` line
  - clean `Immediate next steps`
  - `Open blockers: 3`
  - no `~~`
  - no `**`
  - no `???"`/replacement garbage

## Closure

- The sovereign email loop is now proven end-to-end in runtime truth for:
  - inbound detection
  - durable queueing
  - clarification/ack email
  - directive execution
  - completion email

## Next Locked Step

- chosen failing path: shared transcript/session substrate across P1 server and Electron
- reason: `claursted`'s strongest merge candidate is append-only JSONL session storage, and the current contradiction was that Electron still kept transcript state in memory while browser/P1 used `tmp/transcripts/*.jsonl`

## Contradiction Matrix: Shared Transcript Contract

- Runtime truth before fix:
  - browser/P1 transcript persistence existed in `tmp/transcripts/*.jsonl`
  - Electron had localStorage/session snapshot persistence but no shared transcript loader/writer
  - Python transcript append rewrote the whole JSONL file on every turn
- Code contradiction found:
  - no shared append-only contract across browser/P1 and Electron
  - no lightweight tail metadata for fast session summaries
  - `cc_server_p1.py` trimmed transcript files by rewriting them during request handling

## Completed Fix: Shared Transcript Contract Slice

- Files changed on this path:
  - `Scripts/nexus_agent.py`
  - `Scripts/cc_server_p1.py`
  - `electron/main.js`
  - `tests/test_transcript_contract.py`
  - `tests/test_electron_memory_autosave.py`
- New behavior:
  - transcript storage is append-only JSONL with typed message rows
  - user turns also write `last-prompt` tail metadata rows
  - `load_transcript(..., limit=N)` now reads message entries only and does not rewrite files
  - `list_transcript_sessions()` exposes recent session summaries from tail metadata
  - Electron now reads and writes the shared `tmp/transcripts/*.jsonl` substrate
  - Electron fallback paths receive prior transcript context instead of acting as stateless turns

## Proof

- `python -m pytest -q tests/test_transcript_contract.py tests/test_electron_memory_autosave.py tests/test_cc_server_harness.py` -> `33 passed in 0.36s`
- `node --check electron\\main.js` -> pass
- direct transcript contract proof:
  - `LOAD=[{"role": "user", ...}, {"role": "assistant", ...}]`
  - `LIST=[{"session_id": "demo", ..., "last_prompt": "hello"}]`
- live Electron proof:
  - `tmp/electron-smoke-current.json` -> `ok: true`
  - provider: `claude`
  - result: `ELECTRON_TRANSCRIPT_OK`
  - latest transcript file now contains:
    - typed `user` row
    - `last-prompt` metadata row
    - typed `assistant` row

## Remaining Blocker

- The running P1 `cc_server_p1.py` process on `http://127.0.0.1:7891` has not yet been restarted onto the new code.
- Live proof showed:
  - response ok: `TRANSCRIPT_PROOF_OK`
  - transcript file for that request still used the old `{role, content, ts}` shape
- Therefore this slice is code-complete and Electron-live-complete, but NOT fully live-complete on the P1 server until that runtime is restarted and re-verified.

## Closure Update

- The P1 server was cleanly restarted and re-verified.
- Final live proof:
  - response ok: `TRANSCRIPT_RELOAD_OK`
  - transcript file now contains:
    - typed `user` row
    - `last-prompt` metadata row
    - typed `assistant` row
- Therefore the shared transcript/session substrate slice is now fully closed in live truth across:
  - P1 server
  - browser contract
  - Electron

## Next Locked Step

- chosen failing path: Archon email cadence split
- reason: code and runtime still encode a single 30-minute `CC-Archon-Agent` loop, but the current architecture requires:
  - inbox/directive watcher every 15 minutes
  - status email every 60 minutes

## Contradiction Matrix: Archon Email Cadence

- Runtime truth before fix:
  - `CC-Archon-Agent` scheduled task repeats every 30 minutes
  - `cc_email_daemon.py` status cadence was also 30 minutes
- Code contradiction found:
  - watcher cadence and status cadence were fused
  - no independent watcher gate file existed
- Code fix completed:
  - `Scripts/cc_email_daemon.py`
  - `Scripts/cc_archon_agent.ps1`
  - `tests/test_cc_email_daemon.py`
  - added `CHECK_INTERVAL_MIN = 15`
  - changed `STATUS_INTERVAL_MIN = 60`
  - added `CHECK_LAST_FILE` gate
  - status body now reports both watcher and status cadence
  - targeted tests pass: `8 passed`
- Remaining blocker:
  - live Windows scheduled task still repeats every 30 minutes
  - this requires a P1 task update to fully close the path in runtime truth

## Closure Update

- The P1 scheduled task was updated and re-verified by live user proof.
- Final live proof:
  - `schtasks /change /TN "CC-Archon-Agent" /RI 15` -> `SUCCESS`
  - `schtasks /query /TN "CC-Archon-Agent" /V /FO LIST` -> `Repeat: Every: 0 Hour(s), 15 Minute(s)`
- Therefore the Archon cadence split is now closed in live truth:
  - watcher/check cadence: 15 minutes
  - status email cadence: 60 minutes

## Next Locked Step

- chosen failing path: Vesper auto-dream / consolidation gating
- reason: `claursted`'s next strongest merge candidate is cheap-first gated consolidation with persisted state and stale-lock handling, while the live repo contradiction was:
  - the real watchdog file `Scripts/vesper_watchdog.py` had no consolidation primitive
  - the stale twin `Vesper/vesper_watchdog.py` contained an ungated consolidation routine

## Contradiction Matrix: Vesper Consolidation Gating

- Runtime/code truth before fix:
  - `Scripts/vesper_watchdog.py` is the real candidate pipeline file (676 lines, candidate emitters, ambient extraction)
  - `Vesper/vesper_watchdog.py` is the stale twin (347 lines)
  - only the stale twin contained `consolidate_memories()`
  - the stale routine had no persisted state file, no cheap-first time gate, and no stale-lock gate
- Merge decision:
  - ADAPT `claursted`'s gate contract:
    - persisted state
    - time gate first
    - new-entry gate second
    - stale-lock gate third
  - ADAPT the stale twin's local-Ollama consolidation routine into the live watchdog file
  - REJECT the stale twin itself as source of truth

## Completed Fix: Vesper Consolidation Slice

- Files changed on this path:
  - `Scripts/vesper_watchdog.py`
  - `tests/test_vesper_watchdog_consolidation.py`
- New behavior in the live watchdog file:
  - added `CONSOLIDATION_STATE_FILE`, `CONSOLIDATION_LOCK_FILE`, and live consolidation constants
  - added persisted state helpers:
    - `load_consolidation_state()`
    - `save_consolidation_state(...)`
    - `mark_consolidation_complete(...)`
  - added cheap-first gate helpers:
    - `time_gate_passes(...)`
    - `entry_gate_passes(...)`
    - `lock_gate_passes(...)`
    - `should_consolidate(...)`
  - added gated local consolidation flow:
    - selects recent unconsolidated entries from the real evolution log
    - calls local Ollama only after gates pass
    - appends `vesper_consolidations.jsonl`
    - marks selected evolution entries `consolidated: true`
    - persists `last_consolidated_at`
  - watchdog main path now calls `consolidate_memories()` in the live file

## Proof

- `python -m pytest -q tests/test_vesper_watchdog_consolidation.py tests/test_vesper_governor.py` -> `7 passed in 0.11s`
- `python -m py_compile Scripts\\vesper_watchdog.py` -> pass
- direct local runtime proof:
  - `[watchdog] consolidated 2 entries -> continuity anchored through shared transcripts`
  - `CHANGED=2`
  - state file written with `last_consolidated_at`
  - consolidation record appended to `vesper_consolidations.jsonl`
  - selected evolution rows rewritten with `"consolidated": true`

## Remaining Blocker

- The deployed/live K2 watchdog service still points at the separate runtime file:
  - `/mnt/c/dev/Karma/k2/aria/vesper_watchdog.py`
- Therefore this slice is closed in repo code, tests, and direct local runtime proof, but NOT yet closed as deployed K2 runtime truth until that K2 file is updated or resynced and re-verified.

## Closure Update

- The repaired watchdog file was copied to K2 and executed directly on the deployed runtime path.
- Final live K2 proof:
  - `python3 /mnt/c/dev/Karma/k2/aria/vesper_watchdog.py`
    - emitted `consolidation gated: count=0 threshold=10 min_hours=24.0`
    - completed normally
  - `ls -la /mnt/c/dev/Karma/k2/cache/vesper_consolidation_state.json /mnt/c/dev/Karma/k2/cache/vesper_consolidations.jsonl`
    - `vesper_consolidation_state.json` exists
    - `vesper_consolidations.jsonl` exists and grew
  - `tail -n 2 /mnt/c/dev/Karma/k2/cache/vesper_consolidations.jsonl`
    - shows a fresh `2026-04-05T21:28:25.417859Z` consolidation record
- Therefore the Vesper consolidation slice is now closed in:
  - repo code
  - tests
  - direct local runtime proof
  - deployed K2 runtime truth

## Residual Issue

- `vesper_watchdog.py` on K2 still emits `datetime.utcnow()` deprecation warnings.
- This is real but non-blocking for the closed consolidation path.

## Next Locked Step

- chosen failing path: Electron hub token / desktop-to-browser contract
- reason: user-reported runtime truth says the Electron harness does not accept or use the Karma chat hub token correctly, which blocks the merged workspace contract even if the backend slices are healthy

## Closure Update

- The dedicated Electron gate smoke was rerun against the current static desktop build and no longer reproduces the token failure.
- Final proof artifact:
  - `tmp/electron-smoke-gate.json`
  - `ok: true`
  - `directResult.provider: claude`
  - `result.provider: claude`
  - `uiResult.ok: true`
  - desktop UI turn persisted to claude-mem and transcript substrate
- Ground-truth observations:
  - `.hub-chat-token` exists at repo root and is readable by Electron
  - preload exposes `hubToken`
  - static `frontend/out` build already contains:
    - Electron gate auto-auth
    - `file:` fetch rewrite to `http://127.0.0.1:7891`
- Therefore the Electron hub-token / desktop gate path is currently closed in runtime truth.

## Residual Issue

- The earlier user-reported failure was real at the time reported, but it is not currently reproducible under the dedicated gate smoke.
- If it recurs, the next proof target should be the exact visible desktop state of the already-open window, not the static build.

## Next Locked Step

- chosen failing path: UTC/deprecation drift in the live watchdog path
- reason: the deployed K2 watchdog is now part of the verified consolidation/runtime truth, and it was still emitting `datetime.utcnow()` deprecation warnings during real execution

## Contradiction Matrix: Watchdog UTC Drift

- Runtime truth before fix:
  - `python -W default Scripts\\vesper_watchdog.py` emitted deprecation warnings from `datetime.datetime.utcnow()`
  - K2 proof files from `docs/forCodex/step1.txt` showed the same warning on the deployed watchdog path
- Code contradiction found:
  - `Scripts/vesper_watchdog.py` already had timezone-aware helpers `_utc_now()` / `_iso_utc(...)`
  - but a set of older candidate/timestamp paths still called `datetime.datetime.utcnow()` directly

## Completed Fix: Watchdog UTC Cleanup Slice

- Files changed on this path:
  - `Scripts/vesper_watchdog.py`
  - `tests/test_vesper_watchdog_consolidation.py`
- New behavior:
  - all remaining `datetime.datetime.utcnow()` calls in the live watchdog file were replaced with `_utc_now()` / `_iso_utc(...)`
  - added a RED test forbidding deprecated `utcnow()` usage in the live watchdog file

## Proof

- `python -m pytest -q tests/test_vesper_watchdog_consolidation.py tests/test_vesper_governor.py` -> `8 passed in 0.08s`
- `python -W default Scripts\\vesper_watchdog.py` -> watchdog runs with no deprecation warnings

## Remaining Blocker

- The deployed K2 runtime still has the previously copied watchdog file.
- Therefore this UTC-cleanup slice is closed in repo code and local runtime proof, but NOT yet closed on deployed K2 until the updated `Scripts/vesper_watchdog.py` is recopied to `/mnt/c/dev/Karma/k2/aria/vesper_watchdog.py` and rerun there.
- 2026-04-05T22:08Z — Closed direct-Anthropic drift in active K2 cc_bus_reader.py.
  - RED: python -m pytest -q tests/test_cc_bus_reader_routing.py would have failed before patch because pi.anthropic.com and ANTHROPIC_API_KEY were present in Scripts/cc_bus_reader.py.
  - GREEN: python -m pytest -q tests/test_cc_bus_reader_routing.py -> 3 passed in 0.03s.
  - GREEN: python -m py_compile Scripts\cc_bus_reader.py.
  - Deploy: copied Scripts/cc_bus_reader.py to /mnt/c/dev/Karma/k2/scripts/cc_bus_reader.py and compiled on K2 (K2_COPY_OK).
  - Live proof: posted coordination bus message Please analyze this routing proof and reply with exactly CCBUSLIVE_72a2680b and nothing else. from karma to cc; then ran ssh karma@192.168.0.226 'HUB_AUTH_TOKEN= env -u ANTHROPIC_API_KEY python3 /mnt/c/dev/Karma/k2/scripts/cc_bus_reader.py'.
  - Live result: K2 script output Processing [cloud]... Response posted... Done. Processed 1 new message(s).
  - Bus proof: recent coordination entries include rom=cc, 	o=karma, content=CCBUSLIVE_72a2680b, created_at=2026-04-05T22:06:50.516Z.
- 2026-04-05T22:14Z — Closed direct-Anthropic drift in active K2 `karma_regent.py`.
  - RED: `python -m pytest -q tests/test_karma_regent_routing.py` would have failed before patch because `Scripts/karma_regent.py` still contained `api.anthropic.com`, `ANTHROPIC_API_KEY`, and a direct `call_claude` fallback.
  - GREEN: `python -m pytest -q tests/test_karma_regent_routing.py` -> `2 passed in 0.02s`.
  - GREEN: inline proof for `Scripts.regent_inference.call_with_local_first(... fallback_label="cc_harness")` returned `fallback-ok` / `cc_harness`.
  - GREEN: `python -m py_compile Scripts\karma_regent.py Scripts\regent_inference.py`.
  - Deploy: synced `Scripts/karma_regent.py` and `Scripts/regent_inference.py` to `/mnt/c/dev/Karma/k2/aria/`.
  - Live proof: posted `Please analyze this routing proof and reply with exactly REGENTLIVE_d98f1732 and nothing else.` to `regent`; deployed daemon replied `REGENTLIVE_d98f1732` on the coordination bus.
- 2026-04-05T22:18Z — Closed K2 regent dedup-watermark startup error and UTC deprecation spam.
  - RED: live K2 log showed `[regent] dedup watermark load error: 'set' object is not subscriptable` and multiple `datetime.utcnow()/utcfromtimestamp()` deprecation warnings.
  - GREEN: `python -m pytest -q tests/test_karma_regent_dedup.py tests/test_karma_regent_routing.py` -> `5 passed in 0.05s`.
  - GREEN: `python -m py_compile Scripts\karma_regent.py`.
  - Deploy: synced patched `Scripts/karma_regent.py` to `/mnt/c/dev/Karma/k2/aria/karma_regent.py`.
  - Live proof: current startup chunk in `/mnt/c/dev/Karma/k2/cache/regent.log` has `DEP_WARN_COUNT 0` and shows `dedup watermark loaded: 115 ids` instead of the old exception.
  - Isolated probe: `python3 -u -W default /mnt/c/dev/Karma/k2/aria/karma_regent.py` -> `DEP_WARN_COUNT 0`.
- 2026-04-05T22:22Z — Closed K2 cron secret leak and restored crontab after failed edit.
  - RED: K2 `crontab -l` still injected `ANTHROPIC_API_KEY=$(cat /mnt/c/dev/Karma/k2/cache/.secrets/anthropic_api_key)` into the live `cc_bus_reader.py` schedule even though the reader no longer used it.
  - Regression during fix: an earlier edit attempt emptied the K2 crontab; restored immediately from the last known-good live snapshot.
  - GREEN: current K2 crontab includes `cc_bus_reader.py` again with only `HUB_AUTH_TOKEN`, and `grep anthropic_api_key` on the crontab returns no matches.
  - GREEN: manual K2 run `ssh karma@192.168.0.226 'HUB_AUTH_TOKEN=$(cat /mnt/c/dev/Karma/k2/cache/.secrets/hub_auth_token) /usr/bin/python3 /mnt/c/dev/Karma/k2/scripts/cc_bus_reader.py'` -> `Done. Processed 0 new message(s).`
- 2026-04-05T22:36Z — Closed K2 regent triage model/env drift against the real local model floor.
  - RED: live K2 inventory proved `host.docker.internal:11434` serves `qwen3.5:4b` and does **not** serve `nemotron-mini:latest`; the deployed regent env still carried `REGENT_TRIAGE_MODEL=qwen3:8b`, while `Scripts/regent_triage.py` still defaulted to `nemotron-mini:latest`.
  - GREEN: `python -m pytest -q tests/test_local_inference_defaults.py` -> `3 passed in 0.03s`.
  - GREEN: `python -m py_compile Scripts\regent_triage.py Vesper\regent_triage.py`.
  - Repo fix: `Scripts/regent_triage.py` and mirrored `Vesper/regent_triage.py` now default to `K2_OLLAMA_URL=http://host.docker.internal:11434` and `REGENT_TRIAGE_MODEL=qwen3.5:4b`.
  - Deploy: copied `Scripts/regent_triage.py` to `/mnt/c/dev/Karma/k2/aria/regent_triage.py`.
  - Live env fix: updated `/etc/karma-regent.env` to `REGENT_TRIAGE_MODEL=qwen3.5:4b` and removed the no-longer-needed `ANTHROPIC_API_KEY` from that regent-specific systemd env file.
  - Live proof: remote import reports `TRIAGE_URL http://host.docker.internal:11434`, `TRIAGE_MODEL qwen3.5:4b`, and `TRIAGE_RESULT reason` for a non-ack test message.
  - Service proof: `systemctl show karma-regent.service -p ActiveState -p SubState -p ExecMainPID -p NRestarts -p ActiveEnterTimestamp` -> `ActiveState=active`, `SubState=running`, `NRestarts=0`, `ExecMainPID=60404`.
  - Live env proof (non-secret subset): `K2_OLLAMA_PRIMARY_MODEL=qwen3.5:4b`, `K2_OLLAMA_FALLBACK_MODEL=`, `P1_OLLAMA_MODEL=sam860/LFM2:350m`, `REGENT_TRIAGE_MODEL=qwen3.5:4b`, `ANTHROPIC_PRESENT=False`.
- 2026-04-05T22:42Z — Closed nightly session-review model drift against the proven K2/P1 review floor.
  - RED: `Scripts/Run-SessionIngest.ps1` still drove the nightly review pass through `OLLAMA_URL=http://localhost:11434` and `REVIEW_MODEL=sam860/LFM2:350m`, even though P1 can reach K2 `qwen3.5:4b` directly and this ingest path is the continuity-quality review pass.
  - Runtime proof before fix: P1 direct probes returned `OK http://100.75.109.92:11434 qwen3.5:4b OK` and `OK http://localhost:11434 sam860/LFM2:350m ...`, proving K2 is reachable and should be primary while P1 remains the fallback floor.
  - GREEN: `python -m pytest -q tests/test_session_review.py tests/test_local_inference_defaults.py` -> `6 passed in 0.04s`.
  - GREEN: `python -m py_compile Scripts\session_review.py`.
  - Repo fix: `Scripts/session_review.py` now defaults to `OLLAMA_URL=http://100.75.109.92:11434`, `REVIEW_MODEL=qwen3.5:4b`, and keeps `LOCAL_OLLAMA_URL=http://localhost:11434`, `REVIEW_FALLBACK_MODEL=sam860/LFM2:350m`.
  - Task fix: `Scripts/Run-SessionIngest.ps1` now sets `OLLAMA_URL=http://100.75.109.92:11434`, `REVIEW_MODEL=qwen3.5:4b`, `REVIEW_FALLBACK_MODEL=sam860/LFM2:350m` and logs the corrected cascade.
  - Live proof: importing `Scripts.session_review` now reports `OLLAMA_URL http://100.75.109.92:11434`, `MODEL qwen3.5:4b`, `LOCAL_OLLAMA_URL http://localhost:11434`, `LOCAL_OLLAMA_MODEL sam860/LFM2:350m`.
  - Live proof: `Scripts.session_review.call_review_model('Return exactly [] and nothing else.')` returned `[]` through the corrected module path.
- 2026-04-06T14:00Z — Closed hub-bridge future-rebuild regression trap.
  - RED: the live `anr-hub-bridge` container was correctly running `["node","proxy.js"]`, but the checked-in and vault-side Dockerfile path used for future rebuilds still built the old heavy `server.js` image.
  - GREEN: `python -m pytest -q tests/test_hub_bridge_dockerfile.py` -> `1 passed in 0.02s`.
  - Repo fix: `hub-bridge/app/Dockerfile` now matches the live thin-proxy image (`proxy.js`, `public/`, no npm install, no `lib/`, `CMD ["node", "proxy.js"]`).
  - Deploy fix: `/home/neo/karma-sade/hub-bridge/app/Dockerfile` and `/opt/seed-vault/memory_v1/hub_bridge/app/Dockerfile` now contain the same thin-proxy Dockerfile.
  - Live proof: `docker inspect anr-hub-bridge --format '{{json .Config.Cmd}} {{json .Config.WorkingDir}}'` -> `["node","proxy.js"] "/app"`.
- 2026-04-06T14:04Z — Closed SmartRouter K2 model drift in the active P1 server path.
  - RED: `Scripts/cc_server_p1.py` imports `Scripts.smart_router.SmartRouter`, and a live probe `SmartRouter().route('hi')` returned `{'provider': 'k2-ollama', 'model': 'qwen3:8b', ...}` even though the real K2 floor is `qwen3.5:4b`.
  - GREEN: `python -m pytest -q tests/test_local_inference_defaults.py` -> `5 passed in 0.03s`.
  - GREEN: `python -m py_compile Scripts\smart_router.py`.
  - Repo fix: `Scripts/smart_router.py` now resolves K2 tier-0 model as `K2_OLLAMA_MODEL` or `K2_OLLAMA_PRIMARY_MODEL` or default `qwen3.5:4b`.
  - Live proof: `SmartRouter().route('hi')` now returns `{'provider': 'k2-ollama', 'model': 'qwen3.5:4b', 'tier': 0, ...}`.
- 2026-04-06T14:07Z — Closed K2 MCP tool default-model drift.
  - RED: `Scripts/k2_mcp_server.py` still advertised `qwen3:8b` as the default `k2_ollama_chat` model even though the proven live K2 floor is `qwen3.5:4b`.
  - GREEN: `python -m pytest -q tests/test_local_inference_defaults.py` -> `6 passed in 0.03s`.
  - GREEN: `python -m py_compile Scripts\k2_mcp_server.py`.
  - Repo fix: `Scripts/k2_mcp_server.py` now documents inventory as live-dependent, defaults the `k2_ollama_chat` tool to `qwen3.5:4b`, and routes missing-model calls to `arguments.get("model", "qwen3.5:4b")`.
- 2026-04-06T14:08Z — Closed CC email personal-outreach dead-model bug.
  - RED: live local probe to `http://localhost:11434/v1/chat/completions` returned `HTTP Error 404: Not Found` for `llama3.1:8b`, while `sam860/LFM2:350m` succeeded.
  - RED: `py -3 Scripts\cc_email_daemon.py personal` returned `personal skipped: ollama unavailable or empty response`.
  - GREEN: `python -m pytest -q tests/test_cc_email_daemon.py` -> `9 passed in 0.07s`.
  - Repo fix: `Scripts/cc_email_daemon.py` now reads `EMAIL_OLLAMA_URL`/`EMAIL_OLLAMA_MODEL` from env when present and defaults the personal-outreach path to `http://localhost:11434/v1/chat/completions` with `sam860/LFM2:350m`.
  - Live proof: importing the module reports `OLLAMA_URL http://localhost:11434/v1/chat/completions` and `OLLAMA_MODEL sam860/LFM2:350m`.
  - Live proof: `py -3 Scripts\cc_email_daemon.py personal` now returns `sent: [CC] personal — 2026-04-06 14:07 UTC`.
- 2026-04-06T17:00Z — Closed K2 local-floor host-boundary drift and re-selected the K2 local model from runtime evidence.
  - RED: SSH-visible K2 proved `localhost:11434` and `127.0.0.1:11434` refused connections, while `host.docker.internal:11434` returned the live model inventory. `sudo -n systemctl status ollama` also proved there is no Linux `ollama.service` on that K2 side.
  - RED: active deployed K2 files still defaulted to `http://localhost:11434`: `/mnt/c/dev/Karma/k2/aria/karma_regent.py` and `/mnt/c/dev/Karma/k2/aria/julian_cortex.py`.
  - RED: runtime model comparison on actual installed K2 models showed `nomic-embed-text:latest` is not a chat option (`HTTP 400` on `/api/chat`), `gemma4:e4b` timed out on most bounded structured tasks, and `qwen3.5:4b` materially outperformed Gemma on completed structured tasks despite remaining timeout weakness.
  - GREEN: repo defaults corrected in `Scripts/karma_regent.py`, `Vesper/karma_regent.py`, and `k2/aria/julian_cortex.py` to `http://host.docker.internal:11434`.
  - GREEN: `python -m pytest -q tests/test_local_inference_defaults.py` -> `7 passed in 0.03s`.
  - GREEN: `python -m py_compile Scripts\karma_regent.py Vesper\karma_regent.py k2\aria\julian_cortex.py`.
  - Deploy: synced corrected `karma_regent.py` and `julian_cortex.py` to `/mnt/c/dev/Karma/k2/aria/` and restarted `karma-regent.service` + `julian-cortex.service` successfully (`active`, `active`).
  - Live proof: remote file inspection now shows `host.docker.internal:11434` in both deployed files.
  - Live proof: direct qwen probe after restart returned `NEXUS_OK` from `http://100.75.109.92:11434/api/chat` in `14.76s`.
  - Decision: keep `qwen3.5:4b` as the current K2 local floor. `gemma4:e4b` remains installed for future reevaluation, but it is not the current operational choice.
