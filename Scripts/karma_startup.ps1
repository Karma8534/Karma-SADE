<#
.SYNOPSIS
    Karma SADE — Ordered Startup Orchestrator v1.0.0
.DESCRIPTION
    Replaces the two independent VBS scripts that race on login.
    Starts services in dependency order with health-gate between each:
      1. Ollama (if not running)
      2. Open WebUI (depends on Ollama for local models)
      3. Cockpit (depends on Open WebUI for pinned tab)
    Each service must pass its HTTP health check before the next starts.
    Logs everything to Logs/karma-startup.log.
.NOTES
    Launched by karma_startup.vbs from the Windows Startup folder.
    Replaces: start_openwebui.vbs + start_cockpit.vbs
#>

$ErrorActionPreference = "Stop"

# ─── Configuration ────────────────────────────────────────────────────────────
$Config = @{
    # Paths
    OpenWebUIExe   = "C:\openwebui\venv\Scripts\open-webui.exe"
    CockpitScript  = "C:\Users\raest\Documents\Karma_SADE\Scripts\karma_cockpit_service.py"
    SecretsScript  = "C:\Users\raest\Documents\Karma_SADE\Scripts\karma_secrets.ps1"
    LogDir         = "C:\Users\raest\Documents\Karma_SADE\Logs"

    # Endpoints
    OllamaUrl      = "http://localhost:11434"
    OpenWebUIUrl   = "http://localhost:8080"
    CockpitUrl     = "http://localhost:9400/health"

    # Timeouts (seconds)
    OllamaTimeout    = 30
    OpenWebUITimeout = 120   # Open WebUI can be slow to initialize
    CockpitTimeout   = 60
    PollInterval     = 3     # Seconds between health check polls

    # Retry
    MaxRestartAttempts = 2
}

$LogFile = Join-Path $Config.LogDir "karma-startup.log"

# ─── Logging ──────────────────────────────────────────────────────────────────
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] [$Level] $Message"
    Write-Host $line -ForegroundColor $(switch ($Level) {
        "OK"    { "Green" }
        "WARN"  { "Yellow" }
        "ERROR" { "Red" }
        "WAIT"  { "Cyan" }
        default { "White" }
    })
    if (-not (Test-Path $Config.LogDir)) {
        New-Item -ItemType Directory -Path $Config.LogDir -Force | Out-Null
    }
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

# ─── Health Check ─────────────────────────────────────────────────────────────
function Test-ServiceHealth {
    param(
        [string]$Url,
        [string]$ServiceName,
        [int]$TimeoutSeconds,
        [int]$PollSeconds = $Config.PollInterval
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $attempt = 0

    while ((Get-Date) -lt $deadline) {
        $attempt++
        try {
            $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Log "$ServiceName is healthy (HTTP 200, attempt $attempt)" "OK"
                return $true
            }
        }
        catch {
            # Expected during startup — service not ready yet
        }
        Start-Sleep -Seconds $PollSeconds
    }

    Write-Log "$ServiceName did NOT become healthy within ${TimeoutSeconds}s ($attempt attempts)" "ERROR"
    return $false
}

