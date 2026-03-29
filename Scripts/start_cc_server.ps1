# DEPRECATED — Use Start-CCServer.ps1 instead (reads token from file, has PID tracking + logging)
# This script exists only as a fallback. Token is loaded from .hub-chat-token file.
$TokenFile = "C:\Users\raest\Documents\Karma_SADE\.hub-chat-token"
if (Test-Path $TokenFile) {
    $env:HUB_CHAT_TOKEN = (Get-Content $TokenFile -Raw).Trim()
} else {
    Write-Host "[cc-server] WARNING: No token file at $TokenFile — auth disabled"
}
while ($true) {
    Write-Host "[cc-server] Starting..."
    python C:\Users\raest\Documents\Karma_SADE\Scripts\cc_server_p1.py
    Write-Host "[cc-server] Crashed or stopped. Restarting in 5s..."
    Start-Sleep 5
}
