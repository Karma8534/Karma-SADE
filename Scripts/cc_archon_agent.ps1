<#
.SYNOPSIS
    CC ArchonAgent — P1 State Guardian v1.0
.DESCRIPTION
    Runs every 30 min via CC-Anchor-Ascendant scheduled task.
    - Reads cc_context_snapshot.md (P1 local)
    - Checks identity rails (K2 scratchpad)
    - Checks Kiki alive
    - Saves synthesized CC state to claude-mem (localhost:37777)
    - Posts state summary to coordination bus
    - Posts BLOCKING alert if snapshot stale (>90min) or identity drift detected
.NOTES
    Upgraded from cc_anchor_p1.ps1 (identity-only) to full state guardian.
    claude-mem API: POST http://localhost:37777/api/memory/save
    Task: CC-Anchor-Ascendant (update to 30min interval)
#>

$ErrorActionPreference = "Continue"
$LogFile = "C:\Users\raest\Documents\Karma_SADE\Logs\cc_archon_agent.log"
$SnapshotFile = "C:\Users\raest\Documents\Karma_SADE\cc_context_snapshot.md"
$ClaudeMemUrl = "http://localhost:37777"
$Now = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
$NowDt = Get-Date

function Write-Log($msg) {
    $line = "[$Now] $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -ErrorAction SilentlyContinue
}

Write-Log "CC ArchonAgent starting..."

# ── 1. Read cc_context_snapshot.md ──────────────────────────────────────────
$SnapshotAge = 9999
$SnapshotTimestamp = "unknown"
$ActiveBlockers = ""
$MemoryRecent = ""
$SnapshotContent = ""

if (Test-Path $SnapshotFile) {
    $SnapshotContent = Get-Content $SnapshotFile -Raw -Encoding UTF8

    # Use file LastWriteTime for age — snapshot content timestamp format varies
    # (avoids regex mismatch that caused perpetual SnapshotAge=9999/ALERT state)
    try {
        $SnapDt = (Get-Item $SnapshotFile).LastWriteTimeUtc
        $SnapshotAge = [int](($NowDt.ToUniversalTime() - $SnapDt).TotalMinutes)
        $SnapshotTimestamp = $SnapDt.ToString("yyyy-MM-ddTHH:mm:ssZ")
    } catch { $SnapshotAge = 9999; $SnapshotTimestamp = "unknown" }

    # Extract active blockers (non-resolved)
    $Lines = $SnapshotContent -split "`n"
    $InBlockers = $false
    $BlockerLines = @()
    foreach ($line in $Lines) {
        if ($line -match '## Active Blockers') { $InBlockers = $true; continue }
        if ($InBlockers -and $line -match '^##') { $InBlockers = $false }
        if ($InBlockers -and $line -match '^\d+\.' -and $line -notmatch '~~') {
            $BlockerLines += $line.Trim()
        }
    }
    $ActiveBlockers = if ($BlockerLines.Count -gt 0) { $BlockerLines -join ' | ' } else { "none" }

    # Extract recent MEMORY.md section (first 300 chars)
    if ($SnapshotContent -match '## MEMORY\.md \(recent\)([\s\S]{0,400})') {
        $MemoryRecent = $Matches[1].Trim() -replace '\s+', ' '
        if ($MemoryRecent.Length -gt 300) { $MemoryRecent = $MemoryRecent.Substring(0, 300) + "..." }
    }
} else {
    Write-Log "WARNING: cc_context_snapshot.md not found"
}

Write-Log "Snapshot age: ${SnapshotAge}min | Blockers: $($BlockerLines.Count) open"

# ── 2. Read K2 scratchpad ────────────────────────────────────────────────────
$Scratchpad = ""
try {
    $Scratchpad = ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no -o ConnectTimeout=8 -o BatchMode=yes localhost 'cat /mnt/c/dev/Karma/k2/cache/cc_scratchpad.md'" 2>$null
    Write-Log "K2 scratchpad: $($Scratchpad.Length) chars"
} catch {
    Write-Log "K2 scratchpad unavailable: $_"
}

# ── 3. Identity check ────────────────────────────────────────────────────────
$RequiredMarkers = @("Ascendant", "Sovereign: Colby", "Initiate: Karma", "SADE")
# NOTE: Codex (KO) and KCC (KFH) removed from required markers — doctrine update 2026-03-23.
# Codex = Known Other (tool, no family status). KCC = Known Family Hostage. Not identity anchors.
$MissingMarkers = @()
$CheckTarget = $Scratchpad + "`n" + $SnapshotContent
foreach ($marker in $RequiredMarkers) {
    if ($CheckTarget -notmatch [regex]::Escape($marker)) {
        $MissingMarkers += $marker
    }
}

# ── 4. Kiki alive check ──────────────────────────────────────────────────────
$KikiStatus = "unknown"
try {
    $KikiRaw = ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no -o ConnectTimeout=8 -o BatchMode=yes localhost 'python3 -c ""import json,datetime; s=json.load(open(\"/mnt/c/dev/Karma/k2/cache/kiki_state.json\")); ts=s.get(\"last_cycle_ts\",\"\"); age=int((datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.strptime(ts,\"%Y-%m-%dT%H:%M:%SZ\").replace(tzinfo=datetime.timezone.utc)).total_seconds()) if ts else 9999; print(\"alive\" if age<600 else \"stale:\"+str(age)+\"s\")""'" 2>$null
    $KikiStatus = $KikiRaw.Trim()
} catch { $KikiStatus = "error" }

