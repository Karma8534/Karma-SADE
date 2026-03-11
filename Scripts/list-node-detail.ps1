Get-Process -Name node -ErrorAction SilentlyContinue | ForEach-Object {
    $wmi = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        PID       = $_.Id
        CPU       = [math]::Round($_.CPU, 1)
        StartTime = $_.StartTime.ToString("HH:mm:ss")
        ParentPID = $wmi.ParentProcessId
    }
} | Sort-Object StartTime | Format-Table -AutoSize
