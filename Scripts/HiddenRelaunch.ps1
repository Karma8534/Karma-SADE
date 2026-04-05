function Invoke-HiddenRelaunchIfNeeded {
    param(
        [Parameter(Mandatory = $true)][string]$ScriptPath,
        [Parameter(Mandatory = $true)][bool]$HiddenRelaunch,
        [string[]]$ExtraArgs = @()
    )

    if ($HiddenRelaunch) {
        return
    }

    if (-not $scriptPath) {
        return
    }

    $wscript = Join-Path $env:SystemRoot "System32\wscript.exe"
    $hiddenLauncher = Join-Path $PSScriptRoot "RunHiddenPowerShell.vbs"
    if (-not (Test-Path $wscript) -or -not (Test-Path $hiddenLauncher)) {
        return
    }

    $argumentList = @("//B", "//nologo", $hiddenLauncher, $scriptPath, "-HiddenRelaunch")
    if ($ExtraArgs.Count -gt 0) {
        $argumentList += $ExtraArgs
    }

    Start-Process -FilePath $wscript -ArgumentList $argumentList | Out-Null
    exit 0
}
