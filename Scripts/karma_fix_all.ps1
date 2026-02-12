<#
.SYNOPSIS
    Karma SADE — Fix All Critical Issues v1.0.0
.DESCRIPTION
    Comprehensive fix for all deployment issues found in audit:
    1. Fix watchdog privileges (requires admin)
    2. Verify sqlite3 installation
    3. Test startup script
    4. Create rollback backup
    5. Initialize secrets management (optional)
    6. Restart Cockpit with dashboard enabled

    Run this with admin rights to fix all issues at once.
.NOTES
    This is a ONE-TIME fix for Warp Dev's deployment gaps.
    After running, system will be fully operational.
#>

param(
    [switch]$SkipWatchdogFix,
    [switch]$SkipStartupTest,
    [switch]$SkipSecretsSetup
)

$ErrorActionPreference = "Continue"

# ─── Header ──────────────────────────────────────────────────────────────────
Clear-Host
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         KARMA SADE — Fix All Critical Issues v1.0.0               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin -and -not $SkipWatchdogFix) {
    Write-Host "[WARN] Not running as administrator" -ForegroundColor Yellow
    Write-Host "       Watchdog fix will be skipped (requires admin)" -ForegroundColor Yellow
    Write-Host ""
    $SkipWatchdogFix = $true
}

$issues = @()
$fixed = @()
$warnings = @()

# ─── Fix 1: Watchdog Privileges ─────────────────────────────────────────────
Write-Host "[1/6] Checking Watchdog Privileges..." -ForegroundColor Cyan

if ($SkipWatchdogFix) {
    Write-Host "  ⊘ Skipped (no admin rights)" -ForegroundColor Yellow
    $warnings += "Watchdog privileges not fixed (rerun as admin)"
}
else {
    try {
        $task = Get-ScheduledTask -TaskName "KarmaSADE-Watchdog" -ErrorAction Stop
        $runLevel = $task.Principal.RunLevel

        if ($runLevel -ne "Highest") {
            Write-Host "  ⚠ Watchdog has '$runLevel' privileges (should be 'Highest')" -ForegroundColor Yellow
            Write-Host "    Recreating task with elevation..." -ForegroundColor Cyan

            # Delete and recreate
            Unregister-ScheduledTask -TaskName "KarmaSADE-Watchdog" -Confirm:$false -ErrorAction Stop

            $scriptPath = "C:\Users\raest\Documents\Karma_SADE\Scripts\karma_watchdog.ps1"
            $result = & schtasks /create /tn "KarmaSADE-Watchdog" /tr "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`"" /sc minute /mo 5 /ru "$env:USERNAME" /rl highest /f 2>&1

            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✓ Watchdog privileges fixed" -ForegroundColor Green
                $fixed += "Watchdog privileges"
            }
            else {
                Write-Host "  ✗ Failed to fix: $result" -ForegroundColor Red
                $issues += "Watchdog privileges"
            }
        }
        else {
            Write-Host "  ✓ Already has highest privileges" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
        $issues += "Watchdog privileges check"
    }
}

Write-Host ""

# ─── Fix 2: SQLite3 Installation ────────────────────────────────────────────
Write-Host "[2/6] Checking SQLite3..." -ForegroundColor Cyan

$sqlite3 = Get-Command "sqlite3" -ErrorAction SilentlyContinue
if ($sqlite3) {
    Write-Host "  ✓ sqlite3 found at: $($sqlite3.Source)" -ForegroundColor Green
}
else {
    Write-Host "  ⚠ sqlite3 NOT found in PATH" -ForegroundColor Yellow
    Write-Host "    Backups will use less-safe file copy method" -ForegroundColor Yellow
    Write-Host "    Install with: choco install sqlite  OR  scoop install sqlite" -ForegroundColor Cyan
    $warnings += "sqlite3 not installed (backups less safe)"
}

Write-Host ""

# ─── Fix 3: Rollback Backup ─────────────────────────────────────────────────
Write-Host "[3/6] Creating Rollback Backup..." -ForegroundColor Cyan

$backupDir = Join-Path $env:USERPROFILE "karma\backups\rollback"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupZip = Join-Path $backupDir "resilience-v1-$timestamp.zip"

