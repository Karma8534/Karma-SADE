<#
.SYNOPSIS
    Karma SADE — Comprehensive Health Check v1.0.0
.DESCRIPTION
    Quick visual dashboard of all Karma SADE components.
    Run this anytime to check system status.

    Checks:
    - Service health (HTTP endpoints)
    - Scheduled task status
    - Watchdog state
    - Backup status
    - Secrets configuration
    - Recent errors in logs

    Color-coded output:
    - Green: Healthy
    - Yellow: Warning
    - Red: Critical issue

.EXAMPLE
    .\karma_health_check.ps1

.EXAMPLE
    .\karma_health_check.ps1 -Detailed
#>

param(
    [switch]$Detailed,
    [switch]$Json
)

$ErrorActionPreference = "Continue"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

function Test-ServiceHealth {
    param([string]$Url, [string]$Name)

    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        return @{
            name = $Name
            status = "healthy"
            code = $response.StatusCode
            url = $Url
        }
    }
    catch {
        return @{
            name = $Name
            status = "down"
            error = $_.Exception.Message
            url = $Url
        }
    }
}

function Get-ColoredStatus {
    param([string]$Status)

    switch ($Status) {
        "healthy" { return "Green" }
        "ok" { return "Green" }
        "ready" { return "Green" }
        "warning" { return "Yellow" }
        "degraded" { return "Yellow" }
        "down" { return "Red" }
        "critical" { return "Red" }
        "error" { return "Red" }
        default { return "White" }
    }
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "═══ $Title " -NoNewline -ForegroundColor Cyan
    Write-Host ("═" * (65 - $Title.Length)) -ForegroundColor Cyan
}

# ---------------------------------------------------------------------------
# Health Checks
# ---------------------------------------------------------------------------

$results = @{}

# Header
if (-not $Json) {
    Clear-Host
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         KARMA SADE — System Health Check v1.0.0                   ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
}

# ── Services ──
if (-not $Json) { Write-Section "Services" }

$services = @(
    Test-ServiceHealth -Url "http://localhost:11434" -Name "Ollama"
    Test-ServiceHealth -Url "http://localhost:8080" -Name "Open WebUI"
    Test-ServiceHealth -Url "http://localhost:9400/health" -Name "Cockpit"
)

$results["services"] = $services

if (-not $Json) {
    foreach ($svc in $services) {
        $color = Get-ColoredStatus $svc.status
        $icon = if ($svc.status -eq "healthy") { "✓" } else { "✗" }
        Write-Host "  $icon " -NoNewline -ForegroundColor $color
        Write-Host ("{0,-15}" -f $svc.name) -NoNewline
        Write-Host (" {0,-10}" -f $svc.status.ToUpper()) -ForegroundColor $color -NoNewline
        if ($svc.code) {
            Write-Host " (HTTP $($svc.code))" -ForegroundColor Gray
        } elseif ($svc.error) {
            Write-Host " ($($svc.error.Substring(0, [Math]::Min(40, $svc.error.Length))))" -ForegroundColor Gray
        } else {
            Write-Host ""
        }
    }
}

# ── Scheduled Tasks ──
if (-not $Json) { Write-Section "Scheduled Tasks" }

