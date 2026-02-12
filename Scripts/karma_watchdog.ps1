<#
.SYNOPSIS
    Karma SADE — Service Watchdog v1.0.0
.DESCRIPTION
    Monitors Open WebUI, Cockpit, and Ollama via HTTP health checks.
    Restarts any service that fails its health check.
    Designed to run via Task Scheduler every 5 minutes.

    Restart logic:
    - Checks HTTP endpoint (more reliable than process name detection)
    - If unhealthy, kills any zombie process on the port, then restarts
    - Tracks consecutive failures per service to avoid restart loops
    - After 3 consecutive restart failures, stops trying and logs CRITICAL
    - Resets failure counter on successful health check

    Logs to: Logs/karma-watchdog.log
    State:   Logs/watchdog-state.json (tracks failure counts across runs)
.NOTES
    Register with Task Scheduler:
    schtasks /create /tn "KarmaSADE-Watchdog" /tr "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\Users\raest\Documents\Karma_SADE\Scripts\karma_watchdog.ps1" /sc minute /mo 5 /ru "%USERNAME%" /rl highest
#>

$ErrorActionPreference = "Continue"

# ─── Configuration ────────────────────────────────────────────────────────────
$Config = @{
    LogDir           = "C:\Users\raest\Documents\Karma_SADE\Logs"
    StateFile        = "C:\Users\raest\Documents\Karma_SADE\Logs\watchdog-state.json"
    MaxConsecutiveFails = 3    # Stop restarting after this many consecutive failures
    HealthTimeout    = 10      # Seconds to wait for HTTP response
    PostRestartWait  = 30      # Seconds to wait after restart before re-checking
}

$Services = @(
    @{
        Name        = "Ollama"
        Url         = "http://localhost:11434"
        Port        = 11434
        StartCmd    = "ollama"
        StartArgs   = "serve"
        ProcessHint = "ollama"  # For zombie kill
    },
    @{
        Name        = "OpenWebUI"
        Url         = "http://localhost:8080"
        Port        = 8080
        StartCmd    = "C:\openwebui\venv\Scripts\open-webui.exe"
        StartArgs   = "serve"
        ProcessHint = "open-webui"
    },
    @{
        Name        = "Cockpit"
        Url         = "http://localhost:9400/health"
        Port        = 9400
        StartCmd    = "python"
        StartArgs   = "`"C:\Users\raest\Documents\Karma_SADE\Scripts\karma_cockpit_service.py`""
        ProcessHint = $null  # Python process — can't reliably match by name
    }
)

$LogFile = Join-Path $Config.LogDir "karma-watchdog.log"

# ─── Logging ──────────────────────────────────────────────────────────────────
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] [watchdog] [$Level] $Message"
    if (-not (Test-Path $Config.LogDir)) {
        New-Item -ItemType Directory -Path $Config.LogDir -Force | Out-Null
    }
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

# ─── State Management ─────────────────────────────────────────────────────────
function Get-WatchdogState {
    if (Test-Path $Config.StateFile) {
        try {
            return Get-Content $Config.StateFile -Raw | ConvertFrom-Json
        }
        catch {
            Write-Log "Corrupted state file, resetting" "WARN"
        }
    }
    # Default state
    return @{
        Ollama    = @{ consecutive_fails = 0; last_restart = $null; gave_up = $false }
        OpenWebUI = @{ consecutive_fails = 0; last_restart = $null; gave_up = $false }
        Cockpit   = @{ consecutive_fails = 0; last_restart = $null; gave_up = $false }
    }
}

function Save-WatchdogState {
    param($State)
    $State | ConvertTo-Json -Depth 3 | Set-Content -Path $Config.StateFile -Encoding UTF8
}

# ─── Health Check ─────────────────────────────────────────────────────────────
function Test-ServiceUp {
    param([string]$Url)
    try {
        $r = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec $Config.HealthTimeout -UseBasicParsing -ErrorAction Stop
        return ($r.StatusCode -eq 200)
    }
    catch {
        return $false
    }
}

# ─── Port Zombie Killer ──────────────────────────────────────────────────────
function Stop-ZombieOnPort {
    param([int]$Port, [string]$ServiceName)

    $lines = netstat -ano 2>$null | Select-String ":${Port}\s+.*LISTEN"
    foreach ($line in $lines) {
        if ($line -match '\s(\d+)\s*$') {
            $pid = [int]$Matches[1]
            if ($pid -gt 0) {
                Write-Log "Killing zombie PID $pid on port $Port ($ServiceName)" "WARN"
                try {
                    Stop-Process -Id $pid -Force -ErrorAction Stop
                    Start-Sleep -Seconds 2
                    Write-Log "Killed PID $pid" "OK"
                }
                catch {
                    Write-Log "Failed to kill PID $pid`: $($_.Exception.Message)" "ERROR"
                }
            }
        }
    }
}

