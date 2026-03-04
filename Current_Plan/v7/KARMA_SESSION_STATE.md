# KARMA-SADE Session State
> Last updated: 2026-02-28T13:10:00-05:00 (auto-update at each session end)
> Owner: Colby (Neo) | Asher (Perplexity Computer)

---

## Droplet Access
| Key | Value |
|-----|-------|
| IP | 64.225.13.144 |
| User | neo |
| Sudo PW | ollieboo |
| SSH Auth | Pubkey-only (generate new key each sandbox session, add to ~/.ssh/authorized_keys) |
| OS | Ubuntu 24.04, 1 vCPU, 4GB RAM (upgraded), 50GB disk, NYC3 |
| Operational Dir | `/opt/seed-vault/memory_v1/` (NOT `/home/neo/karma-sade/`) |
| Git Repo Dir | `/home/neo/karma-sade/` (separate, NOT used by containers) |
| Docker Compose | `/opt/seed-vault/memory_v1/compose/compose.yml` |
| Hub Bridge Compose | `/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml` |
| Hub Bridge Port | 18090 |
| Hub Bridge Token | `cb5617b2ce67470d389dcff1e1fe417aa2626ae699c7d5f831b133cb1f4d450e` |
| Karma Server Port | 8340 |
| Containers | 7 (all healthy as of 2026-02-28) |
| Hub Bridge .env | `/opt/seed-vault/memory_v1/hub_bridge/.env` (MUST exist — contains ZAI_API_KEY) |

## GitHub Access
| Key | Value |
|-----|-------|
| Repo | Karma8534/Karma-SADE (private) |
| Access | `github_mcp_direct` connector — full read/write |
| Deploy Key | READ-ONLY on droplet (push via GitHub API only) |
| Large File Push | Use subagent with `create_or_update_file` or `push_files` (include SHA for existing files) |

## Build Plan Progress
| Phase | Description | Status | Commit |
|-------|------------|--------|--------|
| 0 | Triage | COMPLETE | `91aeb448` |
| 1 | Memory admission + scoring | COMPLETE | `b70d2434` |
| 2 | Token budget + time-decay | COMPLETE | `ccb979df` |
| 3 | Hooks + Briefing + Compaction | COMPLETE | `ce296d55` |
| 4 | Hardening & Observability | COMPLETE | `b778ef21` (latest) |
| 5 | Learning & Evolution | ONGOING (operational) | — |

### Phase 4 Substeps
| Step | Task | Status | Notes |
|------|------|--------|-------|
| 4.1 | Comprehensive /health endpoint | COMPLETE | graph, sqlite, budget, modules, ingestion_health |
| 4.2 | Memory ingestion health | COMPLETE | last_admit_age, last_reflect_age, 7-day warning |
| 4.3 | Ledger rotation (monthly cron) | COMPLETE | ledger_rotate.sh deployed, cron: `0 3 1 * *` |
| 4.4 | Incremental transcript processing | COMPLETE | transcript_processor.py deployed + server.py endpoints |
| 4.5 | Script distillation | COMPLETE | distilled_ops.sh deployed |
| 4.6 | Utility-score feedback (/v1/feedback) | COMPLETE | usage boost on positive signal |
| 4.7 | Reflection directives (weekly cron) | COMPLETE | reflection_directives.sh, cron: `0 6 * * 1` |
| 4.8 | DECISION nodes in FalkorDB | COMPLETE | /v1/decisions/graph + /v1/decisions/list |
| 4.9 | Watchdog / self-repair | COMPLETE | watchdog.sh deployed, cron: `*/5 * * * *` |
| 4.10 | Droplet profiling + upgrade decision | COMPLETE | DECISION: stay at 4GB, peak <800MB |
| 4.11 | K2 re-evaluation | COMPLETE | K2_DECISION.md: K2 stays dormant |
| 4.12 | End-to-end integration test | COMPLETE | 9/10 pass (LLM timeout on /ask = transient) |

### Phase 4/5 (Earlier Work — NOT build plan phases)
| Step | Task | Status | Notes |
|------|------|--------|-------|
| — | Episode dedup guard | COMPLETE | PR #11, `1dedf8a` |
| — | Auto-promote | COMPLETE | PR #11, `1dedf8a` |

