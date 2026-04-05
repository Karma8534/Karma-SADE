# start-karma-watcher.ps1
# Thin wrapper with hardcoded correct paths.
# The scheduled task runs this — no long argument list needed.
param(
    [switch]$HiddenRelaunch
)

. (Join-Path $PSScriptRoot "HiddenRelaunch.ps1")
Invoke-HiddenRelaunchIfNeeded -ScriptPath $PSCommandPath -HiddenRelaunch:$HiddenRelaunch

$root = "C:\Users\raest\Documents\Karma_SADE"
& "$root\Scripts\karma-inbox-watcher.ps1" `
    -InboxPath      "$root\Karma_PDFs\Inbox" `
    -GatedPath      "$root\Karma_PDFs\Gated" `
    -ProcessingPath "$root\Karma_PDFs\Processing" `
    -DonePath       "$root\Karma_PDFs\Done" `
    -TokenFile      "$root\.hub-chat-token"
