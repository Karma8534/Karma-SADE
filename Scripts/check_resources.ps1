# Quick resource check
Get-Process | Where-Object {$_.WorkingSet -gt 100MB} |
    Select-Object ProcessName,@{Name='MemoryMB';Expression={[math]::Round($_.WorkingSet/1MB,2)}} |
    Sort-Object MemoryMB -Descending |
    Select-Object -First 10 |
    Format-Table -AutoSize