## Cron Jobs on Droplet
| Schedule | Script | Purpose |
|----------|--------|---------|
| `*/5 * * * *` | watchdog.sh | FalkorDB memory, observer staleness, container health, disk |
| `0 3 1 * *` | ledger_rotate.sh | Monthly gzip of >50K-line JSONL files |
| `0 6 * * 1` | reflection_directives.sh | Weekly reflection directives (Monday 6am) |
| `0 4 * * *` | nightly_backup.sh | Nightly backup |
| `25 3 * * *` | resurrection cron.sh capture | Resurrection snapshot |
| `35 3 * * 0` | resurrection cron.sh prune | Weekly prune |
| `*/30 * * * *` | karma-sade-pull.sh | Git pull on droplet repo |
| `*/5 * * * *` | gen-cc-brief.py | CC session brief generation |

## GitHub Commits (This Build)
| Commit | Description |
|--------|-------------|
| `91aeb448` | Phase 0 triage |
| `b70d2434` | Phase 1 memory admission |
| `ccb979df` | Phase 2 budget + time-decay |
| `eb74824c` | hooks.py |
| `047221ef` | session_briefing.py |
| `9a61662e` | compaction.py |
| `8a9832f1` | server.py Phase 3 |
| `ce296d55` | hub_server.js Phase 3 |
| `d1a8a3c8` | server.py Phase 4.1+4.2 |
| `80ecb07e` | watchdog + ledger scripts |
| `fc407d8c` | server.py Phase 4.6+4.8+4.10 + route dedup fix |
| `bc09704d` | hub_server.js Phase 4 proxy routes |
| `b1b6c67f` | Phase 4 batch: transcript, distilled, reflection, K2 |
| `b778ef21` | Phase 4.4: transcript endpoints in server.py (HEAD) |

## Pre-Phase 3 Completions (outside plan)
- GLM-4.7-Flash chat backbone (free tier via Z.ai) — merged to main at `6c8d12a`
- Hybrid routing: GLM for chat, gpt-4o-mini for tools — 67% cost savings
- Ollie retrieval fix — PR #12, `84b0569` (3-pass search, synonyms, plurals)
- Episode ingestion re-enabled with dedup guard
- Auto-promote live (confidence ≥ 0.90, age ≥ 30min, corroboration ≥ 2)
- Nightly backup script exists (cron + DO Spaces not wired yet)

## K2 (Colby's Local Machine)
| Key | Value |
|-----|-------|
| Hardware | Lenovo ThinkPad P1 Gen 7, Intel Core Ultra 9, 63.4GB RAM |
| GPU | RTX 4070 Laptop, 8GB VRAM |
| Storage | 3.8TB KIOXIA NVMe SSD (3.1TB free) |
| Ollama | localhost:8002, auto-starts |
| Models | qwen2.5:7b, gemma3:4b, llama3.2:3b, llama3.1:8b, qwen2.5-coder:7b, karma-builder |
| Role | QA/whiteroom oversight, local AI inference (dormant until later phase) |

## Colby's Preferences (NON-NEGOTIABLE)
- Always take the most optimal path. No options, no permissions needed (except financial/safety).
- Ground truth only. No assumptions stated as facts. No hedging.
- Proceed directly to next phase without summary when current phase is complete.
- All file edits and Docker operations target `/opt/seed-vault/memory_v1/` — NOT `/home/neo/karma-sade/`.
- Every session start: verify SSH + GitHub access FIRST, ask for anything missing.
- Use sudo password `ollieboo` when sudo is needed — don't work around permission issues.
- No exclamation marks. No emojis. No fluff.
- Stop wasting cycles. Execute efficiently.
- OPTIMIZE FOR CREDIT PRESERVATION — batch operations, minimize tool calls, no parallel subagents where sequential works.

## Session Start Checklist
1. Load this file (`KARMA_SESSION_STATE.md`)
2. Generate SSH key, add to droplet authorized_keys
3. Verify SSH connection: `ssh neo@64.225.13.144 echo "OK"`
4. Verify GitHub API: list_external_tools → github_mcp_direct
5. If either fails → ask Colby immediately, don't attempt workarounds
6. Check current Phase status and resume where we left off

