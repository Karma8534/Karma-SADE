param([int]$ProcessId)
if (-not $ProcessId) {
  $p = Get-Process arknexusv6, julian -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($p) { $ProcessId = $p.Id }
}
if (-not $ProcessId) { Write-Host 'no_tauri_process'; exit 0 }
$proc = Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId" -ErrorAction SilentlyContinue
if (-not $proc) { Write-Host "pid_gone $ProcessId"; exit 0 }
Write-Host ("cmdline: " + $proc.CommandLine)
Write-Host ("exe: " + $proc.ExecutablePath)
Get-Process arknexusv6, julian -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
'killed'
