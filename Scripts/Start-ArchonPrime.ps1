# Start-ArchonPrime.ps1
# PROOF-A: ArchonPrime Watcher — auto-restart wrapper
# Triggers Codex on K2 when structural bus events arrive.

$WorkDir   = "C:\Users\raest\Documents\Karma_SADE"
$Script    = "$WorkDir\Scripts\archonprime_watcher.py"
$LogFile   = "$WorkDir\Logs\archonprime.log"
$TokenFile = "$WorkDir\.hub-chat-token"
$MutexName = "Global\KarmaArchonPrimeLauncher"

if (-not (Test-Path "$WorkDir\Logs")) {
    New-Item -ItemType Directory -Path "$WorkDir\Logs" | Out-Null
}

if (Test-Path $TokenFile) {
    $env:HUB_CHAT_TOKEN = (Get-Content $TokenFile -Raw).Trim()
}

Write-Host "[archonprime] Starting at $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"

$mutex = New-Object System.Threading.Mutex($false, $MutexName)
$hasHandle = $false
try {
    $hasHandle = $mutex.WaitOne(0, $false)
} catch [System.Threading.AbandonedMutexException] {
    $hasHandle = $true
}

if (-not $hasHandle) {
    Write-Host "[archonprime] Another launcher already owns $MutexName — exiting"
    exit 0
}

try {
    while ($true) {
        $proc = Start-Process py -ArgumentList "-3 $Script" `
            -WorkingDirectory $WorkDir `
            -RedirectStandardOutput $LogFile `
            -RedirectStandardError "$WorkDir\Logs\archonprime-err.log" `
            -WindowStyle Hidden `
            -PassThru

        Write-Host "[archonprime] PID $($proc.Id) started"
        $proc.WaitForExit()
        Write-Host "[archonprime] Exited code $($proc.ExitCode) — restarting in 10s"
        Start-Sleep -Seconds 10
    }
}
finally {
    if ($hasHandle) {
        $mutex.ReleaseMutex() | Out-Null
    }
    $mutex.Dispose()
}
