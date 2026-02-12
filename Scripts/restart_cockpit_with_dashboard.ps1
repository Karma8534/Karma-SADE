# Restart Cockpit with Dashboard
# This script stops the current Cockpit and starts it fresh with dashboard enabled

Write-Host ""
Write-Host "Restarting Cockpit with Dashboard..." -ForegroundColor Cyan
Write-Host ""

# Stop current Cockpit
Write-Host "[1/3] Stopping current Cockpit..." -ForegroundColor Cyan
$stopped = $false
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        Write-Host "  Stopped PID $($_.Id)" -ForegroundColor Green
        $stopped = $true
    }
    catch {}
}

if (-not $stopped) {
    Write-Host "  No Cockpit process found (already stopped)" -ForegroundColor Yellow
}

Start-Sleep -Seconds 2

# Start Cockpit with dashboard
Write-Host ""
Write-Host "[2/3] Starting Cockpit with dashboard..." -ForegroundColor Cyan
$cockpitScript = "C:\Users\raest\Documents\Karma_SADE\Scripts\karma_cockpit_service.py"

try {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "python"
    $psi.Arguments = "`"$cockpitScript`""
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden

    $proc = [System.Diagnostics.Process]::Start($psi)
    Write-Host "  Cockpit started (PID $($proc.Id))" -ForegroundColor Green

    # Wait for startup
    Write-Host "  Waiting for Cockpit to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5

    # Verify health
    try {
        $health = Invoke-WebRequest -Uri "http://localhost:9400/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        Write-Host "  Cockpit healthy!" -ForegroundColor Green
    }
    catch {
        Write-Host "  Warning: Cockpit started but not responding yet" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "  Error starting Cockpit: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3/3] Opening dashboard in browser..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
Start-Process "http://localhost:9400/dashboard"
Write-Host "  Browser launched" -ForegroundColor Green

Write-Host ""
Write-Host "Dashboard URL: http://localhost:9400/dashboard" -ForegroundColor Cyan
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
Write-Host ""
