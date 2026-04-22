# TEST: ascendance-init-run.ps1 creates all required run artifacts
# RED_WHY: green when init produces session.json + EVIDENCE_INDEX.json + GAP_MATRIX.md + PROBE_LOG.md + dual-write-queue.jsonl
$ErrorActionPreference = 'Stop'
$tmp = Join-Path $env:TEMP "asc-test-init-$(Get-Random)"
try {
  & (Join-Path $PSScriptRoot '..\..\Scripts\ascendance-init-run.ps1') -Dry -RunId "test-$(Get-Random)" | Out-Null
  $latest = Get-ChildItem 'C:\Users\raest\Documents\Karma_SADE\evidence' -Directory | Where-Object { $_.Name -like 'ascendance-dry-run-test-*' } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if (-not $latest) { throw 'run dir not created' }
  foreach ($f in @('session.json','EVIDENCE_INDEX.json','GAP_MATRIX.md','PROBE_LOG.md','dual-write-queue.jsonl')) {
    if (-not (Test-Path (Join-Path $latest.FullName $f))) { throw "missing $f" }
  }
  Remove-Item -Recurse -Force $latest.FullName
  Write-Host 'PASS'; exit 0
} catch { Write-Host "FAIL: $_"; exit 1 }
