param()
# RUN AS ADMINISTRATOR — right-click this script in Explorer → Run with PowerShell (as admin)
# OR: open PowerShell as admin and run: pwsh -File fix-watcher-task-ADMIN.ps1
$ErrorActionPreference = 'Stop'

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Must run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell -> Run as Administrator, then: pwsh -File `"$PSCommandPath`""
    Read-Host "Press Enter to exit"
    exit 1
}

$BaseDir   = 'C:\Users\raest\Documents\Karma_SADE'
$TokenFile = "$BaseDir\.hub-chat-token"
$Script    = "$BaseDir\Scripts\karma-inbox-watcher.ps1"
$TaskName  = 'KarmaInboxWatcher'
$User      = "$env:USERDOMAIN\$env:USERNAME"

$WatcherArgs = "-WindowStyle Hidden -NonInteractive -File `"$Script`"" +
    " -InboxPath `"$BaseDir\Karma_PDFs\Inbox`"" +
    " -GatedPath `"$BaseDir\Karma_PDFs\Gated`"" +
    " -ProcessingPath `"$BaseDir\Karma_PDFs\Processing`"" +
    " -DonePath `"$BaseDir\Karma_PDFs\Done`"" +
    " -TokenFile `"$TokenFile`""

Write-Host "[1/3] Removing old task..." -ForegroundColor Cyan
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "  Done"

Write-Host "[2/3] Creating task with correct settings..." -ForegroundColor Cyan

$xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Karma inbox watcher — monitors Karma_PDFs/Inbox for new PDFs. Always on.</Description>
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
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
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

$xmlPath = "$env:TEMP\KarmaInboxWatcher.xml"
$xml | Set-Content -Path $xmlPath -Encoding Unicode
Register-ScheduledTask -TaskName $TaskName -Xml (Get-Content $xmlPath -Raw) -Force | Out-Null
Remove-Item $xmlPath -Force
Write-Host "  Task registered" -ForegroundColor Green

Write-Host "[3/3] Starting task..." -ForegroundColor Cyan
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 3
$state = (Get-ScheduledTask -TaskName $TaskName).State
Write-Host "  State: $state" -ForegroundColor $(if ($state -eq 'Running') { 'Green' } else { 'Yellow' })

Write-Host ""
Write-Host "DONE. Settings applied:" -ForegroundColor Green
Write-Host "  - StopIfGoingOnBatteries: FALSE"
Write-Host "  - DisallowStartIfOnBatteries: FALSE"
Write-Host "  - Restarts: 9999 times, every 2 min on failure"
Write-Host "  - Triggers: AtLogon + AtStartup"
Write-Host "  - Paths: Karma_PDFs/Inbox (correct)"
