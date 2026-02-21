# K2 FalkorDB Replication — Design Doc

**Date:** 2026-02-21
**Status:** Approved by Karma and Colby

---

## Goal

Make K2 (192.168.0.226) a live read-only replica of vault-neo's FalkorDB, providing disaster recovery with near-zero lag and no changes to vault-neo's infrastructure.

---

## Architecture

```
K2 Windows host
  └── FalkorDB-Tunnel.ps1 (Task Scheduler, runs at logon)
       ├── SSH tunnel: K2:17687 → vault-neo:7687 (localhost on vault-neo host)
       └── docker exec falkordb redis-cli REPLICAOF 127.0.0.1 17687
                                │
                           SSH (port 22)
                                │
                         vault-neo (64.225.13.144)
                           └── localhost:7687 → FalkorDB container:6379
```

---

## Confirmed Facts

- **vault-neo FalkorDB**: internal port 6379 mapped to host port 7687. `nc -zv localhost 7687` succeeds from vault-neo host. ✅
- **K2 SSH key**: `C:\Users\karma\.ssh\id_ed25519`, passwordless, connects to `neo@64.225.13.144:22` ✅
- **K2 FalkorDB**: `falkordb/falkordb:latest`, container `c7082788609c`, Docker Desktop ✅
- **Tunnel target**: `localhost:7687` on vault-neo (not `falkordb:6379` — Docker DNS only resolves inside the container network, not from the host)

---

## Components

### 1. vault-neo: close port 7687

```bash
ufw deny 7687
```

Port 7687 is currently publicly exposed with no auth. The SSH tunnel makes external exposure unnecessary. Closing it is pure hygiene. Internal Docker access (`falkordb:6379`) is unaffected.

### 2. `FalkorDB-Tunnel.ps1` — persistent tunnel keeper (K2)

Runs as a background Task Scheduler job. Loop:
1. Spawn `ssh -N -L 17687:localhost:7687 neo@64.225.13.144` as a background job
2. Wait 3 seconds for tunnel to stabilise
3. Run `docker exec falkordb redis-cli REPLICAOF 127.0.0.1 17687`
4. Wait for SSH job to exit (disconnect/timeout)
5. Sleep 10 seconds, loop back to step 1

On every reconnect, REPLICAOF is re-issued (handles FalkorDB container restarts too).

### 3. `Setup-FalkorDB-Replica.ps1` — one-time installer (K2, run via RDP)

- Creates `C:\Users\karma\FalkorDB-Sync\`
- Writes `FalkorDB-Tunnel.ps1` inline
- Registers Task Scheduler task: trigger=AtLogOn, action=hidden PowerShell, RunLevel=Highest, restart on failure (3×, 1min interval)
- Starts task immediately

---

## Failure Modes

| Event | Behaviour |
|-------|-----------|
| SSH tunnel drops | FalkorDB goes read-only from last sync. Script reconnects in 10s. |
| K2 FalkorDB container restarts | REPLICAOF re-issued on next tunnel reconnect. ~10s lag. |
| vault-neo FalkorDB restarts | Tunnel stays up. Replication resumes automatically. |
| K2 reboots | Task Scheduler starts tunnel keeper at logon. |
| vault-neo unreachable | K2 FalkorDB serves last-known state read-only. |

---

## Failover (manual)

If vault-neo goes down and K2 needs to become primary:
```powershell
docker exec falkordb redis-cli REPLICAOF NO ONE
```
K2 FalkorDB becomes writable with last-replicated state.

---

## Not In Scope

- Automatic failover (manual only — human decision)
- Writing to K2 FalkorDB while replication is active (it's read-only)
- Option B (RDB snapshot) — superseded by Option C
- NSSM or WSL (not needed — native Windows SSH client is sufficient)
