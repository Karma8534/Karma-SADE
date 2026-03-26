# Start-ChromeDebug.ps1 — Launch Chrome with CDP debug port
# Ensures no existing Chrome processes interfere with debug port binding
# Use: Run at login via Scheduled Task or Desktop shortcut

$ChromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$DebugPort = 9222

# Kill any existing Chrome processes
$procs = Get-Process -Name chrome -ErrorAction SilentlyContinue
if ($procs) {
    Write-Host "[ChromeDebug] Stopping $($procs.Count) Chrome processes..."
    Stop-Process -Name chrome -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3

    # Verify dead
    $remaining = Get-Process -Name chrome -ErrorAction SilentlyContinue
    if ($remaining) {
        Write-Host "[ChromeDebug] WARNING: $($remaining.Count) Chrome processes still running"
        Stop-Process -Name chrome -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

Write-Host "[ChromeDebug] Launching Chrome with --remote-debugging-port=$DebugPort"
Start-Process $ChromePath -ArgumentList "--remote-debugging-port=$DebugPort"

# Wait for debug port to be available
$maxWait = 15
$waited = 0
while ($waited -lt $maxWait) {
    Start-Sleep -Seconds 1
    $waited++
    $test = Test-NetConnection 127.0.0.1 -Port $DebugPort -WarningAction SilentlyContinue
    if ($test.TcpTestSucceeded) {
        Write-Host "[ChromeDebug] Port $DebugPort is OPEN after ${waited}s"

        # Update DevToolsActivePort with real WebSocket path
        try {
            $version = Invoke-RestMethod "http://127.0.0.1:$DebugPort/json/version"
            $wsUrl = $version.webSocketDebuggerUrl
            if ($wsUrl -match "ws://127\.0\.0\.1:\d+(.+)") {
                $wsPath = $Matches[1]
                $portFileContent = "$DebugPort`n$wsPath"
                $portFilePath = Join-Path $env:LOCALAPPDATA "Google\Chrome\User Data\DevToolsActivePort"
                Set-Content -Path $portFilePath -Value $portFileContent -NoNewline
                Write-Host "[ChromeDebug] DevToolsActivePort updated: $DebugPort $wsPath"
            }
        } catch {
            Write-Host "[ChromeDebug] Could not update DevToolsActivePort: $_"
        }

        exit 0
    }
}

Write-Host "[ChromeDebug] WARNING: Port $DebugPort not open after ${maxWait}s"
exit 1
