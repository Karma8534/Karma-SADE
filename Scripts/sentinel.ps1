<#
.SYNOPSIS
    Karma SADE Sentinel - Health Monitoring Script v1.1.0
.DESCRIPTION
    Monitors Ollama, Open WebUI, Cockpit, and system resources.
    Logs results to sentinel-runtime.log and sentinel-latest.json

    v1.1.0 changes:
    - Added Cockpit HTTP health check (was a blind spot)
    - Fixed: overall status now based on HTTP checks only (process name
      detection was unreliable and caused phantom "unhealthy" reports)
    - Process checks kept for diagnostic info but don't drive overall status
    - Log line now includes Cockpit status
.NOTES
    Run via Task Scheduler every 15 minutes
#>

$ErrorActionPreference = "Continue"

# Configuration
$Config = @{
    OllamaUrl = "http://localhost:11434"
    OpenWebUIUrl = "http://localhost:8080"
    CockpitUrl = "http://localhost:9400/health"
    DiskWarnThreshold = 80
    DiskCriticalThreshold = 90
    LogsPath = "C:\Users\raest\Documents\Karma_SADE\Logs"
    TimeoutSeconds = 10
}

# Ensure Logs directory exists
if (-not (Test-Path $Config.LogsPath)) {
    New-Item -ItemType Directory -Path $Config.LogsPath -Force | Out-Null
}

$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$DateOnly = Get-Date -Format "yyyy-MM-dd"

# Initialize health report
$HealthReport = @{
    timestamp = $Timestamp
    overall_status = "healthy"
    checks = @{}
    errors = @()
}

# Function to test HTTP endpoint
function Test-HttpEndpoint {
    param(
        [string]$Url,
        [string]$ServiceName
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec $Config.TimeoutSeconds -UseBasicParsing -ErrorAction Stop
        return @{
            status = "healthy"
            http_code = $response.StatusCode
            response_time_ms = $null
        }
    }
    catch {
        return @{
            status = "unhealthy"
            http_code = $null
            error = $_.Exception.Message
        }
    }
}

# Function to check disk usage
function Get-DiskHealth {
    $disk = Get-PSDrive -Name C
    $usedPercent = [math]::Round((($disk.Used) / ($disk.Used + $disk.Free)) * 100, 1)

    $status = "healthy"
    if ($usedPercent -ge $Config.DiskCriticalThreshold) {
        $status = "critical"
    }
    elseif ($usedPercent -ge $Config.DiskWarnThreshold) {
        $status = "warning"
    }

    return @{
        status = $status
        used_percent = $usedPercent
        free_gb = [math]::Round($disk.Free / 1GB, 2)
        used_gb = [math]::Round($disk.Used / 1GB, 2)
    }
}

# Function to check if process is running (diagnostic only, does NOT drive overall status)
function Test-ProcessRunning {
    param([string]$ProcessName)

    $process = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($process) {
        $startTime = $null
        try {
            if ($process.StartTime) {
                $startTime = $process.StartTime.ToString("yyyy-MM-dd HH:mm:ss")
            }
        } catch { }

        return @{
            status = "running"
            pid = $process.Id
            start_time = $startTime
        }
    }
    return @{
        status = "not_running"
        pid = $null
        start_time = $null
    }
}

# === Run Health Checks ===

# 1. Ollama process (diagnostic)
$ollamaProcess = Test-ProcessRunning -ProcessName "ollama"
$HealthReport.checks["ollama_process"] = $ollamaProcess

# 2. Ollama HTTP endpoint (authoritative)
$ollamaHttp = Test-HttpEndpoint -Url $Config.OllamaUrl -ServiceName "Ollama"
$HealthReport.checks["ollama_http"] = $ollamaHttp

# 3. Open WebUI process (diagnostic)
$openwebuiProcess = Test-ProcessRunning -ProcessName "open-webui"
$HealthReport.checks["openwebui_process"] = $openwebuiProcess

# 4. Open WebUI HTTP endpoint (authoritative)
$openwebuiHttp = Test-HttpEndpoint -Url $Config.OpenWebUIUrl -ServiceName "OpenWebUI"
$HealthReport.checks["openwebui_http"] = $openwebuiHttp

# 5. Cockpit HTTP endpoint (authoritative) — NEW in v1.1.0
$cockpitHttp = Test-HttpEndpoint -Url $Config.CockpitUrl -ServiceName "Cockpit"
$HealthReport.checks["cockpit_http"] = $cockpitHttp

# 6. Disk health
$diskHealth = Get-DiskHealth
$HealthReport.checks["disk_c"] = $diskHealth

# === Determine Overall Status ===
# FIX: Only HTTP checks and disk drive overall status.
# Process name detection is unreliable (different executable names, Python wrappers)
# and was causing phantom "unhealthy" when services were actually responding fine.
$statuses = @(
    $ollamaHttp.status,
    $openwebuiHttp.status,
    $cockpitHttp.status,
    $diskHealth.status
)

if ($statuses -contains "critical" -or $statuses -contains "unhealthy") {
    $HealthReport.overall_status = "unhealthy"
}
elseif ($statuses -contains "warning") {
    $HealthReport.overall_status = "warning"
}

# === Write Outputs ===

# Write to sentinel-latest.json (overwrite for easy parsing)
$jsonPath = Join-Path $Config.LogsPath "sentinel-latest.json"
$HealthReport | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonPath -Encoding UTF8

# Append to sentinel-runtime.log
$logPath = Join-Path $Config.LogsPath "sentinel-runtime.log"
$logEntry = "[$Timestamp] STATUS=$($HealthReport.overall_status) | " +
            "Ollama=$($ollamaHttp.status) | " +
            "OpenWebUI=$($openwebuiHttp.status) | " +
            "Cockpit=$($cockpitHttp.status) | " +
            "Disk=$($diskHealth.status) ($($diskHealth.used_percent)%)"

Add-Content -Path $logPath -Value $logEntry -Encoding UTF8

# Output for console (useful when running manually)
Write-Host "=== Karma SADE Sentinel Report v1.1.0 ===" -ForegroundColor Cyan
Write-Host "Timestamp: $Timestamp"
Write-Host "Overall Status: $($HealthReport.overall_status)" -ForegroundColor $(
    switch ($HealthReport.overall_status) {
        "healthy" { "Green" }
        "warning" { "Yellow" }
        "unhealthy" { "Red" }
        default { "White" }
    }
)
Write-Host ""
Write-Host "Service Health (HTTP — authoritative):"
Write-Host "  Ollama:    $($ollamaHttp.status)"
Write-Host "  Open WebUI: $($openwebuiHttp.status)"
Write-Host "  Cockpit:   $($cockpitHttp.status)"
Write-Host ""
Write-Host "Process Info (diagnostic only):"
Write-Host "  Ollama PID:    $($ollamaProcess.pid) ($($ollamaProcess.status))"
Write-Host "  Open WebUI PID: $($openwebuiProcess.pid) ($($openwebuiProcess.status))"
Write-Host ""
Write-Host "Disk C: $($diskHealth.status) ($($diskHealth.used_percent)% used, $($diskHealth.free_gb) GB free)"
Write-Host ""
Write-Host "Logs written to: $($Config.LogsPath)"
