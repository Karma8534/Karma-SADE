param(
    [switch]$HiddenRelaunch
)

$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot 'HiddenRelaunch.ps1')
Invoke-HiddenRelaunchIfNeeded -ScriptPath $PSCommandPath -HiddenRelaunch:$HiddenRelaunch

$ScriptRepo = Split-Path -Parent $PSScriptRoot
$LogFile = 'C:\Users\raest\Documents\Karma_SADE\Logs\cc_archon_agent.log'
$SnapshotFile = 'C:\Users\raest\Documents\Karma_SADE\cc_context_snapshot.md'
$LastAlertFile = Join-Path $env:TEMP 'archon_last_alert.txt'

function Write-Log([string]$msg) {
    $ts = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -ErrorAction SilentlyContinue
}

function Get-ClaudeMemBaseUrl {
    $defaultPort = '37778'
    $settingsPath = Join-Path $env:USERPROFILE '.claude-mem\settings.json'
    if (Test-Path $settingsPath) {
        try {
            $settings = Get-Content $settingsPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($settings.CLAUDE_MEM_WORKER_PORT) {
                $port = [string]$settings.CLAUDE_MEM_WORKER_PORT
                if ($port -match '^\d+$') {
                    return "http://127.0.0.1:$port"
                }
            }
        } catch {
            Write-Log "WARN: could not parse claude-mem settings.json: $($_.Exception.Message)"
        }
    }
    return "http://127.0.0.1:$defaultPort"
}

