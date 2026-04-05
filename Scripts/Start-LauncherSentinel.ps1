$WorkDir = "C:\Users\raest\Documents\Karma_SADE"
$LogDir = "$WorkDir\Logs"
$LogFile = "$LogDir\launcher-sentinel.log"
$AuditScript = "$WorkDir\Scripts\Audit-PersistentLaunchers.ps1"
$RepairScript = "$WorkDir\Scripts\Repair-PersistentLaunchers.ps1"
$IntervalSeconds = 120
$MutexName = "Global\KarmaLauncherSentinel"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

$mutex = New-Object System.Threading.Mutex($false, $MutexName)
$hasHandle = $false
try {
    $hasHandle = $mutex.WaitOne(0, $false)
} catch [System.Threading.AbandonedMutexException] {
    $hasHandle = $true
}

if (-not $hasHandle) {
    exit 0
}

function Write-Log {
    param([string]$Message)
    $ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    Add-Content -Path $LogFile -Value "[$ts] $Message" -Encoding UTF8
}

try {
    while ($true) {
        $auditOutput = & $AuditScript 2>&1
        $auditCode = $LASTEXITCODE
        if ($auditCode -ne 0) {
            Write-Log ("audit_fail " + (($auditOutput | ForEach-Object { $_.ToString().Trim() } | Where-Object { $_ }) -join " | "))
            $repairOutput = & $RepairScript 2>&1
            Write-Log ("repair_run " + (($repairOutput | ForEach-Object { $_.ToString().Trim() } | Where-Object { $_ }) -join " | "))
        } else {
            Write-Log "audit_ok"
        }
        Start-Sleep -Seconds $IntervalSeconds
    }
}
finally {
    if ($hasHandle) {
        $mutex.ReleaseMutex() | Out-Null
    }
    $mutex.Dispose()
}
