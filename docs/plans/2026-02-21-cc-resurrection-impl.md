# CC Resurrection — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** At every CC session start, inject Karma's live canonical graph context (identity, memories, preferences) into CC's working context via `Get-KarmaContext.ps1` → `karma-context.md`.

**Architecture:** PowerShell script fetches vault-neo `/raw-context?q=session_start&lane=canonical` via SSH, writes output atomically to `karma-context.md`. K2 fallback (192.168.0.226:6379) uses a minimal PowerShell RESP TCP client to query FalkorDB directly when vault-neo is unreachable. CLAUDE.md updated to read karma-context.md at session start.

**Tech Stack:** PowerShell 5.1, SSH (`vault-neo` alias), vault-neo karma-server `/raw-context`, FalkorDB RESP protocol (Redis-compatible), System.Net.Sockets.TcpClient

---

## Pre-flight checks (run before starting)

```bash
# Verify vault-neo raw-context works
ssh vault-neo "curl -s 'http://localhost:8340/raw-context?q=session_start&lane=canonical' | python3 -c 'import sys,json; d=json.load(sys.stdin); print(\"ok:\", d[\"ok\"], \"len:\", len(d[\"context\"]))'"
# Expected: ok: True len: ~1400+

# Verify K2 FalkorDB is reachable
powershell.exe -Command "Test-NetConnection 192.168.0.226 -Port 6379 | Select-Object TcpTestSucceeded"
# Expected: TcpTestSucceeded: True
```

---

## Task 1: Add .gitignore entries

**Files:**
- Modify: `.gitignore`

**Step 1: Add entries**

Open `.gitignore` and append at the bottom:

```
# Karma context snapshot (generated at CC session start, machine-local)
karma-context.md
karma-context.md.tmp
```

**Step 2: Verify**

```bash
cd "C:\Users\raest\Documents\Karma_SADE"
git check-ignore -v karma-context.md
# Expected: .gitignore:<line>:karma-context.md  karma-context.md
```

**Step 3: Commit**

```bash
git add .gitignore
git commit -m "phase-6: gitignore karma-context.md (cc resurrection output)"
```

---

## Task 2: Write Get-KarmaContext.ps1 — primary path

**Files:**
- Create: `Scripts/resurrection/Get-KarmaContext.ps1`

**Step 1: Create the script**

Create `Scripts/resurrection/Get-KarmaContext.ps1` with this exact content (ASCII, CRLF):

```powershell
# Get-KarmaContext.ps1
# Fetches Karma's live canonical graph context at CC session start.
# Writes to karma-context.md (gitignored) for CC to read.
# Primary: vault-neo /raw-context via SSH. Fallback: K2 FalkorDB at 192.168.0.226:6379.

param(
    [string]$OutputFile  = "$PSScriptRoot\..\..\karma-context.md",
    [string]$TmpFile     = "$PSScriptRoot\..\..\karma-context.md.tmp",
    [string]$VaultNeoAlias = "vault-neo",
    [string]$K2Host      = "192.168.0.226",
    [int]$K2Port         = 6379,
    [string]$GraphName   = "neo_workspace",
    [int]$VaultTimeoutSec = 3,
    [int]$K2TimeoutMs    = 2000
)

$OutputFile = [System.IO.Path]::GetFullPath($OutputFile)
$TmpFile    = [System.IO.Path]::GetFullPath($TmpFile)
$Timestamp  = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Context {
    param([string]$Content)
    [System.IO.File]::WriteAllText($TmpFile, $Content, [System.Text.Encoding]::UTF8)
    Move-Item -Path $TmpFile -Destination $OutputFile -Force
}

# --- Primary path: vault-neo SSH ---
function Get-VaultNeoContext {
    try {
        $job = Start-Job {
            param($alias)
            ssh $alias "curl -s 'http://localhost:8340/raw-context?q=session_start&lane=canonical'"
        } -ArgumentList $VaultNeoAlias
        $completed = Wait-Job $job -Timeout $VaultTimeoutSec
        if (-not $completed) {
            Remove-Job $job -Force
            return $null
        }
        $raw = Receive-Job $job
        Remove-Job $job -Force
        if (-not $raw) { return $null }
        $json = $raw | ConvertFrom-Json -ErrorAction Stop
        if (-not $json.ok -or -not $json.context) { return $null }
        return $json
    } catch {
        return $null
    }
}

# --- Fallback path: K2 FalkorDB via RESP TCP ---
function Invoke-FalkorQuery {
    param([string]$Query)
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $ar  = $tcp.BeginConnect($K2Host, $K2Port, $null, $null)
        if (-not $ar.AsyncWaitHandle.WaitOne($K2TimeoutMs)) {
            $tcp.Close(); return $null
        }
        $tcp.EndConnect($ar)
        $stream = $tcp.GetStream()
        $stream.ReadTimeout = $K2TimeoutMs

        # Build RESP array: *3\r\n $11\r\nGRAPH.QUERY\r\n $<n>\r\n<graph>\r\n $<m>\r\n<query>\r\n
        $cmd   = "GRAPH.QUERY"
        $parts = @($cmd, $GraphName, $Query)
        $sb    = New-Object System.Text.StringBuilder
        $sb.Append("*$($parts.Count)`r`n") | Out-Null
        foreach ($p in $parts) {
            $bytes = [System.Text.Encoding]::UTF8.GetByteCount($p)
            $sb.Append("`$$bytes`r`n$p`r`n") | Out-Null
        }
        $buf = [System.Text.Encoding]::UTF8.GetBytes($sb.ToString())
        $stream.Write($buf, 0, $buf.Length)
        $stream.Flush()

        $rbuf = New-Object byte[] 65536
        $n    = $stream.Read($rbuf, 0, $rbuf.Length)
        $resp = [System.Text.Encoding]::UTF8.GetString($rbuf, 0, $n)
        $tcp.Close()
        return $resp
    } catch {
        return $null
    }
}

