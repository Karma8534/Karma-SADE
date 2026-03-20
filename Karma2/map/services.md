# Services — Ground Truth (2026-03-20)

## vault-neo (arknexus.net, DigitalOcean NYC3)
| Container | Status | Image | Role |
|-----------|--------|-------|------|
| anr-hub-bridge | Up 26h | hub_bridge-hub-bridge | API gateway, model routing, tools |
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
| aria.service | RUNNING | /mnt/c/dev/Karma/k2/aria/aria.py |
| karma-regent.service | RUNNING | /mnt/c/dev/Karma/k2/aria/karma_regent.py |

Chromium: /snap/bin/chromium + /usr/bin/chromium-browser (INSTALLED, last used 2026-03-09)
K2 Ollama: health check FAILED from vault-neo tunnel (may be internal-only)
K2 Ollama models (from env): qwen3:8b (primary), qwen3.5:4b (fallback)

## P1 (PAYBACK / 100.124.194.102)
Ollama: running (localhost:11434)
P1_OLLAMA_MODEL=nemotron-mini:latest — OPEN BLOCKER (model may not exist on P1)
P1_OLLAMA_URL: http://100.124.194.102:11434

## Coordination Bus
Endpoint: http://localhost:18090/v1/coordination (vault-neo internal) | https://hub.arknexus.net/v1/coordination
Active agents: regent, kcc, cc, codex, colby
Dispatch: NOT connected — no bus presence, no channel
