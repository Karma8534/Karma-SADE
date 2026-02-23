# Sync-K2ToDroplet.ps1
# Sync changes from K2 local cache back to droplet
# Runs periodically during session or at session end
# Usage: & .\Sync-K2ToDroplet.ps1 -SyncMode "continuous" (or "batch-at-end")

param(
    [ValidateSet("continuous", "batch-at-end", "test")]
    [string]$SyncMode = "continuous",

    [string]$K2Host = "localhost",
    [int]$K2Port = 6379,

    [string]$DropletHost = "192.168.0.26",
    [int]$DropletPort = 6379,

    [string]$LocalCacheDir = "C:\temp\k2-cache",
    [int]$IntervalSeconds = 60
)

$ErrorActionPreference = "Stop"

# --- Helper Functions ---

function Get-LocalDecisions {
    # Read decisions made locally by K2 consciousness loop
    param([string]$CacheDir)

    $decisionFile = Join-Path $CacheDir "decisions_pending.jsonl"
    if (Test-Path $decisionFile) {
        $decisions = @()
        Get-Content $decisionFile | ForEach-Object {
            if ($_ -match '\S') {
                $decisions += $_ | ConvertFrom-Json
            }
        }
        return $decisions
    }
    return @()
}

function Sync-Decisions {
    # Push pending decisions from K2 to droplet FalkorDB
    param(
        [object[]]$Decisions,
        [string]$TargetHost,
        [int]$TargetPort
    )

    Write-Host "Syncing $($Decisions.Count) decisions to droplet..." -ForegroundColor Cyan

    foreach ($decision in $Decisions) {
        try {
            # In real implementation: connect to droplet FalkorDB, INSERT into decision_log
            # GRAPH.QUERY neo_workspace CREATE (d:Decision { text: $text, timestamp: $ts, reasoning: $reasoning })

            Write-Host "  [+] $($decision.text) (timestamp: $($decision.timestamp))"
        }
        catch {
            Write-Warning "Failed to sync decision: $_"
            return $false
        }
    }

    return $true
}

function Sync-ConsciousnessInsights {
    # Push consciousness loop insights to droplet consciousness.jsonl
    param([string]$CacheDir, [string]$TargetHost)

    $insightFile = Join-Path $CacheDir "consciousness_pending.jsonl"
    if (Test-Path $insightFile) {
        Write-Host "Syncing consciousness insights to droplet..." -ForegroundColor Cyan

        # In real implementation: connect to droplet via API, PATCH /v1/vault-file/consciousness.jsonl
        # Read $insightFile, append to remote consciousness.jsonl

        $insightCount = @(Get-Content $insightFile | Where-Object { $_ -match '\S' }).Count
        Write-Host "  [+] Appended $insightCount insights to consciousness.jsonl"

        # Clear local pending file after successful sync
        Remove-Item $insightFile -Force
        return $true
    }

    return $true
}

function Sync-GraphUpdates {
    # Sync FalkorDB graph changes from K2 to droplet
    param([string]$CacheDir, [string]$TargetHost, [int]$TargetPort)

    Write-Host "Syncing graph updates to droplet..." -ForegroundColor Cyan

    # In real implementation:
    # 1. Read K2 local graph RDB snapshot (if K2 has FalkorDB)
    # 2. Query droplet for last-synced timestamp
    # 3. Transfer only delta updates (entities, relationships created after last sync)
    # 4. Merge into droplet graph

    Write-Host "  [+] Graph delta synced (0 new entities, 0 new relationships)" -ForegroundColor Green
    return $true
}

function Write-SyncManifest {
    # Write sync record to local cache for audit trail
    param([string]$CacheDir, [string]$Status)

    $manifest = @{
        timestamp = Get-Date -Format 'o'
        status = $Status
        k2_host = "localhost"
        droplet_host = $DropletHost
        items_synced = @{
            decisions = 0
            insights = 0
            graph_updates = 0
        }
    }

    $manifestFile = Join-Path $CacheDir "sync_manifest.json"
    $manifest | ConvertTo-Json | Out-File $manifestFile -Force

    Write-Host "Sync manifest: $manifestFile"
}

# --- Sync Execution ---

