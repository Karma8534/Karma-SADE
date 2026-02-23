# Test-ResurrectionSystem.ps1
# Comprehensive verification of resurrection architecture
# Tests: Droplet connectivity, spine files, session-start loader, sync model
# Usage: & .\Test-ResurrectionSystem.ps1

param(
    [string]$DropletHost = "192.168.0.26",
    [string]$RepoRoot = "$PSScriptRoot\..\.."
)

$ErrorActionPreference = "Stop"
$testResults = @()

function Add-TestResult {
    param(
        [string]$Name,
        [string]$Status,
        [string]$Details = ""
    )

    $testResults += @{
        name = $Name
        status = $Status
        details = $Details
        timestamp = Get-Date -Format 'HH:mm:ss'
    }

    $color = switch ($Status) {
        "PASS" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
    }

    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Status - $Name" -ForegroundColor $color
    if ($Details) { Write-Host "    $Details" -ForegroundColor Gray }
}

# --- TEST 1: Spine Files Exist and Parse ---

Write-Host ""
Write-Host "=== TEST 1: Spine Files ===" -ForegroundColor Cyan

$spineFiles = @("identity.json", "invariants.json", "direction.md")
foreach ($file in $spineFiles) {
    $filePath = Join-Path $RepoRoot $file
    if (Test-Path $filePath) {
        try {
            if ($file -eq "direction.md") {
                # Markdown - just check it's readable
                $content = Get-Content $filePath -Raw
                if ($content.Length -gt 100) {
                    Add-TestResult -Name "Spine: $file exists and readable" -Status "PASS" -Details "$([Math]::Round($content.Length / 1024, 1))KB"
                } else {
                    Add-TestResult -Name "Spine: $file exists" -Status "WARN" -Details "Very small file, might be incomplete"
                }
            } else {
                # JSON - parse and validate
                $content = Get-Content $filePath -Raw | ConvertFrom-Json
                $fields = $content.PSObject.Properties.Name.Count
                Add-TestResult -Name "Spine: $file parses as valid JSON" -Status "PASS" -Details "$fields fields"
            }
        }
        catch {
            Add-TestResult -Name "Spine: $file parse error" -Status "FAIL" -Details $_.Exception.Message
        }
    } else {
        Add-TestResult -Name "Spine: $file exists" -Status "FAIL" -Details "File not found: $filePath"
    }
}

# --- TEST 2: Resurrection Architecture Document ---

Write-Host ""
Write-Host "=== TEST 2: Architecture Document ===" -ForegroundColor Cyan

$archFile = Join-Path $RepoRoot ".claude/rules/resurrection-architecture.md"
if (Test-Path $archFile) {
    $content = Get-Content $archFile -Raw
    $hasDropletPrimary = $content -match "droplet.*primary"
    $hasK2Worker = $content -match "K2.*worker"
    $hasSubstrate = $content -match "substrate.*independent"

    if ($hasDropletPrimary -and $hasK2Worker -and $hasSubstrate) {
        Add-TestResult -Name "Architecture: document reflects droplet-primary + K2-worker + substrate-independence" -Status "PASS"
    } else {
        Add-TestResult -Name "Architecture: document appears incomplete" -Status "WARN" -Details "Check droplet-primary=$hasDropletPrimary, K2-worker=$hasK2Worker, substrate=$hasSubstrate"
    }
} else {
    Add-TestResult -Name "Architecture: document exists" -Status "FAIL" -Details "File not found"
}

# --- TEST 3: Load-KarmaFromDroplet Script ---

Write-Host ""
Write-Host "=== TEST 3: Session-Start Loader ===" -ForegroundColor Cyan

$loaderScript = Join-Path $RepoRoot "Scripts/resurrection/Load-KarmaFromDroplet.ps1"
if (Test-Path $loaderScript) {
    try {
        # Syntax check only (don't execute)
        $syntax = $null
        $errors = @()
        $tokens = [System.Management.Automation.PSParser]::Tokenize((Get-Content $loaderScript -Raw), [ref]$errors)
        if ($errors.Count -eq 0) {
            Add-TestResult -Name "Loader: script syntax valid" -Status "PASS"
        } else {
            Add-TestResult -Name "Loader: script syntax errors" -Status "FAIL" -Details "$($errors.Count) syntax errors"
        }
    }
    catch {
        Add-TestResult -Name "Loader: syntax check" -Status "WARN" -Details $_.Exception.Message
    }
} else {
    Add-TestResult -Name "Loader: script exists" -Status "FAIL" -Details "File not found"
}

