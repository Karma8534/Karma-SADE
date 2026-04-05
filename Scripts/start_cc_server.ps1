$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "Start-CCServer.ps1"

if (-not (Test-Path $scriptPath)) {
    throw "Missing launcher: $scriptPath"
}

& $scriptPath
