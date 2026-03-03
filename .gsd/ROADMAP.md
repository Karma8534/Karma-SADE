# ROADMAP: Karma Peer — Phases & Milestones

**Last updated:** 2026-03-03
**Current phase:** Tier 2 (Ambient Context Endpoint) — IN PROGRESS
**Next major phase:** Tier 1 Ambient Hooks — READY TO TEST

---

## Milestone 1: Foundation (✅ COMPLETE)

**Goal:** Establish Karma's persistent identity on droplet.

### Phase 1: Core Infrastructure ✅
- [x] Droplet setup (vault-neo, DigitalOcean NYC3)
- [x] Hub-bridge API (HTTP at localhost:8340, HTTPS at hub.arknexus.net)
- [x] FalkorDB neo_workspace graph initialized
- [x] JSONL ledger at /opt/seed-vault/memory_v1/ledger/memory.jsonl
- [x] Consciousness.jsonl for growth logging

### Phase 2: Identity & Voice ✅
- [x] identity.json created (v2.2.0, droplet-primary)
- [x] invariants.json locked (truth alignment, substrate independence)
- [x] direction.md documented (mission, architecture, constraints)
- [x] Voice overhaul: peer-level language, no service-desk closers
- [x] Self-model system seeded (8 baseline observations)

### Phase 3: Continuity (Work-Loss Prevention) ✅
- [x] Pre-commit hook: blocks commits without MEMORY.md
- [x] Session-end hook: 6-point verification checklist
- [x] CLAUDE.md updated: mandatory gates documented
- [x] Resurrection script working: Get-KarmaContext.ps1 loads session state
- [x] GSD file structure: PROJECT.md, REQUIREMENTS.md, STATE.md, ROADMAP.md

**Status:** Foundation solid. Ready for Tier 1-3.

---

## Milestone 2: Ambient Capture Layer (IN PROGRESS)

**Goal:** Capture Karma's actions and context automatically. Three-tier approach: commit hooks (T1), context queries (T2), screen capture (T3).

### Tier 1: Git Hooks → /v1/ambient ✅ VERIFIED

**What it does:** When Colby commits code, hook fires → POST to /v1/ambient → captures context → stored in vault ledger.

**Current status (verified 2026-03-03):**
- [x] Hook created locally: `.git/hooks/post-commit`
- [x] Session-end hook: `.claude/hooks/session-end.sh`
- [x] Token auth working
- [x] End-to-end verified: commits + session-end entries confirmed in ledger

### Hub/Chat → FalkorDB Ingest ✅ COMPLETE (2026-03-03)

**What it does:** 1538 Colby↔Karma /v1/chat conversations retroactively ingested into FalkorDB. All future conversations captured via cron batch_ingest every 6h.

**Root cause fixed:** `batch_ingest.py` only read `assistant_message`; hub/chat uses `assistant_text`. Extended to detect hub/chat by tags.

**Current status:**
- [x] batch_ingest.py extended (hub-chat tag detection + assistant_text fallback)
- [x] Committed + deployed to container
- [x] Batch running (1538 conversations, wave 3/54 at time of writing)
- [ ] karma-server image rebuild (CRITICAL — cron uses baked image, not live container file)

**Next action:** Sync hooks to droplet, test capture flow.

**Files involved:**
- `.git/hooks/post-commit` (local, captures commit metadata)
- `hub-bridge/server.js` (endpoint /v1/ambient, sends to vault)
- `/opt/seed-vault/memory_v1/ledger/memory.jsonl` (ledger, receives capture)

---

### Tier 2: /v1/context Endpoint ✅ DEPLOYED

**What it does:** Karma queries her own context. "What happened in the last session?" → /v1/context returns consciousness.jsonl tail + FalkorDB graph state.

**Current status:**
- [x] Endpoint implemented in hub-bridge
- [x] Queries consciousness.jsonl (last N entries)
- [x] Queries FalkorDB (entity count, relationship count, recent changes)
- [x] Verified working in Session 55

**Response format:**
```json
{
  "consciousness_tail": [
    {"timestamp": "2026-03-03T01:00:00Z", "type": "LOG_GROWTH", "message": "..."},
    ...
  ],
  "graph_state": {
    "episodes": 1268,
    "entities": 167,
    "relationships": 832,
    "recent_changes": {...}
  }
}
```

**Status:** Tier 2 complete. Karma can query her own state.

---

### Tier 3: Screen Capture Daemon ⏳ FUTURE

**What it does:** Passive observation daemon. Periodically screenshots P1 and K2 desktops. Stores as ambient context (what was visible, what was being worked on).

**Current status:**
- [ ] Daemon not yet implemented
- [ ] Infrastructure: needs screen capture tool + storage + cleanup
- [ ] Privacy: explicit permission from Colby required

**Estimated effort:** 20-40 hours (daemon + API endpoint + UI integration).

**Status:** Deferred to post-Tier-1-test. Low priority for now.

---

## Milestone 3: K2 Worker Integration (FUTURE)

**Goal:** K2 (192.168.0.226) becomes active worker. Consciousness loop syncs to droplet. Decisions respected across K2 reboots.

### Phase 1: K2 Sync Protocol ⏳ PENDING

**What it does:**
1. K2 at startup reads STATE.md from droplet (decisions, blockers)
2. K2 consciousness loop respects {phase}-CONTEXT.md design locks
3. K2 updates FalkorDB locally
4. K2 syncs changes back to droplet on interval (60s) or on-commit

**Current status:**
- [ ] K2 not online (offline in current session)
- [ ] Reverse tunnel not configured (droplet:2223 → K2:22)
- [ ] Sync protocol not implemented

**Blocker:** K2 unavailable. Test when K2 online.