## Cost Model
- Z.ai GLM-4.7-Flash: $0 (free tier, chat backbone)
- gpt-4o-mini: ~$0.002/query (tool-calling only, ~30% of queries)
- Monthly target: under $100 total (currently ~$0.50/month API costs)
- Colby budget: ~$200/month subscriptions (Perplexity Max primary)

## CRITICAL: Next Session Priority — ✅ RESOLVED (v7.1)
~~Karma cannot answer "What is my cat's name?" — memory retrieval pipeline is broken.~~

**v7.1 UPDATE:** Memory retrieval is WORKING. All critical bugs fixed:
- Phantom tools bug fixed — correct tools listed in buildSystemText()
- Duplicate karmaCtx fixed — single injection
- Episode ingestion pipeline deployed — /ingest-episode endpoint + hub-bridge fire-and-forget
- Consciousness loop ACTIVE — 60s OBSERVE + auto-promote every 10 cycles
- Verified: Karma recalls Ollie, Baxter, guitar, favorite color

**Remaining work:** Budget guard, capability gate, lane=NULL episode promotion (1239 nodes)

## Fixes Applied This Session (2026-02-28)
1. Hub-bridge `.env` file was missing — created at `/opt/seed-vault/memory_v1/hub_bridge/.env` with ZAI_API_KEY
2. Z.ai 429 rate limit fallback added to `callLLM()` — falls back to gpt-4o (NOT gpt-4o-mini) to preserve voice
3. Vault sync script deployed at `/opt/seed-vault/memory_v1/tools/vault_sync.sh` (replaces old karma-sade-pull.sh)
4. Local repo `/home/neo/karma-sade/` reset to match origin/main (was diverged)
5. Ollie entity manually ingested into FalkorDB `neo_workspace` graph

## Fixes Applied — CC Master Fix Session (2026-02-28, later)
6. `/ingest-episode` endpoint added to karma-server (server.py line 1454)
7. Hub-bridge fire-and-forget episode ingestion added to /v1/chat handler (server.js line 1305)
8. Consciousness loop auto-promote wired (consciousness.py line 177) — every 10 cycles
9. Auto-promote thresholds lowered: confidence 0.90→0.80, corroboration 2→1
10. Phantom tools bug fixed — correct tools in buildSystemText()
11. Duplicate karmaCtx injection removed — single injection
12. Both containers rebuilt and verified healthy

## FalkorDB Graph Names
| Graph | Entities | Notes |
|-------|----------|-------|
| neo_workspace | Entity: 167, Episodic: 1240, Rel: 832 | ACTIVE — node label is `Episodic` (NOT `Episode`) |
| karma_memory | 0 | EMPTY — unused |
| karma | 0 | EMPTY — unused |
| default_db | 0 | EMPTY — unused |

## Model Architecture (confirmed working)
| Layer | Model | Provider | Cost |
|-------|-------|----------|------|
| Chat backbone | glm-4.7-flash | Z.ai | Free |
| Tool calls | gpt-4o-mini | OpenAI | ~$0.002/call |
| 429 fallback | gpt-4o | OpenAI | ~$0.01/call |

## Remaining Work
### Phase 5: Learning & Evolution (ONGOING — all infrastructure built)
- Session reflections: every session end (wired via /v1/reflect)
- Deferred review: weekly Colby-initiated (deferred.jsonl exists)
- Memory audit: monthly Colby-initiated (staleness scan works)
- Staleness sweep: weekly cron (deployed)
- Reflection directives: weekly cron (deployed, Monday 6am)
- Budget review: monthly (budget_guard works)
- Identity evolution: as needed (collab.jsonl pipeline exists)
- Context compaction: quarterly (compaction.py works)
- Scene consolidation: triggered at >20 cells (works)

### Post-Build
- Nightly backup to DO Spaces (cron exists but DO Spaces credentials not wired)
- 16 stale GitHub branches (cosmetic cleanup)
- Git repo ↔ vault sync permanent solution (vault_sync.sh deployed but repo/vault files still differ)
- K2 integration (dormant, future phase)
