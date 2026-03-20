$env:HUB_CHAT_TOKEN = "cb5617b2ce67470d389dcff1e1fe417aa2626ae699c7d5f831b133cb1f4d450e"
while ($true) {
    Write-Host "[cc-server] Starting..."
    python C:\Users\raest\Documents\Karma_SADE\Scripts\cc_server_p1.py
    Write-Host "[cc-server] Crashed or stopped. Restarting in 5s..."
    Start-Sleep 5
}
