# Start-CCServer.ps1
# Persistent CC server on P1 — registered as Scheduled Task (KarmaFileServer pattern)
# Runs cc_server_p1.py on port 7891, survives reboot, auto-restarts on failure.

$WorkDir   = "C:\Users\raest\Documents\Karma_SADE"
$Script    = "$WorkDir\Scripts\cc_server_p1.py"
$LogFile   = "$WorkDir\Logs\cc-server.log"
$TokenFile = "$WorkDir\.hub-chat-token"
$PidFile   = "$WorkDir\Scripts\cc_server.pid"
$MutexName = "Global\KarmaSovereignHarnessCCServer"
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonExe) {
    $PythonExe = (Get-Command py -ErrorAction SilentlyContinue).Source
}
if (-not $PythonExe) {
    throw "python executable not found in PATH"
}

$mutex = New-Object System.Threading.Mutex($false, $MutexName)
$hasHandle = $false
try {
    $hasHandle = $mutex.WaitOne(0, $false)
} catch [System.Threading.AbandonedMutexException] {
    $hasHandle = $true
}

if (-not $hasHandle) {
    Write-Host "[cc-server] Another Start-CCServer instance already owns $MutexName — exiting"
    exit 0
}

try {

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

    # Max/OAuth auth should not be shadowed by stale Anthropic Console API keys.
    Remove-Item Env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:CLAUDE_API_KEY -ErrorAction SilentlyContinue

    Write-Host "[cc-server] Starting cc_server_p1.py on port 7891 at $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"

    # Kill any existing processes on port 7891 before spawning new one
    $existingPids = @(netstat -ano | Select-String ":7891 " | ForEach-Object {
        $parts = ($_ -split '\s+') | Where-Object { $_ -ne '' }
        $parts[-1]
    } | Select-Object -Unique)
    if ($existingPids.Count -gt 0) {
        Write-Host "[cc-server] Killing $($existingPids.Count) existing process(es) on port 7891: $($existingPids -join ', ')"
        $existingPids | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
        Start-Sleep -Seconds 1
    }

    # Auto-restart loop — if server crashes, restart after 10s
    while ($true) {
        $arguments = if ($PythonExe -like "*\py.exe") { @("-3", $Script) } else { @($Script) }
        $proc = Start-Process $PythonExe -ArgumentList $arguments `
            -WorkingDirectory $WorkDir `
            -RedirectStandardOutput $LogFile `
            -RedirectStandardError "$WorkDir\Logs\cc-server-err.log" `
            -WindowStyle Hidden `
            -PassThru

        # Write PID for monitoring
        $proc.Id | Out-File $PidFile -Encoding ascii

        Write-Host "[cc-server] PID $($proc.Id) started at $(Get-Date -Format 'HH:mm:ss')"
        $proc.WaitForExit()
        $exitCode = $proc.ExitCode

        Write-Host "[cc-server] Exited with code $exitCode at $(Get-Date -Format 'HH:mm:ss') — restarting in 10s"
        Start-Sleep -Seconds 10
    }
}
finally {
    if ($hasHandle) {
        $mutex.ReleaseMutex() | Out-Null
    }
    $mutex.Dispose()
}
