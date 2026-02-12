<#
.SYNOPSIS
    Test Karma Dashboard v1.0.0
.DESCRIPTION
    Quick test script to verify dashboard is working correctly.
    Tests all endpoints and opens the visual dashboard in browser.
#>

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Karma SADE Dashboard Test" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Test 1: Cockpit Health
Write-Host "[1/5] Testing Cockpit health..." -ForegroundColor Cyan
try {
    $health = Invoke-WebRequest -Uri "http://localhost:9400/health" -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "  ✓ Cockpit is running (HTTP $($health.StatusCode))" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Cockpit is not responding" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Start Cockpit first: python Scripts\karma_cockpit_service.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Dashboard JSON endpoint
Write-Host "[2/5] Testing dashboard JSON API..." -ForegroundColor Cyan
try {
    $dashboard = Invoke-WebRequest -Uri "http://localhost:9400/dashboard" -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop -Headers @{"Accept"="application/json"}
    $data = $dashboard.Content | ConvertFrom-Json
    Write-Host "  ✓ Dashboard API working (HTTP $($dashboard.StatusCode))" -ForegroundColor Green
    Write-Host "  Overall status: $($data.overall)" -ForegroundColor $(if ($data.overall -eq "healthy") { "Green" } else { "Yellow" })
}
catch {
    Write-Host "  ✗ Dashboard API failed" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Dashboard HTML file
Write-Host "[3/5] Testing dashboard HTML file..." -ForegroundColor Cyan
$dashboardFile = Join-Path $env:USERPROFILE "Documents\Karma_SADE\Dashboard\index.html"
if (Test-Path $dashboardFile) {
    $size = (Get-Item $dashboardFile).Length / 1KB
    Write-Host "  ✓ Dashboard HTML exists ($([math]::Round($size, 1)) KB)" -ForegroundColor Green
}
else {
    Write-Host "  ✗ Dashboard HTML not found at: $dashboardFile" -ForegroundColor Red
}

Write-Host ""

# Test 4: Service endpoints
Write-Host "[4/5] Testing service endpoints..." -ForegroundColor Cyan
$endpoints = @(
    @{Name="Services"; Path="/dashboard/services"},
    @{Name="Tasks"; Path="/dashboard/tasks"},
    @{Name="Watchdog"; Path="/dashboard/watchdog"},
    @{Name="Backups"; Path="/dashboard/backups"}
)

foreach ($ep in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9400$($ep.Path)" -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop -Headers @{"Accept"="application/json"}
        Write-Host "  ✓ $($ep.Name) endpoint working" -ForegroundColor Green
    }
    catch {
        Write-Host "  ⚠ $($ep.Name) endpoint issue: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host ""

# Test 5: Open in browser
Write-Host "[5/5] Opening dashboard in browser..." -ForegroundColor Cyan
try {
    Start-Process "http://localhost:9400/dashboard"
    Write-Host "  ✓ Browser launched" -ForegroundColor Green
    Write-Host ""
    Write-Host "The dashboard should open in your default browser." -ForegroundColor White
    Write-Host "If you see a login prompt, the HTML isn't being served correctly." -ForegroundColor Gray
}
catch {
    Write-Host "  ⚠ Could not launch browser: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "  Manually open: http://localhost:9400/dashboard" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard URL: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:9400/dashboard" -ForegroundColor Cyan
Write-Host ""
Write-Host "JSON API: " -NoNewline -ForegroundColor White
Write-Host "curl http://localhost:9400/dashboard" -ForegroundColor Cyan
Write-Host ""
Write-Host "Health Check: " -NoNewline -ForegroundColor White
Write-Host ".\karma_health_check.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
