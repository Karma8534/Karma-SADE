# TEST: final-gate exit non-zero against deliberately-invalid fixture
# RED_WHY: Phase 4 implements diagnostic reasons
$ErrorActionPreference = 'Stop'
$fx = Join-Path $env:TEMP "asc-fx-fail-$(Get-Random)"
New-Item -ItemType Directory -Path $fx -Force | Out-Null
try {
  # No session.json at all — verifier must reject
  & (Join-Path $PSScriptRoot '..\..\Scripts\ascendance-final-gate.ps1') -RunDir $fx 2>&1 | Out-Null
  if ($LASTEXITCODE -eq 0) { throw "should reject missing session.json but exited 0" }
  Write-Host "PASS exit=$LASTEXITCODE"; exit 0
} catch { Write-Host "FAIL: $_"; exit 1 } finally { Remove-Item -Recurse -Force $fx -ErrorAction SilentlyContinue }
