# Services — Ground Truth (2026-03-27, updated Session 145)

## vault-neo (arknexus.net, DigitalOcean NYC3)
| Container | Status | Image | Role |
|-----------|--------|-------|------|
| anr-hub-bridge | Up (rebuilt S145) | hub_bridge-hub-bridge | API gateway, orchestrator, model routing, tools, /v1/status, /v1/trace |
| karma-server | Up HEALTHY | compose-karma-server | FalkorDB queries, batch_ingest, consciousness loop |
| anr-vault-search | Up HEALTHY | compose-search | FAISS semantic search (193K+ entries) |
| anr-vault-db | Up HEALTHY | postgres:16-alpine | Vault API database |
| anr-vault-api | Up HEALTHY | compose-api | Ledger write endpoint (209K+ entries) |
| anr-vault-caddy | Up | compose-caddy | Reverse proxy / TLS |
| falkordb | Up | falkordb/falkordb | Graph DB (neo_workspace, 4789+ nodes) |

Compose files: compose.yml (vault stack) | compose.hub.yml (hub-bridge stack)
Both at: /opt/seed-vault/memory_v1/

## K2 (192.168.0.226 / Tailscale 100.75.109.92)
| Service | Status | File |
|---------|--------|------|
| julian-cortex.service | RUNNING (qwen3.5:4b 32K, port 7892, live K2-side Ollama bridge via host.docker.internal:11434 / P1 reachability via 100.75.109.92:11434) | /mnt/c/dev/Karma/k2/aria/julian_cortex.py |
| aria.service | RUNNING (port 7890, Flask, tools/exec) | /mnt/c/dev/Karma/k2/aria/aria.py |
| karma-regent.service | RUNNING (Vesper pipeline, 1284 promotions, spine v1242) | /mnt/c/dev/Karma/k2/aria/karma_regent.py |
| karma-kiki.service | RUNNING (autonomous task agent) | /mnt/c/dev/Karma/k2/scripts/karma_kiki.py |
| cc-regent.service | RUNNING (CC continuity subagent) | K2 systemd |

### K2 Cron Agents
| Script | Cadence | Role |
|--------|---------|------|
| bus_to_cortex.py | Every 2min | Bus messages → cortex ingestion ($0) |
| cc_bus_reader.py | Every 2min | Reads bus for `to: cc` messages, calls Anthropic, posts response |
| cc_hourly_report.py | Every 1h | Posts CC/Karma status to bus |
| cc_anchor_agent.py | Every 3h | Verifies CC identity rails |
| kiki_pulse.py | Every 2h | Kiki governance heartbeat |
| promote_shadow.py | Every 30min | Shadow pattern promotion |
| sync-from-vault.sh pull | Every 30min | Pulls identity/invariants/direction from vault-neo (tightened S145 from 6h) |
| sync-from-vault.sh push | Every 1h | Pushes k2_local_observations.jsonl to /v1/ambient |
| ingest_recent.sh | Every 4h | Synthesizes recent ledger entries → cortex + vault |

K2 local-model runtime truth: SSH-visible K2 Linux does not expose localhost:11434; the live bridge is `host.docker.internal:11434` on K2 and `100.75.109.92:11434` from P1. Installed models now include `qwen3.5:4b`, `gemma4:e4b`, and `nomic-embed-text:latest`. Current loaded floor: `qwen3.5:4b`.

## P1 (PAYBACK / 100.124.194.102)
| Service | Status |
|---------|--------|
| Ollama | RUNNING (localhost:11434) — sam860/LFM2:350m + nomic-embed-text:latest (tiny local fallback / autonomy floor) |
| julian_cortex_p1.py | RUNNING (port 7893, 123+ blocks, fallback) |
| CC server (cc_server_p1.py) | RUNNING (port 7891, HKCU Run key) |
| KarmaCortexSync (schtasks) | Every 30min — syncs K2→P1 cortex blocks |

P1 Ollama models: sam860/LFM2:350m, nomic-embed-text:latest

## Model Routing (hub-bridge, Decision #35 S145)
| Tier | Model | Cost | When |
|------|-------|------|------|
| 0 (cortex) | qwen3.5:4b (K2→P1 failover) | $0 | Recall pattern matched |
| 1-2 (default) | gpt-5.4-mini | $0.75/$4.50 per 1M | Standard chat |
| 3 (escalation) | gpt-5.4 | $2.50/$15.00 per 1M | Deep mode / complex |
| Verifier | claude-sonnet-4-6 | $3.00/$15.00 per 1M | Structural changes (gated, default off) |

## Coordination Bus
Endpoint: hub.arknexus.net/v1/coordination
Active agents: regent, kcc, cc, codex, colby
