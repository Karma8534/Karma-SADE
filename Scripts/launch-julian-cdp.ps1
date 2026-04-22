# launch-julian-cdp.ps1 - Launch Julian with WEBVIEW2 CDP debug port enabled
# Use env-then-Start-Process so child Julian inherits.
param(
  [string]$JulianExe = 'C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\target\release\julian.exe',
  [int]$CdpPort = 9222
)
$ErrorActionPreference = 'Stop'
Get-Process julian -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
$env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = "--remote-debugging-port=$CdpPort --remote-allow-origins=*"
$p = Start-Process $JulianExe -PassThru
Write-Host ("pid=" + $p.Id)
$p.Id | Out-File -LiteralPath (Join-Path $env:TEMP 'julian-cdp.pid') -Encoding ascii
# Poll for CDP port for up to 30s
for ($i = 0; $i -lt 30; $i++) {
  Start-Sleep -Seconds 1
  $conn = Get-NetTCPConnection -LocalPort $CdpPort -State Listen -ErrorAction SilentlyContinue
  if ($conn) { Write-Host ("cdp_listening_after_sec=" + ($i + 1)); break }
}
if (-not (Get-NetTCPConnection -LocalPort $CdpPort -State Listen -ErrorAction SilentlyContinue)) {
  Write-Host 'cdp_not_listening_after_30s'
  exit 1
}
exit 0
