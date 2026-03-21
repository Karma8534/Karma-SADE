# Start-ArchonPrime.ps1
# PROOF-A: ArchonPrime Watcher — auto-restart wrapper
# Triggers Codex on K2 when structural bus events arrive.

$WorkDir   = "C:\Users\raest\Documents\Karma_SADE"
$Script    = "$WorkDir\Scripts\archonprime_watcher.py"
$LogFile   = "$WorkDir\Logs\archonprime.log"
$TokenFile = "$WorkDir\.hub-chat-token"

if (-not (Test-Path "$WorkDir\Logs")) {
    New-Item -ItemType Directory -Path "$WorkDir\Logs" | Out-Null
}

if (Test-Path $TokenFile) {
    $env:HUB_CHAT_TOKEN = (Get-Content $TokenFile -Raw).Trim()
}

Write-Host "[archonprime] Starting at $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"

while ($true) {
    $proc = Start-Process py -ArgumentList "-3 $Script" `
        -WorkingDirectory $WorkDir `
        -RedirectStandardOutput $LogFile `
        -RedirectStandardError "$WorkDir\Logs\archonprime-err.log" `
        -PassThru -NoNewWindow

    Write-Host "[archonprime] PID $($proc.Id) started"
    $proc.WaitForExit()
    Write-Host "[archonprime] Exited code $($proc.ExitCode) — restarting in 10s"
    Start-Sleep -Seconds 10
}
