# Start-RegentWatchdog.ps1 — Hidden launcher for regent_watchdog.py
# Runs pythonw (no console window) with regent_watchdog.py
# Registered as KarmaRegentWatchdog scheduled task

$scriptPath = "C:\Users\raest\Documents\Karma_SADE\Scripts\regent_watchdog.py"
$logPath = "C:\Users\raest\Documents\Karma_SADE\tmp\regent_watchdog.log"

# Use pythonw for no-console, fall back to python with hidden window
$pythonw = "C:\Python314\pythonw.exe"
$python = "C:\Python314\python.exe"

if (Test-Path $pythonw) {
    Start-Process -FilePath $pythonw -ArgumentList $scriptPath -WindowStyle Hidden -RedirectStandardOutput $logPath -RedirectStandardError "$logPath.err"
} elseif (Test-Path $python) {
    Start-Process -FilePath $python -ArgumentList $scriptPath -WindowStyle Hidden -RedirectStandardOutput $logPath -RedirectStandardError "$logPath.err"
} else {
    Write-Error "Python not found at expected paths"
    exit 1
}