function Parse-RespStrings {
    param([string]$raw)
    if (-not $raw) { return @() }
    $lines  = $raw -split "\r\n"
    $values = [System.Collections.Generic.List[string]]::new()
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^\$(\d+)$') {
            $len = [int]$Matches[1]
            if ($i + 1 -lt $lines.Count -and $lines[$i+1].Length -eq $len) {
                $values.Add($lines[$i+1])
                $i++
            }
        }
    }
    return $values.ToArray()
}

function Get-K2Context {
    # Test connectivity
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $ar  = $tcp.BeginConnect($K2Host, $K2Port, $null, $null)
        $ok  = $ar.AsyncWaitHandle.WaitOne($K2TimeoutMs)
        if ($ok) { $tcp.EndConnect($ar) }
        $tcp.Close()
        if (-not $ok) { return $null }
    } catch { return $null }

    # Query 1: identity entities
    $idResp = Invoke-FalkorQuery "MATCH (n:Entity) WHERE toLower(n.name) IN ['colby', 'user', 'neo'] RETURN n.name, n.summary"
    $idVals = Parse-RespStrings $idResp

    # Query 2: recent canonical episodes
    $epResp = Invoke-FalkorQuery "MATCH (e:Episodic) WHERE e.lane = 'canonical' RETURN e.content ORDER BY e.created_at DESC LIMIT 5"
    $epVals = Parse-RespStrings $epResp

    # Query 3: graph stats
    $stResp = Invoke-FalkorQuery "MATCH (n:Entity) RETURN count(n) AS cnt"
    $stVals = Parse-RespStrings $stResp
    $entityCount = if ($stVals.Count -gt 0) { $stVals[-1] } else { "?" }

    # Format output matching /raw-context shape
    $parts = [System.Collections.Generic.List[string]]::new()

    # Identity
    if ($idVals.Count -ge 2) {
        $parts.Add("## User Identity (CRITICAL)")
        for ($i = 0; $i -lt $idVals.Count - 1; $i += 2) {
            $name = $idVals[$i]; $summary = $idVals[$i+1]
            if ($name -and $summary) {
                if ($name -ieq "colby") { $parts.Add("REAL NAME: Colby") }
                $parts.Add("- **${name}**: $($summary.Substring(0, [Math]::Min(200, $summary.Length)))")
            }
        }
    }

    # Episodes
    if ($epVals.Count -gt 0) {
        $parts.Add("`n## Recent Memories (canonical)")
        foreach ($ep in $epVals) {
            if ($ep) { $parts.Add("- $($ep.Substring(0, [Math]::Min(200, $ep.Length)))") }
        }
    }

    return @{
        context      = ($parts -join "`n")
        entity_count = $entityCount
        source       = "K2-FALLBACK"
    }
}

# --- Main ---
Write-Host "[Karma] Fetching graph context..."

$ctx = Get-VaultNeoContext
if ($ctx) {
    $output = "# Karma Graph Context -- $Timestamp (vault-neo)`n# Query: session_start | Lane: canonical`n`n$($ctx.context)"
    Write-Context $output
    Write-Host "[Karma] Context written from vault-neo ($($ctx.context.Length) chars)"
    exit 0
}

