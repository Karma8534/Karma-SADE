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
    [int]$DebounceSeconds = 10,
    [int]$PollSeconds = 15,
    [switch]$HiddenRelaunch
)

$ErrorActionPreference = 'SilentlyContinue'
. (Join-Path $PSScriptRoot "HiddenRelaunch.ps1")
Invoke-HiddenRelaunchIfNeeded -ScriptPath $PSCommandPath -HiddenRelaunch:$HiddenRelaunch -ExtraArgs @(
    "-WatchDir", $WatchDir,
    "-ScriptDir", $ScriptDir,
    "-DebounceSeconds", $DebounceSeconds.ToString(),
    "-PollSeconds", $PollSeconds.ToString()
)

$LogFile = "$ScriptDir\Logs\karma_session_indexer.log"
$MutexName = "Global\KarmaSessionIndexer"
$indexerMutex = New-Object System.Threading.Mutex($false, $MutexName)
$hasIndexerHandle = $false
try {
    $hasIndexerHandle = $indexerMutex.WaitOne(0, $false)
} catch [System.Threading.AbandonedMutexException] {
    $hasIndexerHandle = $true
}

if (-not $hasIndexerHandle) {
    Write-Host "[KarmaSessionIndexer] Another instance already owns $MutexName. Exiting."
    exit 0
}

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

function Invoke-HarvestForFile {
    param(
        [Parameter(Mandatory = $true)][string]$FullPath,
        [Parameter(Mandatory = $true)][string]$Reason
    )

    $fileName = Split-Path $FullPath -Leaf
    Write-Log "Session file detected [$Reason]: $fileName"
    Start-Sleep -Seconds 3
    $result = python $HarvestScript 2>&1
    if ($LASTEXITCODE -eq 0) {
        $summary = ($result | Select-String 'New observations extracted|Done\.|Output:') | ForEach-Object { $_.Line.Trim() }
        Write-Log "Extraction complete for $fileName. $($summary -join ' | ')"
    } else {
        $tail = ($result | Select-Object -Last 3) -join ' '
        Write-Log "Extraction ERROR for $fileName`: $tail"
    }
}

Write-Log "Polling for .jsonl changes every $PollSeconds seconds."

$knownFiles = @{}
Get-ChildItem -Path $WatchDir -Filter '*.jsonl' -File | ForEach-Object {
    $knownFiles[$_.FullName] = $_.LastWriteTimeUtc
}

try {
    while ($true) {
        Start-Sleep -Seconds $PollSeconds
        $now = [datetime]::UtcNow
        Get-ChildItem -Path $WatchDir -Filter '*.jsonl' -File | ForEach-Object {
            $fullPath = $_.FullName
            $lastWrite = $_.LastWriteTimeUtc
            $knownWrite = $knownFiles[$fullPath]
            $ageSeconds = ($now - $lastWrite).TotalSeconds

            if ($ageSeconds -lt 2) {
                return
            }

            if (-not $knownFiles.ContainsKey($fullPath)) {
                $knownFiles[$fullPath] = $lastWrite
                Invoke-HarvestForFile -FullPath $fullPath -Reason 'created'
                return
            }

            if ($lastWrite -gt $knownWrite.AddSeconds($DebounceSeconds)) {
                $knownFiles[$fullPath] = $lastWrite
                Invoke-HarvestForFile -FullPath $fullPath -Reason 'changed'
            }
        }
    }
} finally {
    Write-Log "KarmaSessionIndexer stopped."
    if ($hasIndexerHandle) {
        $indexerMutex.ReleaseMutex() | Out-Null
    }
    $indexerMutex.Dispose()
}
