<#
.SYNOPSIS
    Karma SADE Sentinel - Daily Summary Generator
.DESCRIPTION
    Aggregates the day's health check logs into a daily summary.
    Run once per day (e.g., at 11:59 PM or on-demand).
.NOTES
    Reads from sentinel-runtime.log, writes to sentinel-daily-summary.log
#>

$ErrorActionPreference = "Continue"

$LogsPath = "C:\Users\raest\Documents\Karma_SADE\Logs"
$RuntimeLog = Join-Path $LogsPath "sentinel-runtime.log"
$DailySummaryLog = Join-Path $LogsPath "sentinel-daily-summary.log"

$Today = Get-Date -Format "yyyy-MM-dd"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Check if runtime log exists
if (-not (Test-Path $RuntimeLog)) {
    Write-Host "No runtime log found at $RuntimeLog" -ForegroundColor Yellow
    exit 0
}

# Read today's entries from runtime log
$todayEntries = Get-Content $RuntimeLog | Where-Object { $_ -match "^\[$Today" }

if ($todayEntries.Count -eq 0) {
    Write-Host "No entries found for $Today" -ForegroundColor Yellow
    exit 0
}

# Count statuses
$healthyCount = ($todayEntries | Where-Object { $_ -match "STATUS=healthy" }).Count
$warningCount = ($todayEntries | Where-Object { $_ -match "STATUS=warning" }).Count
$unhealthyCount = ($todayEntries | Where-Object { $_ -match "STATUS=unhealthy" }).Count
$totalChecks = $todayEntries.Count

# Calculate uptime percentage
$uptimePercent = [math]::Round(($healthyCount / $totalChecks) * 100, 1)

# Find any unhealthy periods
$unhealthyEntries = $todayEntries | Where-Object { $_ -match "STATUS=unhealthy" }

# Build summary
$summary = @"
================================================================================
DAILY SUMMARY: $Today
Generated: $Timestamp
================================================================================

HEALTH CHECK STATISTICS:
  Total Checks:     $totalChecks
  Healthy:          $healthyCount
  Warning:          $warningCount
  Unhealthy:        $unhealthyCount
  Uptime:           $uptimePercent%

"@

if ($unhealthyEntries.Count -gt 0) {
    $summary += "UNHEALTHY PERIODS:`n"
    foreach ($entry in $unhealthyEntries) {
        $summary += "  $entry`n"
    }
    $summary += "`n"
}

# Get first and last check times
$firstEntry = $todayEntries | Select-Object -First 1
$lastEntry = $todayEntries | Select-Object -Last 1

if ($firstEntry -match '\[([^\]]+)\]') {
    $summary += "First Check: $($Matches[1])`n"
}
if ($lastEntry -match '\[([^\]]+)\]') {
    $summary += "Last Check:  $($Matches[1])`n"
}

$summary += "================================================================================`n"

# Append to daily summary log
Add-Content -Path $DailySummaryLog -Value $summary -Encoding UTF8

# Output to console
Write-Host $summary -ForegroundColor Cyan
Write-Host "Summary appended to: $DailySummaryLog" -ForegroundColor Green