# ─── Service Restart ──────────────────────────────────────────────────────────
function Restart-Service-Karma {
    param($ServiceDef)

    $name = $ServiceDef.Name

    # Kill zombies on the port first
    Stop-ZombieOnPort -Port $ServiceDef.Port -ServiceName $name

    Write-Log "Starting $name ($($ServiceDef.StartCmd) $($ServiceDef.StartArgs))"

    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $ServiceDef.StartCmd
        $psi.Arguments = $ServiceDef.StartArgs
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        $psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden

        $proc = [System.Diagnostics.Process]::Start($psi)
        Write-Log "$name started (PID $($proc.Id)), waiting ${($Config.PostRestartWait)}s for health..."

        Start-Sleep -Seconds $Config.PostRestartWait

        # Verify it came up
        if (Test-ServiceUp -Url $ServiceDef.Url) {
            Write-Log "$name restarted successfully and is healthy" "OK"
            return $true
        }
        else {
            Write-Log "$name started but not healthy after ${($Config.PostRestartWait)}s" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Failed to start $name`: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# ─── Main Loop ────────────────────────────────────────────────────────────────
function Invoke-WatchdogCycle {

    $state = Get-WatchdogState
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $anyAction = $false

    foreach ($svc in $Services) {
        $name = $svc.Name

        # Ensure state entry exists (handles first run or new services)
        if (-not $state.$name) {
            $state | Add-Member -NotePropertyName $name -NotePropertyValue @{
                consecutive_fails = 0
                last_restart = $null
                gave_up = $false
            } -Force
        }

        $svcState = $state.$name
        $healthy = Test-ServiceUp -Url $svc.Url

        if ($healthy) {
            # Reset failure counter on success
            if ($svcState.consecutive_fails -gt 0 -or $svcState.gave_up) {
                Write-Log "$name recovered (was at $($svcState.consecutive_fails) consecutive fails)" "OK"
                $svcState.consecutive_fails = 0
                $svcState.gave_up = $false
                $anyAction = $true
            }
            continue
        }

        # ── Service is unhealthy ──
        $anyAction = $true

        if ($svcState.gave_up) {
            # Already gave up — just log periodically
            Write-Log "$name still down (gave up after $($Config.MaxConsecutiveFails) restart attempts)" "ERROR"
            continue
        }

        $svcState.consecutive_fails++
        Write-Log "$name is DOWN (consecutive fail #$($svcState.consecutive_fails))" "WARN"

        if ($svcState.consecutive_fails -gt $Config.MaxConsecutiveFails) {
            Write-Log "$name has failed $($svcState.consecutive_fails) times — GIVING UP (manual intervention required)" "ERROR"
            $svcState.gave_up = $true
            continue
        }

        # Attempt restart
        Write-Log "Attempting restart of $name (attempt $($svcState.consecutive_fails)/$($Config.MaxConsecutiveFails))..."
        $success = Restart-Service-Karma -ServiceDef $svc

        if ($success) {
            $svcState.consecutive_fails = 0
            $svcState.gave_up = $false
        }
        $svcState.last_restart = $ts
    }

    Save-WatchdogState -State $state

    if (-not $anyAction) {
        # All healthy, minimal log (one line per cycle max)
        Add-Content -Path $LogFile -Value "[$ts] [watchdog] [OK] All services healthy" -Encoding UTF8
    }
}

# ── Run ──
Invoke-WatchdogCycle
