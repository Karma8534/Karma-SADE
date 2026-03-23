# Services — Ground Truth (2026-03-23, updated session 127)

## vault-neo (arknexus.net, DigitalOcean NYC3)
| Container | Status | Image | Role |
|-----------|--------|-------|------|
| anr-hub-bridge | Up (rebuilt session 127) | hub_bridge-hub-bridge | API gateway, model routing, tools. /v1/cypher LIVE. |
| karma-server | Up 7d HEALTHY | compose-karma-server | FalkorDB queries, batch_ingest, consciousness loop |
| anr-vault-search | Up 8d HEALTHY | compose-search | FAISS semantic search |
| anr-vault-db | Up 2wk HEALTHY | postgres:16-alpine | Vault API database |
| anr-vault-api | Up 2wk HEALTHY | compose-api | Ledger write endpoint |
| anr-vault-caddy | Up 3wk | compose-caddy | Reverse proxy / TLS |
| falkordb | Up 3wk | falkordb/falkordb | Graph DB (neo_workspace) |

Compose files: compose.yml (vault stack) | compose.hub.yml (hub-bridge stack)
Both at: /opt/seed-vault/memory_v1/

## K2 (192.168.0.226 / Tailscale 100.75.109.92)
| Service | Status | File |
|---------|--------|------|
| aria.service | RUNNING (PID 423990, fixed session 127 — zombie+drop-in fix) | /mnt/c/dev/Karma/k2/aria/aria.py |
| karma-regent.service | RUNNING via systemd (enabled, /etc/systemd/system/karma-regent.service, PID 243460) | /mnt/c/dev/Karma/k2/aria/karma_regent.py |

### K2 Cron Agents (always running — NOT session-dependent)
| Script | Cadence | Role |
|--------|---------|------|
| cc_hourly_report.py | Every 1h | Posts CC/Karma system status to Agora bus (from: cc, to: all) |
| cc_anchor_agent.py | Every 3h | Verifies CC identity rails in cc_scratchpad.md; posts DRIFT ALERT if degraded |
| kiki_pulse.py | Every 2h | Kiki governance heartbeat |
| promote_shadow.py | Every 30min | Shadow pattern promotion pipeline |
| sync-from-vault.sh pull | Every 6h | Pulls identity/invariants/direction/corrections from vault-neo to K2 |
| sync-from-vault.sh push | Every 1h | Pushes k2_local_observations.jsonl to hub /v1/ambient |

| cc_bus_reader.py | Every 2min | Reads bus for `to: cc` messages, calls Anthropic API with CC identity, posts response back — **@cc is now reactive** |

CC is now fully bidirectional on the bus.

Chromium: /snap/bin/chromium + /usr/bin/chromium-browser (INSTALLED, last used 2026-03-09)
K2 Ollama models: qwen3:8b (primary), qwen3.5:4b (fallback)

## P1 (PAYBACK / 100.124.194.102)
Ollama: running (localhost:11434)
P1_OLLAMA_MODEL=nemotron-mini:latest — RESOLVED (model exists, verified session 125)
P1_OLLAMA_URL: http://100.124.194.102:11434

## Coordination Bus
Endpoint: http://localhost:18090/v1/coordination (vault-neo internal) | https://hub.arknexus.net/v1/coordination
Active agents: regent, kcc, cc, codex, colby
Dispatch: NOT connected — no bus presence, no channel