# ─── Process Launcher ─────────────────────────────────────────────────────────
function Start-ServiceProcess {
    param(
        [string]$ServiceName,
        [string]$Executable,
        [string[]]$Arguments = @(),
        [string]$ProcessName  # For duplicate detection
    )

    # Check if already running by testing the HTTP endpoint first
    # (more reliable than process name matching)
    Write-Log "Checking if $ServiceName is already running..."

    # Check by process name as a quick pre-check
    if ($ProcessName) {
        $existing = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
        if ($existing) {
            Write-Log "$ServiceName already running (PID $($existing[0].Id))" "OK"
            return $true
        }
    }

    Write-Log "Starting $ServiceName..."

    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $Executable
        $psi.Arguments = $Arguments -join " "
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        $psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden

        $proc = [System.Diagnostics.Process]::Start($psi)
        Write-Log "$ServiceName launched (PID $($proc.Id))"
        return $true
    }
    catch {
        Write-Log "Failed to start $ServiceName`: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# ─── Main Startup Sequence ───────────────────────────────────────────────────
function Start-KarmaServices {
    Write-Log "=========================================="
    Write-Log "Karma SADE Startup Orchestrator v1.0.0"
    Write-Log "=========================================="

    $startTime = Get-Date
    $allHealthy = $true

    # ── Step 0: Load Secrets ──
    Write-Log "── Step 0/3: Secrets Management ──"

    if (Test-Path $Config.SecretsScript) {
        try {
            & $Config.SecretsScript -Action env 2>&1 | Out-Null
            Write-Log "API keys loaded from encrypted store" "OK"
        }
        catch {
            Write-Log "Secrets script failed: $($_.Exception.Message)" "WARN"
            Write-Log "Services will use keys from database (if configured)" "WARN"
        }
    }
    else {
        Write-Log "Secrets script not found — skipping (keys from database)" "WARN"
    }

    # ── Step 1: Ollama ──
    Write-Log "── Step 1/3: Ollama ──"

    # Ollama is typically started by its own service/autostart, but verify
    $ollamaHealthy = $false
    try {
        $r = Invoke-WebRequest -Uri $Config.OllamaUrl -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -eq 200) {
            Write-Log "Ollama already running and healthy" "OK"
            $ollamaHealthy = $true
        }
    }
    catch {
        Write-Log "Ollama not responding, attempting to start..." "WARN"
        # Ollama is typically started via 'ollama serve' or its Windows service
        $ollamaPath = Get-Command "ollama" -ErrorAction SilentlyContinue
        if ($ollamaPath) {
            Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
            Write-Log "Issued 'ollama serve', waiting for health..."
            $ollamaHealthy = Test-ServiceHealth -Url $Config.OllamaUrl -ServiceName "Ollama" -TimeoutSeconds $Config.OllamaTimeout
        }
        else {
            Write-Log "Ollama not found in PATH — check installation" "ERROR"
            # Non-fatal: Open WebUI can still work with remote models (Groq/OpenAI)
        }
    }

    # ── Step 2: Open WebUI ──
    Write-Log "── Step 2/3: Open WebUI ──"

    # Check if already healthy
    $webuiAlreadyUp = $false
    try {
        $r = Invoke-WebRequest -Uri $Config.OpenWebUIUrl -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -eq 200) {
            Write-Log "Open WebUI already running and healthy" "OK"
            $webuiAlreadyUp = $true
        }
    }
    catch {}

    if (-not $webuiAlreadyUp) {
        if (-not (Test-Path $Config.OpenWebUIExe)) {
            Write-Log "Open WebUI executable not found at $($Config.OpenWebUIExe)" "ERROR"
            $allHealthy = $false
        }
        else {
            $launched = Start-ServiceProcess -ServiceName "Open WebUI" `
                -Executable $Config.OpenWebUIExe `
                -Arguments @("serve") `
                -ProcessName "open-webui"

            if ($launched) {
                Write-Log "Waiting for Open WebUI to become healthy (up to $($Config.OpenWebUITimeout)s)..." "WAIT"
                $webuiHealthy = Test-ServiceHealth -Url $Config.OpenWebUIUrl `
                    -ServiceName "Open WebUI" `
                    -TimeoutSeconds $Config.OpenWebUITimeout

                if (-not $webuiHealthy) {
                    Write-Log "Open WebUI failed to start — Cockpit will start but pinned tab may fail" "ERROR"
                    $allHealthy = $false
                }
            }
            else {
                $allHealthy = $false
            }
        }
    }

    # ── Step 3: Cockpit ──
    Write-Log "── Step 3/3: Cockpit ──"

    # Check if already healthy
    $cockpitAlreadyUp = $false
    try {
        $r = Invoke-WebRequest -Uri $Config.CockpitUrl -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -eq 200) {
            Write-Log "Cockpit already running and healthy" "OK"
            $cockpitAlreadyUp = $true
        }
    }
    catch {}

    if (-not $cockpitAlreadyUp) {
        # Kill any zombie on port 9400
        $zombies = netstat -ano 2>$null | Select-String ":9400\s+.*LISTEN"
        if ($zombies) {
            Write-Log "Port 9400 in use but Cockpit not healthy — killing zombie processes" "WARN"
            foreach ($line in $zombies) {
                if ($line -match '\s(\d+)\s*$') {
                    $pid = [int]$Matches[1]
                    if ($pid -gt 0) {
                        try {
                            Write-Log "Killing zombie PID $pid on port 9400" "WARN"
                            Stop-Process -Id $pid -Force -ErrorAction Stop
                            Start-Sleep -Seconds 2
                            Write-Log "Killed PID $pid" "OK"
                        }
                        catch {
                            Write-Log "Failed to kill PID $pid: $($_.Exception.Message)" "ERROR"
                        }
                    }
                }
            }
        }

        if (-not (Test-Path $Config.CockpitScript)) {
            Write-Log "Cockpit script not found at $($Config.CockpitScript)" "ERROR"
            $allHealthy = $false
        }
        else {
            $launched = Start-ServiceProcess -ServiceName "Cockpit" `
                -Executable "python" `
                -Arguments @("`"$($Config.CockpitScript)`"") `
                -ProcessName "python"

            if ($launched) {
                Write-Log "Waiting for Cockpit to become healthy (up to $($Config.CockpitTimeout)s)..." "WAIT"
                $cockpitHealthy = Test-ServiceHealth -Url $Config.CockpitUrl `
                    -ServiceName "Cockpit" `
                    -TimeoutSeconds $Config.CockpitTimeout

                if (-not $cockpitHealthy) {
                    Write-Log "Cockpit failed to start" "ERROR"
                    $allHealthy = $false
                }
            }
            else {
                $allHealthy = $false
            }
        }
    }

    # ── Summary ──
    $elapsed = ((Get-Date) - $startTime).TotalSeconds
    Write-Log "=========================================="
    if ($allHealthy) {
        Write-Log "Startup complete — all services healthy (${elapsed}s)" "OK"
    }
    else {
        Write-Log "Startup complete with ERRORS (${elapsed}s) — check log" "ERROR"
    }
    Write-Log "=========================================="
}

# ── Run ──
Start-KarmaServices
