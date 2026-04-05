$ErrorActionPreference = "Stop"

$repoRoot = "C:\Users\raest\Documents\Karma_SADE"
$wscript = Join-Path $env:SystemRoot "System32\wscript.exe"
$hiddenLauncher = Join-Path $repoRoot "Scripts\RunHiddenPowerShell.vbs"
if (-not (Test-Path $wscript)) {
    throw "wscript.exe not found at $wscript"
}
if (-not (Test-Path $hiddenLauncher)) {
    throw "Hidden launcher helper missing at $hiddenLauncher"
}
$runKeyPath = "Software\Microsoft\Windows\CurrentVersion\Run"

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

    $quotedLauncher = '"' + $hiddenLauncher + '"'
    $quotedScript = '"' + $ScriptPath + '"'
    $arguments = "//B //nologo $quotedLauncher $quotedScript"

    $action = New-ScheduledTaskAction -Execute $wscript -Argument $arguments -WorkingDirectory $repoRoot
    $triggers = @(
        (New-ScheduledTaskTrigger -AtLogOn),
        (New-ScheduledTaskTrigger -AtStartup)
    )
    $settings = New-ScheduledTaskSettingsSet `
        -ExecutionTimeLimit 0 `
        -RestartCount 999 `
        -RestartInterval (New-TimeSpan -Minutes $RestartMinutes) `
        -MultipleInstances IgnoreNew `
        -StartWhenAvailable `
        -Hidden

    try {
        Register-ScheduledTask `
            -TaskName $TaskName `
            -Action $action `
            -Trigger $triggers `
            -RunLevel Highest `
            -Settings $settings `
            -Description $Description `
            -Force `
            -ErrorAction Stop | Out-Null

        $runKey = [Microsoft.Win32.Registry]::CurrentUser.CreateSubKey($runKeyPath)
        try {
            $runKey.DeleteValue($TaskName, $false)
        } finally {
            $runKey.Close()
        }

        Start-ScheduledTask -TaskName $TaskName -ErrorAction Stop
        return [pscustomobject]@{
            Name = $TaskName
            Mode = "scheduled_task"
        }
    } catch {
        $runCommand = '"' + $wscript + '" //B //nologo ' + $quotedLauncher + ' ' + $quotedScript
        $runKey = [Microsoft.Win32.Registry]::CurrentUser.CreateSubKey($runKeyPath)
        $runKey.SetValue($TaskName, $runCommand, [Microsoft.Win32.RegistryValueKind]::String)
        $runKey.Flush()
        $actual = $runKey.GetValue($TaskName, "")
        $runKey.Close()
        if ($actual -ne $runCommand) {
            throw "Failed to persist HKCU Run entry for $TaskName"
        }
        Start-Process -FilePath $wscript -ArgumentList "//B", "//nologo", $hiddenLauncher, $ScriptPath
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
        TaskName = "KarmaLauncherSentinel"
        ScriptPath = "$repoRoot\Scripts\Start-LauncherSentinel.ps1"
        Description = "Hidden persistent launcher sentinel for auditing and repairing launcher drift. Survives reboot and restarts on failure."
        RestartMinutes = 1
    },
    @{
        TaskName = "KarmaInboxWatcher"
        ScriptPath = "$repoRoot\Scripts\start-karma-watcher.ps1"
        Description = "Hidden persistent launcher for the Karma PDF inbox watcher. Survives reboot and restarts on failure."
        RestartMinutes = 1
    },
    @{
        TaskName = "KarmaFileServer"
        ScriptPath = "$repoRoot\Scripts\karma-file-server.ps1"
        Description = "Hidden persistent launcher for the Karma local file server. Survives reboot and restarts on failure."
        RestartMinutes = 1
    },
    @{
        TaskName = "KarmaSessionIndexer"
        ScriptPath = "$repoRoot\Scripts\karma_session_indexer.ps1"
        Description = "Hidden persistent launcher for Claude session JSONL indexing. Survives reboot and restarts on failure."
        RestartMinutes = 1
    }
)

$results = foreach ($task in $tasks) {
    Register-PersistentTask @task
}

$results
