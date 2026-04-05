# Run-SessionIngest.ps1 — Nightly CC session extraction + review
# Registered as Windows Scheduled Task "KarmaSessionIngest" on P1
# Runs at 2:30 AM daily
# Uses K2 Ollama (qwen3:8b) at 100.75.109.92:11434 for review quality

param(
    [switch]$HiddenRelaunch
)

$ErrorActionPreference = "Continue"
. (Join-Path $PSScriptRoot "HiddenRelaunch.ps1")
Invoke-HiddenRelaunchIfNeeded -ScriptPath $PSCommandPath -HiddenRelaunch:$HiddenRelaunch

$RepoDir = "C:\Users\raest\Documents\Karma_SADE"
$LogFile = "$RepoDir\Logs\session_ingest.log"
$ObsWatermarkFile = "$RepoDir\Logs\session_obs_ingested.json"
$ClaudeMemUrl = "http://127.0.0.1:37778/api/memory/save"

$ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
Add-Content $LogFile "=== SESSION INGEST RUN $ts ==="

# Step 1: Extract new CC sessions from JSONL files
Write-Host "Step 1: Extracting CC sessions..."
Add-Content $LogFile "Step 1: extract_cc_sessions.py"

$env:PYTHONIOENCODING = "utf-8"
$result = & python3 "$RepoDir\Scripts\extract_cc_sessions.py" 2>&1
Add-Content $LogFile $result
Write-Host $result

# Step 2: Review new sessions with working local/fallback inference
Write-Host "Step 2: Reviewing sessions..."
Add-Content $LogFile "Step 2: session_review.py --source json (OLLAMA_URL=http://localhost:11434, REVIEW_MODEL=sam860/LFM2:350m, Groq fallback enabled)"

$env:OLLAMA_URL = "http://localhost:11434"
$env:REVIEW_MODEL = "sam860/LFM2:350m"
$result2 = & python3 "$RepoDir\Scripts\session_review.py" --source json 2>&1
Add-Content $LogFile $result2
Write-Host $result2

# Step 3: Emit observation list for CC to process next session
Write-Host "Step 3: Emitting observations..."
Add-Content $LogFile "Step 3: session_obs_writer.py"

$result3 = & python3 "$RepoDir\Scripts\session_obs_writer.py" 2>&1
$ObsFile = "$RepoDir\Logs\pending_observations.txt"
$result3 | Set-Content $ObsFile -Encoding UTF8
Add-Content $LogFile "Observations written to: $ObsFile"

# Step 4: Auto-save reviewed observations to claude-mem (idempotent via watermark)
Write-Host "Step 4: Saving observations to claude-mem..."
Add-Content $LogFile "Step 4: save reviewed observations to claude-mem"

$watermark = @{ hashes = @() }
if (Test-Path $ObsWatermarkFile) {
    try {
        $loaded = Get-Content $ObsWatermarkFile -Raw | ConvertFrom-Json
        if ($loaded -and $loaded.hashes) { $watermark.hashes = @($loaded.hashes) }
    } catch {}
}
$knownHashes = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($h in $watermark.hashes) { $null = $knownHashes.Add([string]$h) }

$obsText = ($result3 -join "`n")
$blocks = $obsText -split "(?m)^---\s*$"
$savedCount = 0

foreach ($block in $blocks) {
    $trimmed = $block.Trim()
    if (-not $trimmed.StartsWith("{")) { continue }
    try {
        $obs = $trimmed | ConvertFrom-Json
    } catch {
        continue
    }
    $obsTitle = if ($null -ne $obs.title) { [string]$obs.title } else { "" }
    $obsTextValue = if ($null -ne $obs.text) { [string]$obs.text } else { "" }
    $obsProject = if ($null -ne $obs.project) { [string]$obs.project } else { "Karma_SADE" }
    $hashSource = "{0}`n{1}" -f $obsTitle, $obsTextValue
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($hashSource)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha.ComputeHash($bytes)
    } finally {
        $sha.Dispose()
    }
    $hash = [System.BitConverter]::ToString($hashBytes).Replace("-", "").ToLowerInvariant()
    if ($knownHashes.Contains($hash)) { continue }
    try {
        $payload = @{
            title = $obsTitle
            text = $obsTextValue
            project = $obsProject
        } | ConvertTo-Json -Depth 4
        $resp = Invoke-RestMethod -Uri $ClaudeMemUrl -Method Post -ContentType "application/json" -Body $payload -TimeoutSec 10
        if ($resp.success -or $resp.id) {
            $null = $knownHashes.Add($hash)
            $savedCount += 1
        }
    } catch {
        Add-Content $LogFile "claude-mem save failed for reviewed observation: $($_.Exception.Message)"
    }
}

$outWatermark = @{ hashes = @($knownHashes) }
$outWatermark | ConvertTo-Json -Depth 4 | Set-Content $ObsWatermarkFile -Encoding UTF8
Add-Content $LogFile "Reviewed observations saved to claude-mem: $savedCount"
Write-Host "Reviewed observations saved to claude-mem: $savedCount"

$ts2 = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
Add-Content $LogFile "=== COMPLETE $ts2 ==="
Write-Host "Session ingest complete. Observations at: $ObsFile"
