param()
# Diagnose watcher failure

Write-Output '=== ERROR FILES IN INBOX ==='
$errors = Get-ChildItem 'Karma_PDFs/Inbox' -Filter '*.error.txt'
foreach ($f in $errors) {
    Write-Output "--- $($f.Name) ---"
    Get-Content $f.FullName | Select-Object -First 30
    Write-Output ''
}

Write-Output '=== WATCHER LOG (last 50 lines) ==='
$logPath = 'Karma_PDFs/watcher.log'
if (Test-Path $logPath) {
    Get-Content $logPath -Tail 50
} else {
    Write-Output "No watcher.log at $logPath"
    $altLogs = Get-ChildItem 'Karma_PDFs' -Filter '*.log' -ErrorAction SilentlyContinue
    if ($altLogs) {
        foreach ($l in $altLogs) { Write-Output "  Found: $($l.FullName)" }
    }
}

Write-Output '=== TASK SCHEDULER ==='
$tasks = Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object { $_.TaskName -like '*karma*' -or $_.TaskName -like '*watcher*' -or $_.TaskName -like '*inbox*' }
if ($tasks) {
    $tasks | Select-Object TaskName, State | Format-Table -AutoSize
} else {
    Write-Output 'No scheduled tasks found for karma/watcher/inbox'
}