Write-Host "[Karma] vault-neo unreachable, trying K2 fallback (${K2Host}:${K2Port})..."
$ctx = Get-K2Context
if ($ctx) {
    $output = "# Karma Graph Context -- $Timestamp [K2-FALLBACK]`n# Note: vault-neo unreachable. K2 replica used. Preferences section unavailable.`n`n$($ctx.context)"
    Write-Context $output
    Write-Host "[Karma] Context written from K2 fallback"
    exit 0
}

# Both unreachable
$stub = "# Karma Graph Context -- UNAVAILABLE`n# Fetched: $Timestamp`n# Reason: vault-neo SSH timeout (${VaultTimeoutSec}s) + K2 TCP timeout (${K2Host}:${K2Port}, ${K2TimeoutMs}ms)`n# CC: proceed with MEMORY.md context only."
Write-Context $stub
Write-Host "[Karma] Both vault-neo and K2 unreachable. UNAVAILABLE stub written."
exit 1
```

**Step 2: Verify file encoding is clean**

```powershell
powershell.exe -Command "& { \$f = 'C:\Users\raest\Documents\Karma_SADE\Scripts\resurrection\Get-KarmaContext.ps1'; if (Test-Path \$f) { Write-Host 'exists'; \$bytes = [IO.File]::ReadAllBytes(\$f); \$hasBom = (\$bytes[0] -eq 0xEF -and \$bytes[1] -eq 0xBB -and \$bytes[2] -eq 0xBF); Write-Host \"BOM: \$hasBom\" } }"
# Expected: exists / BOM: False  (UTF-8 without BOM is fine — no em dashes in script)
```

**Step 3: Commit**

```bash
git add Scripts/resurrection/Get-KarmaContext.ps1
git commit -m "phase-6: Get-KarmaContext.ps1 — CC resurrection script (primary + K2 fallback)"
```

---

## Task 3: Smoke test — primary path

**Step 1: Run the script**

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
& "C:\Users\raest\Documents\Karma_SADE\Scripts\resurrection\Get-KarmaContext.ps1"
# Expected: [Karma] Fetching graph context...
#           [Karma] Context written from vault-neo (XXXX chars)
```

**Step 2: Verify karma-context.md was written**

```powershell
Get-Content "C:\Users\raest\Documents\Karma_SADE\karma-context.md" | Select-Object -First 15
# Expected:
#   # Karma Graph Context -- 2026-02-21 HH:MM:SS (vault-neo)
#   # Query: session_start | Lane: canonical
#   [empty line]
#   ## CC Has a Proposal   ← OR ##  User Identity, depending on collab queue state
#   ...
```

**Step 3: Verify content contains identity block**

```powershell
Select-String -Path "C:\Users\raest\Documents\Karma_SADE\karma-context.md" -Pattern "REAL NAME|User Identity|What I Know"
# Expected: at least one match (Colby identity present)
```

**Step 4: Verify .tmp file is gone (atomic write worked)**

```powershell
Test-Path "C:\Users\raest\Documents\Karma_SADE\karma-context.md.tmp"
# Expected: False
```

---

## Task 4: Smoke test — K2 fallback path

**Step 1: Run script with a fake vault-neo alias to force fallback**

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
& "C:\Users\raest\Documents\Karma_SADE\Scripts\resurrection\Get-KarmaContext.ps1" -VaultNeoAlias "vault-neo-does-not-exist" -VaultTimeoutSec 1
# Expected: [Karma] Fetching graph context...
#           [Karma] vault-neo unreachable, trying K2 fallback (192.168.0.226:6379)...
#           [Karma] Context written from K2 fallback
```

**Step 2: Verify K2 fallback content**

```powershell
Get-Content "C:\Users\raest\Documents\Karma_SADE\karma-context.md" | Select-Object -First 10
# Expected:
#   # Karma Graph Context -- <timestamp> [K2-FALLBACK]
#   # Note: vault-neo unreachable. K2 replica used...
#   [content with ## User Identity block from FalkorDB]
```

**Step 3: If K2 fallback content is empty or missing User Identity, debug**

```powershell
# Test raw TCP connection to K2
Test-NetConnection 192.168.0.226 -Port 6379
# Expected: TcpTestSucceeded: True

