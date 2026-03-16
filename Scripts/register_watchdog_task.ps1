$action = New-ScheduledTaskAction -Execute 'python' -Argument 'C:\Users\raest\Documents\Karma_SADE\Scripts\regent_watchdog.py' -WorkingDirectory 'C:\Users\raest\Documents\Karma_SADE'
$trigger = New-ScheduledTaskTrigger -AtLogon
$settings = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit 0 -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName 'KarmaRegentWatchdog' -Action $action -Trigger $trigger -Settings $settings -Force | Select-Object TaskName, State
Start-ScheduledTask -TaskName 'KarmaRegentWatchdog'
Get-ScheduledTask -TaskName 'KarmaRegentWatchdog' | Select-Object TaskName, State
