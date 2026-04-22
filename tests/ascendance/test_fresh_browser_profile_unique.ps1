# TEST: ritual harness launches Chromium with unique --user-data-dir per SESSION_ID
# RED_WHY: Phase 3.4/3.6 rewrite ritual-harness + family-harness to enforce fresh profile
$ErrorActionPreference = 'Stop'
try {
  $h = 'C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-ritual-harness.ps1'
  if (-not (Test-Path $h)) { throw 'ritual harness missing' }
  $c = Get-Content $h -Raw
  if ($c -notmatch 'user-data-dir|ark-\{SESSION_ID\}|fresh profile') { throw 'ritual harness does not enforce fresh user-data-dir yet (Phase 3)' }
  Write-Host 'PASS'; exit 0
} catch { Write-Host "FAIL: $_"; exit 1 }