try {
    $tasks = Get-ScheduledTask -TaskName "KarmaSADE-*" -ErrorAction SilentlyContinue |
        Select-Object TaskName, State, @{Name="LastRun";Expression={(Get-ScheduledTaskInfo -TaskName $_.TaskName).LastRunTime}}, @{Name="Result";Expression={(Get-ScheduledTaskInfo -TaskName $_.TaskName).LastTaskResult}}

    $results["scheduled_tasks"] = $tasks | ForEach-Object {
        @{
            name = $_.TaskName
            state = $_.State
            last_run = $_.LastRun
            last_result = $_.Result
        }
    }

    if (-not $Json) {
        foreach ($task in $tasks) {
            $healthy = ($task.State -eq "Ready" -and $task.Result -eq 0)
            $color = if ($healthy) { "Green" } else { "Yellow" }
            $icon = if ($healthy) { "✓" } else { "⚠" }
            $name = $task.TaskName -replace "KarmaSADE-", ""

            Write-Host "  $icon " -NoNewline -ForegroundColor $color
            Write-Host ("{0,-20}" -f $name) -NoNewline
            Write-Host ("{0,-10}" -f $task.State) -ForegroundColor $color -NoNewline

            if ($Detailed -and $task.LastRun) {
                $ago = ((Get-Date) - $task.LastRun).TotalMinutes
                Write-Host (" (ran {0:N0}m ago)" -f $ago) -ForegroundColor Gray
            } else {
                Write-Host ""
            }
        }
    }
}
catch {
    $results["scheduled_tasks"] = @{ error = $_.Exception.Message }
    if (-not $Json) {
        Write-Host "  ✗ Failed to query tasks: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ── Watchdog State ──
if (-not $Json) { Write-Section "Watchdog" }

$watchdogState = "C:\Users\raest\Documents\Karma_SADE\Logs\watchdog-state.json"
if (Test-Path $watchdogState) {
    try {
        $state = Get-Content $watchdogState -Raw | ConvertFrom-Json
        $results["watchdog"] = $state

        if (-not $Json) {
            foreach ($svc in $state.PSObject.Properties) {
                $fails = $svc.Value.consecutive_fails
                $gaveUp = $svc.Value.gave_up

                $status = if ($gaveUp) { "GAVE UP" } elseif ($fails -gt 0) { "FAILING" } else { "HEALTHY" }
                $color = if ($gaveUp) { "Red" } elseif ($fails -gt 0) { "Yellow" } else { "Green" }
                $icon = if ($gaveUp) { "✗" } elseif ($fails -gt 0) { "⚠" } else { "✓" }

                Write-Host "  $icon " -NoNewline -ForegroundColor $color
                Write-Host ("{0,-15}" -f $svc.Name) -NoNewline
                Write-Host ("{0,-10}" -f $status) -ForegroundColor $color

                if ($Detailed -and $fails -gt 0) {
                    Write-Host "      └─ Consecutive failures: $fails" -ForegroundColor Gray
                    if ($svc.Value.last_restart) {
                        Write-Host "      └─ Last restart: $($svc.Value.last_restart)" -ForegroundColor Gray
                    }
                }
            }
        }
    }
    catch {
        $results["watchdog"] = @{ error = $_.Exception.Message }
        if (-not $Json) {
            Write-Host "  ✗ Failed to read watchdog state" -ForegroundColor Red
        }
    }
}
else {
    $results["watchdog"] = @{ status = "no_data" }
    if (-not $Json) {
        Write-Host "  ⚠ Watchdog has not run yet" -ForegroundColor Yellow
    }
}

# ── Backups ──
if (-not $Json) { Write-Section "Backups" }

$backupDir = Join-Path $env:USERPROFILE "karma\backups"
if (Test-Path $backupDir) {
    $backups = Get-ChildItem -Path $backupDir -Filter "webui_*.db" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending

    if ($backups) {
        $latest = $backups[0]
        $ageHours = ((Get-Date) - $latest.LastWriteTime).TotalHours
        $stale = $ageHours -gt 26  # Should run daily at 3am

        $results["backups"] = @{
            latest_file = $latest.Name
            age_hours = [math]::Round($ageHours, 1)
            size_mb = [math]::Round($latest.Length / 1MB, 2)
            total_count = $backups.Count
            stale = $stale
        }

        if (-not $Json) {
            $color = if ($stale) { "Yellow" } else { "Green" }
            $icon = if ($stale) { "⚠" } else { "✓" }

            Write-Host "  $icon Latest backup: " -NoNewline -ForegroundColor $color
            Write-Host "$($latest.Name)" -ForegroundColor White
            Write-Host "    Age: " -NoNewline -ForegroundColor Gray
            Write-Host ("{0:N1} hours" -f $ageHours) -ForegroundColor $(if ($stale) { "Yellow" } else { "White" })
            Write-Host "    Size: " -NoNewline -ForegroundColor Gray
            Write-Host ("{0:N2} MB" -f ($latest.Length / 1MB)) -ForegroundColor White
            Write-Host "    Total backups: " -NoNewline -ForegroundColor Gray
            Write-Host $backups.Count -ForegroundColor White
        }
    }
    else {
        $results["backups"] = @{ status = "no_backups" }
        if (-not $Json) {
            Write-Host "  ✗ No backups found!" -ForegroundColor Red
        }
    }
}
else {
    $results["backups"] = @{ status = "no_directory" }
    if (-not $Json) {
        Write-Host "  ✗ Backup directory does not exist" -ForegroundColor Red
    }
}

# ── Secrets ──
if (-not $Json) { Write-Section "Secrets Management" }

$secretsFile = Join-Path $env:USERPROFILE "karma\secrets.json"
if (Test-Path $secretsFile) {
    try {
        $secrets = Get-Content $secretsFile -Raw | ConvertFrom-Json
        $keyCount = ($secrets.PSObject.Properties | Measure-Object).Count

        $results["secrets"] = @{
            configured = $true
            key_count = $keyCount
        }

        if (-not $Json) {
            Write-Host "  ✓ Configured" -ForegroundColor Green
            Write-Host "    Keys stored: $keyCount" -ForegroundColor White
        }
    }
    catch {
        $results["secrets"] = @{ configured = $true; error = "corrupted" }
        if (-not $Json) {
            Write-Host "  ⚠ File exists but is corrupted" -ForegroundColor Yellow
        }
    }
}
else {
    $results["secrets"] = @{ configured = $false }
    if (-not $Json) {
        Write-Host "  ✗ NOT CONFIGURED — API keys may be in plaintext!" -ForegroundColor Red
        Write-Host "    Action required: Run .\karma_secrets.ps1" -ForegroundColor Yellow
    }
}

# ── Recent Errors ──
if ($Detailed -and -not $Json) {
    Write-Section "Recent Errors (Last 24h)"

    $logDir = "C:\Users\raest\Documents\Karma_SADE\Logs"
    $errorCount = 0

    Get-ChildItem -Path $logDir -Filter "*.log" -ErrorAction SilentlyContinue | ForEach-Object {
        $cutoff = (Get-Date).AddHours(-24)
        $errors = Get-Content $_.FullName -Tail 500 -ErrorAction SilentlyContinue |
            Where-Object { $_ -match "\[ERROR\]|\[CRITICAL\]" } |
            Where-Object {
                if ($_ -match '^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]') {
                    try {
                        $timestamp = [datetime]::ParseExact($Matches[1], "yyyy-MM-dd HH:mm:ss", $null)
                        return $timestamp -gt $cutoff
                    } catch {
                        return $false
                    }
                }
                return $false
            }

        if ($errors) {
            $errorCount += $errors.Count
            Write-Host "  ⚠ $($_.Name): $($errors.Count) errors" -ForegroundColor Yellow
            $errors | Select-Object -First 3 | ForEach-Object {
                $line = $_ -replace '\[ERROR\]|\[CRITICAL\]', '' -replace '^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]', ''
                Write-Host "      └─ $($line.Trim().Substring(0, [Math]::Min(70, $line.Length)))" -ForegroundColor Gray
            }
        }
    }

    if ($errorCount -eq 0) {
        Write-Host "  ✓ No errors in last 24 hours" -ForegroundColor Green
    }
}

# ── Summary ──
if (-not $Json) {
    Write-Host ""
    Write-Host "═══ Summary " -NoNewline -ForegroundColor Cyan
    Write-Host ("═" * 60) -ForegroundColor Cyan

    $servicesDown = ($services | Where-Object { $_.status -ne "healthy" }).Count
    $tasksIssues = ($tasks | Where-Object { $_.State -ne "Ready" -or $_.Result -ne 0 }).Count
    $watchdogIssues = if ($results.watchdog.error -or $results.watchdog.status -eq "no_data") { 1 } else {
        ($state.PSObject.Properties | Where-Object { $_.Value.consecutive_fails -gt 0 -or $_.Value.gave_up }).Count
    }
    $backupStale = $results.backups.stale -eq $true
    $secretsMissing = $results.secrets.configured -eq $false

    $overallStatus = if ($servicesDown -gt 0) {
        "CRITICAL"
    } elseif ($watchdogIssues -gt 0 -or $tasksIssues -gt 0) {
        "DEGRADED"
    } elseif ($backupStale -or $secretsMissing) {
        "WARNING"
    } else {
        "HEALTHY"
    }

    $color = Get-ColoredStatus $overallStatus
    Write-Host ""
    Write-Host "  Overall Status: " -NoNewline -ForegroundColor White
    Write-Host $overallStatus -ForegroundColor $color
    Write-Host ""

    if ($servicesDown -gt 0) {
        Write-Host "  ✗ $servicesDown service(s) down" -ForegroundColor Red
    }
    if ($tasksIssues -gt 0) {
        Write-Host "  ⚠ $tasksIssues scheduled task(s) have issues" -ForegroundColor Yellow
    }
    if ($watchdogIssues -gt 0) {
        Write-Host "  ⚠ $watchdogIssues service(s) with watchdog issues" -ForegroundColor Yellow
    }
    if ($backupStale) {
        Write-Host "  ⚠ Backups are stale (>26 hours old)" -ForegroundColor Yellow
    }
    if ($secretsMissing) {
        Write-Host "  ✗ Secrets management not configured" -ForegroundColor Red
    }
    if ($overallStatus -eq "HEALTHY") {
        Write-Host "  ✓ All systems operational" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "═" * 71 -ForegroundColor Cyan
    Write-Host ""
}

# ── JSON Output ──
if ($Json) {
    $results | ConvertTo-Json -Depth 5
}