try {
    $scriptsDir = "C:\Users\raest\Documents\Karma_SADE\Scripts"
    $startupVBS = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup\karma_startup.vbs"

    $filesToBackup = @(
        $scriptsDir + "\karma_startup.ps1",
        $scriptsDir + "\karma_watchdog.ps1",
        $scriptsDir + "\karma_backup_webui.ps1",
        $scriptsDir + "\karma_secrets.ps1",
        $startupVBS
    ) | Where-Object { Test-Path $_ }

    if ($filesToBackup.Count -gt 0) {
        Compress-Archive -Path $filesToBackup -DestinationPath $backupZip -Force
        $size = (Get-Item $backupZip).Length / 1KB
        Write-Host "  ✓ Backup created: $backupZip ($([math]::Round($size, 1)) KB)" -ForegroundColor Green
        $fixed += "Rollback backup"
    }
    else {
        Write-Host "  ⚠ No files found to backup" -ForegroundColor Yellow
        $warnings += "No files backed up"
    }
}
catch {
    Write-Host "  ✗ Backup failed: $($_.Exception.Message)" -ForegroundColor Red
    $issues += "Rollback backup"
}

Write-Host ""

# ─── Fix 4: Secrets Management ──────────────────────────────────────────────
Write-Host "[4/6] Checking Secrets Management..." -ForegroundColor Cyan

$secretsFile = Join-Path $env:USERPROFILE "karma\secrets.json"

if (Test-Path $secretsFile) {
    try {
        $secrets = Get-Content $secretsFile -Raw | ConvertFrom-Json
        $keyCount = ($secrets.PSObject.Properties | Measure-Object).Count
        Write-Host "  ✓ Secrets configured ($keyCount keys stored)" -ForegroundColor Green
    }
    catch {
        Write-Host "  ⚠ Secrets file exists but is corrupted" -ForegroundColor Yellow
        $warnings += "Secrets file corrupted"
    }
}
else {
    Write-Host "  ⚠ Secrets NOT configured" -ForegroundColor Yellow
    Write-Host "    API keys may be in plaintext in Open WebUI database" -ForegroundColor Yellow
    Write-Host ""

    if ($SkipSecretsSetup) {
        Write-Host "    Skipped secrets setup (use -SkipSecretsSetup:$false to enable)" -ForegroundColor Cyan
        $warnings += "Secrets not configured"
    }
    else {
        Write-Host "    Would you like to configure secrets now? (y/n): " -NoNewline -ForegroundColor Cyan
        $response = Read-Host

        if ($response -eq "y") {
            Write-Host ""
            Write-Host "    Launching secrets manager..." -ForegroundColor Cyan
            Write-Host "    You'll be prompted to enter your API keys." -ForegroundColor Gray
            Write-Host ""

            $secretsScript = "C:\Users\raest\Documents\Karma_SADE\Scripts\karma_secrets.ps1"

            foreach ($key in @("openai_api_key", "groq_api_key", "gemini_api_key")) {
                Write-Host "    Enter $key (or leave blank to skip): " -ForegroundColor Cyan
                & $secretsScript -Action store -Key $key
                Write-Host ""
            }

            Write-Host "  ✓ Secrets configured" -ForegroundColor Green
            $fixed += "Secrets management"
        }
        else {
            Write-Host "  ⊘ Skipped by user" -ForegroundColor Yellow
            $warnings += "Secrets not configured"
        }
    }
}

Write-Host ""

# ─── Fix 5: Test Startup Script ────────────────────────────────────────────
Write-Host "[5/6] Testing Startup Script..." -ForegroundColor Cyan

if ($SkipStartupTest) {
    Write-Host "  ⊘ Skipped (use -SkipStartupTest:$false to enable)" -ForegroundColor Yellow
    $warnings += "Startup script not tested"
}
else {
    $startupScript = "C:\Users\raest\Documents\Karma_SADE\Scripts\karma_startup.ps1"

    if (Test-Path $startupScript) {
        Write-Host "  Running startup orchestrator..." -ForegroundColor Cyan
        Write-Host "  (This may take up to 3 minutes)" -ForegroundColor Gray
        Write-Host ""

        try {
            & $startupScript 2>&1 | Out-Null
            $logFile = "C:\Users\raest\Documents\Karma_SADE\Logs\karma-startup.log"

            if (Test-Path $logFile) {
                $lastLines = Get-Content $logFile -Tail 5
                $success = $lastLines | Where-Object { $_ -match "all services healthy" }

                if ($success) {
                    Write-Host "  ✓ Startup test successful" -ForegroundColor Green
                    $fixed += "Startup script tested"
                }
                else {
                    Write-Host "  ⚠ Startup completed with warnings" -ForegroundColor Yellow
                    Write-Host "    Check log: $logFile" -ForegroundColor Cyan
                    $warnings += "Startup had warnings"
                }
            }
            else {
                Write-Host "  ⚠ Startup ran but no log created" -ForegroundColor Yellow
                $warnings += "No startup log"
            }
        }
        catch {
            Write-Host "  ✗ Startup failed: $($_.Exception.Message)" -ForegroundColor Red
            $issues += "Startup script test"
        }
    }
    else {
        Write-Host "  ✗ Startup script not found" -ForegroundColor Red
        $issues += "Startup script missing"
    }
}

