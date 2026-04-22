# TEST: final-gate exits non-zero when EVIDENCE_INDEX entry has artifacts but no sha256
# RED_WHY: Phase 4 implements sha256 validation
$ErrorActionPreference = 'Stop'
$fx = Join-Path $env:TEMP "asc-fx-missha-$(Get-Random)"
New-Item -ItemType Directory -Path $fx -Force | Out-Null
try {
  '[{"gate_id":"G1","artifacts":["/tmp/foo.png"],"sha256":{},"status":"VERIFIED"}]' | Out-File -LiteralPath (Join-Path $fx 'EVIDENCE_INDEX.json') -Encoding utf8NoBOM
  '{"SESSION_ID":"fx"}' | Out-File -LiteralPath (Join-Path $fx 'session.json') -Encoding utf8NoBOM
  & (Join-Path $PSScriptRoot '..\..\Scripts\ascendance-final-gate.ps1') -RunDir $fx 2>&1 | Out-Null
  if ($LASTEXITCODE -eq 0) { throw "should reject missing sha256 but exited 0" }
  Write-Host "PASS_PROVISIONAL exit=$LASTEXITCODE"; exit 0
} catch { Write-Host "FAIL: $_"; exit 1 } finally { Remove-Item -Recurse -Force $fx -ErrorAction SilentlyContinue }
