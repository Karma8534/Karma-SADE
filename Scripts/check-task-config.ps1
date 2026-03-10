param()
$task = Get-ScheduledTask -TaskName 'KarmaInboxWatcher' -ErrorAction SilentlyContinue
if (-not $task) { Write-Output 'Task not found'; exit }

Write-Output '=== ACTIONS ==='
foreach ($a in $task.Actions) {
    Write-Output "Execute: $($a.Execute)"
    Write-Output "Arguments: $($a.Arguments)"
    Write-Output "WorkDir: $($a.WorkingDirectory)"
}

Write-Output ''
Write-Output '=== TRIGGERS ==='
foreach ($t in $task.Triggers) {
    Write-Output "$($t.GetType().Name): Enabled=$($t.Enabled)"
}

Write-Output ''
Write-Output '=== SETTINGS ==='
$s = $task.Settings
Write-Output "ExecutionTimeLimit: $($s.ExecutionTimeLimit)"
Write-Output "RestartCount: $($s.RestartCount)"
Write-Output "RestartInterval: $($s.RestartInterval)"
Write-Output "StopIfGoingOnBatteries: $($s.StopIfGoingOnBatteries)"
Write-Output "DisallowStartIfOnBatteries: $($s.DisallowStartIfOnBatteries)"
Write-Output "MultipleInstances: $($s.MultipleInstances)"

Write-Output ''
Write-Output '=== LAST RUN INFO ==='
Write-Output "State: $($task.State)"
$info = $task | Get-ScheduledTaskInfo
Write-Output "LastRunTime: $($info.LastRunTime)"
Write-Output "LastTaskResult: $($info.LastTaskResult)"
Write-Output "NextRunTime: $($info.NextRunTime)"