Write-Host ""

# ─── Fix 6: Restart Cockpit with Dashboard ─────────────────────────────────
Write-Host "[6/6] Restarting Cockpit with Dashboard..." -ForegroundColor Cyan

try {
    # Kill existing Cockpit
    $cockpitProcesses = Get-Process python -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*karma_cockpit_service.py*" }

    foreach ($proc in $cockpitProcesses) {
        Write-Host "  Stopping existing Cockpit (PID $($proc.Id))..." -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force
    }

    Start-Sleep -Seconds 2

    # Start Cockpit
    $cockpitScript = "C:\Users\raest\Documents\Karma_SADE\Scripts\karma_cockpit_service.py"

    if (Test-Path $cockpitScript) {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = "python"
        $psi.Arguments = "`"$cockpitScript`""
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        $psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden

        $proc = [System.Diagnostics.Process]::Start($psi)
        Write-Host "  Cockpit started (PID $($proc.Id))" -ForegroundColor Green

        # Wait for health
        Start-Sleep -Seconds 5

        $health = Invoke-WebRequest -Uri "http://localhost:9400/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($health.StatusCode -eq 200) {
            Write-Host "  ✓ Cockpit healthy" -ForegroundColor Green

            # Test dashboard
            try {
                $dashboard = Invoke-WebRequest -Uri "http://localhost:9400/dashboard" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
                if ($dashboard.StatusCode -eq 200) {
                    Write-Host "  ✓ Dashboard enabled at http://localhost:9400/dashboard" -ForegroundColor Green
                    $fixed += "Cockpit dashboard"
                }
                else {
                    Write-Host "  ⚠ Dashboard endpoint returned HTTP $($dashboard.StatusCode)" -ForegroundColor Yellow
                    $warnings += "Dashboard status $($dashboard.StatusCode)"
                }
            }
            catch {
                Write-Host "  ⚠ Dashboard not responding: $($_.Exception.Message)" -ForegroundColor Yellow
                $warnings += "Dashboard not available"
            }
        }
        else {
            Write-Host "  ⚠ Cockpit running but not healthy (HTTP $($health.StatusCode))" -ForegroundColor Yellow
            $warnings += "Cockpit not healthy"
        }
    }
    else {
        Write-Host "  ✗ Cockpit script not found" -ForegroundColor Red
        $issues += "Cockpit script missing"
    }
}
catch {
    Write-Host "  ✗ Failed to restart Cockpit: $($_.Exception.Message)" -ForegroundColor Red
    $issues += "Cockpit restart"
}

# ─── Summary ─────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                            SUMMARY                                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

if ($fixed.Count -gt 0) {
    Write-Host "✓ Fixed ($($fixed.Count)):" -ForegroundColor Green
    foreach ($item in $fixed) {
        Write-Host "  • $item" -ForegroundColor Green
    }
    Write-Host ""
}

if ($warnings.Count -gt 0) {
    Write-Host "⚠ Warnings ($($warnings.Count)):" -ForegroundColor Yellow
    foreach ($item in $warnings) {
        Write-Host "  • $item" -ForegroundColor Yellow
    }
    Write-Host ""
}

if ($issues.Count -gt 0) {
    Write-Host "✗ Issues Remaining ($($issues.Count)):" -ForegroundColor Red
    foreach ($item in $issues) {
        Write-Host "  • $item" -ForegroundColor Red
    }
    Write-Host ""
}

# Overall status
$overallStatus = if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    "FULLY OPERATIONAL"
} elseif ($issues.Count -eq 0) {
    "OPERATIONAL WITH WARNINGS"
} else {
    "ISSUES REMAIN"
}

$color = if ($overallStatus -eq "FULLY OPERATIONAL") { "Green" } elseif ($issues.Count -eq 0) { "Yellow" } else { "Red" }

Write-Host "System Status: " -NoNewline -ForegroundColor White
Write-Host $overallStatus -ForegroundColor $color
Write-Host ""

# Next steps
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host ""

if ($issues.Count -gt 0) {
    Write-Host "  1. Review and fix remaining issues above" -ForegroundColor Yellow
}

if ($warnings -contains "Watchdog privileges not fixed (rerun as admin)") {
    Write-Host "  2. Rerun this script as admin to fix watchdog" -ForegroundColor Yellow
}

Write-Host "  3. Run health check: .\karma_health_check.ps1" -ForegroundColor Cyan
Write-Host "  4. View dashboard: http://localhost:9400/dashboard" -ForegroundColor Cyan
Write-Host "  5. Test reboot (optional): Restart Windows and verify all services start" -ForegroundColor Cyan
Write-Host ""

Write-Host "═" * 71 -ForegroundColor Cyan
Write-Host ""
