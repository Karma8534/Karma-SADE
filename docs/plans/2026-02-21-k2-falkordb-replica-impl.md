# K2 FalkorDB Replication Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make K2 (192.168.0.226) a live read-only replica of vault-neo's FalkorDB via a persistent SSH tunnel and Redis REPLICAOF.

**Architecture:** A PowerShell tunnel-keeper script runs on K2 as a Task Scheduler job at logon. It opens `ssh -N -L 17687:localhost:7687 neo@64.225.13.144`, then issues `docker exec falkordb redis-cli REPLICAOF 127.0.0.1 17687`. On disconnect it reconnects automatically. A one-time installer script registers the task and starts it.

**Tech Stack:** PowerShell 5+, Windows Task Scheduler, Windows OpenSSH client, Docker Desktop (K2), ufw (vault-neo)

---

## Task 1 — vault-neo: close public port 7687

**Files:** none (ufw rule only)

### Step 1: Check current ufw status

```bash
ssh vault-neo "ufw status numbered | grep -E '7687|Status'"
```
Expected: Either `7687` appears as ALLOW, or it's absent (no explicit rule, but port is exposed via Docker).

### Step 2: Add deny rule for port 7687

```bash
ssh vault-neo "ufw deny 7687 && ufw status | grep 7687"
```
Expected: `7687` appears with `DENY` action.

**Note:** `ufw deny` blocks external connections. The SSH tunnel destination `localhost:7687` is host-local and unaffected by this rule.

### Step 3: Verify FalkorDB still responds internally

```bash
ssh vault-neo "docker exec falkordb redis-cli -p 6379 ping"
```
Expected: `PONG`

### Step 4: Verify port 7687 is now blocked externally

From P1 (not vault-neo):
```bash
nc -zv -w 3 64.225.13.144 7687 2>&1 || echo "blocked as expected"
```
Expected: `Connection refused` or `timed out` — NOT `succeeded`.

### Step 5: Commit note

```bash
cd /c/Users/raest/Documents/Karma_SADE
git commit --allow-empty -m "phase-6: vault-neo ufw deny 7687 — close public Redis port (tunnel replaces it)"
```

---

## Task 2 — Write FalkorDB-Tunnel.ps1

**Files:**
- Create: `scripts/k2-falkordb-sync/FalkorDB-Tunnel.ps1`

### Step 1: Create directory

```bash
mkdir -p /c/Users/raest/Documents/Karma_SADE/scripts/k2-falkordb-sync
```

### Step 2: Write FalkorDB-Tunnel.ps1

Create `scripts/k2-falkordb-sync/FalkorDB-Tunnel.ps1` with this exact content:

```powershell
# FalkorDB-Tunnel.ps1
# Keeps SSH tunnel to vault-neo alive and maintains K2 FalkorDB in replica mode.
# Run via Task Scheduler at logon — do not run manually unless testing.

param(
    [string]$VaultNeoHost = "64.225.13.144",
    [int]$VaultNeoPort    = 22,
    [int]$TunnelLocalPort = 17687,
    [int]$TunnelRemotePort = 7687,
    [string]$SshKeyPath   = "$env:USERPROFILE\.ssh\id_ed25519",
    [string]$SshUser      = "neo"
)

$LogFile = "$PSScriptRoot\tunnel.log"

function Write-Log {
    param([string]$Msg)
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Msg"
    Add-Content -Path $LogFile -Value $line
    Write-Host $line
}

function Get-FalkorContainer {
    $name = docker ps --filter "ancestor=falkordb/falkordb" --format "{{.Names}}" 2>$null |
            Select-Object -First 1
    if (-not $name) { $name = "falkordb" }  # fallback to well-known name
    return $name
}

function Set-Replication {
    param([string]$Container, [int]$Port)
    $result = docker exec $Container redis-cli REPLICAOF 127.0.0.1 $Port 2>&1
    Write-Log "[REPLICATION] docker exec $Container redis-cli REPLICAOF 127.0.0.1 $Port -> $result"
    return ($result -match "OK")
}

Write-Log "[TUNNEL] FalkorDB tunnel keeper started. Key=$SshKeyPath Target=$SshUser@${VaultNeoHost}:$VaultNeoPort"

while ($true) {
    Write-Log "[TUNNEL] Opening tunnel K2:$TunnelLocalPort -> ${VaultNeoHost}:$TunnelRemotePort"

    # Start SSH tunnel as background job
    $sshArgs = @(
        "-N",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=30",
        "-o", "ServerAliveCountMax=3",
        "-i", $SshKeyPath,
        "-p", $VaultNeoPort,
        "-L", "${TunnelLocalPort}:localhost:${TunnelRemotePort}",
        "${SshUser}@${VaultNeoHost}"
    )
    $job = Start-Job -ScriptBlock {
        param($args)
        & ssh @args
    } -ArgumentList (, $sshArgs)

    # Wait for tunnel to stabilise
    Start-Sleep -Seconds 3

    # Issue REPLICAOF
    $container = Get-FalkorContainer
    $ok = Set-Replication -Container $container -Port $TunnelLocalPort
    if (-not $ok) {
        Write-Log "[REPLICATION] WARNING: REPLICAOF did not return OK — will retry on next reconnect"
    }

    # Wait for SSH job to exit (means tunnel died)
    Wait-Job $job | Out-Null
    $exitState = $job.State
    Remove-Job $job -Force
    Write-Log "[TUNNEL] Tunnel exited (state=$exitState). Reconnecting in 10s..."
    Start-Sleep -Seconds 10
}
```

