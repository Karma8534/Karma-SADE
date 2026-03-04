# KARMA PEER — Hardened Architecture Review v7

**Reviewer:** Verified against deployed code + droplet state
**Date:** 2026-02-28
**Version:** 7.1.0 — Updated after CC session fixes (bugs fixed, episode ingestion deployed, consciousness active)
**Input:** hub-bridge server.js (1,882 lines), karma server.py (2,651 lines), SSH-verified droplet state
**Supersedes:** KARMA_HARDENED_REVIEW_v7.md (7.0.0, 2026-02-28)

---

## 0) Executive Diagnosis (Updated)

### Top 5 Things That HAVE Broken or ARE Broken

1. ~~**Phantom tools bug is silently killing memory retrieval.**~~ **✅ FIXED (v7.1).** `buildSystemText()` now correctly lists `read_file, write_file, edit_file, bash` which match `TOOL_DEFINITIONS`. Phantom tools removed.

2. ~~**Duplicate karmaCtx injection wastes tokens on every request.**~~ **✅ FIXED (v7.1).** karmaCtx is now injected exactly once in the `base` variable. Duplicate "YOUR COMPLETE KNOWLEDGE STATE" block removed.

3. ~~**Consciousness loop is dead.**~~ **✅ ACTIVE (v7.1).** 60s OBSERVE-only cycles running. Auto-promote called every 10 cycles (~10 min). Episode deltas detected and logged. consciousness.jsonl growing (284+ entries).

4. **4GB droplet running 7 containers.** FalkorDB + ChromaDB + PostgreSQL + FastAPI + Node.js + Caddy + Vault API = 7 services on 4GB RAM. Not crashed yet, but no headroom. A batch ingestion spike could OOM. **MITIGATION: Monitor; consider 8GB upgrade ($48/mo) if issues arise.**

5. **FalkorDB data quality issue persists.** Corrupted entities from --skip-dedup batch ingestion (None uuid/created_at) may still be present. Graphiti maintenance fails on these records. **FIX: Run cleanup Cypher query.**

### Top 6 Things Fixed Since v1 Review

