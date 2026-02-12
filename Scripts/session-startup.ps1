# Karma SADE Session Startup
# Run at the start of each new conversation
# Usage: karma (or newchat)

param([switch]$SkipDroplet)

$scriptsDir = "C:\Users\raest\Documents\Karma_SADE\Scripts"

Write-Host "Karma SADE - Session Sync" -ForegroundColor Cyan

# 1. Run memory sync (extract facts, update prompt, sync to Vault)
Write-Host "`n[1/2] Memory sync..." -ForegroundColor Yellow
& python.exe "$scriptsDir\karma_memory_sync.py"

# 2. Sync docs to droplet (unless skipped)
if (-not $SkipDroplet) {
    Write-Host "`n[2/2] Droplet sync..." -ForegroundColor Yellow
    & python.exe "$scriptsDir\sync_docs_to_droplet.py"
} else {
    Write-Host "`n[2/2] Droplet sync skipped" -ForegroundColor DarkYellow
}

Write-Host "`n[OK] Session ready" -ForegroundColor Green