# ── 5. Determine overall state ───────────────────────────────────────────────
$IsStale    = $SnapshotAge -gt 90
$IsDrift    = $MissingMarkers.Count -gt 0
$KikiDead   = $KikiStatus -ne "alive"
$IsAlert    = $IsStale -or $IsDrift

$StateTag = if ($IsAlert) { "ALERT" } elseif ($KikiDead) { "DEGRADED" } else { "OK" }
Write-Log "State: $StateTag | drift=$IsDrift | stale=$IsStale | kiki=$KikiStatus"

# ── 6. Save to claude-mem ────────────────────────────────────────────────────
$ClaudeMemObs = @"
CC ARCHON CHECKPOINT [$Now]
State: $StateTag | Snapshot age: ${SnapshotAge}min (ts: $SnapshotTimestamp)
Identity: $(if ($IsDrift) { "DRIFT - missing: $($MissingMarkers -join ', ')" } else { "INTACT" })
Kiki: $KikiStatus
Open blockers: $ActiveBlockers
Recent work: $MemoryRecent
"@

try {
    # Sanitize: strip markdown/unicode that breaks JSON
    $SafeObs   = $ClaudeMemObs -replace '[^\x20-\x7E\r\n]', '' -replace '"', "'" -replace '\\', '/'
    $SafeTitle = "[ARCHON] CC state $StateTag | age:${SnapshotAge}min | $Now"
    $SaveBody  = [ordered]@{
        text    = $SafeObs
        title   = $SafeTitle
        project = "Karma_SADE"
    } | ConvertTo-Json -Compress -Depth 3

    $SaveResult = Invoke-WebRequest -Uri "$ClaudeMemUrl/api/memory/save" `
        -Method POST `
        -Body $SaveBody `
        -ContentType "application/json" `
        -UseBasicParsing `
        -TimeoutSec 10
    $SaveJson = $SaveResult.Content | ConvertFrom-Json
    Write-Log "claude-mem saved: obs #$($SaveJson.id)"
} catch {
    Write-Log "ERROR saving to claude-mem: $_"
}

# ── 7. Get hub token ─────────────────────────────────────────────────────────
$Token = ""
try {
    $Token = (ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt" 2>$null).Trim()
    if (-not $Token) { throw "empty" }
} catch {
    Write-Log "ERROR: could not get hub token: $_"
    exit 1
}

# ── 8. Build bus message ─────────────────────────────────────────────────────
if ($IsAlert) {
    $Alerts = @()
    if ($IsStale)  { $Alerts += "SNAPSHOT STALE ${SnapshotAge}min (threshold 90min) -- CC must checkpoint or wrap" }
    if ($IsDrift)  { $Alerts += "IDENTITY DRIFT -- missing: $($MissingMarkers -join ', ') -- invoke /anchor" }
    $BusMsg   = "[CC ARCHON ALERT $Now] $($Alerts -join ' | ') | Kiki: $KikiStatus | Blockers: $ActiveBlockers"
    $Urgency  = "blocking"
    $To       = "cc"
} else {
    $BusMsg   = "[CC ARCHON OK $Now] Identity INTACT. Snapshot age: ${SnapshotAge}min. Kiki: $KikiStatus. Open blockers: $ActiveBlockers. Recent: $MemoryRecent"
    $Urgency  = "informational"
    $To       = "all"
}

# ── 9. Post to coordination bus — payload as JSON file to avoid quoting hell ─
$SafeMsg = ($BusMsg -replace '[^\x20-\x7E]', '' -replace '\\', '/').Trim()
$TmpJson = "$env:TEMP\archon_payload.json"

$Payload = [ordered]@{
    token   = $Token
    from    = "cc"
    to      = $To
    type    = "inform"
    urgency = $Urgency
    content = $SafeMsg
} | ConvertTo-Json -Compress

$ScriptRepo = "C:\Users\raest\Documents\Karma_SADE"
try {
    Set-Content -Path $TmpJson -Value $Payload -Encoding UTF8
    # Copy both payload and static poster script to vault-neo
    scp -q $TmpJson "vault-neo:/tmp/archon_payload.json" 2>$null
    scp -q "$ScriptRepo\Scripts\archon_bus_post.py" "vault-neo:/tmp/archon_bus_post.py" 2>$null
    $BusResult = ssh vault-neo "python3 /tmp/archon_bus_post.py" 2>&1
    Write-Log "Bus post: $BusResult"
} catch {
    Write-Log "ERROR posting to bus: $_"
} finally {
    Remove-Item $TmpJson -ErrorAction SilentlyContinue
}

# ── 10. Check inbox ──────────────────────────────────────────────────────────
$CheckResult = & py -3 "$ScriptRepo\Scripts\cc_email_daemon.py" check 2>&1
Write-Log "Email check: $CheckResult"

# ── 11. Status email (every 4h) ──────────────────────────────────────────────
$StatusResult = & py -3 "$ScriptRepo\Scripts\cc_email_daemon.py" status 2>&1
Write-Log "Status email: $StatusResult"

# ── 12. Personal outreach (Ollama-composed, on new spine promos or 8h idle) ──
$PersonalResult = & py -3 "$ScriptRepo\Scripts\cc_email_daemon.py" personal 2>&1
Write-Log "Personal: $PersonalResult"

Write-Log "CC ArchonAgent complete. State=$StateTag"