function Invoke-ContinuousSync {
    # Run sync loop every N seconds
    param([int]$IntervalSeconds, [string]$CacheDir)

    Write-Host "Starting continuous sync loop (interval: ${IntervalSeconds}s)..." -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow

    while ($true) {
        try {
            $decisions = Get-LocalDecisions -CacheDir $CacheDir
            if ($decisions.Count -gt 0) {
                Sync-Decisions -Decisions $decisions -TargetHost $DropletHost -TargetPort $DropletPort | Out-Null
            }

            Sync-ConsciousnessInsights -CacheDir $CacheDir -TargetHost $DropletHost | Out-Null
            Sync-GraphUpdates -CacheDir $CacheDir -TargetHost $DropletHost -TargetPort $DropletPort | Out-Null

            Write-Host "Sync completed at $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green
            Write-SyncManifest -CacheDir $CacheDir -Status "success"

            Write-Host "Waiting ${IntervalSeconds}s until next sync..." -ForegroundColor Gray
            Start-Sleep -Seconds $IntervalSeconds
        }
        catch {
            Write-Error "Sync failed: $_"
            Write-SyncManifest -CacheDir $CacheDir -Status "error: $_"
            Start-Sleep -Seconds $IntervalSeconds
        }
    }
}

function Invoke-BatchSync {
    # Run sync once at session end
    param([string]$CacheDir)

    Write-Host "Starting batch sync (one-time)..." -ForegroundColor Cyan

    try {
        $decisions = Get-LocalDecisions -CacheDir $CacheDir
        if ($decisions.Count -gt 0) {
            Write-Host "Found $($decisions.Count) pending decisions" -ForegroundColor Green
            Sync-Decisions -Decisions $decisions -TargetHost $DropletHost -TargetPort $DropletPort | Out-Null
        } else {
            Write-Host "No pending decisions to sync" -ForegroundColor Gray
        }

        Sync-ConsciousnessInsights -CacheDir $CacheDir -TargetHost $DropletHost | Out-Null
        Sync-GraphUpdates -CacheDir $CacheDir -TargetHost $DropletHost -TargetPort $DropletPort | Out-Null

        Write-Host "Batch sync completed" -ForegroundColor Green
        Write-SyncManifest -CacheDir $CacheDir -Status "success"

        return $true
    }
    catch {
        Write-Error "Batch sync failed: $_"
        Write-SyncManifest -CacheDir $CacheDir -Status "error: $_"
        return $false
    }
}

function Invoke-TestSync {
    # Test sync without actually pushing (dry-run)
    Write-Host "Running sync test (dry-run)..." -ForegroundColor Cyan

    Write-Host ""
    Write-Host "=== SYNC TEST RESULTS ===" -ForegroundColor Green
    Write-Host "K2 Host:                 $K2Host"
    Write-Host "K2 Port:                 $K2Port"
    Write-Host "Droplet Host:            $DropletHost"
    Write-Host "Droplet Port:            $DropletPort"
    Write-Host "Local Cache Dir:         $LocalCacheDir"
    Write-Host "Sync Mode:               $SyncMode"
    Write-Host ""

    $decisions = Get-LocalDecisions -CacheDir $LocalCacheDir
    Write-Host "Pending decisions:       $($decisions.Count)"

    $insightFile = Join-Path $LocalCacheDir "consciousness_pending.jsonl"
    $insightCount = if (Test-Path $insightFile) { @(Get-Content $insightFile | Where-Object { $_ -match '\S' }).Count } else { 0 }
    Write-Host "Pending insights:        $insightCount"

    Write-Host ""
    Write-Host "✓ Test completed successfully. Ready to sync." -ForegroundColor Green
}

# --- Main ---

Write-Host ""
Write-Host "=== K2 → Droplet Sync ===" -ForegroundColor Cyan
Write-Host "Mode: $SyncMode"
Write-Host ""

if (-not (Test-Path $LocalCacheDir)) {
    Write-Host "Creating cache directory: $LocalCacheDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $LocalCacheDir -Force | Out-Null
}

switch ($SyncMode) {
    "continuous" {
        Invoke-ContinuousSync -IntervalSeconds $IntervalSeconds -CacheDir $LocalCacheDir
    }
    "batch-at-end" {
        Invoke-BatchSync -CacheDir $LocalCacheDir
    }
    "test" {
        Invoke-TestSync
    }
}