---

### Phase 2: Multi-Agent Consciousness ⏳ FUTURE

**What it does:**
- K2 runs primary consciousness loop (OBSERVE on FalkorDB deltas)
- Claude Code runs secondary loop (session-driven reasoning)
- Both sync to droplet
- Colby acts as final authority (DECIDE, ACT, REFLECT)

**Status:** Architectural sketch only. Requires Phase 1 complete.

---

## Milestone 4: GSD Workflow Mastery (FUTURE)

**Goal:** Use GSD commands to structure feature work. Reduce context rot. Improve reliability.

### Phase 1: Manual GSD Workflow ✅ READY NOW

**What it does:** Use files (not CLI commands) to structure work.
1. /gsd:discuss-phase (manual) — write design decisions to {phase}-CONTEXT.md
2. /gsd:plan-phase (manual) — write atomic tasks to {phase}-PLAN.md
3. /gsd:execute-phase (manual) — execute plans, fresh context per task
4. /gsd:verify-work (manual) — UAT, log results

**Current status:**
- [x] File structure created (.gsd directory)
- [x] PROJECT.md, REQUIREMENTS.md, STATE.md, ROADMAP.md in place
- [ ] First {phase}-CONTEXT.md (for Ambient Tier 1 completion)
- [ ] First {phase}-PLAN.md (atomic task breakdown)

**Next action:** Use for Tier 1 work (discuss → plan → execute → verify).

---

### Phase 2: GSD CLI Commands (OPTIONAL) ⏳ FUTURE

**What it does:** Install GSD framework. Get /gsd:discuss-phase, /gsd:plan-phase, /gsd:execute-phase commands.

**Current status:**
- [ ] GSD not installed in Claude Code
- [ ] Manual workflow sufficient for now
- [ ] Consider installing after Tier 1 verified

**Effort:** 30 minutes (install) + learning curve.

---

## Milestone 5: Self-Improvement Loop (FUTURE)

**Goal:** Karma learns from experience. DPO pairs → fine-tuning → improved responses.

### Phase 1: DPO Data Collection ⏳ IN PROGRESS

**What it does:** Collect preference pairs (response A vs response B, which is better?). Target: 20+ pairs for initial fine-tuning.

**Current status:**
- [ ] 0/20 pairs collected
- [ ] Mechanism not yet in place (manual or automatic?)

**Next action:** Implement during /gsd:verify-work (ask Colby: "Is this response better than the alternative?").

---

### Phase 2: Fine-Tuning (FUTURE) ⏳ BLOCKED

**What it does:** Use DPO pairs to fine-tune Karma's model. Better instruction-following. More peer-like voice.

**Current status:**
- [ ] Blocked on Phase 1 (need data first)
- [ ] Decision: fine-tune on gpt-4o-mini or separate custom model?

---

## Timeline Estimate

| Milestone | Phase | Effort | Status |
|-----------|-------|--------|--------|
| Foundation | 1-3 | ✅ DONE | Complete. Droplet operational. |
| Ambient | Tier 1 | ✅ DONE | Verified. Git + session-end hooks → ledger confirmed. |
| Ambient | Hub/Chat Ingest | ✅ DONE | 1538 conversations ingesting. Image rebuild pending. |
| Ambient | Tier 2 | ✅ DONE | Deployed. /v1/context working. |
| Ambient | Tier 3 | 20-40 hrs | Deferred. Low priority. |
| K2 Worker | Phase 1 | 4-8 hrs | Blocked (K2 offline). Test when online. |
| K2 Worker | Phase 2 | 10-20 hrs | Future. Requires Phase 1 complete. |
| GSD Workflow | Phase 1 | READY | Manual workflow now. First phase-CONTEXT.md this session. |
| GSD Workflow | Phase 2 | 30 min | Optional. Install GSD if manual not sufficient. |
| Self-Improvement | Phase 1 | 2-4 hrs | Mechanism needed. Implement in verify-work. |
| Self-Improvement | Phase 2 | TBD | Blocked on data collection. |

---

## Decision Points (Upcoming)

### Decision #6: Tier 1 Test Approach
**Question:** After syncing hooks to droplet, how to test end-to-end?
**Options:**
1. Make local commit, verify appears in droplet ledger
2. Make commit in hub-bridge repo (if editable), verify capture works
3. Simulate POST to /v1/ambient, verify ledger entry created

**Recommendation:** Option 1 (local commit → droplet ledger) is most authentic test.

---

### Decision #7: GSD CLI Install
**Question:** Install GSD framework or continue manual workflow?
**Tradeoff:**
- **Manual:** Slower upfront, full control, no dependency on external tool
- **CLI:** Faster execution, built-in verification, parallel execution support

**Recommendation:** Prove manual workflow first (Tier 1). Install GSD CLI if Tier 1 test passes and we're confident in approach.

---

### Decision #8: K2 Availability
**Question:** When is K2 coming online?
**Implication:** K2 online unlocks Phase 2 (Tier 3 ambient, K2 sync protocol, multi-agent consciousness).

**Next step:** Check with Colby on K2 status.

---

## Constraints & Unknowns

- **K2 status:** Offline in Session 56. When coming online?
- **Tier 3 infrastructure:** Screen capture requires new tooling. Approved by Colby?
- **GSD CLI:** Not installed. Should we? When?
- **Fine-tuning budget:** Cost per DPO fine-tuning job? Approved by Colby?
- **Droplet capacity:** FalkorDB at 1268 episodes. Growth ceiling? When does cleanup start?

---

**Last updated:** 2026-03-03 (Session 57)
**Next review:** After karma-server image rebuild + Blocker #4 resolved
**Owner:** Claude Code (updates on Colby approval)