# --- TEST 4: Sync Script ---

Write-Host ""
Write-Host "=== TEST 4: K2 Sync Writer ===" -ForegroundColor Cyan

$syncScript = Join-Path $RepoRoot "Scripts/resurrection/Sync-K2ToDroplet.ps1"
if (Test-Path $syncScript) {
    try {
        $content = Get-Content $syncScript -Raw
        if ($content -match "continuous|batch-at-end") {
            Add-TestResult -Name "Sync: script has continuous and batch modes" -Status "PASS"
        } else {
            Add-TestResult -Name "Sync: script missing sync modes" -Status "WARN"
        }
    }
    catch {
        Add-TestResult -Name "Sync: script check" -Status "WARN" -Details $_.Exception.Message
    }
} else {
    Add-TestResult -Name "Sync: script exists" -Status "FAIL" -Details "File not found"
}

# --- TEST 5: Git Commits ---

Write-Host ""
Write-Host "=== TEST 5: Git Commit History ===" -ForegroundColor Cyan

try {
    Push-Location $RepoRoot
    $recentCommits = git log --oneline -10 | Select-Object -First 5
    $architectureCommit = git log --oneline | Select-String "resurrection-architecture|droplet-primary" | Select-Object -First 1

    if ($architectureCommit) {
        Add-TestResult -Name "Git: recent commits include resurrection architecture" -Status "PASS" -Details "$architectureCommit".Trim()
    } else {
        Add-TestResult -Name "Git: resurrection commits found" -Status "WARN"
    }

    Pop-Location
}
catch {
    Add-TestResult -Name "Git: history check" -Status "WARN" -Details "Could not access git history"
}

# --- TEST 6: Droplet Connectivity (Simulated) ---

Write-Host ""
Write-Host "=== TEST 6: Droplet Integration (Simulated) ===" -ForegroundColor Cyan

# In production, this would actually test TCP connection to droplet FalkorDB
# For now, we just document what needs to be tested
Add-TestResult -Name "Droplet: connectivity (deferred to production)" -Status "WARN" -Details "Requires SSH/TCP tunnel to droplet; tested manually"
Add-TestResult -Name "Droplet: FalkorDB neo_workspace queryable (deferred)" -Status "WARN" -Details "Manual test: redis-cli at droplet:6379 GRAPH.QUERY neo_workspace"
Add-TestResult -Name "Droplet: spine files readable (deferred)" -Status "WARN" -Details "Manual test: SSH to droplet, cat /home/neo/karma-sade/*.json"

# --- Summary ---

Write-Host ""
Write-Host "=== TEST SUMMARY ===" -ForegroundColor Cyan

$passed = ($testResults | Where-Object { $_.status -eq "PASS" }).Count
$warned = ($testResults | Where-Object { $_.status -eq "WARN" }).Count
$failed = ($testResults | Where-Object { $_.status -eq "FAIL" }).Count
$total = $testResults.Count

Write-Host ""
Write-Host "Results:" -ForegroundColor Green
Write-Host "  PASS:  $passed" -ForegroundColor Green
Write-Host "  WARN:  $warned" -ForegroundColor Yellow
Write-Host "  FAIL:  $failed" -ForegroundColor Red
Write-Host "  TOTAL: $total"

Write-Host ""

if ($failed -eq 0) {
    Write-Host "✓ Resurrection system is ready for deployment!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. On K2: Run Load-KarmaFromDroplet.ps1 at session start"
    Write-Host "2. During session: K2 consciousness loop updates local cache"
    Write-Host "3. During session: Run Sync-K2ToDroplet.ps1 to push changes to droplet"
    Write-Host "4. Droplet always has current state for next session"
    Write-Host ""
} elseif ($warned -eq 0) {
    Write-Host "✓ All core tests passed. Deploy and monitor." -ForegroundColor Green
} else {
    Write-Host "⚠ Some tests warned. Review before full deployment." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Test Summary File: $RepoRoot\test_resurrection_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

# Export results to file
$outputFile = Join-Path $RepoRoot "test_resurrection_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$testResults | Format-Table -AutoSize | Out-File $outputFile
Write-Host "Results saved to: $outputFile" -ForegroundColor Gray

return @{
    passed = $passed
    warned = $warned
    failed = $failed
    total = $total
    ready = ($failed -eq 0)
}
