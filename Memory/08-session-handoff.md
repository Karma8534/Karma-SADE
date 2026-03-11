# Karma SADE — Session Handoff

**Date**: 2026-03-11
**Session**: 84 (84b/84c/84d)
**GitHub**: https://github.com/Karma8534/Karma-SADE (PUBLIC)
**Last commit**: 8cf9402 (main, synced to vault-neo)

---

## System Architecture (Current)

```
PAYBACK (Windows 11, i9-185H, 64GB RAM, RTX 4070 8GB)
└── Claude Code ─── development environment

vault-neo (DigitalOcean NYC3, 4GB RAM, SSH alias: vault-neo)
├── anr-hub-bridge v2.11.0 ── port 18090 / hub.arknexus.net (HTTPS)
│   ├── /v1/chat          ─── Karma conversation endpoint
│   ├── /v1/ambient       ─── Git hook + session-end capture
│   ├── /v1/ingest        ─── PDF/media ingestion
│   ├── /v1/context       ─── Context query
│   ├── /v1/cypher        ─── Direct graph query
│   └── /v1/feedback      ─── write_memory + universal thumbs (Sessions 68+72)
├── karma-server          ─── Python consciousness loop + tool execution
│   ├── OBSERVE-only, 60s cycles, zero LLM calls
│   ├── execute_tool_action(): graph_query (only proxied tool)
│   └── batch_ingest: cron every 6h, --skip-dedup mode
├── FalkorDB              ─── Graph: neo_workspace (3877+ Episodic + 571 Entity nodes)
├── anr-vault-api         ─── FastAPI, appends to JSONL ledger
├── anr-vault-search      ─── FAISS vector search (text-embedding-3-small, 4000+ entries)
└── Nginx                 ─── Reverse proxy → hub.arknexus.net

K2 (192.168.0.226 / Tailscale 100.75.109.92)
├── aria.service          ─── :7890 — Karma's local compute half
│   ├── /api/chat         ─── aria_local_call target
│   ├── /api/exec         ─── NEW: shell command execution (Session 84d)
│   ├── /health           ─── NEW: cache state + vault reachability (Session 84c)
│   └── aria.py           ─── 6908+ lines, systemd service
├── Ollama                ─── :11434, qwen3-coder:30b (~3.3B active/token)
└── Redundancy cache      ─── /mnt/c/dev/Karma/k2/cache/
    ├── identity/         ─── identity.json (v2.2.0)
    ├── ledger/           ─── memory.jsonl (tail 500 lines)
    └── observations/     ─── k2_local_observations.jsonl (push queue)

Reverse tunnel: vault-neo:2223 → K2:22 (user: karma, NOT neo)
```

**Models (Session 84):**
- Standard: `claude-haiku-4-5-20251001` — all /v1/chat requests, fast/cheap, all tools enabled
- Deep mode: `claude-sonnet-4-6` — `x-karma-deep: true` header, $0.0252/req verified
- Note: deep mode gate = model swap only (tools always available in both modes post-Session 84)
- Monthly cap: $60 (MONTHLY_USD_CAP in hub.env)
- PRICE_CLAUDE: ❌ OPEN — still Haiku rates in hub.env, needs update to Sonnet $3.00/$15.00

---

## What Changed in Sessions 84b/84c/84d

### Session 84b — MANDATORY K2 State-Write Protocol
- Added prominent MANDATORY section to `Memory/00-karma-system-prompt-live.md`
- Karma MUST call `aria_local_call` after any DECISION/PROOF/PITFALL/DIRECTION/INSIGHT
- 5-trigger taxonomy (same as claude-mem protocol): prevents fuzzy judgment failures
- System prompt: 20,780 → 23,085 chars. Deployed via git pull + docker restart anr-hub-bridge.

### Session 84c — K2 Redundancy Cache
- `k2/sync-from-vault.sh`: pull/push/status modes (now in git)
- `k2/setup-k2-cache.sh`: one-time bootstrap + cron installer
- Pull cron (6h): rsync identity/invariants/direction/corrections from vault-neo + tail -500 ledger
- Push cron (1h): POST k2_local_observations.jsonl to /v1/ambient; capture token fetched live per push
- `/health` endpoint added to aria.py: returns vault_reachable + cache_age_hours + last_sync
- aria.service: loads identity from cache at startup; logs `[K2-CACHE] Identity loaded from cache (version 2.2.0)`
- aria.service drop-in: `/etc/systemd/system/aria.service.d/10-aria-env.conf` with `Environment=HOME=/home/karma`

