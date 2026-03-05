# Karma SADE — Health Monitoring (Current System)

**Last updated:** 2026-03-05 (Session 66)

> Previously described Ollama + Open WebUI monitoring. That system is DEPRECATED.
> Current system is vault-neo Docker containers. This document reflects actual production.

---

## 1. What "Healthy" Means

All 7 containers on vault-neo must show "Up" (not "Restarting" or "Exited"):

| Container | Role | Healthy = |
|-----------|------|-----------|
| `anr-hub-bridge` | API surface (/v1/chat, /v1/ambient, /v1/ingest, etc.) | `Up` + responds to POST /v1/chat |
| `karma-server` | Consciousness loop + tool executor | `Up (healthy)` + RestartCount=0 |
| `falkordb` | Graph database (neo_workspace, 3621+ nodes) | `Up` + accepts Cypher queries |
| `anr-vault-api` | JSONL ledger write endpoint | `Up (healthy)` |
| `anr-vault-db` | PostgreSQL backing store | `Up (healthy)` |
| `anr-vault-search` | FAISS vector search (text-embedding-3-small) | `Up (healthy)` |
| `anr-vault-caddy` | Reverse proxy → hub.arknexus.net | `Up` |

## 2. Health Check Commands

```bash
# Quick: all 7 containers
ssh vault-neo "docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E 'karma|hub|vault|falkor|caddy'"

# Detail: restart counts (karma-server must be 0)
ssh vault-neo "docker inspect karma-server --format 'RestartCount: {{.RestartCount}} | State: {{.State.Status}}'"

# Smoke test hub-bridge (requires auth token)
TOKEN=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")
curl -s -o /dev/null -w "%{http_code}" -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"ping"}]}'
# Expected: 200

# FalkorDB node count
ssh vault-neo "docker exec falkordb redis-cli -p 6379 GRAPH.QUERY neo_workspace 'MATCH (n) RETURN count(n)'"
```

## 3. Session-End Verification Gate

`.claude/hooks/session-end-verify.sh` runs 7 checks before ending any session:

| Check | What it verifies |
|-------|-----------------|
| 1 | Git status clean (no uncommitted changes) |
| 2 | MEMORY.md recently updated |
| 3 | Recent commits exist |
| 4 | On correct branch (main) |
| 5 | No large untracked files (WARN only — PDFs in gitignored dirs ok) |
| 6 | vault-neo HEAD matches local HEAD |
| 7 | No abandoned worktrees |

**Run before ending every session:** `.claude/hooks/session-end-verify.sh`

All FAIL checks must be resolved. Check 5 WARN is acceptable (gitignored PDF dirs).

## 4. Tool Health (Session 66+)

Karma's tools require specific health conditions beyond container status:

| Tool | Health requirement |
|------|-------------------|
| `graph_query` | falkordb Up + karma-server Up + hooks.py whitelist includes `graph_query` |
| `get_vault_file` | anr-hub-bridge Up + `/karma/` volume mount active |
| `read_file`, `write_file`, `edit_file`, `bash` | karma-server Up + hooks.py whitelist |

**If tool calls return `{"ok":false,"error":"Unknown tool: X"}`**: check `karma-core/hooks.py` ALLOWED_TOOLS set first — this is the silent whitelist gate before `execute_tool_action()`.

## 5. Cron-Based Health

| Job | Schedule | What |
|-----|----------|------|
| `batch_ingest` cron | Every 6h | Reads ledger → writes Episodic nodes to FalkorDB `neo_workspace` via Graphiti watermark mode |
| Vault-neo dirty-check cron | Hourly | Alerts if vault-neo git repo has uncommitted edits (enforces droplet-is-deployment-only rule) |

**Check batch_ingest last run:**
```bash
ssh vault-neo "docker exec karma-server cat /tmp/batch.log 2>/dev/null | tail -5"
```

## 6. Deprecated Monitoring (No Longer Applicable)

- ~~Ollama (localhost:11434)~~ — not running on current system
- ~~Open WebUI (localhost:8080)~~ — not running on current system
- ~~Disk usage checks on C: drive~~ — monitoring target is vault-neo, not PAYBACK
- ~~sentinel.ps1 / sentinel-daily-summary.ps1~~ — Windows-local scripts for old system

Windows disk health and local machine monitoring is not part of the current Karma SADE production scope.
