<#
.SYNOPSIS
    Karma SADE — webui.db Backup v1.0.0
.DESCRIPTION
    Creates timestamped backups of the Open WebUI SQLite database.
    Uses SQLite's .backup command for safe hot-copy (no corruption risk
    even if Open WebUI is actively writing).

    Falls back to file copy if sqlite3 CLI is not available, but warns
    that this is less safe while the DB is in use.

    Backup location: ~\karma\backups\
    Retention: Keeps last 7 daily backups + last 4 weekly backups
    Schedule: Run daily via Task Scheduler

    Register:
    schtasks /create /tn "KarmaSADE-BackupDB" /tr "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\Users\raest\Documents\Karma_SADE\Scripts\karma_backup_webui.ps1" /sc daily /st 03:00 /ru "%USERNAME%"

.NOTES
    Worst case: If webui.db is corrupted and no backup exists, you lose
    all Open WebUI config (API keys, model settings, chat history).
    That's why this script exists.
#>

$ErrorActionPreference = "Continue"

# ─── Configuration ────────────────────────────────────────────────────────────
$Config = @{
    SourceDB       = "C:\openwebui\venv\Lib\site-packages\open_webui\data\webui.db"
    BackupDir      = Join-Path $env:USERPROFILE "karma\backups"
    LogDir         = "C:\Users\raest\Documents\Karma_SADE\Logs"
    DailyRetention = 7     # Keep last N daily backups
    WeeklyRetention = 4    # Keep last N weekly backups (Sunday)
}

$LogFile = Join-Path $Config.LogDir "karma-backup.log"

# ─── Logging ──────────────────────────────────────────────────────────────────
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] [backup] [$Level] $Message"
    if (-not (Test-Path $Config.LogDir)) {
        New-Item -ItemType Directory -Path $Config.LogDir -Force | Out-Null
    }
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    Write-Host $line -ForegroundColor $(switch ($Level) {
        "OK"    { "Green" }
        "WARN"  { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    })
}

# ─── Backup ───────────────────────────────────────────────────────────────────
function New-DatabaseBackup {

    # Verify source exists
    if (-not (Test-Path $Config.SourceDB)) {
        Write-Log "Source database not found: $($Config.SourceDB)" "ERROR"
        Write-Log "Open WebUI may not be installed or DB path has changed" "ERROR"
        return $false
    }

    # Create backup directory
    if (-not (Test-Path $Config.BackupDir)) {
        New-Item -ItemType Directory -Path $Config.BackupDir -Force | Out-Null
        Write-Log "Created backup directory: $($Config.BackupDir)"
    }

    # Generate backup filename
    $timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
    $dayOfWeek = (Get-Date).DayOfWeek
    $backupName = "webui_${timestamp}.db"
    $backupPath = Join-Path $Config.BackupDir $backupName

    # Get source file size for verification
    $sourceSize = (Get-Item $Config.SourceDB).Length
    $sourceSizeMB = [math]::Round($sourceSize / 1MB, 2)
    Write-Log "Source DB size: ${sourceSizeMB} MB"

    # Attempt SQLite safe backup first
    $sqlite3 = Get-Command "sqlite3" -ErrorAction SilentlyContinue
    $backupOk = $false

    if ($sqlite3) {
        Write-Log "Using sqlite3 .backup (safe hot-copy)..."
        try {
            $result = & sqlite3 $Config.SourceDB ".backup '$backupPath'" 2>&1
            if ($LASTEXITCODE -eq 0 -and (Test-Path $backupPath)) {
                $backupOk = $true
                Write-Log "SQLite backup created successfully" "OK"
            }
            else {
                Write-Log "sqlite3 backup failed: $result" "WARN"
            }
        }
        catch {
            Write-Log "sqlite3 backup error: $($_.Exception.Message)" "WARN"
        }
    }
    else {
        Write-Log "sqlite3 not found in PATH — using file copy (less safe if DB is in use)" "WARN"
    }

    # Fallback: file copy
    if (-not $backupOk) {
        try {
            Copy-Item -Path $Config.SourceDB -Destination $backupPath -Force
            $backupOk = $true
            Write-Log "File copy backup created (warn: may be inconsistent if DB was being written)" "WARN"
        }
        catch {
            Write-Log "File copy failed: $($_.Exception.Message)" "ERROR"
            return $false
        }
    }

    # Also copy WAL and SHM files if they exist (needed for consistency)
    foreach ($ext in @("-wal", "-shm")) {
        $walFile = $Config.SourceDB + $ext
        if (Test-Path $walFile) {
            $walDest = $backupPath + $ext
            try {
                Copy-Item -Path $walFile -Destination $walDest -Force
                Write-Log "Copied ${ext} file"
            }
            catch {
                Write-Log "Failed to copy ${ext}: $($_.Exception.Message)" "WARN"
            }
        }
    }

    # Verify backup
    $backupSize = (Get-Item $backupPath).Length
    $backupSizeMB = [math]::Round($backupSize / 1MB, 2)

    if ($backupSize -eq 0) {
        Write-Log "Backup file is EMPTY — backup failed" "ERROR"
        Remove-Item $backupPath -Force
        return $false
    }

    # Warn if backup is significantly smaller (possible corruption)
    $ratio = $backupSize / $sourceSize
    if ($ratio -lt 0.5) {
        Write-Log "Backup is ${backupSizeMB} MB but source is ${sourceSizeMB} MB (ratio: $([math]::Round($ratio, 2))) — possible truncation" "WARN"
    }
    else {
        Write-Log "Backup verified: ${backupSizeMB} MB ($backupName)" "OK"
    }

    # Tag weekly backups (for retention logic)
    if ($dayOfWeek -eq "Sunday") {
        $weeklyName = "webui_weekly_${timestamp}.db"
        $weeklyPath = Join-Path $Config.BackupDir $weeklyName
        Copy-Item -Path $backupPath -Destination $weeklyPath -Force
        Write-Log "Weekly backup saved: $weeklyName" "OK"
    }

    return $true
}

