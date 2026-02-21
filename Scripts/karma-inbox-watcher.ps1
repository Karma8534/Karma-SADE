# karma-inbox-watcher.ps1
# Watches OneDrive/Karma/Inbox for new PDF/text files and sends them to Karma for evaluation.
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
    [string]$HubUrl         = "https://hub.arknexus.net/v1/ingest",
    [string]$TokenFile      = "$env:USERPROFILE\Documents\Karma_SADE\.hub-chat-token"
)

$ErrorActionPreference = "Continue"

# Verify paths
foreach ($p in @($InboxPath, $ProcessingPath, $DonePath)) {
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
    param([string]$FilePath)

    $filename  = Split-Path $FilePath -Leaf
    $ext       = [System.IO.Path]::GetExtension($filename)
    $procFile  = Join-Path $ProcessingPath $filename
    $timestamp = Get-Date -Format 'HH:mm:ss'

    Write-Host "[$timestamp] Processing: $filename"

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
        $verdictText = @"
file: $filename
processed_at: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')
chunks: $($response.chunks)
results:
$($resultLines -join "`n")
"@
        $verdictText | Set-Content -Path $verdictFile -Encoding UTF8

        # Move to Done/
        Move-Item -Path $procFile -Destination (Join-Path $DonePath $filename) -Force
        Write-Host "[$timestamp] Done: $filename ($($response.chunks) chunk(s))"

    } catch {
        Write-Host "[$timestamp] ERROR: $filename — $_"
        # Move back to Inbox for retry, write error sidecar
        try { Move-Item -Path $procFile -Destination $FilePath -Force } catch {}
        "$_" | Set-Content -Path (Join-Path $InboxPath "$filename.error.txt") -Encoding UTF8
    }
}

# Process any files already in Inbox at startup
Write-Host "[INIT] Checking Inbox for existing files..."
Get-ChildItem -Path $InboxPath -File | Where-Object {
    $SUPPORTED_EXTENSIONS -contains $_.Extension -and
    -not $_.Name.EndsWith('.error.txt')
} | ForEach-Object {
    Send-ToKarma $_.FullName
}

# Set up FileSystemWatcher for new arrivals
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
    if ($ext -notin @('.pdf', '.txt', '.md', '.jpg', '.jpeg', '.png', '.gif', '.webp'))   { return }

    # Wait briefly for file to finish copying (OneDrive sync can be slow)
    Start-Sleep -Seconds 3

    # Verify file still exists and is readable
    if (Test-Path $path) {
        & $using:function:Send-ToKarma $path
    }
}

Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action | Out-Null

Write-Host ""
Write-Host "Karma inbox watcher running."
Write-Host "  Inbox:      $InboxPath"
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
    Write-Host "Watcher stopped."
}
