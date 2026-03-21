# P0N-B: Start Channels Bridge with auto-restart
# Usage: powershell -WindowStyle Hidden -File Scripts\start_channels_bridge.ps1

$TokenFile = Join-Path $PSScriptRoot "..\.hub-chat-token"
if (Test-Path $TokenFile) {
    $env:HUB_CHAT_TOKEN = (Get-Content $TokenFile -Raw).Trim()
}

$ScriptPath = Join-Path $PSScriptRoot "channels_bridge.py"
$WorkDir = Split-Path $PSScriptRoot -Parent

Write-Host "[start_channels_bridge] Starting Channels Bridge (P0N-B)..."

while ($true) {
    try {
        $proc = Start-Process -FilePath "python" -ArgumentList "`"$ScriptPath`"" `
            -WorkingDirectory $WorkDir -NoNewWindow -PassThru -Wait
        Write-Host "[start_channels_bridge] Bridge exited (code $($proc.ExitCode)), restarting in 5s..."
    } catch {
        Write-Host "[start_channels_bridge] Error: $_. Restarting in 5s..."
    }
    Start-Sleep -Seconds 5
}
