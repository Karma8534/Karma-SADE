# TEST: pre-commit hook requires MEMORY.md staged with SESSION_ID for ascendance-run commits
# RED_WHY: Phase 4 adds MEMORY.md schema validation
$ErrorActionPreference = 'Stop'
try {
  $hook = 'C:\Users\raest\Documents\Karma_SADE\.git\hooks\pre-commit'
  if (-not (Test-Path $hook)) { throw 'pre-commit hook missing' }
  $content = Get-Content $hook -Raw
  if ($content -notmatch 'MEMORY\.md') { throw 'hook does not reference MEMORY.md' }
  if ($content -notmatch 'Ascendance Run|SESSION_ID') { throw 'hook does not enforce Ascendance Run section schema yet (Phase 4)' }
  Write-Host 'PASS'; exit 0
} catch { Write-Host "FAIL: $_"; exit 1 }
