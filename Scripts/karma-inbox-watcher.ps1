# karma-inbox-watcher.ps1
# Watches OneDrive/Karma/Inbox and OneDrive/Karma/Gated for new PDF/text files.
#
# Inbox/  — entity extraction only (fast pipeline, auto-processed)
# Gated/  — entity extraction + queued for Karma's deliberate conversational review
#           (files flagged priority:true in /v1/ingest → written to review_queue.jsonl)
#
# Rate-limit behavior:
#   - On 429/rate-limit: backs off $RateLimitBackoffSec, retries up to $MaxRetries
#   - After max retries: writes $filename.jammed.txt sidecar and leaves file in Processing/
#   - Jammed files require manual intervention (move back to Inbox/Gated to retry)
#
# Time-window scheduling (batch only, live events always process):
#   - Set $ProcessingWindowStart/$ProcessingWindowEnd to restrict startup batch to off-peak hours
#   - 0/0 (default) = no restriction
#   - Example: -ProcessingWindowStart 22 -ProcessingWindowEnd 6  (10pm–6am)
#
# Usage:
#   pwsh -File karma-inbox-watcher.ps1
#   pwsh -File karma-inbox-watcher.ps1 -ProcessingWindowStart 22 -ProcessingWindowEnd 6
#   pwsh -File karma-inbox-watcher.ps1 -InboxPath "G:\My Drive\Karma\Inbox"  # Google Drive
#
# Install as scheduled task (run at login, stays in background):
#   $action = New-ScheduledTaskAction -Execute "pwsh" -Argument "-WindowStyle Hidden -File C:\Users\raest\Documents\Karma_SADE\scripts\karma-inbox-watcher.ps1"
#   $trigger = New-ScheduledTaskTrigger -AtLogOn
#   Register-ScheduledTask -TaskName "KarmaInboxWatcher" -Action $action -Trigger $trigger -RunLevel Highest

param(
    [string]$InboxPath              = "$env:USERPROFILE\Documents\Karma_SADE\Karma_PDFs\Inbox",
    [string]$ProcessingPath         = "$env:USERPROFILE\Documents\Karma_SADE\Karma_PDFs\Processing",
    [string]$DonePath               = "$env:USERPROFILE\Documents\Karma_SADE\Karma_PDFs\Reviewed",
    [string]$GatedPath              = "$env:USERPROFILE\Documents\Karma_SADE\Karma_PDFs\Gated",
    [string]$HubUrl                 = "https://hub.arknexus.net/v1/ingest",
    [string]$TokenFile              = "$env:USERPROFILE\Documents\Karma_SADE\.hub-chat-token",
    [int]$IngestDelaySec            = 8,    # seconds between batch files — prevents GLM rate-limit starvation
    [int]$MaxRetries                = 3,    # max attempts per file before jamming
    [int]$RateLimitBackoffSec       = 60,   # seconds to wait after a 429 before retrying
    [int]$ProcessingWindowStart     = 0,    # hour (0-23) batch window opens; 0 = no restriction
    [int]$ProcessingWindowEnd       = 0     # hour (0-23) batch window closes; 0 = no restriction
)

$ErrorActionPreference = "Continue"

# Verify paths
foreach ($p in @($InboxPath, $ProcessingPath, $DonePath, $GatedPath)) {
    if (-not (Test-Path $p)) {
        New-Item -ItemType Directory -Path $p -Force | Out-Null
        Write-Host "[INIT] Created: $p"
    }
}

# Load Bearer token
if (-not (Test-Path $TokenFile)) {
    Write-Error "Token file not found: $TokenFile"
    exit 1
}
$token = (Get-Content $TokenFile -Raw).Trim()

$SUPPORTED_EXTENSIONS = @('.pdf', '.PDF', '.txt', '.md', '.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.gif', '.GIF', '.webp', '.WEBP')

