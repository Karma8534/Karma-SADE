# Karma SADE Resilience Deployment
# Date: 2026-02-12
# Purpose: Deploy startup orchestrator, watchdog, DB backup, and secrets manager
# Run as: .\deploy_resilience.ps1 -WhatIf (dry-run) | .\deploy_resilience.ps1 (execute)

[CmdletBinding(SupportsShouldProcess)]
param(
    [switch]$SkipSecrets,  # Skip API key migration
    [switch]$Force         # Overwrite existing tasks
)

$ErrorActionPreference = "Stop"
$scriptsDir = "C:\Users\raest\Documents\Karma_SADE\Scripts"
$startupDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"

Write-Host "`n=== Karma SADE Resilience Deployment ===" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
if ($WhatIfPreference) { Write-Host "[DRY-RUN MODE - No changes will be made]`n" -ForegroundColor Yellow }

# Pre-flight checks
Write-Host "`n[Pre-flight Checks]" -ForegroundColor Yellow
$checks = @{
    "Scripts directory" = Test-Path $scriptsDir
    "karma_startup.ps1" = Test-Path "$scriptsDir\karma_startup.ps1"
    "karma_startup.vbs" = Test-Path "$scriptsDir\karma_startup.vbs"
    "karma_watchdog.ps1" = Test-Path "$scriptsDir\karma_watchdog.ps1"
    "karma_backup_webui.ps1" = Test-Path "$scriptsDir\karma_backup_webui.ps1"
    "karma_secrets.ps1" = Test-Path "$scriptsDir\karma_secrets.ps1"
    "Startup folder" = Test-Path $startupDir
}

$failed = $false
foreach ($check in $checks.GetEnumerator()) {
    $status = if ($check.Value) { "✓" } else { "✗"; $failed = $true }
    $color = if ($check.Value) { "Green" } else { "Red" }
    Write-Host "  $status $($check.Key)" -ForegroundColor $color
}

if ($failed) {
    Write-Host "`nPre-flight checks failed. Aborting." -ForegroundColor Red
    exit 1
}

# Step 1: Replace Startup Scripts
Write-Host "`n[Step 1/7] Replace Startup Scripts" -ForegroundColor Cyan
$oldVBS = @("start_openwebui.vbs", "start_cockpit.vbs")
foreach ($file in $oldVBS) {
    $path = Join-Path $startupDir $file
    if (Test-Path $path) {
        if ($PSCmdlet.ShouldProcess($path, "Remove old startup script")) {
            Remove-Item $path -Force
            Write-Host "  Removed: $file" -ForegroundColor Green
        }
    } else {
        Write-Host "  Not found: $file (OK)" -ForegroundColor Gray
    }
}

$newVBS = "karma_startup.vbs"
$source = Join-Path $scriptsDir $newVBS
$dest = Join-Path $startupDir $newVBS
if ($PSCmdlet.ShouldProcess($dest, "Copy new unified startup launcher")) {
    Copy-Item $source $dest -Force
    Write-Host "  Installed: $newVBS" -ForegroundColor Green
}

# Step 2: Register Watchdog Task
Write-Host "`n[Step 2/7] Register Watchdog Scheduled Task" -ForegroundColor Cyan
$taskName = "KarmaSADE-Watchdog"
$taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($taskExists -and -not $Force -and -not $WhatIfPreference) {
    Write-Host "  Task '$taskName' already exists. Use -Force to overwrite." -ForegroundColor Yellow
} else {
    $action = "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File $scriptsDir\karma_watchdog.ps1"
    if ($PSCmdlet.ShouldProcess($taskName, "Register scheduled task (every 5 min)")) {
        schtasks /create /tn $taskName /tr $action /sc minute /mo 5 /ru $env:USERNAME /rl highest /f | Out-Null
        Write-Host "  Registered: $taskName (runs every 5 minutes)" -ForegroundColor Green
    }
}

# Step 3: Register DB Backup Task
Write-Host "`n[Step 3/7] Register DB Backup Scheduled Task" -ForegroundColor Cyan
$taskName = "KarmaSADE-BackupDB"
$taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($taskExists -and -not $Force -and -not $WhatIfPreference) {
    Write-Host "  Task '$taskName' already exists. Use -Force to overwrite." -ForegroundColor Yellow
} else {
    $action = "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File $scriptsDir\karma_backup_webui.ps1"
    if ($PSCmdlet.ShouldProcess($taskName, "Register scheduled task (daily 3:00 AM)")) {
        schtasks /create /tn $taskName /tr $action /sc daily /st 03:00 /ru $env:USERNAME /f | Out-Null
        Write-Host "  Registered: $taskName (runs daily at 3:00 AM)" -ForegroundColor Green
    }
}

