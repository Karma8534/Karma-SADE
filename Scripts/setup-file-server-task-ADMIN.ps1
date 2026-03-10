param()
# RUN AS ADMINISTRATOR
$ErrorActionPreference = 'Stop'

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Must run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell -> Run as Administrator, then: pwsh -File `"$PSCommandPath`""
    Read-Host "Press Enter to exit"
    exit 1
}

$BaseDir  = 'C:\Users\raest\Documents\Karma_SADE'
$Script   = "$BaseDir\Scripts\karma-file-server.ps1"
$TaskName = 'KarmaFileServer'
$User     = "$env:USERDOMAIN\$env:USERNAME"
$WatcherArgs = "-WindowStyle Hidden -NonInteractive -File `"$Script`""

Write-Host "[0/4] Adding URL ACL for http://+:7771/ ..." -ForegroundColor Cyan
$aclResult = netsh http add urlacl url=http://+:7771/ user=$User 2>&1
Write-Host "  $aclResult"

Write-Host "[1/4] Removing old task..." -ForegroundColor Cyan
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "  Done"

Write-Host "[2/4] Creating task..." -ForegroundColor Cyan

$xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Karma local file server — serves Karma_SADE folder to hub-bridge via Tailscale on port 7771.</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger><Enabled>true</Enabled></LogonTrigger>
    <BootTrigger><Enabled>true</Enabled></BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$User</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT2M</Interval>
      <Count>9999</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>pwsh</Command>
      <Arguments>$WatcherArgs</Arguments>
      <WorkingDirectory>$BaseDir</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

$xmlPath = "$env:TEMP\KarmaFileServer.xml"
$xml | Set-Content -Path $xmlPath -Encoding Unicode
Register-ScheduledTask -TaskName $TaskName -Xml (Get-Content $xmlPath -Raw) -Force | Out-Null
Remove-Item $xmlPath -Force
Write-Host "  Task registered" -ForegroundColor Green

Write-Host "[3/4] Starting task..." -ForegroundColor Cyan
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 5
$state = (Get-ScheduledTask -TaskName $TaskName).State
Write-Host "  State: $state" -ForegroundColor $(if ($state -eq 'Running') { 'Green' } else { 'Yellow' })

Write-Host "[4/4] Verifying port 7771 is listening..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
$listening = netstat -an | Select-String '7771'
if ($listening) {
    Write-Host "  Port 7771 ACTIVE: $listening" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Port 7771 not yet detected in netstat (may need a moment)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "DONE. KarmaFileServer task registered and running." -ForegroundColor Green
Write-Host "  - StopIfGoingOnBatteries: FALSE"
Write-Host "  - DisallowStartIfOnBatteries: FALSE"
Write-Host "  - Restarts: 9999 times, every 2 min on failure"
Write-Host "  - Triggers: AtLogon + AtStartup"
Write-Host "  - URL ACL: http://+:7771/"
