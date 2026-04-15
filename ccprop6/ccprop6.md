# ccprop6 -- Foundation-First Harness Plan

**Version:** 1.0.0 | **Date:** 2026-04-09 | **Status:** PLAN (not implemented)
**Owner:** Colby (Sovereign) + Julian (CC Ascendant)
**Supersedes:** All prior plans for Tauri harness work (originally Electron). Does NOT supersede nexus.md as identity/architecture reference -- only its build order.

---

## Why the Old Plan Failed

nexus.md is a comprehensive architecture document with real infrastructure underneath. But it failed as a BUILD PLAN because:

1. It raced past its own gates (Phase D/F never passed, but 79 "HAVE" claimed)
2. It optimized before existence (AAAK compression before basic features)
3. It declared sensors as shipped systems (all watchers produce noise, not value)
4. It never produced a Sovereign-verified product moment in 163 sessions
5. It accumulated contradictions without reconciliation (merged workspace "exists" AND is a "shell")

ccprop6 is smaller, harsher, more binary. Foundation first. One phase at a time. No advancement without proof.

---

## PHASE 0: RUNTIME TRUTH

### Objective
A single endpoint returns live ground truth about what's actually running. No more reading STATE.md or MEMORY.md for system state.

### Exact Scope
- Add `GET /v1/runtime/truth` to hub-bridge proxy.js
- Queries: Docker container health, model config, K2 reachability, ledger count, FalkorDB node count, last batch_ingest timestamp
- Returns JSON. Not cached. Not from docs.

### Dependencies
- hub-bridge running on vault-neo (EXISTS)
- Docker socket access from hub-bridge container (VERIFY)

### Anti-Goals
- NOT a dashboard UI. JSON endpoint only.
- NOT a replacement for /health (which stays as a simple liveness check).
- NOT recursive -- does not check watcher health or Vesper state.

### Concrete Deliverables
1. `GET /v1/runtime/truth` returns 200 with `{hub_bridge, falkordb, karma_server, vault_search, k2, model_default, model_deep, ledger_count, falkordb_nodes, last_batch_ingest, timestamp}`
2. Each service field: `{status: "up"|"down"|"unknown", container_id?, uptime_s?}`

### Proof Requirements
```bash
curl -s -H "Authorization: Bearer $TOKEN" https://hub.arknexus.net/v1/runtime/truth | python3 -m json.tool
```
Must return JSON with all fields populated. No "undefined" or "null" for running services.

### Break Tests
- What if FalkorDB is down? -> returns `{status: "down"}` for falkordb, not 500.
- What if K2 is unreachable? -> returns `{status: "unknown"}` for k2, not timeout.
- What if Docker socket isn't mounted? -> returns error explaining the gap.

### Failure Modes
- Docker socket not available in hub-bridge container -> needs volume mount in compose.hub.yml
- K2 health check timeout blocks response -> use Promise.race with 3s timeout

### Exit Criteria
- `curl /v1/runtime/truth` returns accurate, live data for all services
- Data matches `docker ps` output on vault-neo
- Sovereign confirms: "I can see what's running"

### Rollback Criteria
- If endpoint causes hub-bridge instability, revert proxy.js to prior version

### NOT Allowed to Start Yet
- No dashboard UI. No frontend work. No Tauri work.

---

## PHASE 1: SESSION CONTINUITY

### Objective
A conversation survives browser refresh, API errors, and server restart. The foundational requirement that was broken (STATE.md L572-584).

### Exact Scope
- Server-side conversation store in hub-bridge (in-memory Map + periodic disk flush)
- Keyed by session_id (UUID from client localStorage)
- `POST /v1/session/{id}/save` -- save a turn
- `GET /v1/session/{id}/history` -- retrieve turns
- Client (unified.html) calls save after each turn, calls history on page load

### Dependencies
- Phase 0 complete (runtime truth endpoint confirms hub-bridge healthy)
- unified.html exists (it does)
- session_id already exists in client (karmaSessionId -- verified in nexus.md L581)

### Anti-Goals
- NOT a database. In-memory + JSONL disk backup.
- NOT cross-device sync.
- NOT offline mode.
- NOT versioned conversation threads.

