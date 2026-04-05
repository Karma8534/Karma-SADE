param(
    [switch]$HiddenRelaunch
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "HiddenRelaunch.ps1")
Invoke-HiddenRelaunchIfNeeded -ScriptPath $PSCommandPath -HiddenRelaunch:$HiddenRelaunch

$scriptPath = Join-Path $PSScriptRoot "Start-CCServer.ps1"

if (-not (Test-Path $scriptPath)) {
    throw "Missing launcher: $scriptPath"
}

& $scriptPath
