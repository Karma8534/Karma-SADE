param([int]$Pid)
if (-not $Pid) {
  $p = Get-Process julian -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($p) { $Pid = $p.Id }
}
if (-not $Pid) { Write-Host 'no_julian'; exit 0 }
$proc = Get-CimInstance Win32_Process -Filter "ProcessId=$Pid" -ErrorAction SilentlyContinue
if (-not $proc) { Write-Host "pid_gone $Pid"; exit 0 }
Write-Host ("cmdline: " + $proc.CommandLine)
Write-Host ("exe: " + $proc.ExecutablePath)
Get-Process julian | Stop-Process -Force -ErrorAction SilentlyContinue
'killed'
