<#
NexusContinuation.ps1
Lightweight continuation/heartbeat for Nexus build.
- Runs sovereign email check
- Skips if tmp\CONTINUATION_PAUSE exists
- Writes log and state to tmp\
Safe to run every 5 minutes via Task Scheduler.
#>

$ErrorActionPreference = 'Stop'

$repo   = "C:\Users\raest\Documents\Karma_SADE"
$tmp    = Join-Path $repo "tmp"
$log    = Join-Path $tmp "continuation_worker.log"
$state  = Join-Path $tmp "continuation_worker_state.json"
$pause  = Join-Path $tmp "CONTINUATION_PAUSE"

New-Item -ItemType Directory -Path $tmp -Force | Out-Null

$now = Get-Date
$entry = [ordered]@{
    ts            = $now.ToString("o")
    paused        = $false
    actions       = @()
    results       = @{}
    ok            = $true
}

function Write-Log($msg) {
    $line = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    Add-Content -Path $log -Value $line
}

try {
    if (Test-Path $pause) {
        $entry.paused = $true
        $entry.ok = $true
        Write-Log "[paused] CONTINUATION_PAUSE present, skipping run"
    } else {
        # Sovereign email check
        $entry.actions += "cc_email_daemon_check"
        $checkOut = & py -3 (Join-Path $repo "Scripts\cc_email_daemon.py") check 2>&1
        $entry.results.cc_email_daemon_check = $checkOut -join "`n"
        Write-Log "[email_check] $($entry.results.cc_email_daemon_check | Out-String -Width 200).Trim()"
    }
}
catch {
    $entry.ok = $false
    $entry.results.error = $_.Exception.Message
    Write-Log "[error] $_"
}
finally {
    $entry | ConvertTo-Json -Depth 5 | Set-Content -Path $state -Encoding UTF8
}
