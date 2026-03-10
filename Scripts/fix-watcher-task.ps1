param()
$ErrorActionPreference = 'Stop'
$BaseDir   = 'C:\Users\raest\Documents\Karma_SADE'
$TokenFile = "$BaseDir\.hub-chat-token"
$TaskName  = 'KarmaInboxWatcher'
$Script    = "$BaseDir\Scripts\karma-inbox-watcher.ps1"

# Build argument string with all correct paths
$WatcherArgs = "-WindowStyle Hidden -NonInteractive -File `"$Script`"" +
    " -InboxPath `"$BaseDir\Karma_PDFs\Inbox`"" +
    " -GatedPath `"$BaseDir\Karma_PDFs\Gated`"" +
    " -ProcessingPath `"$BaseDir\Karma_PDFs\Processing`"" +
    " -DonePath `"$BaseDir\Karma_PDFs\Done`"" +
    " -TokenFile `"$TokenFile`""

Write-Output '=== Step 1+2: Already done (files archived, errors cleared) ==='

Write-Output ''
Write-Output '=== Step 3: Recreate KarmaInboxWatcher task via schtasks.exe ==='

# Delete old task
Write-Output '  Deleting old task...'
$del = & schtasks /delete /tn $TaskName /f 2>&1
Write-Output "  Delete result: $del"

# Recreate via XML for full control over settings (battery, triggers, restart)
$xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Karma inbox watcher — monitors Karma_PDFs/Inbox and Karma_PDFs/Gated for new PDFs</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$env:USERDOMAIN\$env:USERNAME</UserId>
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
    <WakeToRun>false</WakeToRun>
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
Write-Output '  XML task definition written'

$create = & schtasks /create /tn $TaskName /xml $xmlPath /f 2>&1
Write-Output "  Create result: $create"
Remove-Item $xmlPath -Force

Write-Output ''
Write-Output '=== Step 4: Start KarmaInboxWatcher now ==='
$run = & schtasks /run /tn $TaskName 2>&1
Write-Output "  Run result: $run"

Start-Sleep -Seconds 4

Write-Output ''
Write-Output '=== Verification ==='
$q = & schtasks /query /tn $TaskName /fo LIST 2>&1
Write-Output $q
