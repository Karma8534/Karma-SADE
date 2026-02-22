# karma-inbox-watcher.ps1
# Watches OneDrive/Karma/Inbox and OneDrive/Karma/Gated for new PDF/text files.
#
# Inbox/  — entity extraction only (fast pipeline, auto-processed)
# Gated/  — entity extraction + queued for Karma's deliberate conversational review
#           (files flagged priority:true in /v1/ingest → written to review_queue.jsonl)
#
# Usage:
#   pwsh -File karma-inbox-watcher.ps1
#   pwsh -File karma-inbox-watcher.ps1 -InboxPath "G:\My Drive\Karma\Inbox"  # Google Drive
#
# Install as scheduled task (run at login, stays in background):
#   $action = New-ScheduledTaskAction -Execute "pwsh" -Argument "-WindowStyle Hidden -File C:\Users\raest\Documents\Karma_SADE\scripts\karma-inbox-watcher.ps1"
#   $trigger = New-ScheduledTaskTrigger -AtLogOn
#   Register-ScheduledTask -TaskName "KarmaInboxWatcher" -Action $action -Trigger $trigger -RunLevel Highest

param(
    [string]$InboxPath      = "$env:USERPROFILE\OneDrive\Karma\Inbox",
    [string]$ProcessingPath = "$env:USERPROFILE\OneDrive\Karma\Processing",
    [string]$DonePath       = "$env:USERPROFILE\OneDrive\Karma\Done",
    [string]$GatedPath      = "$env:USERPROFILE\OneDrive\Karma\Gated",
    [string]$HubUrl         = "https://hub.arknexus.net/v1/ingest",
    [string]$TokenFile      = "$env:USERPROFILE\Documents\Karma_SADE\.hub-chat-token"
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

function Send-ToKarma {
    param(
        [string]$FilePath,
        [switch]$Priority
    )

    $filename  = Split-Path $FilePath -Leaf
    $ext       = [System.IO.Path]::GetExtension($filename)
    $procFile  = Join-Path $ProcessingPath $filename
    $timestamp = Get-Date -Format 'HH:mm:ss'
    $tag       = if ($Priority) { '[GATED]' } else { '' }

    Write-Host "[$timestamp]$tag Processing: $filename"

    # Move to Processing/ so we know it's in flight
    try {
        Move-Item -Path $FilePath -Destination $procFile -Force
    } catch {
        Write-Host "[$timestamp] WARN: could not move to Processing — $_"
        return
    }

    try {
        # Encode file as base64
        $bytes = [System.IO.File]::ReadAllBytes($procFile)
        $b64   = [Convert]::ToBase64String($bytes)

        # Use filename (without extension) as topic hint
        $hint = [System.IO.Path]::GetFileNameWithoutExtension($filename) -replace '[-_]', ' '

        $bodyObj = @{
            file_b64 = $b64
            filename = $filename
            hint     = $hint
        }
        if ($Priority) { $bodyObj['priority'] = $true }
        $bodyJson = $bodyObj | ConvertTo-Json -Depth 2 -Compress

        # POST to hub-bridge /v1/ingest
        $response = Invoke-RestMethod `
            -Uri $HubUrl `
            -Method POST `
            -Headers @{
                Authorization  = "Bearer $token"
                "Content-Type" = "application/json"
            } `
            -Body $bodyJson `
            -TimeoutSec 180

        # Write .verdict.txt sidecar
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

        # Move to Done/
        Move-Item -Path $procFile -Destination (Join-Path $DonePath $filename) -Force
        $priorityNote = if ($Priority) { ' [queued for Karma review]' } else { '' }
        Write-Host "[$timestamp] Done: $filename ($($response.chunks) chunk(s))$priorityNote"

    } catch {
        Write-Host "[$timestamp] ERROR: $filename — $_"
        # Move back to source dir for retry, write error sidecar
        $sourceDir = if ($Priority) { $GatedPath } else { $InboxPath }
        try { Move-Item -Path $procFile -Destination (Join-Path $sourceDir $filename) -Force } catch {}
        "$_" | Set-Content -Path (Join-Path $sourceDir "$filename.error.txt") -Encoding UTF8
    }
}

# Process any files already in Inbox at startup
Write-Host "[INIT] Checking Inbox for existing files..."
Get-ChildItem -Path $InboxPath -File | Where-Object {
    $SUPPORTED_EXTENSIONS -contains $_.Extension -and
    -not $_.Name.EndsWith('.error.txt') -and
    -not $_.Name.EndsWith('.verdict.txt')
} | ForEach-Object {
    Send-ToKarma $_.FullName
}

# Process any files already in Gated at startup
Write-Host "[INIT] Checking Gated for existing files..."
Get-ChildItem -Path $GatedPath -File | Where-Object {
    $SUPPORTED_EXTENSIONS -contains $_.Extension -and
    -not $_.Name.EndsWith('.error.txt') -and
    -not $_.Name.EndsWith('.verdict.txt')
} | ForEach-Object {
    Send-ToKarma $_.FullName -Priority
}

# Set up FileSystemWatcher for Inbox
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path                  = $InboxPath
$watcher.Filter                = "*.*"
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents   = $true

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $ext  = [System.IO.Path]::GetExtension($path).ToLower()
    $name = Split-Path $path -Leaf

    # Skip error/verdict sidecars and unsupported types
    if ($name -match '\.(error|verdict)\.txt$') { return }
    if ($ext -notin @('.pdf', '.txt', '.md', '.jpg', '.jpeg', '.png', '.gif', '.webp')) { return }

    # Wait briefly for file to finish copying (OneDrive sync can be slow)
    Start-Sleep -Seconds 3

    # Verify file still exists and is readable
    if (Test-Path $path) {
        & $using:function:Send-ToKarma $path
    }
}

Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action | Out-Null

# Set up FileSystemWatcher for Gated (same logic, Priority=$true)
$gatedWatcher = New-Object System.IO.FileSystemWatcher
$gatedWatcher.Path                  = $GatedPath
$gatedWatcher.Filter                = "*.*"
$gatedWatcher.IncludeSubdirectories = $false
$gatedWatcher.EnableRaisingEvents   = $true

$gatedAction = {
    $path = $Event.SourceEventArgs.FullPath
    $ext  = [System.IO.Path]::GetExtension($path).ToLower()
    $name = Split-Path $path -Leaf

    if ($name -match '\.(error|verdict)\.txt$') { return }
    if ($ext -notin @('.pdf', '.txt', '.md', '.jpg', '.jpeg', '.png', '.gif', '.webp')) { return }

    Start-Sleep -Seconds 3

    if (Test-Path $path) {
        & $using:function:Send-ToKarma $path -Priority
    }
}

Register-ObjectEvent -InputObject $gatedWatcher -EventName Created -Action $gatedAction | Out-Null

Write-Host ""
Write-Host "Karma inbox watcher running."
Write-Host "  Inbox:      $InboxPath  (entity extraction only)"
Write-Host "  Gated:      $GatedPath  (entity extraction + queued for Karma review)"
Write-Host "  Processing: $ProcessingPath"
Write-Host "  Done:       $DonePath"
Write-Host "  Hub:        $HubUrl"
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
