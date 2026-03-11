Get-Process -Name claude -ErrorAction SilentlyContinue | ForEach-Object {
    $wmi = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        PID       = $_.Id
        CPU       = [math]::Round($_.CPU, 1)
        StartTime = $_.StartTime.ToString("HH:mm:ss")
        ParentPID = $wmi.ParentProcessId
        CmdLine   = if ($wmi) { ($wmi.CommandLine -replace '"','') | Select-Object -First 1 } else { "N/A" }
    }
} | Format-Table -AutoSize
