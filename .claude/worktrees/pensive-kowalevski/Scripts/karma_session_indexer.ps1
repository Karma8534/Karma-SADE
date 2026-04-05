# KARMA_REPO_FORWARDER
param(
    [string]$WatchDir = "$env:USERPROFILE\.claude\projects\C--Users-raest-Documents-Karma-SADE",
    [string]$ScriptDir = "C:\Users\raest\Documents\Karma_SADE",
    [int]$DebounceSeconds = 10,
    [int]$PollSeconds = 15,
    [switch]$HiddenRelaunch
)

& "C:\Users\raest\Documents\Karma_SADE\Scripts\karma_session_indexer.ps1" `
    -WatchDir $WatchDir `
    -ScriptDir $ScriptDir `
    -DebounceSeconds $DebounceSeconds `
    -PollSeconds $PollSeconds `
    -HiddenRelaunch:$HiddenRelaunch
