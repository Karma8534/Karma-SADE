$scriptPath = "C:\Users\raest\Documents\Karma_SADE\Scripts\karma-inbox-watcher.ps1"

$action   = New-ScheduledTaskAction -Execute "pwsh" -Argument "-WindowStyle Hidden -NonInteractive -File $scriptPath"
$trigger  = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit 0 -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)

Register-ScheduledTask `
    -TaskName "KarmaInboxWatcher" `
    -Action $action `
    -Trigger $trigger `
    -RunLevel Highest `
    -Force `
    -Settings $settings | Select-Object TaskName, State

# Start it now (don't wait for next logon)
Start-ScheduledTask -TaskName "KarmaInboxWatcher"
Write-Host "Watcher started. Check Task Scheduler or Get-ScheduledTask -TaskName KarmaInboxWatcher"
