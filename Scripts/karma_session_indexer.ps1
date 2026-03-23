#Requires -Version 5.1
<#
.SYNOPSIS
    karma_session_indexer.ps1 — Plan-A Task 5 (A2)
    FileSystemWatcher on ~/.claude/projects/C--Users-raest-Documents-Karma-SADE/
    Detects new .jsonl session files and runs harvest_jsonl_sessions.py on them.
    Registered as Windows Scheduled Task "KarmaSessionIndexer" (trigger: at login).

.DESCRIPTION
    Watches for new Claude Code session files and auto-extracts observations
    to Scripts/harvest_jsonl_output.json for claude-mem ingestion.

.NOTES
    To register as scheduled task (run once as admin):
        schtasks /create /tn "KarmaSessionIndexer" /tr "powershell.exe -WindowStyle Hidden -File '$PSScriptRoot\karma_session_indexer.ps1'" /sc onlogon /ru "$env:USERNAME" /f

    To check if running:
        Get-ScheduledTask -TaskName "KarmaSessionIndexer"
#>

param(
    [string]$WatchDir = "$env:USERPROFILE\.claude\projects\C--Users-raest-Documents-Karma-SADE",
    [string]$ScriptDir = "$PSScriptRoot\..",
    [int]$DebounceSeconds = 10
)

$ErrorActionPreference = 'SilentlyContinue'
$LogFile = "$ScriptDir\Logs\karma_session_indexer.log"

# Ensure log directory exists
$null = New-Item -ItemType Directory -Force -Path (Split-Path $LogFile)

function Write-Log {
    param([string]$Message)
    $ts = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'
    $line = "[$ts] $Message"
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    Write-Host $line
}

if (-not (Test-Path $WatchDir)) {
    Write-Log "Watch directory not found: $WatchDir"
    exit 1
}

$HarvestScript = Join-Path $ScriptDir "Scripts\harvest_jsonl_sessions.py"
if (-not (Test-Path $HarvestScript)) {
    Write-Log "Harvest script not found: $HarvestScript"
    exit 1
}

Write-Log "KarmaSessionIndexer started. Watching: $WatchDir"

# FileSystemWatcher setup
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $WatchDir
$watcher.Filter = "*.jsonl"
$watcher.NotifyFilter = [System.IO.NotifyFilters]'FileName,LastWrite'
$watcher.EnableRaisingEvents = $true

# Debounce: track recently processed files
$recentlyProcessed = @{}

$action = {
    $eventFile = $Event.SourceEventArgs.FullPath
    $eventType = $Event.SourceEventArgs.ChangeType

    # Skip if recently processed (debounce)
    $now = [datetime]::UtcNow
    if ($recentlyProcessed.ContainsKey($eventFile)) {
        $lastProcessed = $recentlyProcessed[$eventFile]
        if (($now - $lastProcessed).TotalSeconds -lt $using:DebounceSeconds) {
            return
        }
    }
    $recentlyProcessed[$eventFile] = $now

    $fileName = Split-Path $eventFile -Leaf
    & $using:function:Write-Log "New session file detected [$eventType]: $fileName"

    # Wait briefly for file to finish writing
    Start-Sleep -Seconds 3

    # Run extraction on the new file only (via watermark it will skip already-processed)
    $result = python $using:HarvestScript 2>&1
    if ($LASTEXITCODE -eq 0) {
        & $using:function:Write-Log "Extraction complete for $fileName. Output: $($result | Select-String 'new observations')"
    } else {
        & $using:function:Write-Log "Extraction ERROR for $fileName`: $($result | Select-Object -Last 3)"
    }
}

# Register events
$createdJob = Register-ObjectEvent $watcher 'Created' -Action $action
$changedJob = Register-ObjectEvent $watcher 'Changed' -Action $action

Write-Log "Watching for new .jsonl files. Press Ctrl+C to stop (or task runs in background)."

# Keep alive loop — check every 60 seconds and log heartbeat
try {
    while ($true) {
        Start-Sleep -Seconds 60
        # Check for any pending events
        Get-Job | Where-Object { $_.HasMoreData } | Receive-Job | Out-Null
    }
} finally {
    Unregister-Event $createdJob.Id -ErrorAction SilentlyContinue
    Unregister-Event $changedJob.Id -ErrorAction SilentlyContinue
    $watcher.Dispose()
    Write-Log "KarmaSessionIndexer stopped."
}