# Returns $true on success, $false on terminal failure, $null if jammed (left in Processing for manual recovery)
function Send-ToKarma {
    param(
        [string]$FilePath,
        [switch]$Priority,
        [switch]$IsLiveEvent   # live watcher events skip time-window but still honor rate-limit
    )

    $filename  = Split-Path $FilePath -Leaf
    $procFile  = Join-Path $ProcessingPath $filename
    $sourceDir = if ($Priority) { $GatedPath } else { $InboxPath }
    $tag       = if ($Priority) { '[GATED]' } else { '' }
    $ts        = { Get-Date -Format 'HH:mm:ss' }

    Write-Host "[$(& $ts)]$tag Processing: $filename"

    # Move to Processing/ so we know it's in flight
    try {
        Move-Item -Path $FilePath -Destination $procFile -Force
    } catch {
        Write-Host "[$(& $ts)] WARN: could not move to Processing — $_"
        return $false
    }

    # Encode file as base64
    try {
        $bytes = [System.IO.File]::ReadAllBytes($procFile)
        $b64   = [Convert]::ToBase64String($bytes)
    } catch {
        Write-Host "[$(& $ts)] ERROR: could not read file — $_"
        try { Move-Item -Path $procFile -Destination (Join-Path $sourceDir $filename) -Force } catch {}
        return $false
    }

    $hint = [System.IO.Path]::GetFileNameWithoutExtension($filename) -replace '[-_]', ' '
    $bodyObj = @{
        file_b64 = $b64
        filename = $filename
        hint     = $hint
    }
    if ($Priority) { $bodyObj['priority'] = $true }
    $bodyJson = $bodyObj | ConvertTo-Json -Depth 2 -Compress

    $attempt = 0

    while ($attempt -lt $MaxRetries) {
        $attempt++
        try {
            $response = Invoke-RestMethod `
                -Uri $HubUrl `
                -Method POST `
                -Headers @{
                    Authorization  = "Bearer $token"
                    "Content-Type" = "application/json"
                } `
                -Body $bodyJson `
                -TimeoutSec 180

            # Success — write .verdict.txt sidecar
            $verdictFile = Join-Path $DonePath "$filename.verdict.txt"
            $resultLines = $response.results | ForEach-Object {
                "  chunk $($_.chunk): $($_.signal) — $($_.synthesis)"
            }
            $gatedNote = if ($Priority) { "`npriority: true (queued for Karma review)" } else { "" }
            $verdictText = @"
file: $filename
processed_at: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')
chunks: $($response.chunks)$gatedNote
results:
$($resultLines -join "`n")
"@
            $verdictText | Set-Content -Path $verdictFile -Encoding UTF8
            Move-Item -Path $procFile -Destination (Join-Path $DonePath $filename) -Force
            $priorityNote = if ($Priority) { ' [queued for Karma review]' } else { '' }
            Write-Host "[$(& $ts)] Done: $filename ($($response.chunks) chunk(s))$priorityNote"
            return $true

        } catch {
            # Detect rate-limit (429) vs other error
            $isRateLimit = $false
            try {
                if ($_.Exception.Response) {
                    $statusCode = [int]$_.Exception.Response.StatusCode
                    if ($statusCode -eq 429) { $isRateLimit = $true }
                }
            } catch {}
            # Also catch rate-limit signals in exception message text
            if ($_.ToString() -match '429|rate.?limit|too many request') { $isRateLimit = $true }

            if ($isRateLimit) {
                if ($attempt -lt $MaxRetries) {
                    Write-Host "[$(& $ts)] RATE-LIMIT: $filename (attempt $attempt/$MaxRetries) — backing off ${RateLimitBackoffSec}s"
                    Start-Sleep -Seconds $RateLimitBackoffSec
                    continue
                }

                # Max retries exhausted — jam the file
                Write-Host "[$(& $ts)] JAMMED: $filename — rate-limited after $MaxRetries attempts. File left in Processing/ for manual recovery."
                $jamFile = Join-Path $ProcessingPath "$filename.jammed.txt"
                @"
file: $filename
jammed_at: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')
reason: rate-limit (429) after $MaxRetries attempts
action_required: Move $filename from Processing\ back to $(if ($Priority) { 'Gated' } else { 'Inbox' })\ to retry
"@ | Set-Content -Path $jamFile -Encoding UTF8
                return $null  # $null = jammed, file intentionally left in Processing

            } else {
                # Non-rate-limit error — don't retry, move back to source
                Write-Host "[$(& $ts)] ERROR: $filename — $_"
                try { Move-Item -Path $procFile -Destination (Join-Path $sourceDir $filename) -Force } catch {}
                "$_" | Set-Content -Path (Join-Path $sourceDir "$filename.error.txt") -Encoding UTF8
                return $false
            }
        }
    }
    return $false
}

# Waits until the processing window opens (batch only). Returns immediately if no window configured.
function Wait-ForProcessingWindow {
    if ($ProcessingWindowStart -eq 0 -and $ProcessingWindowEnd -eq 0) { return }

    $now         = Get-Date
    $currentHour = $now.Hour

    $inWindow = if ($ProcessingWindowStart -le $ProcessingWindowEnd) {
        # Same-day window e.g. 8–18
        $currentHour -ge $ProcessingWindowStart -and $currentHour -lt $ProcessingWindowEnd
    } else {
        # Overnight window e.g. 22–6
        $currentHour -ge $ProcessingWindowStart -or $currentHour -lt $ProcessingWindowEnd
    }

    if ($inWindow) { return }

    # Calculate time until window opens
    $target = (Get-Date -Hour $ProcessingWindowStart -Minute 0 -Second 0)
    if ($target -le $now) { $target = $target.AddDays(1) }
    $waitMin = [int](($target - $now).TotalMinutes)

    Write-Host "[BATCH] Outside processing window ($ProcessingWindowStart`:00–$ProcessingWindowEnd`:00). Waiting $waitMin min until window opens at $($target.ToString('HH:mm'))..."
    Start-Sleep -Seconds ([int](($target - $now).TotalSeconds))
    Write-Host "[BATCH] Processing window open. Starting batch."
}

