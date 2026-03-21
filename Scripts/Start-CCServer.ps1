# Start-CCServer.ps1
# Persistent CC server on P1 — registered as Scheduled Task (KarmaFileServer pattern)
# Runs cc_server_p1.py on port 7891, survives reboot, auto-restarts on failure.

$WorkDir   = "C:\Users\raest\Documents\Karma_SADE"
$Script    = "$WorkDir\Scripts\cc_server_p1.py"
$LogFile   = "$WorkDir\Logs\cc-server.log"
$TokenFile = "$WorkDir\.hub-chat-token"
$PidFile   = "$WorkDir\Scripts\cc_server.pid"

# Ensure log directory exists
if (-not (Test-Path "$WorkDir\Logs")) {
    New-Item -ItemType Directory -Path "$WorkDir\Logs" | Out-Null
}

# Load token from local cache
if (Test-Path $TokenFile) {
    $env:HUB_CHAT_TOKEN = (Get-Content $TokenFile -Raw).Trim()
} else {
    Write-Host "[cc-server] WARNING: No token file found at $TokenFile — auth disabled"
}

Write-Host "[cc-server] Starting cc_server_p1.py on port 7891 at $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"

# Auto-restart loop — if server crashes, restart after 10s
while ($true) {
    $proc = Start-Process python -ArgumentList $Script `
        -WorkingDirectory $WorkDir `
        -RedirectStandardOutput $LogFile `
        -RedirectStandardError "$WorkDir\Logs\cc-server-err.log" `
        -PassThru -NoNewWindow

    # Write PID for monitoring
    $proc.Id | Out-File $PidFile -Encoding ascii

    Write-Host "[cc-server] PID $($proc.Id) started at $(Get-Date -Format 'HH:mm:ss')"
    $proc.WaitForExit()
    $exitCode = $proc.ExitCode

    Write-Host "[cc-server] Exited with code $exitCode at $(Get-Date -Format 'HH:mm:ss') — restarting in 10s"
    Start-Sleep -Seconds 10
}
