<#
.SYNOPSIS
    Karma SADE Sentinel - Health Monitoring Script
.DESCRIPTION
    Monitors Ollama, Open WebUI, and system resources.
    Logs results to sentinel-runtime.log and sentinel-latest.json
.NOTES
    Run via Task Scheduler every 15 minutes
#>

$ErrorActionPreference = "Continue"

# Configuration
$Config = @{
    OllamaUrl = "http://localhost:11434"
    OpenWebUIUrl = "http://localhost:8080"
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

# Function to check if process is running
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

# 1. Check Ollama process
$ollamaProcess = Test-ProcessRunning -ProcessName "ollama"
$HealthReport.checks["ollama_process"] = $ollamaProcess

# 2. Check Ollama HTTP endpoint
$ollamaHttp = Test-HttpEndpoint -Url $Config.OllamaUrl -ServiceName "Ollama"
$HealthReport.checks["ollama_http"] = $ollamaHttp

# 3. Check Open WebUI process
$openwebuiProcess = Test-ProcessRunning -ProcessName "open-webui"
$HealthReport.checks["openwebui_process"] = $openwebuiProcess

# 4. Check Open WebUI HTTP endpoint
$openwebuiHttp = Test-HttpEndpoint -Url $Config.OpenWebUIUrl -ServiceName "OpenWebUI"
$HealthReport.checks["openwebui_http"] = $openwebuiHttp

# 5. Check disk health
$diskHealth = Get-DiskHealth
$HealthReport.checks["disk_c"] = $diskHealth

# === Determine Overall Status ===
$statuses = @(
    $ollamaProcess.status,
    $ollamaHttp.status,
    $openwebuiProcess.status,
    $openwebuiHttp.status,
    $diskHealth.status
)

if ($statuses -contains "critical" -or $statuses -contains "unhealthy" -or $statuses -contains "not_running") {
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
            "Disk=$($diskHealth.status) ($($diskHealth.used_percent)%)"

Add-Content -Path $logPath -Value $logEntry -Encoding UTF8

# Output for console (useful when running manually)
Write-Host "=== Karma SADE Sentinel Report ===" -ForegroundColor Cyan
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
Write-Host "Checks:"
Write-Host "  Ollama Process: $($ollamaProcess.status)"
Write-Host "  Ollama HTTP: $($ollamaHttp.status)"
Write-Host "  Open WebUI Process: $($openwebuiProcess.status)"
Write-Host "  Open WebUI HTTP: $($openwebuiHttp.status)"
Write-Host "  Disk C: $($diskHealth.status) ($($diskHealth.used_percent)% used, $($diskHealth.free_gb) GB free)"
Write-Host ""
Write-Host "Logs written to: $($Config.LogsPath)"
