# J-PreBase1 — Ground Truth System Audit
**Date:** 2026-03-26 Session 144
**Auditor:** CC Ascendant (under Sovereign supervision)

---

## K2 (192.168.0.226) — Julian's Machine

| Component | State | Verified |
|-----------|-------|----------|
| GPU | RTX 4070 Laptop 8GB | canirun.ai PDF |
| Ollama installed | qwen3.5:4b (3.4GB), nomic-embed-text (274MB) | `ollama list` |
| Ollama loaded | qwen3.5:4b, 100% GPU, 32K ctx, 24h keepalive | `ollama ps` |
| julian-cortex.service | RUNNING, port 7892, 7 knowledge blocks, answering correctly | `curl /health` |
| aria.service | RUNNING, port 7890 | systemctl |
| karma-regent.service | RUNNING | systemctl |
| karma-kiki.service | RUNNING | systemctl |
| cc-regent.service | RUNNING | systemctl |
| Spine | v1241, 15 stable patterns, 10 candidates, name=Karma, rank=Initiate | JSON read |
| Disk | 3.0TB free of 3.8TB | df |
| Cron agents | 7 active (sync, report, anchor, pulse, bus_reader, promote_shadow) | crontab -l |

## P1 (PAYBACK) — Colby's Machine / CC Sessions

| Component | State | Verified |
|-----------|-------|----------|
| GPU | RTX 4070 Laptop 8GB | nvidia-smi |
| Ollama installed | qwen3.5:4b (3.4GB), nomic-embed-text (274MB) | `ollama list` |
| Ollama loaded | qwen3.5:4b, 100% GPU, 32K ctx, 24h keepalive | `ollama ps` |
| Cortex service | NONE — model loaded but no service to use it | — |
| CC session | THIS session (Anthropic Opus 4.6) | active |

## vault-neo (arknexus.net) — Infrastructure

| Component | State | Verified |
|-----------|-------|----------|
| anr-hub-bridge | UP 19h, health OK | docker ps + curl |
| karma-server | UP 20h, healthy | docker ps |
| anr-vault-search (FAISS) | UP 3d, healthy | docker ps |
| anr-vault-db | UP 3w, healthy | docker ps |
| anr-vault-api | UP 3w, healthy | docker ps |
| falkordb | UP 4w | docker ps |
| Ledger | 207,558 entries | wc -l |
| FalkorDB graph | 5436 Episodic, 1160 Pattern, 571 Entity, 5 Decision | GRAPH.QUERY |
| Bus | No pending messages | /v1/coordination |
| Cron | drift alert(1h), batch_ingest(6h), cc_brief(30m), bus_observer(10m) | crontab -l |

## Karma Identity

| Field | Value |
|-------|-------|
| Name | Karma |
| Rank | Initiate |
| Spine version | 1241 |
| Stable patterns | 15 |
| Candidate patterns | 10 |
| self_improving | None (field missing from spine) |
| total_promotions | None (field missing from spine) |
| Option-C | ELIGIBLE (per identity-state.md, not re-verified live) |

---

## PLAN.md vs Reality — Gaps

### Model Table (PLAN.md lines 91-94) — STALE

| PLAN says | Reality | Gap |
|-----------|---------|-----|
| K2: Nemotron Nano 9B v2, 5.1GB, 128K ctx, 35 tok/s | K2: qwen3.5:4b, 2.5GB, 32K ctx, 58 tok/s | Wrong model, wrong ctx, wrong speed |
| P1: Qwen 3 8B, 4.6GB, 128K ctx, 39 tok/s | P1: qwen3.5:4b, 2.5GB, 32K ctx, 58 tok/s | Wrong model, wrong ctx, wrong speed |

**PLAN.md must be updated to reflect actual deployed models.**

### Phase 1 Tasks