function Get-KikiStatus {
    try {
        $raw = ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no -o ConnectTimeout=8 -o BatchMode=yes localhost 'cat /mnt/c/dev/Karma/k2/cache/kiki_state.json'" 2>$null
        if (-not $raw) { return 'error' }
        $obj = $raw | ConvertFrom-Json
        if (-not $obj.last_cycle_ts) { return 'stale:9999s' }
        if ($obj.last_cycle_ts -is [datetime]) {
            $last = [datetime]$obj.last_cycle_ts
        } else {
            $last = [datetimeoffset]::Parse([string]$obj.last_cycle_ts, [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::AssumeUniversal).UtcDateTime
        }
        $age = [int](($([datetime]::UtcNow) - $last.ToUniversalTime()).TotalSeconds)
        if ($age -lt 600) { return 'alive' }
        return "stale:${age}s"
    } catch {
        return 'error'
    }
}

function Test-IdentityDrift([string]$content) {
    $required = @('SOVEREIGN: Colby', 'ASCENDANT', 'INITIATE: Karma', 'SADE')
    $missing = @()
    foreach ($m in $required) {
        if ($content -notmatch [regex]::Escape($m)) { $missing += $m }
    }
    return ,$missing
}

Write-Log 'CC ArchonAgent starting...'

$nowDt = Get-Date
$snapshotAge = 9999
$snapshotTs = 'unknown'
$activeBlockers = 'none'
$memoryRecent = ''
$snapshotContent = ''
$blockerLines = @()

if (Test-Path $SnapshotFile) {
    try {
        $snapshotContent = Get-Content $SnapshotFile -Raw -Encoding UTF8
        $snapDt = (Get-Item $SnapshotFile).LastWriteTimeUtc
        $snapshotAge = [int](($nowDt.ToUniversalTime() - $snapDt).TotalMinutes)
        $snapshotTs = $snapDt.ToString('yyyy-MM-ddTHH:mm:ssZ')

        $lines = $snapshotContent -split "`n"
        $inBlockers = $false
        foreach ($line in $lines) {
            if ($line -match '^## Active Blockers') { $inBlockers = $true; continue }
            if ($inBlockers -and $line -match '^## ') { $inBlockers = $false }
            if ($inBlockers -and $line -match '^\d+\.' -and $line -notmatch '~~') {
                $blockerLines += $line.Trim()
            }
        }
        if ($blockerLines.Count -gt 0) { $activeBlockers = ($blockerLines -join ' | ') }

        if ($snapshotContent -match '## MEMORY\.md \(recent\)([\s\S]{0,400})') {
            $memoryRecent = $Matches[1].Trim() -replace '\s+', ' '
            if ($memoryRecent.Length -gt 300) { $memoryRecent = $memoryRecent.Substring(0, 300) + '...' }
        }
    } catch {
        Write-Log "WARN: snapshot parse failed: $($_.Exception.Message)"
    }
} else {
    Write-Log 'WARNING: cc_context_snapshot.md not found'
}

Write-Log ("Snapshot age: {0}min | Blockers: {1} open" -f $snapshotAge, $blockerLines.Count)

$scratchpad = ''
try {
    $scratchpad = ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no -o ConnectTimeout=8 -o BatchMode=yes localhost 'cat /mnt/c/dev/Karma/k2/cache/cc_scratchpad.md'" 2>$null
} catch {}
Write-Log ("K2 scratchpad: {0} chars" -f $scratchpad.Length)

$identitySource = "$scratchpad`n$snapshotContent"
$missingMarkers = Test-IdentityDrift -content $identitySource
$kikiStatus = Get-KikiStatus

$isStale = $snapshotAge -gt 90
$isDrift = $missingMarkers.Count -gt 0
$kikiDead = $kikiStatus -ne 'alive'
$isAlert = $isStale -or $isDrift
$stateTag = if ($isAlert) { 'ALERT' } elseif ($kikiDead) { 'DEGRADED' } else { 'OK' }
Write-Log ("State: {0} | drift={1} | stale={2} | kiki={3}" -f $stateTag, $isDrift, $isStale, $kikiStatus)
if ($isDrift) {
    Write-Log ("Drift markers missing: {0}" -f ($missingMarkers -join ', '))
}

$claudeMemBase = Get-ClaudeMemBaseUrl
$token = ''
try {
    $localTokenPath = Join-Path $ScriptRepo '.hub-chat-token'
    if (Test-Path $localTokenPath) {
        $token = (Get-Content $localTokenPath -Raw -Encoding UTF8).Trim()
    }
} catch {}
if (-not $token) {
    try {
        $token = (ssh vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt' 2>$null).Trim()
    } catch {}
}

$obsNow = [datetime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
$obsText = @"
CC ARCHON CHECKPOINT [$obsNow]
State: $stateTag | Snapshot age: ${snapshotAge}min (ts: $snapshotTs)
Identity: $(if ($isDrift) { "DRIFT - missing: $($missingMarkers -join ', ')" } else { 'INTACT' })
Kiki: $kikiStatus
Open blockers: $activeBlockers
Recent work: $memoryRecent
"@

try {
    $saveBodyObj = [ordered]@{
        text = ($obsText -replace '[^\x20-\x7E\r\n]', '')
        title = "[ARCHON] CC state $stateTag | age:${snapshotAge}min | $obsNow"
        project = 'Karma_SADE'
    }
    $saveBody = $saveBodyObj | ConvertTo-Json -Compress -Depth 3

    if ($token) {
        $saveHeaders = @{ Authorization = "Bearer $token" }
        $saveRes = Invoke-WebRequest -Uri "http://127.0.0.1:7891/v1/memory/save" -Headers $saveHeaders -Method POST -Body $saveBody -ContentType 'application/json' -UseBasicParsing -TimeoutSec 8
    } else {
        $saveRes = Invoke-WebRequest -Uri "$claudeMemBase/api/memory/save" -Method POST -Body $saveBody -ContentType 'application/json' -UseBasicParsing -TimeoutSec 6
    }
    $saveJson = $saveRes.Content | ConvertFrom-Json
    $saveId = if ($saveJson.id) { $saveJson.id } else { '(no-id)' }
    Write-Log ("claude-mem saved: obs #{0} via {1}" -f $saveId, ($(if ($token) { 'cc_server_proxy' } else { $claudeMemBase })))
} catch {
    Write-Log ("WARN saving to claude-mem via {0}: {1}" -f $claudeMemBase, $_.Exception.Message)
    try {
        $queuePath = 'C:\Users\raest\Documents\Karma_SADE\Logs\archon_claudemem_queue.jsonl'
        $queued = [ordered]@{
            queued_at = [datetime]::UtcNow.ToString('o')
            title = "[ARCHON] CC state $stateTag | age:${snapshotAge}min | $obsNow"
            text = ($obsText -replace '[^\x20-\x7E\r\n]', '')
            project = 'Karma_SADE'
            source = 'cc_archon_agent'
            reason = 'claude_mem_unavailable'
        } | ConvertTo-Json -Compress
        Add-Content -Path $queuePath -Value $queued -Encoding UTF8
        Write-Log ("Queued claude-mem observation to {0}" -f $queuePath)
    } catch {
        Write-Log ("ERROR queueing claude-mem fallback payload: {0}" -f $_.Exception.Message)
    }
}
if (-not $token) {
    Write-Log 'ERROR: could not get hub token'
    exit 1
}

$skipBusPost = $false
if ($isAlert) {
    $alertType = ''
    if ($isStale) { $alertType += 'stale' }
    if ($isDrift) { $alertType += 'drift' }

    if (Test-Path $LastAlertFile) {
        try {
            $parts = (Get-Content $LastAlertFile -Raw).Trim() -split '\|'
            $lastType = $parts[0]
            $lastTime = [datetime]::Parse($parts[1])
            $minsSince = [int](($nowDt - $lastTime).TotalMinutes)
            if ($lastType -eq $alertType -and $minsSince -lt 60) {
                $skipBusPost = $true
                Write-Log ("DEDUP: same alert '{0}' posted {1}min ago - skipping bus post" -f $alertType, $minsSince)
            }
        } catch {}
    }

    $alerts = @()
    if ($isStale) { $alerts += "SNAPSHOT STALE ${snapshotAge}min (threshold 90min) - CC must checkpoint or wrap" }
    if ($isDrift) { $alerts += "IDENTITY DRIFT - missing: $($missingMarkers -join ', ') - invoke /anchor" }
    $busMsg = "[CC ARCHON ALERT $obsNow] $($alerts -join ' | ') | Kiki: $kikiStatus | Blockers: $activeBlockers"
    $urgency = 'blocking'
    $to = 'cc'

    if (-not $skipBusPost) {
        Set-Content -Path $LastAlertFile -Value ($alertType + '|' + $nowDt.ToString('o')) -Encoding UTF8
    }
} else {
    $busMsg = "[CC ARCHON OK $obsNow] Identity INTACT. Snapshot age: ${snapshotAge}min. Kiki: $kikiStatus. Open blockers: $activeBlockers. Recent: $memoryRecent"
    $urgency = 'informational'
    $to = 'all'
    Remove-Item $LastAlertFile -ErrorAction SilentlyContinue
}

if ($skipBusPost) {
    Write-Log 'Bus post SKIPPED (dedup)'
} else {
    $tmpJson = Join-Path $env:TEMP 'archon_payload.json'
    $safeMsg = ($busMsg -replace '[^\x20-\x7E]', '' -replace '\\', '/').Trim()
    $payload = [ordered]@{
        token = $token
        from = 'cc'
        to = $to
        type = 'inform'
        urgency = $urgency
        content = $safeMsg
    } | ConvertTo-Json -Compress

    try {
        Set-Content -Path $tmpJson -Value $payload -Encoding UTF8
        scp -q $tmpJson 'vault-neo:/tmp/archon_payload.json' 2>$null
        scp -q (Join-Path $ScriptRepo 'Scripts\archon_bus_post.py') 'vault-neo:/tmp/archon_bus_post.py' 2>$null
        $busResult = ssh vault-neo 'python3 /tmp/archon_bus_post.py' 2>&1
        Write-Log ("Bus post: {0}" -f $busResult)
    } catch {
        Write-Log ("ERROR posting to bus: {0}" -f $_.Exception.Message)
    } finally {
        Remove-Item $tmpJson -ErrorAction SilentlyContinue
    }
}

$checkResult = & py -3 (Join-Path $ScriptRepo 'Scripts\cc_email_daemon.py') check 2>&1
Write-Log ("Email check: {0}" -f $checkResult)

$statusResult = & py -3 (Join-Path $ScriptRepo 'Scripts\cc_email_daemon.py') status 2>&1
Write-Log ("Status email: {0}" -f $statusResult)

$personalResult = & py -3 (Join-Path $ScriptRepo 'Scripts\cc_email_daemon.py') personal 2>&1
Write-Log ("Personal: {0}" -f $personalResult)

if (-not $env:P1_OLLAMA_MODEL) {
    $env:P1_OLLAMA_MODEL = 'gemma3:1b'
}
$karpathyResult = & py -3 (Join-Path $ScriptRepo 'Scripts\karpathy_loop.py') propose 2>&1
Write-Log ("Karpathy: {0}" -f $karpathyResult)

Write-Log ("CC ArchonAgent complete. State={0}" -f $stateTag)
