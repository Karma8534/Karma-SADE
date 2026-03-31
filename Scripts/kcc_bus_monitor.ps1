<#
.SYNOPSIS
    KCC Codex Bus Monitor — polls coordination bus for ArchonPrime analysis requests.
.DESCRIPTION
    Long-running daemon. Polls bus every 60s for messages to="codex" or containing
    "ArchonPrime"/"analyze". When triggered, calls kcc_codex_trigger.ps1 and posts
    the Codex response back to the bus as [ARCHONPRIME] analysis.
    Persists processed IDs to disk to survive restarts (P022 lesson).
.NOTES
    Run as karma user. Register as KCC-Codex-Monitor scheduled task (run at login).
    Processed IDs: $env:TEMP\kcc_processed_ids.json (survives most restarts)
    Hub token: fetched via SSH vault-neo at startup and refreshed every 10 cycles.
#>

$ErrorActionPreference = "Continue"

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$TriggerScript = Join-Path $ScriptDir "kcc_codex_trigger.ps1"
$ProcessedFile = "$env:TEMP\kcc_processed_ids.json"
$LogFile     = Join-Path (Split-Path $ScriptDir) "Logs\kcc_bus_monitor.log"
$HubUrl      = "https://hub.arknexus.net"
$PollInterval = 60  # seconds
$TokenRefreshEvery = 10  # cycles

function Write-Log($msg) {
    $ts = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -ErrorAction SilentlyContinue
}

function Get-HubToken {
    try {
        $t = (ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt" 2>$null).Trim()
        if (-not $t) { throw "empty" }
        return $t
    } catch {
        Write-Log "ERROR: could not get hub token: $_"
        return $null
    }
}

function Load-ProcessedIds {
    if (Test-Path $ProcessedFile) {
        try {
            return (Get-Content $ProcessedFile -Raw | ConvertFrom-Json -ErrorAction Stop)
        } catch { return @() }
    }
    return @()
}

function Save-ProcessedIds($ids) {
    try {
        # Keep last 1000 IDs to bound file size
        $trimmed = @($ids | Select-Object -Last 1000)
        $trimmed | ConvertTo-Json -Compress | Set-Content $ProcessedFile -Encoding UTF8
    } catch { Write-Log "WARN: could not save processed IDs: $_" }
}

function Is-CodexRequest($msg) {
    # Route: explicit to=codex, or content contains trigger keywords
    if ($msg.to -eq "codex") { return $true }
    $c = [string]$msg.content
    if ($c -match '(?i)(ArchonPrime\s+analysis|analyze\s+this\s+bus|to\s*=\s*codex)') { return $true }
    return $false
}

function Build-AnalysisPrompt($msg) {
    $from    = $msg.from
    $content = $msg.content
    $ts      = $msg.created_at
    return "You are ArchonPrime (Codex), a code and architecture analysis agent. A coordination bus event was received at $ts from '$from'. Analyze it and provide your assessment. Be concise (3-5 sentences max).`n`nBus event content:`n$content"
}

function Post-ToBus($token, $content) {
    $safeContent = ($content -replace '[^\x20-\x7E\r\n]', '').Trim()
    if ($safeContent.Length -gt 2000) { $safeContent = $safeContent.Substring(0, 2000) + "..." }
    $body = [ordered]@{
        from    = "codex"
        to      = "all"
        type    = "inform"
        urgency = "informational"
        content = "[ARCHONPRIME] $safeContent"
    } | ConvertTo-Json -Compress

    try {
        $result = Invoke-WebRequest -Uri "$HubUrl/v1/coordination/post" `
            -Method POST `
            -Headers @{ Authorization = "Bearer $token" } `
            -Body $body `
            -ContentType "application/json" `
            -UseBasicParsing `
            -TimeoutSec 15
        $json = $result.Content | ConvertFrom-Json
        return $json.id
    } catch {
        Write-Log "ERROR posting ArchonPrime response: $_"
        return $null
    }
}

function Poll-Bus($token, [ref]$processedIds) {
    try {
        $resp = Invoke-WebRequest -Uri "$HubUrl/v1/coordination/recent?limit=20&status=pending" `
            -Headers @{ Authorization = "Bearer $token" } `
            -UseBasicParsing `
            -TimeoutSec 15
        $data = $resp.Content | ConvertFrom-Json
        $entries = $data.entries
    } catch {
        Write-Log "WARN: bus poll failed: $_"
        return
    }

    foreach ($msg in $entries) {
        $id = $msg.id
        if (-not $id) { continue }
        if ($processedIds.Value -contains $id) { continue }
        if (-not (Is-CodexRequest $msg)) { continue }

        Write-Log "Codex request detected: $id | from=$($msg.from) | to=$($msg.to)"
        Write-Log "Content: $($msg.content.Substring(0, [Math]::Min(120, $msg.content.Length)))..."

        # Build analysis prompt and call trigger
        $prompt = Build-AnalysisPrompt $msg
        $analysis = & $TriggerScript -Prompt $prompt

        if ($analysis) {
            Write-Log "Codex analysis received ($($analysis.Length) chars)"
            $postId = Post-ToBus $token $analysis
            if ($postId) {
                Write-Log "ArchonPrime response posted: $postId"
            }
        } else {
            Write-Log "WARN: Codex trigger returned no output for $id"
        }

        # Mark as processed even if trigger failed — avoid retry loop
        $processedIds.Value = @($processedIds.Value) + $id
        Save-ProcessedIds $processedIds.Value
    }
}

# ── Main loop ────────────────────────────────────────────────────────────────
Write-Log "KCC Codex Bus Monitor starting. PollInterval=${PollInterval}s"

if (-not (Test-Path $TriggerScript)) {
    Write-Log "FATAL: kcc_codex_trigger.ps1 not found at $TriggerScript"
    exit 1
}

$processedIds = [ref](Load-ProcessedIds)
Write-Log "Loaded $($processedIds.Value.Count) processed IDs from disk"

$Token     = Get-HubToken
$CycleCount = 0

if (-not $Token) {
    Write-Log "FATAL: could not get hub token at startup"
    exit 1
}

Write-Log "Hub token acquired. Entering poll loop."

while ($true) {
    $CycleCount++

    # Refresh token every N cycles
    if ($CycleCount % $TokenRefreshEvery -eq 0) {
        $newToken = Get-HubToken
        if ($newToken) { $Token = $newToken; Write-Log "Token refreshed (cycle $CycleCount)" }
    }

    Poll-Bus $Token ([ref]$processedIds.Value)

    Start-Sleep -Seconds $PollInterval
}
