$ErrorActionPreference = "Stop"

$repoRoot = "C:\Users\raest\Documents\Karma_SADE"
$pwsh = (Get-Command pwsh.exe -ErrorAction SilentlyContinue).Source
if (-not $pwsh) {
    $pwsh = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
}
if (-not $pwsh) {
    throw "pwsh.exe not found in PATH"
}

function Register-PersistentTask {
    param(
        [Parameter(Mandatory = $true)][string]$TaskName,
        [Parameter(Mandatory = $true)][string]$ScriptPath,
        [Parameter(Mandatory = $true)][string]$Description,
        [int]$RestartMinutes = 1
    )

    if (-not (Test-Path $ScriptPath)) {
        throw "Missing script for task ${TaskName}: $ScriptPath"
    }

    $quotedScript = '"' + $ScriptPath + '"'
    $arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -NonInteractive -File $quotedScript"

    $action = New-ScheduledTaskAction -Execute $pwsh -Argument $arguments -WorkingDirectory $repoRoot
    $triggers = @(
        (New-ScheduledTaskTrigger -AtLogOn),
        (New-ScheduledTaskTrigger -AtStartup)
    )
    $settings = New-ScheduledTaskSettingsSet `
        -ExecutionTimeLimit 0 `
        -RestartCount 999 `
        -RestartInterval (New-TimeSpan -Minutes $RestartMinutes) `
        -MultipleInstances IgnoreNew `
        -StartWhenAvailable

    try {
        Register-ScheduledTask `
            -TaskName $TaskName `
            -Action $action `
            -Trigger $triggers `
            -RunLevel Highest `
            -Settings $settings `
            -Description $Description `
            -Force | Out-Null

        Start-ScheduledTask -TaskName $TaskName
        return [pscustomobject]@{
            Name = $TaskName
            Mode = "scheduled_task"
        }
    } catch {
        $runCommand = '"' + $pwsh + '" -ExecutionPolicy Bypass -WindowStyle Hidden -NonInteractive -File ' + $quotedScript
        $runKeyPath = "Software\Microsoft\Windows\CurrentVersion\Run"
        $runKey = [Microsoft.Win32.Registry]::CurrentUser.CreateSubKey($runKeyPath)
        $runKey.SetValue($TaskName, $runCommand, [Microsoft.Win32.RegistryValueKind]::String)
        $runKey.Flush()
        $actual = $runKey.GetValue($TaskName, "")
        $runKey.Close()
        if ($actual -ne $runCommand) {
            throw "Failed to persist HKCU Run entry for $TaskName"
        }
        Start-Process -FilePath $pwsh -ArgumentList "-ExecutionPolicy Bypass -WindowStyle Hidden -NonInteractive -File $quotedScript" -WindowStyle Hidden
        return [pscustomobject]@{
            Name = $TaskName
            Mode = "hkcu_run"
        }
    }
}

$tasks = @(
    @{
        TaskName = "KarmaSovereignHarness"
        ScriptPath = "$repoRoot\Scripts\Start-CCServer.ps1"
        Description = "Hidden persistent launcher for cc_server_p1.py. Survives reboot and restarts on failure."
        RestartMinutes = 1
    },
    @{
        TaskName = "KarmaChannelsBridge"
        ScriptPath = "$repoRoot\Scripts\Start-ChannelsBridge.ps1"
        Description = "Hidden persistent launcher for channels_bridge.py. Survives reboot and restarts on failure."
        RestartMinutes = 1
    },
    @{
        TaskName = "KarmaCortexSync"
        ScriptPath = "$repoRoot\Scripts\Start-CortexSync.ps1"
        Description = "Hidden persistent launcher for cortex sync. Survives reboot and restarts on failure."
        RestartMinutes = 2
    },
    @{
        TaskName = "KarmaRegentWatchdog"
        ScriptPath = "$repoRoot\Scripts\Start-RegentWatchdog.ps1"
        Description = "Hidden persistent launcher for regent_watchdog.py. Survives reboot and restarts on failure."
        RestartMinutes = 2
    },
    @{
        TaskName = "KarmaArchonPrime"
        ScriptPath = "$repoRoot\Scripts\Start-ArchonPrime.ps1"
        Description = "Hidden persistent launcher for archonprime_watcher.py. Survives reboot and restarts on failure."
        RestartMinutes = 1
    },
    @{
        TaskName = "KarmaInboxWatcher"
        ScriptPath = "$repoRoot\Scripts\start-karma-watcher.ps1"
        Description = "Hidden persistent launcher for the Karma PDF inbox watcher. Survives reboot and restarts on failure."
        RestartMinutes = 1
    }
)

$results = foreach ($task in $tasks) {
    Register-PersistentTask @task
}

$results
