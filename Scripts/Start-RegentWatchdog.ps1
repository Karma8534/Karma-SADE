# Start-RegentWatchdog.ps1 — Hidden launcher for regent_watchdog.py
# Runs pythonw (no console window) with regent_watchdog.py
# Registered as KarmaRegentWatchdog scheduled task

$scriptPath = "C:\Users\raest\Documents\Karma_SADE\Scripts\regent_watchdog.py"
$logPath = "C:\Users\raest\Documents\Karma_SADE\tmp\regent_watchdog.log"
$MutexName = "Global\KarmaRegentWatchdogLauncher"

# Use pythonw for no-console, fall back to python with hidden window
$pythonw = "C:\Python314\pythonw.exe"
$python = "C:\Python314\python.exe"

if (Test-Path $pythonw) {
    $pythonTarget = $pythonw
} elseif (Test-Path $python) {
    $pythonTarget = $python
} else {
    Write-Error "Python not found at expected paths"
    exit 1
}

$mutex = New-Object System.Threading.Mutex($false, $MutexName)
$hasHandle = $false
try {
    $hasHandle = $mutex.WaitOne(0, $false)
} catch [System.Threading.AbandonedMutexException] {
    $hasHandle = $true
}

if (-not $hasHandle) {
    Write-Host "[regent-watchdog] Another launcher already owns $MutexName — exiting"
    exit 0
}

try {
    while ($true) {
        $proc = Start-Process -FilePath $pythonTarget `
            -ArgumentList $scriptPath `
            -WindowStyle Hidden `
            -RedirectStandardOutput $logPath `
            -RedirectStandardError "$logPath.err" `
            -PassThru
        $proc.WaitForExit()
        Start-Sleep -Seconds 10
    }
}
finally {
    if ($hasHandle) {
        $mutex.ReleaseMutex() | Out-Null
    }
    $mutex.Dispose()
}
