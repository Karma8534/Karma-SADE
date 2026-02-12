<#
.SYNOPSIS
    Fix Watchdog Privileges - Recreate task with elevation
.DESCRIPTION
    The watchdog task was created without /rl highest due to access denied.
    This script fixes that by:
    1. Deleting the broken task
    2. Recreating with proper elevation
    3. Verifying it has admin privileges

    Run this with admin rights (right-click PowerShell → Run as Administrator)
.NOTES
    This is a ONE-TIME fix for the deployment issue.
    After running, verify with: Get-ScheduledTask -TaskName "KarmaSADE-Watchdog" | Select Principal
#>

$ErrorActionPreference = "Stop"

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Karma SADE — Watchdog Privilege Fix" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script requires administrator privileges" -ForegroundColor Red
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator', then run this script again." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Running with administrator privileges" -ForegroundColor Green
Write-Host ""

# Step 1: Check current task
Write-Host "[1/4] Checking current watchdog task..." -ForegroundColor Cyan

try {
    $currentTask = Get-ScheduledTask -TaskName "KarmaSADE-Watchdog" -ErrorAction Stop
    $currentRunLevel = $currentTask.Principal.RunLevel

    Write-Host "  Current task found" -ForegroundColor Yellow
    Write-Host "  Run Level: $currentRunLevel" -ForegroundColor Yellow

    if ($currentRunLevel -eq "Highest") {
        Write-Host ""
        Write-Host "[OK] Watchdog already has highest privileges — no fix needed!" -ForegroundColor Green
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 0
    }
    else {
        Write-Host "  Status: NEEDS FIX (should be 'Highest', currently '$currentRunLevel')" -ForegroundColor Red
    }
}
catch {
    Write-Host "  Watchdog task not found — will create it" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Delete broken task
Write-Host "[2/4] Removing broken task..." -ForegroundColor Cyan

try {
    Unregister-ScheduledTask -TaskName "KarmaSADE-Watchdog" -Confirm:$false -ErrorAction Stop
    Write-Host "  Task removed successfully" -ForegroundColor Green
}
catch {
    Write-Host "  No existing task to remove (this is OK)" -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Recreate with elevation
Write-Host "[3/4] Creating task with highest privileges..." -ForegroundColor Cyan

$scriptPath = "C:\Users\raest\Documents\Karma_SADE\Scripts\karma_watchdog.ps1"

if (-not (Test-Path $scriptPath)) {
    Write-Host ""
    Write-Host "[ERROR] Watchdog script not found at: $scriptPath" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

try {
    # Use schtasks with /rl highest
    $result = & schtasks /create `
        /tn "KarmaSADE-Watchdog" `
        /tr "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`"" `
        /sc minute `
        /mo 5 `
        /ru "$env:USERNAME" `
        /rl highest `
        /f 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Task created successfully" -ForegroundColor Green
    }
    else {
        Write-Host ""
        Write-Host "[ERROR] Task creation failed with exit code $LASTEXITCODE" -ForegroundColor Red
        Write-Host "  Output: $result" -ForegroundColor Red
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}
catch {
    Write-Host ""
    Write-Host "[ERROR] Task creation failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Step 4: Verify
Write-Host "[4/4] Verifying privileges..." -ForegroundColor Cyan

Start-Sleep -Seconds 2

try {
    $verifyTask = Get-ScheduledTask -TaskName "KarmaSADE-Watchdog" -ErrorAction Stop
    $verifyRunLevel = $verifyTask.Principal.RunLevel
    $verifyState = $verifyTask.State

    Write-Host "  Task Name: KarmaSADE-Watchdog" -ForegroundColor White
    Write-Host "  Run Level: $verifyRunLevel" -ForegroundColor $(if ($verifyRunLevel -eq "Highest") { "Green" } else { "Red" })
    Write-Host "  State: $verifyState" -ForegroundColor $(if ($verifyState -eq "Ready") { "Green" } else { "Yellow" })

    if ($verifyRunLevel -eq "Highest" -and $verifyState -eq "Ready") {
        Write-Host ""
        Write-Host "=" * 70 -ForegroundColor Green
        Write-Host "[SUCCESS] Watchdog task fixed!" -ForegroundColor Green
        Write-Host "=" * 70 -ForegroundColor Green
        Write-Host ""
        Write-Host "The watchdog can now:" -ForegroundColor White
        Write-Host "  ✓ Kill zombie processes" -ForegroundColor Green
        Write-Host "  ✓ Restart failed services" -ForegroundColor Green
        Write-Host "  ✓ Auto-recover from crashes" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next run: Every 5 minutes" -ForegroundColor Cyan
        Write-Host "Manual test: .\karma_watchdog.ps1" -ForegroundColor Cyan
        Write-Host ""
    }
    else {
        Write-Host ""
        Write-Host "[WARN] Task created but may have issues" -ForegroundColor Yellow
        Write-Host ""
    }
}
catch {
    Write-Host ""
    Write-Host "[ERROR] Could not verify task: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit"