### Step 3: Verify the file was written

```bash
ls -la /c/Users/raest/Documents/Karma_SADE/scripts/k2-falkordb-sync/FalkorDB-Tunnel.ps1
wc -l /c/Users/raest/Documents/Karma_SADE/scripts/k2-falkordb-sync/FalkorDB-Tunnel.ps1
```
Expected: file exists, ~70 lines.

---

## Task 3 — Write Setup-FalkorDB-Replica.ps1

**Files:**
- Create: `scripts/k2-falkordb-sync/Setup-FalkorDB-Replica.ps1`

### Step 1: Write the installer script

Create `scripts/k2-falkordb-sync/Setup-FalkorDB-Replica.ps1` with this exact content:

```powershell
# Setup-FalkorDB-Replica.ps1
# Run ONCE on K2 via RDP to install the FalkorDB tunnel keeper.
# Must be run as the karma user (not Administrator) so Task Scheduler
# uses the correct SSH key at C:\Users\karma\.ssh\id_ed25519

$InstallDir  = "C:\Users\karma\FalkorDB-Sync"
$TunnelScript = Join-Path $InstallDir "FalkorDB-Tunnel.ps1"
$TaskName    = "FalkorDB-Vault-Tunnel"

Write-Host "=== FalkorDB Replica Setup ==="
Write-Host "Install dir: $InstallDir"

# 1. Create install directory
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Write-Host "[1/5] Created $InstallDir"

# 2. Copy tunnel script (this script must live next to FalkorDB-Tunnel.ps1)
$srcScript = Join-Path $PSScriptRoot "FalkorDB-Tunnel.ps1"
if (-not (Test-Path $srcScript)) {
    Write-Error "FalkorDB-Tunnel.ps1 not found next to this script at $srcScript"
    exit 1
}
Copy-Item -Path $srcScript -Destination $TunnelScript -Force
Write-Host "[2/5] Copied FalkorDB-Tunnel.ps1 to $InstallDir"

# 3. Verify SSH key exists
$sshKey = "C:\Users\karma\.ssh\id_ed25519"
if (-not (Test-Path $sshKey)) {
    Write-Error "SSH key not found at $sshKey — cannot proceed"
    exit 1
}
Write-Host "[3/5] SSH key verified at $sshKey"

# 4. Register Task Scheduler task
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -NonInteractive -File `"$TunnelScript`""

$trigger = New-ScheduledTaskTrigger -AtLogOn

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 5 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

# Remove existing task if present
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Maintains SSH tunnel to vault-neo FalkorDB and keeps K2 FalkorDB in replica mode" `
    -RunLevel Highest | Out-Null

Write-Host "[4/5] Registered scheduled task '$TaskName' (triggers: AtLogOn)"

# 5. Start the task now
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 5
$state = (Get-ScheduledTask -TaskName $TaskName).State
Write-Host "[5/5] Task started. Current state: $state"