# Process any files already in Inbox at startup (batch — respects time window and IngestDelaySec)
Write-Host "[INIT] Checking Inbox for existing files..."
Wait-ForProcessingWindow
$inboxBatch = @(Get-ChildItem -Path $InboxPath -File | Where-Object {
    $SUPPORTED_EXTENSIONS -contains $_.Extension -and
    -not $_.Name.EndsWith('.error.txt') -and
    -not $_.Name.EndsWith('.verdict.txt') -and
    -not $_.Name.EndsWith('.jammed.txt')
})
Write-Host "[BATCH] $($inboxBatch.Count) file(s) in Inbox."
foreach ($f in $inboxBatch) {
    Send-ToKarma $f.FullName
    Start-Sleep -Seconds $IngestDelaySec
}

# Process any files already in Gated at startup
Write-Host "[INIT] Checking Gated for existing files..."
$gatedBatch = @(Get-ChildItem -Path $GatedPath -File | Where-Object {
    $SUPPORTED_EXTENSIONS -contains $_.Extension -and
    -not $_.Name.EndsWith('.error.txt') -and
    -not $_.Name.EndsWith('.verdict.txt') -and
    -not $_.Name.EndsWith('.jammed.txt')
})
Write-Host "[BATCH] $($gatedBatch.Count) file(s) in Gated."
foreach ($f in $gatedBatch) {
    Send-ToKarma $f.FullName -Priority
    Start-Sleep -Seconds $IngestDelaySec
}

# Set up FileSystemWatcher for Inbox (live events — no time-window, no IngestDelaySec)
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path                  = $InboxPath
$watcher.Filter                = "*.*"
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents   = $true

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $ext  = [System.IO.Path]::GetExtension($path).ToLower()
    $name = Split-Path $path -Leaf

    if ($name -match '\.(error|verdict|jammed)\.txt$') { return }
    if ($ext -notin @('.pdf', '.txt', '.md', '.jpg', '.jpeg', '.png', '.gif', '.webp')) { return }

    # Wait briefly for file to finish copying (OneDrive sync can be slow)
    Start-Sleep -Seconds 3

    if (Test-Path $path) {
        & $using:function:Send-ToKarma $path -IsLiveEvent
    }
}

Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action | Out-Null

# Set up FileSystemWatcher for Gated
$gatedWatcher = New-Object System.IO.FileSystemWatcher
$gatedWatcher.Path                  = $GatedPath
$gatedWatcher.Filter                = "*.*"
$gatedWatcher.IncludeSubdirectories = $false
$gatedWatcher.EnableRaisingEvents   = $true

$gatedAction = {
    $path = $Event.SourceEventArgs.FullPath
    $ext  = [System.IO.Path]::GetExtension($path).ToLower()
    $name = Split-Path $path -Leaf

    if ($name -match '\.(error|verdict|jammed)\.txt$') { return }
    if ($ext -notin @('.pdf', '.txt', '.md', '.jpg', '.jpeg', '.png', '.gif', '.webp')) { return }

    Start-Sleep -Seconds 3

    if (Test-Path $path) {
        & $using:function:Send-ToKarma $path -Priority -IsLiveEvent
    }
}

Register-ObjectEvent -InputObject $gatedWatcher -EventName Created -Action $gatedAction | Out-Null

Write-Host ""
Write-Host "Karma inbox watcher running."
Write-Host "  Inbox:         $InboxPath  (entity extraction only)"
Write-Host "  Gated:         $GatedPath  (entity extraction + queued for Karma review)"
Write-Host "  Processing:    $ProcessingPath"
Write-Host "  Done:          $DonePath"
Write-Host "  Hub:           $HubUrl"
Write-Host "  Batch delay:   ${IngestDelaySec}s between files"
Write-Host "  Rate-limit:    backoff ${RateLimitBackoffSec}s, max $MaxRetries retries (then → Processing/*.jammed.txt)"
if ($ProcessingWindowStart -ne 0 -or $ProcessingWindowEnd -ne 0) {
    Write-Host "  Batch window:  $ProcessingWindowStart`:00 – $ProcessingWindowEnd`:00 (live events process any time)"
} else {
    Write-Host "  Batch window:  unrestricted"
}
Write-Host "Press Ctrl+C to stop."
Write-Host ""

# Keep process alive
try {
    while ($true) { Start-Sleep -Seconds 10 }
} finally {
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    $gatedWatcher.EnableRaisingEvents = $false
    $gatedWatcher.Dispose()
    Write-Host "Watcher stopped."
}