# Step 4: Store API Keys in Encrypted Vault
Write-Host "`n[Step 4/7] Store API Keys in Encrypted Vault" -ForegroundColor Cyan
if ($SkipSecrets) {
    Write-Host "  Skipped (-SkipSecrets flag)" -ForegroundColor Yellow
} elseif ($WhatIfPreference) {
    Write-Host "  Would prompt for: openai_api_key, groq_api_key, gemini_api_key" -ForegroundColor Gray
} else {
    Write-Host "  This step requires manual input for each API key." -ForegroundColor Yellow
    Write-Host "  Press Enter to continue, or Ctrl+C to skip..." -ForegroundColor Yellow
    Read-Host

    $keys = @("openai_api_key", "groq_api_key", "gemini_api_key")
    foreach ($key in $keys) {
        Write-Host "`n  Storing: $key" -ForegroundColor White
        & "$scriptsDir\karma_secrets.ps1" -Action store -Key $key
    }

    Write-Host "`n  Verifying stored keys:" -ForegroundColor White
    & "$scriptsDir\karma_secrets.ps1" -Action list
}

# Step 5: Run First Backup Manually
Write-Host "`n[Step 5/7] Run First DB Backup" -ForegroundColor Cyan
if ($PSCmdlet.ShouldProcess("webui.db", "Create initial backup")) {
    & "$scriptsDir\karma_backup_webui.ps1"

    $backupDir = "$env:USERPROFILE\karma\backups"
    if (Test-Path $backupDir) {
        $backups = Get-ChildItem $backupDir -Filter "webui-*.db" | Sort-Object LastWriteTime -Descending | Select-Object -First 3
        Write-Host "  Latest backups:" -ForegroundColor Green
        foreach ($backup in $backups) {
            $size = [math]::Round($backup.Length / 1MB, 2)
            Write-Host "    - $($backup.Name) ($size MB)" -ForegroundColor Gray
        }
    }
}

# Step 6: Test Watchdog
Write-Host "`n[Step 6/7] Test Watchdog" -ForegroundColor Cyan
if ($PSCmdlet.ShouldProcess("karma_watchdog.ps1", "Run initial health check")) {
    & "$scriptsDir\karma_watchdog.ps1"

    $logFile = "C:\Users\raest\Documents\Karma_SADE\Logs\karma-watchdog.log"
    if (Test-Path $logFile) {
        Write-Host "  Last 5 log lines:" -ForegroundColor Green
        Get-Content $logFile -Tail 5 | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    }
}

# Step 7: Git Push
Write-Host "`n[Step 7/7] Git Commit + Push" -ForegroundColor Cyan
if ($WhatIfPreference) {
    Write-Host "  Would run: git add -A && git commit && git push origin main" -ForegroundColor Gray
} else {
    Write-Host "  Ready to commit and push changes to GitHub." -ForegroundColor Yellow
    Write-Host "  Commit message: 'resilience: startup orchestrator, watchdog, secrets manager, db backup, sentinel v1.1.0'" -ForegroundColor Gray
    Write-Host "`n  Press Enter to proceed, or Ctrl+C to skip..." -ForegroundColor Yellow
    Read-Host

    Push-Location "C:\Users\raest\Documents\Karma_SADE"
    try {
        git add -A
        git commit -m "resilience: startup orchestrator, watchdog, secrets manager, db backup, sentinel v1.1.0"
        git push origin main
        Write-Host "  ✓ Pushed to GitHub" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Git push failed: $_" -ForegroundColor Red
    } finally {
        Pop-Location
    }
}

# Summary
Write-Host "`n=== Deployment Complete ===" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Reboot PAYBACK to test new startup orchestrator" -ForegroundColor White
Write-Host "  2. Verify services start in order: Ollama → WebUI → Cockpit" -ForegroundColor White
Write-Host "  3. Check watchdog log: Logs\karma-watchdog.log" -ForegroundColor White
Write-Host "  4. Verify backup: $env:USERPROFILE\karma\backups\" -ForegroundColor White
Write-Host "`nResilience gaps 2-5 now deployed. System is hardened.`n" -ForegroundColor Green