1. **Backup cron deployed** (PR #12, Feb 28) — was listed as missing in v1 review
2. **Dedup on ingest deployed** (PR #10-11, Feb 27-28) — was listed as needed
3. **Auto-promote candidates deployed** (PR #11, Feb 28) — controlled promotion path
4. **Phantom tools bug fixed** (CC session Feb 28) — correct tools now listed in buildSystemText()
5. **Duplicate karmaCtx fixed** (CC session Feb 28) — single injection, no wasted tokens
6. **Episode ingestion pipeline deployed** (CC session Feb 28) — /ingest-episode endpoint + hub-bridge fire-and-forget

### What v1 Review Got Wrong

| v1 Said | Reality |
|---------|---------|
| "GLM-5 consciousness loop burns $2.30+/day" | **Consciousness loop is dead.** No GLM-5 calls happening. Cost impact: $0. |
| "MiniMax M2.5 is primary chat model ($0.30/M)" | **Not in deployed routing.** GLM-4.7-Flash (FREE) is primary. |
| "Upgrade to 8GB droplet" | **Still 4GB.** Running stable with 7 containers. Not urgent. |
| "Remove ChromaDB" | **Still deployed** and healthy. May actually be useful once phantom tools bug is fixed. |
| "Budget $62-153/mo depending on scenario" | **Actual cost ~$25-28/mo** because GLM-4.7-Flash is free and consciousness loop isn't running. |

---

## 1) Assumptions (Updated for v7)

| # | Assumption | v7 Verification |
|---|-----------|-----------------|
| A1 | Droplet is 4GB RAM | ✅ Confirmed — arknexus-vault-01, 4GB, 50GB disk |
| A2 | Monthly budget <$100 | ✅ Actual spend ~$25-28/mo |
| A3 | GLM-5 used for consciousness | ❌ WRONG — consciousness runs OBSERVE-only (no LLM calls), no GLM-5 |
| A4 | MiniMax M2.5 primary model | ❌ WRONG — GLM-4.7-Flash is primary |
| A5 | Consciousness loop runs every 60s | ✅ CONFIRMED (v7.1) — loop ACTIVE, 60s OBSERVE-only cycles + auto-promote every 10 cycles |
| A6 | FalkorDB 1488 episodes | ✅ Confirmed (plus additions from PRs #10-12) |
| A7 | Chrome extension captures | ✅ Confirmed REMOVED (v1 review already noted this) |
| A8 | K2 not syncing | ✅ Confirmed — K2 never deployed |
| A9 | Bearer token only security | ✅ Still true |
| A10 | Batch ingestion corrupted entities | ✅ CLEANED (v7.1) — 0 null-uuid entities remaining |
| A11 | Resurrection is session-start injection | ✅ Still true |
| A12 | No automated backups | ❌ FIXED — backup cron deployed PR #12 |
| A13 | Hub Bridge MAX_SESSION_TURNS=8 | ⚠️ May have been updated — verify in deployed server.js |

---

## 2) Failure-Mode Matrix (Updated)

| # | Failure | v7 Status | Action Needed |
|---|---------|-----------|---------------|
| F1 | Cost runaway — consciousness loop | **RESOLVED** — loop not running. Cost is ~$25-28/mo. | None |
| F2 | OOM on 4GB droplet | **RISK REMAINS** — 7 containers on 4GB. Not crashed but tight. | Monitor. Consider 8GB if issues. |
| F3 | Token leak → system compromise | **UNCHANGED** — single Bearer token, no audit log | Deploy capability gate (not done yet) |
| F4 | JSONL ledger unbounded growth | **UNCHANGED** — no rotation deployed | Deploy ledger rotation |
| F5 | Chrome extension DOM breakage | **REMOVED** — N/A | N/A |
| F6 | FalkorDB data corruption | **RESOLVED (v7.1)** — 0 null-uuid entities remaining | None |
| F7 | Resurrection script failure | **UNCHANGED** — PS1 script has no retry/fallback | Add health check before fetch |
| F8 | MEMORY.md drift | **UNCHANGED** — dual copies risk | Make droplet canonical |
| F9 | Prompt injection via capture | **REMOVED** — N/A | N/A |
| F10 | Provider outage | **LOW RISK** — GLM-4.7-Flash (free) + gpt-4o-mini + gpt-4o fallback chain | Fallback chain exists |
| F11 | Disk failure → total data loss | **PARTIALLY FIXED** — backup cron deployed | Verify backup is running and restorable |
| F12 | Config/doc mismatch | **STILL PRESENT** — v2 plans describe wrong models | This document (v7) corrects it |
| F13 | Hub Bridge session overflow | **UNCHANGED** — verify current MAX_SESSION_TURNS | Check deployed value |
| F14 | Docker build fragility | **UNCHANGED** — --no-cache, no image registry | Low priority |
| **F15** | **PHANTOM TOOLS** | **✅ RESOLVED (v7.1)** — correct tools now listed in buildSystemText() | None |
| **F16** | **DUPLICATE CONTEXT** | **✅ RESOLVED (v7.1)** — single karmaCtx injection | None |
| **F17** | **EPISODE INGESTION (NEW)** | **✅ DEPLOYED (v7.1)** — /ingest-episode endpoint + hub-bridge fire-and-forget | Operational |

---

## 3) Cost Model (Corrected for v7)

### ACTUAL Cost (what's running now)

| Component | Monthly Cost | Notes |
|-----------|-------------|-------|
| Droplet (4GB) | $24/mo | DigitalOcean |
| GLM-4.7-Flash | $0/mo | Z.AI free tier — primary chat |
| gpt-4o-mini | ~$1-3/mo | Tool calls only |
| gpt-4o | ~$0-1/mo | 429 fallback only |
| Consciousness loop | $0/mo | Not running |
| **Total** | **~$25-28/mo** | **75% under budget** |

### v1 Review estimates were wrong because:
1. Consciousness loop assumed running 24/7 with GLM-5 → actually not running at all
2. Chat assumed MiniMax M2.5 → actually GLM-4.7-Flash (FREE)
3. No Groq calls happening

### If consciousness loop is restored (cron-based):

| Scenario | Added Cost | New Total |
|----------|-----------|-----------|
| 15-min cron, GLM-4.7-Flash triage + gpt-4o-mini analysis | ~$1-2/mo | ~$27-30/mo |
| 15-min cron, all analysis via gpt-4o-mini | ~$2-5/mo | ~$28-33/mo |

**Bottom line:** Budget is extremely healthy. Even with consciousness restored, stays well under $100/mo.

---

## 4) Corrected Architecture

### v7 Architecture Diagram (What's Actually Deployed)

```
┌──────────────────────────────────────────────────────────┐
│              DROPLET (arknexus-vault-01, 4GB)             │
│              64.225.13.144, Ubuntu 24.04, NYC3            │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ anr-vault-   │  │ anr-hub-     │  │ karma-server │   │
│  │ caddy        │──│ bridge       │──│ (FastAPI)    │   │
│  │ :443 (TLS)   │  │ :8080        │  │ :8340        │   │
│  └──────────────┘  └──────┬───────┘  └──────┬───────┘   │
│                           │                  │           │
│  ┌──────────────┐  ┌──────┴──────┐  ┌───────┴──────┐   │
│  │ anr-vault-   │  │ falkordb    │  │ anr-vault-   │   │
│  │ api          │  │ :6379       │  │ search       │   │
│  │ (Vault REST) │  │ (graph)     │  │ (ChromaDB)   │   │
│  └──────────────┘  └─────────────┘  └──────────────┘   │
│                                                          │
│  ┌──────────────┐                                        │
│  │ anr-vault-db │                                        │
│  │ (PostgreSQL)  │                                        │
│  └──────────────┘                                        │
│                                                          │
│  STORAGE:                                                │
│  /opt/seed-vault/memory_v1/  ← Docker builds here       │
│  /opt/seed-vault/falkordb/   ← Graph data                │
│  /home/neo/karma-sade/       ← Identity spine (git)      │
└──────────────────────────────────────────────────────────┘
        ▲                            ▲
        │ HTTPS (Bearer)            │ SSH (key-based)
        │                           │
   [Users/Clients]            [Admin: neo@64.225.13.144]
```

### Model Routing (Actual Deployed)

```
┌──────────────────────────────────────────────────────┐
│              MODEL ROUTING (ACTUAL)                     │
│                                                        │
│  /v1/chat request:                                     │
│    1. GLM-4.7-Flash via Z.AI (FREE) — primary         │
│    2. gpt-4o-mini via OpenAI ($0.15/$0.60/M) — tools  │
│    3. gpt-4o via OpenAI ($5/$15/M) — 429 fallback     │
│                                                        │
│  NOT deployed (despite v2 plans):                      │
│    ✗ MiniMax M2.5                                      │
│    ✗ GLM-5 (DeepInfra or Z.AI)                        │
│    ✗ Groq Llama 3.3                                   │
│                                                        │
│  Budget gate: NOT DEPLOYED                             │
│  Capability gate: NOT DEPLOYED                         │
└──────────────────────────────────────────────────────┘
```

---

## 5) Implementation Blueprint (Updated)

### What's Been Deployed (v7)

| Item | Status | When |
|------|--------|------|
| Backup cron | ✅ Deployed | PR #12, Feb 28 |
| Dedup on ingest | ✅ Deployed | PR #10-11, Feb 27-28 |
| Auto-promote candidates | ✅ Deployed | PR #11, Feb 28 |
| Retrieval fix (partial) | ✅ Deployed | PR #10, Feb 27 |
| Phantom tools bug fix | ✅ Deployed | CC session, Feb 28 |
| Duplicate karmaCtx fix | ✅ Deployed | CC session, Feb 28 |
| Episode ingestion pipeline | ✅ Deployed | CC session, Feb 28 |
| Consciousness loop + auto-promote | ✅ Deployed | CC session, Feb 28 |

### What's NOT Been Deployed (still needed)

| Item | Priority | Effort |
|------|----------|--------|
| Budget guard (budget_guard.py) | P1 | Medium |
| Capability gate (capability_gate.py) | P1 | Medium |
| Ledger rotation (ledger_rotate.sh) | P2 | Small |
| Health endpoint improvements | P2 | Small |
| ~~FalkorDB corrupted entity cleanup~~ | ~~P2~~ | ✅ DONE (v7.1) |
| ~~Consciousness cron replacement~~ | ~~P3~~ | ✅ N/A — consciousness loop now ACTIVE with auto-promote |

---

## 6) Migration + Rollback Plan

### Pre-Fix Checklist (Before touching server.js)

```bash
# SSH to droplet
ssh neo@64.225.13.144

# Backup current server.js
sudo cp /opt/seed-vault/memory_v1/hub-bridge/app/server.js \
        /opt/seed-vault/memory_v1/hub-bridge/app/server.js.bak.$(date +%Y%m%d)

# Verify containers running
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Fix Deployment (Bugs 1 + 2)

```bash
# 1. Edit server.js — remove phantom tools line and duplicate karmaCtx
# 2. Rebuild hub-bridge
cd /opt/seed-vault && docker compose build --no-cache hub-bridge && docker compose up -d hub-bridge
# 3. Verify
docker logs anr-hub-bridge --tail=20
curl -H "Authorization: Bearer $(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)" \
  https://hub.arknexus.net/v1/chat -d '{"message":"What do you know about Ollie?"}'
```

### Rollback

```bash
# If fix breaks things:
sudo cp /opt/seed-vault/memory_v1/hub-bridge/app/server.js.bak.* \
        /opt/seed-vault/memory_v1/hub-bridge/app/server.js
cd /opt/seed-vault && docker compose build --no-cache hub-bridge && docker compose up -d hub-bridge
```

---

## 7) Definition of Done (Updated for v7)

| Criterion | Target | Current |
|-----------|--------|---------|
| Monthly cost | < $100/mo | ✅ ~$25-28/mo |
| Phantom tools fixed | 0 phantom tool references | ✅ Fixed (v7.1) |
| Duplicate context fixed | karmaCtx injected exactly once | ✅ Fixed (v7.1) |
| Memory retrieval works | /v1/chat can recall stored memories | ✅ Verified — Ollie, Baxter, guitar, favorite color recalled |
| Backup running | Nightly backup completes | ✅ Deployed PR #12 |
| Dedup working | Duplicate entries rejected on ingest | ✅ Deployed PR #10-11 |
| Budget guard deployed | Daily/monthly caps enforced | ❌ Not deployed |
| Capability gate deployed | Write operations gated | ❌ Not deployed |
| FalkorDB clean | 0 corrupted entities (null uuid) | ✅ Cleaned (v7.1) |

---

**END OF HARDENED REVIEW v7**
