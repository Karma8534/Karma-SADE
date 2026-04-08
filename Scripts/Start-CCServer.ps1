# Start-CCServer.ps1
# Persistent CC server on P1. Runs cc_server_p1.py on port 7891 and restarts on failure.

$WorkDir   = "C:\Users\raest\Documents\Karma_SADE"
$Script    = "$WorkDir\Scripts\cc_server_p1.py"
$LogFile   = "$WorkDir\Logs\cc-server.log"
$ErrFile   = "$WorkDir\Logs\cc-server-err.log"
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
    Write-Host "[cc-server] Another launcher already owns $MutexName; exiting"
    exit 0
}

try {
    if (-not (Test-Path "$WorkDir\Logs")) {
        New-Item -ItemType Directory -Path "$WorkDir\Logs" | Out-Null
    }

    if (Test-Path $TokenFile) {
        $env:HUB_CHAT_TOKEN = (Get-Content $TokenFile -Raw).Trim()
    } else {
        Write-Host "[cc-server] WARNING: token file missing at $TokenFile (auth disabled)"
    }

    Remove-Item Env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:CLAUDE_API_KEY -ErrorAction SilentlyContinue

    Write-Host "[cc-server] Starting cc_server_p1.py on port 7891 at $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK')"

    $existingPids = @(netstat -ano | Select-String ":7891 " | ForEach-Object {
        $parts = ($_ -split '\s+') | Where-Object { $_ -ne '' }
        $parts[-1]
    } | Select-Object -Unique)
    if ($existingPids.Count -gt 0) {
        Write-Host "[cc-server] Killing existing process(es) on 7891: $($existingPids -join ', ')"
        $existingPids | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
        Start-Sleep -Seconds 1
    }

    while ($true) {
        $arguments = if ($PythonExe -like "*\py.exe") { @("-3", $Script) } else { @($Script) }
        $proc = Start-Process $PythonExe -ArgumentList $arguments `
            -WorkingDirectory $WorkDir `
            -RedirectStandardOutput $LogFile `
            -RedirectStandardError $ErrFile `
            -WindowStyle Hidden `
            -PassThru

        $proc.Id | Out-File $PidFile -Encoding ascii
        Write-Host "[cc-server] PID $($proc.Id) started at $(Get-Date -Format 'HH:mm:ss')"
        $proc.WaitForExit()
        $exitCode = $proc.ExitCode
        Write-Host "[cc-server] Exited with code $exitCode at $(Get-Date -Format 'HH:mm:ss'); restarting in 10s"
        Start-Sleep -Seconds 10
    }
}
finally {
    if ($hasHandle) {
        $mutex.ReleaseMutex() | Out-Null
    }
    $mutex.Dispose()
}

