# TEST: pre-commit hook rejects staged paths outside Ascendance commit whitelist
# RED_WHY: Phase 4 adds scope-whitelist logic to .git/hooks/pre-commit
$ErrorActionPreference = 'Stop'
try {
  $hook = 'C:\Users\raest\Documents\Karma_SADE\.git\hooks\pre-commit'
  if (-not (Test-Path $hook)) { throw 'pre-commit hook missing' }
  $content = Get-Content $hook -Raw
  if ($content -notmatch 'evidence/ascendance-run-|WHITELIST|scope-whitelist') {
    throw 'pre-commit hook does not enforce Ascendance scope whitelist yet (Phase 4)'
  }
  Write-Host 'PASS'; exit 0
} catch { Write-Host "FAIL: $_"; exit 1 }