# ─── Retention Cleanup ────────────────────────────────────────────────────────
function Remove-OldBackups {

    Write-Log "Running retention cleanup..."

    # Daily backups (non-weekly)
    $dailyBackups = Get-ChildItem -Path $Config.BackupDir -Filter "webui_2*.db" |
        Where-Object { $_.Name -notmatch "weekly" } |
        Sort-Object LastWriteTime -Descending

    if ($dailyBackups.Count -gt $Config.DailyRetention) {
        $toDelete = $dailyBackups | Select-Object -Skip $Config.DailyRetention
        foreach ($file in $toDelete) {
            # Also delete associated WAL/SHM files
            Remove-Item $file.FullName -Force
            foreach ($ext in @("-wal", "-shm")) {
                $assoc = $file.FullName + $ext
                if (Test-Path $assoc) { Remove-Item $assoc -Force }
            }
            Write-Log "Deleted old daily backup: $($file.Name)"
        }
    }

    # Weekly backups
    $weeklyBackups = Get-ChildItem -Path $Config.BackupDir -Filter "webui_weekly_*.db" |
        Sort-Object LastWriteTime -Descending

    if ($weeklyBackups.Count -gt $Config.WeeklyRetention) {
        $toDelete = $weeklyBackups | Select-Object -Skip $Config.WeeklyRetention
        foreach ($file in $toDelete) {
            Remove-Item $file.FullName -Force
            foreach ($ext in @("-wal", "-shm")) {
                $assoc = $file.FullName + $ext
                if (Test-Path $assoc) { Remove-Item $assoc -Force }
            }
            Write-Log "Deleted old weekly backup: $($file.Name)"
        }
    }

    Write-Log "Retention cleanup done"
}

# ─── Main ─────────────────────────────────────────────────────────────────────
Write-Log "=========================================="
Write-Log "Karma SADE — Database Backup"
Write-Log "=========================================="

$success = New-DatabaseBackup

if ($success) {
    Remove-OldBackups
    Write-Log "Backup cycle complete" "OK"
}
else {
    Write-Log "Backup FAILED — see errors above" "ERROR"
}

Write-Log "=========================================="