### Concrete Deliverables
1. Server: `POST /v1/session/{id}/save` accepts `{role, content, turn_id}`, returns 201
2. Server: `GET /v1/session/{id}/history` returns `[{role, content, turn_id, timestamp}]` (max 100)
3. Server: Sessions pruned after 24h inactivity
4. Client: On page load, if karmaSessionId exists, fetch history and rebuild conversation
5. Client: After each assistant response, save both user + assistant turns

### Proof Requirements
1. Send a message in browser. Refresh page. Conversation visible.
2. Send a message. Kill hub-bridge container. Restart. Refresh. Conversation visible (from disk backup).
3. Send a message in browser. Open Tauri (nexus.exe). Same session_id. Same conversation. (requires Phase 3 harness)

### Break Tests
- What if session_id changes? -> New conversation. Old one still on server if within TTL.
- What if disk write fails? -> In-memory still works. Log warning. Data survives until restart.
- What if 10,000 sessions accumulate? -> Prune sessions older than 24h on 5-minute cycle.

### Failure Modes
- Memory exhaustion from unbounded sessions -> Fixed by 24h TTL + 100-turn cap
- Disk backup race condition -> Debounce writes to 5s intervals
- session_id collision (UUID) -> Statistically impossible (2^122)

### Exit Criteria
- Conversation survives browser refresh (Sovereign tests live)
- Conversation survives hub-bridge restart
- Sovereign confirms: "she remembers what I just said"

### Rollback Criteria
- If session store causes hub-bridge OOM or latency > 5s on /v1/chat, remove and revert

### NOT Allowed to Start Yet
- No Tauri work. No settings. No slash commands. No voice.

---

## PHASE 2: VERIFIED CHAT CONTRACT

### Objective
Sovereign sends a message, gets a response with identity + memory + tools. Live verification, not doc claims.

### Exact Scope
- Verify hub.arknexus.net chat actually works end-to-end
- Verify Karma persona loads (not "I'm Claude" or blank)
- Verify memory context appears (not cold start)
- Verify tool access works (at least graph_query)
- Fix anything that doesn't pass
- This is the Phase D from nexus.md that was never done

### Dependencies
- Phase 1 complete (session continuity proven)
- hub-bridge + karma-server + FalkorDB running (verify via Phase 0 endpoint)

### Anti-Goals
- NOT adding new features. Only verifying existing ones work.
- NOT fixing Vesper, Kiki, or any watcher.
- NOT building new tools.

### Concrete Deliverables
1. Sovereign opens hub.arknexus.net in browser
2. Sends "Who are you?" -- response includes Karma identity, not generic Claude
3. Sends "What did we talk about last?" -- response includes context from memory, not "I don't have memory of prior conversations"
4. Sends message requiring tool use (deep mode) -- tool_calls appear in response
5. Any failure: fix root cause, re-test

### Proof Requirements
- Screenshot or transcript of each test
- curl commands with actual responses saved to ccprop6/proof/

### Break Tests
- What if system prompt doesn't load? -> "I'm Claude" response. Fix: verify KARMA_IDENTITY_PROMPT env var.
- What if memory context is empty? -> Cold start response. Fix: verify _memoryMdCache, FAISS, FalkorDB all healthy.
- What if tool calls fail? -> 500 or empty response. Fix: verify hooks.py ALLOWED_TOOLS, karma-server healthy.

### Exit Criteria
- Sovereign says: "She works. She knows who she is. She remembers things."
- This IS Phase F from nexus.md.

### NOT Allowed to Start Yet
- No Tauri. No new UI. No new features.

---

## PHASE 3: MINIMAL ELECTRON HARNESS

### Objective
A Tauri app (nexus.exe) that surfaces hub.arknexus.net with a secure shell, health indicator, shared session, and crash recovery. Nothing more. (Updated 2026-04-15: was Electron, now Tauri per Sovereign directive.)

### Exact Scope
- nexus-tauri/src-tauri/: Tauri Rust backend + tauri.conf.json
- nexus-tauri/dist/: Next.js frontend static export loaded by Tauri WebView
- Status bar or title bar showing health (green/yellow/red from /v1/runtime/truth)
- Crash recovery: on WebView crash -> reload
- Session sharing: Tauri WebView loads hub.arknexus.net -> same localStorage -> same session_id