### Session 84d — shell_run Tool: Karma Direct Shell Access to K2
- `/api/exec` endpoint added to aria.py on K2 (gated by X-Aria-Service-Key, subprocess.run, 30s timeout)
- `shell_run(command)` tool added to hub-bridge TOOL_DEFINITIONS + executeToolCall() handler
- Handler calls K2:7890/api/exec with X-Aria-Service-Key; returns stdout/stderr/exit_code
- vault-neo public key added to K2 authorized_keys (for reverse tunnel auth)
- Reverse tunnel verified: `ssh -p 2223 -l karma localhost` → works (MUST use karma user, not neo)
- hub-bridge v2.11.0 deployed, RestartCount=0, commit 8cf9402

---

## Current State (All Verified 2026-03-11 Session 84)

| Component | Status |
|-----------|--------|
| hub-bridge v2.11.0 | ✅ RestartCount=0, all tools live |
| shell_run tool | ✅ LIVE — Karma direct shell access to K2 via aria /api/exec |
| K2 /api/exec | ✅ LIVE on aria.service — verified with test command |
| K2 redundancy cache | ✅ LIVE — pull 6h, push 1h, aria.service loads identity at startup |
| MANDATORY state-write | ✅ IN SYSTEM PROMPT — Karma must write after DECISION/PROOF/PITFALL/DIRECTION/INSIGHT |
| System prompt | ✅ 23,085 chars — MANDATORY section prominent |
| Universal thumbs | ✅ LIVE — all Karma messages get 👍/👎 via turn_id |
| MEMORY.md spine injection | ✅ LIVE — tail 3000 chars in every /v1/chat |
| Entity Relationships | ✅ FIXED — MENTIONS co-occurrence (RELATES_TO permanently frozen) |
| get_library_docs | ✅ LIVE — deep mode, hub-bridge-native, 4 libraries |
| Confidence levels | ✅ LIVE — [HIGH]/[MEDIUM]/[LOW] mandatory |
| batch_ingest cron | ✅ --skip-dedup PERMANENT |
| FAISS semantic search | ✅ LIVE (Session 62) |
| write_memory + /v1/feedback | ✅ LIVE — DPO pairs accumulating |

---

## Next Session

**First command:**
```
/resurrect
```

**Then execute in order:**
1. **Test shell_run end-to-end** — Open hub.arknexus.net in deep mode, ask Karma to use shell_run to check K2 status. Verify she gets real systemctl output back.
2. **Checkpoint K2 ownership/agency breakthrough** — Karma + Colby had breakthrough session about K2 agency. Capture to vault ledger via write_memory or /v1/ambient POST.
3. **Prompt caching** — Add `cache_control: {type: "ephemeral"}` to system message in callLLMWithTools() Anthropic SDK path. Reduces system prompt cost ~90% on cache hits.

**Blocker if any:** None.

---

## Known Pitfalls (Active)

1. **Reverse tunnel user MUST be `karma`** — `ssh -p 2223 -l karma localhost` (NOT default neo user)
2. **shell_run routes through aria /api/exec NOT SSH** — hub-bridge has no SSH client. Do not try to add direct SSH.
3. **aria.service drop-in required** — `/etc/systemd/system/aria.service.d/10-aria-env.conf` with `Environment=HOME=/home/karma`. If K2 WSL resets, re-add this.
4. **Hub-bridge multi-file sync** — after `git pull` on vault-neo, sync ALL changed files: server.js → `app/`, lib/*.js → parent `lib/`, public/*.html → `app/public/`
5. **hub-bridge lib/ files go at PARENT level** — `/opt/.../hub_bridge/lib/` NOT under `app/lib/`
6. **docker restart ≠ compose up -d** — hub.env changes require `compose up -d`; system prompt changes need only `docker restart`
7. **FalkorDB graph name is `neo_workspace`** — NOT `karma`
8. **RELATES_TO edges permanently frozen at 2026-03-04** — use MENTIONS co-occurrence only
9. **vault-api type enum is closed** — use type:"log" + tags for custom types
10. **batch_ingest cron MUST use --skip-dedup** — Graphiti mode silently fails at scale
11. **MEMORY.md spine is tail 3000 chars** — very long MEMORY.md = older content not visible to Karma
12. **cp -r does NOT overwrite existing files** — always explicit per-file `cp` commands
