# Deployment & Server Operations

## Server Access
- **Host:** arknexus.net (DigitalOcean NYC3, 4GB RAM)
- **SSH:** `ssh vault-neo` (alias configured in local ~/.ssh/config)
- **User:** root (default DO setup)
- **Services:** Docker containers for Vault API, ChromaDB, Hub/Bridge

## Docker Services
All services run via docker-compose on the droplet.

Check status: `ssh vault-neo "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"`

Restart all: `ssh vault-neo "cd /opt/seed-vault && docker-compose restart"`

View logs: `ssh vault-neo "cd /opt/seed-vault && docker-compose logs --tail=50 [service-name]"`

## Key File Locations (Server)
- Ledger: `/opt/seed-vault/memory_v1/ledger/memory.jsonl`
- Docker compose: `/opt/seed-vault/docker-compose.yml`
- Vault API config: `/opt/seed-vault/config/`
- ChromaDB data: `/opt/seed-vault/chromadb/`

## Health Checks
```bash
# Full system check (run this at session start)
ssh vault-neo "systemctl status seed-vault && wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl"

# Test hub endpoint
curl -s -o /dev/null -w "%{http_code}" https://hub.arknexus.net/v1/chatlog

# Test vault API
ssh vault-neo "curl -s localhost:8000/health"

# Check ChromaDB
ssh vault-neo "curl -s localhost:8001/api/v1/heartbeat"

# Count ledger entries
ssh vault-neo "wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl"

# View last capture
ssh vault-neo "tail -1 /opt/seed-vault/memory_v1/ledger/memory.jsonl | jq ."
```

## Troubleshooting
**Hub returns 502/503:**
- Check if Docker containers are running: `ssh vault-neo "docker ps"`
- Check nginx/reverse proxy: `ssh vault-neo "systemctl status nginx && nginx -t"`
- Check Vault API logs: `ssh vault-neo "cd /opt/seed-vault && docker-compose logs --tail=20 vault-api"`

**Ledger not growing after captures:**
- Verify hub is receiving: check hub access logs
- Verify vault is processing: check vault-api container logs
- Verify write permissions: `ssh vault-neo "ls -la /opt/seed-vault/memory_v1/ledger/"`

**ChromaDB search returning no results:**
- Check if auto-reindex is running: look for reindex container/cron
- Manually trigger reindex if needed
- Verify collection exists: `ssh vault-neo "curl localhost:8001/api/v1/collections"`

**Extension not capturing (popup shows 0/0):**
- This is a client-side issue — see extension.md
- Not a server problem if health checks pass

## Cost
- Current: $24/mo (DigitalOcean droplet)
- Phase 4+: $29-34/mo projected (embeddings API usage)
- Annual: $288-408/yr depending on phase
