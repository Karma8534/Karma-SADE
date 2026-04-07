# Start-ChannelsBridge.ps1
# P0N-B Channels Bridge — registered as Windows startup (HKCU Run key)
# Runs channels_bridge.py, survives reboot, auto-restarts on failure.

$WorkDir   = "C:\Users\raest\Documents\Karma_SADE"
$Script    = "$WorkDir\Scripts\channels_bridge.py"
$LogFile   = "$WorkDir\Logs\channels-bridge.log"
$TokenFile = "$WorkDir\.hub-chat-token"
$MutexName = "Global\KarmaChannelsBridgeLauncher"

# Ensure log directory exists
if (-not (Test-Path "$WorkDir\Logs")) {
    New-Item -ItemType Directory -Path "$WorkDir\Logs" | Out-Null
}

$mutex = New-Object System.Threading.Mutex($false, $MutexName)
$hasHandle = $false
try {
    $hasHandle = $mutex.WaitOne(0, $false)
} catch [System.Threading.AbandonedMutexException] {
    $hasHandle = $true
}

if (-not $hasHandle) {
    Write-Host "[channels-bridge] Another launcher already owns $MutexName — exiting"
    exit 0
}

# Load token from local cache
if (Test-Path $TokenFile) {
    $env:HUB_CHAT_TOKEN = (Get-Content $TokenFile -Raw).Trim()
} else {
    Write-Host "[channels-bridge] WARNING: No token file at $TokenFile"
}

Write-Host "[channels-bridge] Starting at $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"

# Auto-restart loop — if bridge crashes, restart after 5s
try {
    while ($true) {
        $proc = Start-Process python -ArgumentList $Script `
            -WorkingDirectory $WorkDir `
            -RedirectStandardOutput $LogFile `
            -RedirectStandardError "$WorkDir\Logs\channels-bridge-err.log" `
            -WindowStyle Hidden `
            -PassThru

        Write-Host "[channels-bridge] PID $($proc.Id) started at $(Get-Date -Format 'HH:mm:ss')"
        $proc.WaitForExit()
        $exitCode = $proc.ExitCode
        Write-Host "[channels-bridge] Exited code $exitCode at $(Get-Date -Format 'HH:mm:ss') — restarting in 5s"
        Start-Sleep -Seconds 5
    }
}
finally {
    if ($hasHandle) {
        $mutex.ReleaseMutex() | Out-Null
    }
    $mutex.Dispose()
}
