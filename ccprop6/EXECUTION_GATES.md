# EXECUTION GATES: Binary Pass/Fail for Every Phase

No fuzzy "mostly done." PASS or FAIL only.

---

## Phase 0: Runtime Truth

| Gate | Test Command | Expected | PASS/FAIL |
|------|-------------|----------|-----------|
| G0-1 | `curl -s -H "Auth: Bearer $TOKEN" https://hub.arknexus.net/v1/runtime/truth \| jq .status` | Not "undefined", not 404, not 500 | PENDING |
| G0-2 | Stop FalkorDB -> query /v1/runtime/truth -> check falkordb.status | "down" | PENDING |
| G0-3 | Query /v1/runtime/truth -> compare model_default to hub.env | Match | PENDING |

**Phase 0 PASS = G0-1 AND G0-2 AND G0-3**

---

## Phase 1: Session Continuity

| Gate | Test Command | Expected | PASS/FAIL |
|------|-------------|----------|-----------|
| G1-1 | Send message in browser -> refresh -> conversation visible | Conversation rebuilt | PENDING |
| G1-2 | Send message -> restart hub-bridge -> refresh -> conversation visible | Conversation from disk | PENDING |
| G1-3 | `GET /v1/session/{id}/history` returns array of turns | Non-empty JSON array | PENDING |
| G1-4 | karmaSessionId in localStorage survives refresh | Same UUID before and after | PENDING |

**Phase 1 PASS = G1-1 AND G1-2 AND G1-3 AND G1-4**

---

## Phase 2: Verified Chat Contract

| Gate | Test Command | Expected | PASS/FAIL |
|------|-------------|----------|-----------|
| G2-1 | Send "Who are you?" at hub.arknexus.net | Response includes Karma identity, not "I'm Claude" | PENDING |
| G2-2 | Send "What did we talk about last?" | Response includes memory context, not "I don't have memory" | PENDING |
| G2-3 | Send deep-mode message requiring tools | tool_calls appear in response payload | PENDING |
| G2-4 | Sovereign confirms: "She works" | Explicit verbal/written confirmation from Colby | PENDING |

**Phase 2 PASS = G2-1 AND G2-2 AND G2-3 AND G2-4**

---

## Phase 3: Minimal Tauri Harness (updated 2026-04-15 — was Electron)

| Gate | Test Command | Expected | PASS/FAIL |
|------|-------------|----------|-----------|
| G3-1 | Run `nexus-tauri/src-tauri/target/release/nexus.exe` | Tauri window opens with hub.arknexus.net | PENDING |
| G3-2 | Title bar shows health status | [OK] or [OFFLINE] visible | PENDING |
| G3-3 | Force renderer crash -> verify auto-reload | Window reloads within 5s | PENDING |
| G3-4 | Chat in Tauri -> close -> reopen -> conversation persists | Session continuity works in Tauri | PENDING |
| G3-5 | Inspect tauri.conf.json security settings | allowlist minimal, no dangerous APIs exposed | PENDING |

**Phase 3 PASS = G3-1 AND G3-2 AND G3-3 AND G3-4 AND G3-5**

---

## Phase 4: Anti-Drift Controls

| Gate | Test Command | Expected | PASS/FAIL |
|------|-------------|----------|-----------|
| G4-1 | GATES.json exists with Phase 0-3 statuses | File exists, all phases have PASS/FAIL/PENDING | PENDING |
| G4-2 | All foundation phases show PASS in GATES.json | No FAIL or PENDING | PENDING |
| G4-3 | Sovereign reviews and approves | Written confirmation | PENDING |

**Phase 4 PASS = G4-1 AND G4-2 AND G4-3**

---

## Foundation PASS = Phase 0 PASS AND Phase 1 PASS AND Phase 2 PASS AND Phase 3 PASS AND Phase 4 PASS

Only after Foundation PASS can expansion work (futurework.md) begin.
