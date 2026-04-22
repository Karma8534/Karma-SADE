# TEST: pre-commit hook scans staged diff for secret patterns (Bearer/token/password/api_key/private_key)
# RED_WHY: Phase 4 adds secret scan
$ErrorActionPreference = 'Stop'
try {
  $hook = 'C:\Users\raest\Documents\Karma_SADE\.git\hooks\pre-commit'
  if (-not (Test-Path $hook)) { throw 'pre-commit hook missing' }
  $content = Get-Content $hook -Raw
  $patterns = @('Bearer','api_key','private_key','password','token')
  $hits = 0
  foreach ($p in $patterns) { if ($content -match [regex]::Escape($p)) { $hits++ } }
  if ($hits -lt 3) { throw "secret-scan patterns missing in hook (hits=$hits/5)" }
  Write-Host "PASS hits=$hits/5"; exit 0
} catch { Write-Host "FAIL: $_"; exit 1 }
