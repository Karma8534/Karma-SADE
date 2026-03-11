Get-Process | Where-Object { $_.Name -match 'claude|node|pwsh|powershell' } | Select-Object Id, Name, CPU, StartTime | Format-Table -AutoSize
