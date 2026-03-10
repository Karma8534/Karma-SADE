$repoRoot      = "C:\Users\raest\Documents\Karma_SADE"
$scriptPath    = "$repoRoot\Scripts\karma-inbox-watcher.ps1"
$inboxPath     = "$repoRoot\Karma_PDFs\Inbox"
$gatedPath     = "$repoRoot\Karma_PDFs\Gated"
$processingPath= "$repoRoot\Karma_PDFs\Processing"
$donePath      = "$repoRoot\Karma_PDFs\Done"
$tokenFile     = "$repoRoot\.hub-chat-token"

$taskArgs = "-WindowStyle Hidden -NonInteractive -File `"$scriptPath`"" +
            " -InboxPath `"$inboxPath`"" +
            " -GatedPath `"$gatedPath`"" +
            " -ProcessingPath `"$processingPath`"" +
            " -DonePath `"$donePath`"" +
            " -TokenFile `"$tokenFile`""

$action   = New-ScheduledTaskAction -Execute "pwsh" -Argument $taskArgs
$triggers = @(
    (New-ScheduledTaskTrigger -AtLogOn)
)
# RestartCount 999 = never gives up. RestartInterval 1min = recovers fast.
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit 0 `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName "KarmaInboxWatcher" `
    -Action $action `
    -Trigger $triggers `
    -RunLevel Highest `
    -Force `
    -Settings $settings `
    -Description "Karma PDF inbox watcher - monitors Karma_PDFs/Inbox and Karma_PDFs/Gated. Restarts automatically on failure." |
    Select-Object TaskName, State

# Start it now (don't wait for next logon/reboot)
Start-ScheduledTask -TaskName "KarmaInboxWatcher"
Write-Host "Watcher started with correct paths. Check: Get-ScheduledTask -TaskName KarmaInboxWatcher"