### Dependencies
- Phase 2 complete (chat contract verified)
- Phase 1 complete (session continuity working)
- Phase 0 complete (health endpoint exists)

### Anti-Goals
- NOT a code editor
- NOT a settings panel
- NOT a git interface
- NOT a file browser
- NOT voice input
- NOT any feature that hub.arknexus.net doesn't already have
- The harness WRAPS the web app. It does not REPLACE it.

### Concrete Deliverables
1. `nexus-tauri/src-tauri/target/release/nexus.exe` opens showing hub.arknexus.net
2. Title bar shows Karma health status
3. Session persists across Tauri restart (same localStorage domain)
4. WebView crash -> auto-reload within 5s
5. tauri.conf.json: minimal allowlist, no dangerous APIs exposed
6. Rust backend sandboxes all WebView access

### Proof Requirements
```bash
cd nexus-tauri && cargo tauri build --release
./src-tauri/target/release/nexus.exe
```
Window opens. Health indicator visible. Chat works. Close and reopen -- conversation persists.

### Break Tests
- What if hub.arknexus.net is down? -> Show error page with retry button, not blank screen.
- What if tauri.conf.json has dangerous allowlist entries? -> Security audit fails.
- What if Tauri WebView crashes? -> Rust backend catches and reloads.
- What if session_id diverges between browser and Tauri? -> Same domain = same localStorage. Test: login in browser, open Tauri, verify same session.

### Exit Criteria
- Sovereign opens Tauri app (nexus.exe), chats with Karma, closes, reopens, conversation persists
- Sovereign opens browser, sees same conversation
- Health indicator is green when services are up, red when down

### NOT Allowed to Start Yet
- No plugins. No extensions. No voice. No MCP tools. No advanced features.

---

## PHASE 4: ANTI-DRIFT CONTROLS

### Objective
Prevent the foundation from being expanded before it's proven, and prevent documentation from claiming what runtime doesn't deliver.

### Exact Scope
- Pre-commit hook: any file outside ccprop6/ or harness/ requires Phase 3 gate passed
- Session-start check: `/v1/runtime/truth` called and logged before any work
- Gate status file: `ccprop6/GATES.json` with PASS/FAIL for each phase
- No new features allowed until all 4 foundation phases PASS

### Dependencies
- Phase 3 complete

### Anti-Goals
- NOT a watcher (those failed)
- NOT autonomous enforcement (human-checked gates)
- NOT blocking emergency fixes

### Concrete Deliverables
1. `ccprop6/GATES.json`: `{phase_0: "PASS|FAIL", phase_1: "PASS|FAIL", phase_2: "PASS|FAIL", phase_3: "PASS|FAIL"}`
2. Gate status checked at session start by resurrect skill
3. If any foundation gate is FAIL, no expansion work allowed

### Exit Criteria
- All 4 foundation gates are PASS
- Sovereign reviews and confirms
- ccprop6 foundation is declared stable

---

## INTENTIONALLY DEFERRED (not built in ccprop6)

| Feature | Why Deferred |
|---------|--------------|
| Slash commands (40+) | UI expansion. Foundation first. |
| Settings panel | UI expansion. Foundation first. |
| Git/diff viewer | UI expansion. Foundation first. |
| Agent panel | UI expansion. Foundation first. |
| Plugin system | Growth layer. Foundation first. |
| Voice input | Transport layer. Foundation first. |
| Self-edit pipeline | Growth layer. Foundation first. |
| Autonomous gap closure | Requires proven executor. Foundation first. |
| Watcher redesign | Demoted to optional diagnostics. Foundation first. |
| Chrome/VS Code extensions | Transport layer. Foundation first. |
| K2 local model routing | Optimization. Foundation first. |
| Fine-tuning (DPO) | Growth layer. Foundation first. |
| Karpathy loop | Highest leverage but requires proven foundation. |
| MemPalace advanced features | Optimization. AAAK compression already deployed. |
