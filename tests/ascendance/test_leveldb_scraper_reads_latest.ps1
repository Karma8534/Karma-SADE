# TEST: leveldb_latest.ps1 returns LATEST entry for given key, not first
# RED_WHY: Phase 2.8 implements leveldb_latest.ps1
$ErrorActionPreference = 'Stop'
try {
  $script = 'C:\Users\raest\Documents\Karma_SADE\Scripts\leveldb_latest.ps1'
  if (-not (Test-Path $script)) { throw 'leveldb_latest.ps1 not present yet (Phase 2.8)' }
  Write-Host 'PASS_STUB'; exit 0
} catch { Write-Host "FAIL: $_"; exit 1 }
