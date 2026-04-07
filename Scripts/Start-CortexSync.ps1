$WorkDir = "C:\Users\raest\Documents\Karma_SADE"
$ScriptPath = "$WorkDir\Scripts\cortex\sync_k2_to_p1.py"
$LogDir = "$WorkDir\Logs"
$LogFile = "$LogDir\cortex-sync.log"
$ErrFile = "$LogDir\cortex-sync.err.log"
$IntervalSeconds = 300
$MutexName = "Global\KarmaCortexSyncLauncher"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

if (-not (Test-Path $ScriptPath)) {
    throw "Missing sync script: $ScriptPath"
}

$mutex = New-Object System.Threading.Mutex($false, $MutexName)
$hasHandle = $false
try {
    $hasHandle = $mutex.WaitOne(0, $false)
} catch [System.Threading.AbandonedMutexException] {
    $hasHandle = $true
}

if (-not $hasHandle) {
    Write-Host "[cortex-sync] Another launcher already owns $MutexName — exiting"
    exit 0
}

try {
    while ($true) {
        $proc = Start-Process python `
            -ArgumentList "`"$ScriptPath`"" `
            -WorkingDirectory $WorkDir `
            -RedirectStandardOutput $LogFile `
            -RedirectStandardError $ErrFile `
            -WindowStyle Hidden `
            -PassThru

        $proc.WaitForExit()
        Start-Sleep -Seconds $IntervalSeconds
    }
}
finally {
    if ($hasHandle) {
        $mutex.ReleaseMutex() | Out-Null
    }
    $mutex.Dispose()
}