Write-Host ""
Write-Host "=== Setup complete ==="
Write-Host "Monitor: Get-ScheduledTask -TaskName '$TaskName'"
Write-Host "Logs:    $InstallDir\tunnel.log"
Write-Host "Stop:    Stop-ScheduledTask -TaskName '$TaskName'"
Write-Host "Test:    docker exec falkordb redis-cli INFO replication"
```

### Step 2: Verify the file was written

```bash
ls -la /c/Users/raest/Documents/Karma_SADE/scripts/k2-falkordb-sync/Setup-FalkorDB-Replica.ps1
wc -l /c/Users/raest/Documents/Karma_SADE/scripts/k2-falkordb-sync/Setup-FalkorDB-Replica.ps1
```
Expected: file exists, ~60 lines.

### Step 3: Commit both scripts

```bash
cd /c/Users/raest/Documents/Karma_SADE
git add scripts/k2-falkordb-sync/
git commit -m "phase-6: K2 FalkorDB replication scripts (tunnel keeper + installer)"
git push origin main
```

---

## Task 4 — Deploy to K2 and install

**Files:** none (deployment only)

### Context
K2 cannot be reached via SSH from P1 (firewall). Scripts must be delivered manually via RDP. Colby will:
1. Open RDP to K2 (192.168.0.226, user: karma)
2. Copy the two scripts from the share to K2
3. Run Setup-FalkorDB-Replica.ps1 in a PowerShell terminal

### Step 1: Confirm share path

Ask Colby: what is the Windows share path for K2? (e.g., `\\K2\share`, `Z:\`, or a mapped drive)

Then copy from P1 to that path:
```powershell
# On P1 — replace \\K2\share with actual path
$src = "C:\Users\raest\Documents\Karma_SADE\scripts\k2-falkordb-sync"
$dst = "\\K2\share\FalkorDB-Sync"   # adjust to actual path
New-Item -ItemType Directory -Force -Path $dst | Out-Null
Copy-Item "$src\FalkorDB-Tunnel.ps1"     "$dst\" -Force
Copy-Item "$src\Setup-FalkorDB-Replica.ps1" "$dst\" -Force
Write-Host "Scripts copied to $dst"
```

### Step 2: On K2 (via RDP) — open PowerShell as karma user

In K2's Start menu: right-click "Windows PowerShell" → "Run as this user: karma" (or just open PowerShell — if logged in as karma, it's already the right context).

### Step 3: On K2 — navigate to scripts and run installer

```powershell
# In K2 PowerShell terminal
cd "C:\Users\karma\Desktop"    # or wherever the share is accessible
# OR directly from share:
cd "\\K2\share\FalkorDB-Sync"  # adjust to actual path

Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
.\Setup-FalkorDB-Replica.ps1
```

Expected output:
```
=== FalkorDB Replica Setup ===
Install dir: C:\Users\karma\FalkorDB-Sync
[1/5] Created C:\Users\karma\FalkorDB-Sync
[2/5] Copied FalkorDB-Tunnel.ps1 to C:\Users\karma\FalkorDB-Sync
[3/5] SSH key verified at C:\Users\karma\.ssh\id_ed25519
[4/5] Registered scheduled task 'FalkorDB-Vault-Tunnel' (triggers: AtLogOn)
[5/5] Task started. Current state: Running
=== Setup complete ===
```

### Step 4: On K2 — verify tunnel is up

Wait ~5 seconds, then in K2 PowerShell:
```powershell
# Check task state
Get-ScheduledTask -TaskName "FalkorDB-Vault-Tunnel" | Select-Object TaskName, State

# Check tunnel log
Get-Content "C:\Users\karma\FalkorDB-Sync\tunnel.log" -Tail 10

# Check FalkorDB replication status
docker exec falkordb redis-cli INFO replication
```

Expected from `INFO replication`:
```
role:slave
master_host:127.0.0.1
master_port:17687
master_link_status:up
```

If `master_link_status:down`, wait 10s and re-check — initial sync can take a moment.

---

## Task 5 — Verify E2E replication

### Step 1: Write a test key to vault-neo FalkorDB

```bash
ssh vault-neo "docker exec falkordb redis-cli SET replication_test_$(date +%s) 'k2_replica_verified'"
```
Expected: `OK`

### Step 2: On K2 — verify the key replicated

In K2 PowerShell:
```powershell
docker exec falkordb redis-cli KEYS "replication_test_*"
```
Expected: shows the key written in Step 1 within a few seconds.

### Step 3: Verify graph data is present on K2

```powershell
docker exec falkordb redis-cli GRAPH.QUERY neo_workspace "MATCH (n) RETURN count(n) LIMIT 1"
```
Expected: returns a count ~501 (matching vault-neo's entity count).

If this hangs or errors, check the tunnel log for replication errors.

### Step 4: Verify K2 FalkorDB is read-only (replica)

```powershell
docker exec falkordb redis-cli GRAPH.QUERY neo_workspace "CREATE (:TestNode {name: 'should_fail'})"
```
Expected: Error — `READONLY You can't write against a read only replica`

### Step 5: Update MEMORY.md

Add to Hub-Bridge History or Infrastructure section:
```
- K2 FalkorDB replication LIVE (2026-02-21): SSH tunnel K2:17687 → vault-neo:7687.
  REPLICAOF active. K2 is read-only replica of vault-neo FalkorDB.
  Task: FalkorDB-Vault-Tunnel (AtLogOn). Logs: C:\Users\karma\FalkorDB-Sync\tunnel.log.
  Failover: docker exec falkordb redis-cli REPLICAOF NO ONE
```

### Step 6: Final commit and push

```bash
cd /c/Users/raest/Documents/Karma_SADE
git add MEMORY.md
git commit -m "phase-6: K2 FalkorDB replication live — SSH tunnel + REPLICAOF"
git push origin main
```

---

## Rollback

If replication causes issues on K2:
```powershell
# On K2: stop task and detach from master
Stop-ScheduledTask -TaskName "FalkorDB-Vault-Tunnel"
docker exec falkordb redis-cli REPLICAOF NO ONE
```
K2 FalkorDB returns to standalone mode with last-replicated state.

To re-enable: `Start-ScheduledTask -TaskName "FalkorDB-Vault-Tunnel"`
