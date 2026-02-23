$scriptPath = "C:\Users\raest\Documents\Karma_SADE\Scripts\karma-inbox-watcher.ps1"

# Kill any existing watcher instances first
Get-Process pwsh -ErrorAction SilentlyContinue | Where-Object {
    try { $_.MainModule.FileName -match 'pwsh' } catch { $false }
} | ForEach-Object {
    # Check if it's running our watcher (by checking command line via WMI)
    $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($cmdline -match 'karma-inbox-watcher') {
        Write-Host "Stopping old watcher PID $($_.Id)"
        Stop-Process -Id $_.Id -Force
    }
}

# Start watcher as a hidden background process
$proc = Start-Process pwsh `
    -ArgumentList "-WindowStyle Hidden -NonInteractive -File `"$scriptPath`"" `
    -WindowStyle Hidden `
    -PassThru

Write-Host "KarmaInboxWatcher started. PID: $($proc.Id)"
Write-Host "Log: To check if running: Get-Process -Id $($proc.Id)"
$proc.Id | Set-Content "$env:USERPROFILE\Documents\Karma_SADE\.watcher.pid"
Write-Host "PID saved to .watcher.pid"
