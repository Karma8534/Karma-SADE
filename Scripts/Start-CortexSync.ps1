$WorkDir = "C:\Users\raest\Documents\Karma_SADE"
$ScriptPath = "$WorkDir\Scripts\cortex\sync_k2_to_p1.py"
$LogDir = "$WorkDir\Logs"
$LogFile = "$LogDir\cortex-sync.log"
$ErrFile = "$LogDir\cortex-sync.err.log"
$IntervalSeconds = 300

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

if (-not (Test-Path $ScriptPath)) {
    throw "Missing sync script: $ScriptPath"
}

while ($true) {
    $proc = Start-Process python `
        -ArgumentList "`"$ScriptPath`"" `
        -WorkingDirectory $WorkDir `
        -RedirectStandardOutput $LogFile `
        -RedirectStandardError $ErrFile `
        -PassThru `
        -NoNewWindow

    $proc.WaitForExit()
    Start-Sleep -Seconds $IntervalSeconds
}