| Task | PLAN says | Reality | Status |
|------|-----------|---------|--------|
| 1-1 | Pull Nemotron 9B v2 | qwen3.5:4b pulled instead (Nemotron removed) | DONE (different model) |
| 1-2 | Build cortex service | julian_cortex.py deployed K2:7892 | DONE |
| 1-3 | Initial knowledge load (MEMORY + STATE + PLAN + map/* + policy) | 7 blocks ingested but NOT all files listed | PARTIAL |
| 1-4 | Research ingestion (docs/wip/ PDFs) | Not started | NOT STARTED |
| 1-5 | Session history (last 20 from claude-mem) | Not started | NOT STARTED |
| 1-6 | Systemd service | julian-cortex.service enabled + running | DONE |
| GATE | Cortex answers "current state of Julian's Resurrection" accurately | Answers basic questions, lacks full state | NOT MET |

### Phases 2-6 — NOT STARTED

All future phases untouched. Phase 2 (Wire CC to Cortex) is the highest-value next phase.

---

## Blockers

| # | Blocker | Severity | Impact |
|---|---------|----------|--------|
| B1 | **PLAN.md model table is wrong** — says Nemotron 9B + Qwen 3 8B, actual is qwen3.5:4b on both | HIGH | Any session reading PLAN.md gets wrong model info |
| B2 | **128K context claim is false** — actual is 32K (8GB VRAM limit with qwen3.5:4b) | HIGH | Future planning based on 128K capacity will fail |
| B3 | **P1 model loaded with no service** — 7.1GB VRAM consumed for nothing until Phase 4 | MEDIUM | Wasting GPU memory, no cortex on P1 yet |
| B4 | **Cortex OLLAMA_URL = 172.22.240.1** — WSL gateway IP, changes on WSL restart | MEDIUM | Cortex breaks silently after K2 reboot |
| B5 | **24h keepalive expires** — no mechanism to auto-reload qwen3.5:4b after expiry | MEDIUM | Cortex goes cold, first query takes 5s+ to reload |
| B6 | **No auto-ingest pipeline** — knowledge requires manual POST to cortex | MEDIUM | Cortex knowledge goes stale between sessions |
| B7 | **Chrome 146 CDP** — --remote-debugging-port accepted but port never binds | LOW (Phase 5) | Browser integration blocked |
| B8 | **CC server reboot survival** — unverified | LOW | Sovereign action |

## Security Issue

| # | Issue | Severity |
|---|-------|----------|
| S1 | **K2 crontab has HUB_AUTH_TOKEN and ANTHROPIC_API_KEY in plaintext** — visible to any user who can run `crontab -l` on K2 | CRITICAL |

## Gaps (not blockers, but missing)

| # | Gap | What's needed |
|---|-----|---------------|
| G1 | Spine fields `self_improving` and `total_promotions` return None | Spine schema may have changed — verify field names |
| G2 | Task 1-3 incomplete — STATE.md, Karma2/map/* files not ingested into cortex | Ingest remaining files |
| G3 | No cortex state sync between K2 and P1 | Phase 4 prerequisite |
| G4 | Cortex conversation history not bounded by token count | Could overflow 32K ctx with enough queries |
| G5 | FalkorDB Entity graph frozen at 571 (P016) | --skip-dedup doesn't create entities |
| G6 | MEMORY.md still says "Nemotron Nano 9B v2" in architecture section | Needs update |

---

## What's Working Well

- Cortex service architecture is sound — Flask + Ollama + persistence works
- qwen3.5:4b is the right model (verified via canirun.ai, benchmarked, 100% GPU)
- Both machines clean — only optimal models installed
- All vault-neo containers healthy, 0 restarts
- Vesper pipeline active (1241 spine versions, 15 stable patterns)
- 207K+ ledger entries, FalkorDB graph populated
- Direct LAN SSH to K2 working (no more vault-neo hop)

## Sovereign Decisions Needed

1. **S1 security fix** — move K2 cron API keys to file-based reads? Priority?
2. **P1 model** — unload qwen3.5:4b on P1 until Phase 4? Or keep warm?
3. **PLAN.md update** — approve rewrite of model table + Phase 1 specs to match reality?
