# launch-julian-cdp.ps1 - Launch Julian/Arknexusv6 with CDP debug port enabled
param(
  [string]$AppExe = 'C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\target\release\arknexusv6.exe',
  [int]$CdpPort = 9222
)
$ErrorActionPreference = 'Stop'
Get-Process julian,arknexusv6 -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
$env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = "--remote-debugging-port=$CdpPort --remote-allow-origins=*"
$env:ARKNEXUS_DEVTOOLS = '1'
$p = Start-Process $AppExe -PassThru
Write-Host ("pid=" + $p.Id + " exe=" + $AppExe)
$p.Id | Out-File -LiteralPath (Join-Path $env:TEMP 'julian-cdp.pid') -Encoding ascii
for ($i = 0; $i -lt 30; $i++) {
  Start-Sleep -Seconds 1
  $conn = Get-NetTCPConnection -LocalPort $CdpPort -State Listen -ErrorAction SilentlyContinue
  if ($conn) { Write-Host ("cdp_listening_after_sec=" + ($i + 1)); exit 0 }
}
Write-Host 'cdp_not_listening_after_30s'
exit 1
