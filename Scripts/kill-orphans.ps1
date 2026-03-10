$targets = @(123572, 175716, 348920, 141700, 328180, 304104)

foreach ($procId in $targets) {
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Output "Killing PID $procId ($($proc.Name)) started $($proc.StartTime.ToString('HH:mm:ss'))"
        Stop-Process -Id $procId -Force
        Write-Output "  Killed"
    } else {
        Write-Output "PID $procId already gone"
    }
}

Write-Output ""
Write-Output "=== Remaining claude/node processes ==="
Get-Process | Where-Object { $_.Name -match 'claude|node' } | Select-Object Id, Name, @{N='Start';E={$_.StartTime.ToString('HH:mm:ss')}} | Format-Table -AutoSize