# If connection succeeds but no data, test the RESP query directly:
# Run a minimal test — check if FalkorDB responds to PING
$tcp = New-Object System.Net.Sockets.TcpClient
$tcp.Connect("192.168.0.226", 6379)
$stream = $tcp.GetStream()
$ping = [System.Text.Encoding]::UTF8.GetBytes("PING`r`n")
$stream.Write($ping, 0, $ping.Length); $stream.Flush()
$buf = New-Object byte[] 1024
$n = $stream.Read($buf, 0, $buf.Length)
[System.Text.Encoding]::UTF8.GetString($buf, 0, $n)
$tcp.Close()
# Expected: +PONG\r\n
```

**Step 4: Restore original vault-neo (run without override to confirm primary still works)**

```powershell
& "C:\Users\raest\Documents\Karma_SADE\Scripts\resurrection\Get-KarmaContext.ps1"
# Expected: Context written from vault-neo
```

---

## Task 5: Update CLAUDE.md — add session-start step

**Files:**
- Modify: `CLAUDE.md` (requires explicit user approval per contract — confirm before this task)

**Step 1: Read current Session Start section**

```bash
grep -A 8 "## Session Start" C:\Users\raest\Documents\Karma_SADE\CLAUDE.md
```

**Step 2: Edit Session Start to add resurrection step**

Change the `## Session Start` section from:
```markdown
## Session Start (Do This First)
1. Read MEMORY.md for current phase status and active task
2. Run: `ssh vault-neo "systemctl status seed-vault && wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl"`
3. Check git log --oneline -5 for recent changes
4. Resume the active task listed in MEMORY.md — do not ask what to work on
```

To:
```markdown
## Session Start (Do This First)
1. Run `Scripts/resurrection/Get-KarmaContext.ps1` then read `karma-context.md` for Karma's live graph context
2. Read MEMORY.md for current phase status and active task
3. Run: `ssh vault-neo "systemctl status seed-vault && wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl"`
4. Check git log --oneline -5 for recent changes
5. Resume the active task listed in MEMORY.md — do not ask what to work on
```

Note: The same change must be applied to `.claude/worktrees/laughing-swartz/CLAUDE.md` — it is a copy of the root CLAUDE.md.

**Step 3: Verify the diff**

```bash
git diff CLAUDE.md
# Expected: +1 line in Session Start, step numbers shifted up by 1
```

**Step 4: Commit**

```bash
git add CLAUDE.md .claude/worktrees/laughing-swartz/CLAUDE.md
git commit -m "phase-6: CLAUDE.md -- add graph context resurrection to session start"
```

---

## Task 6: Update MEMORY.md + final push

**Step 1: Update MEMORY.md Current Task section**

In `MEMORY.md`, update `## Current Task` to reflect resurrection complete:

```
CC Resurrection LIVE (2026-02-21):
- Get-KarmaContext.ps1 in Scripts/resurrection/
- Fetches /raw-context?q=session_start&lane=canonical from vault-neo at CC session start
- Writes karma-context.md (gitignored, atomic write) for CC to read
- K2 fallback: 192.168.0.226:6379 RESP TCP client (verified reachable, 0.0.0.0 bound)
- Context shape: verbatim from build_karma_context() -- identity, episodes, preferences, recent approved
- CLAUDE.md Session Start: step 1 now runs Get-KarmaContext.ps1 + reads karma-context.md
- Smoke tested: primary path (vault-neo) and K2 fallback both verified
```

**Step 2: Secret scan**

```bash
grep -rn "Bearer\|token\|secret\|password\|api_key" --include="*.ps1" Scripts/resurrection/ | grep -v node_modules | grep -v .git
# Expected: no output (no secrets in script)
```

**Step 3: Final commit and push**

```bash
git add MEMORY.md
git commit -m "phase-6: MEMORY.md -- CC resurrection live"
git push origin main
git log --oneline -4
```

---

## Success Criteria

| Check | Command | Expected |
|---|---|---|
| Script runs without error | `& Get-KarmaContext.ps1` | Exit 0, "Context written from vault-neo" |
| karma-context.md exists | `Test-Path karma-context.md` | True |
| Has identity section | `Select-String karma-context.md -Pattern "REAL NAME\|User Identity"` | Match found |
| .tmp file gone | `Test-Path karma-context.md.tmp` | False |
| K2 fallback works | `& Get-KarmaContext.ps1 -VaultNeoAlias bad -VaultTimeoutSec 1` | "Context written from K2 fallback" |
| Git clean | `git status` | Only karma-context.md untracked (gitignored) |

---

## Known Constraints

- **PowerShell 5.1 encoding**: Script uses ASCII-only characters. No em dashes, curly quotes, or non-ASCII. Verified during write.
- **vault-neo SSH alias**: Assumes `vault-neo` is configured in `~/.ssh/config`. Script param `$VaultNeoAlias` allows override.
- **K2 RESP parser**: Handles `$N\r\n<value>\r\n` bulk strings only. Does not parse integers, arrays, or error types. Sufficient for GRAPH.QUERY string results.
- **K2 preferences gap**: K2 fallback cannot provide `## What I Know About The User` (PostgreSQL on vault-neo). Noted in fallback header.
- **worktree CLAUDE.md**: Two copies of CLAUDE.md exist (root + `.claude/worktrees/laughing-swartz/`). Both must be updated in Task 5.
