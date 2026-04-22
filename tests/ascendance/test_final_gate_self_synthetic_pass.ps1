# TEST: final-gate exit 0 against fully-valid synthetic PASS fixture
# RED_WHY: Phase 4 implements full happy-path; skeleton exits 2
$ErrorActionPreference = 'Stop'
$fx = Join-Path $env:TEMP "asc-fx-pass-$(Get-Random)"
New-Item -ItemType Directory -Path $fx -Force | Out-Null
try {
  # Stub fixture for now — Phase 4 will expand
  '{}' | Out-File -LiteralPath (Join-Path $fx 'session.json') -Encoding utf8NoBOM
  '[]' | Out-File -LiteralPath (Join-Path $fx 'EVIDENCE_INDEX.json') -Encoding utf8NoBOM
  & (Join-Path $PSScriptRoot '..\..\Scripts\ascendance-final-gate.ps1') -RunDir $fx 2>&1 | Out-Null
  if ($LASTEXITCODE -eq 0) { Write-Host 'PASS_PHASE4_READY'; exit 0 }
  Write-Host "RED_EXPECTED exit=$LASTEXITCODE (Phase 4 target: exit 0)"; exit 1
} catch { Write-Host "FAIL: $_"; exit 1 } finally { Remove-Item -Recurse -Force $fx -ErrorAction SilentlyContinue }
