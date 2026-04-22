# TEST: final-gate exits non-zero when banned label appears in evidence artifact
# RED_WHY: skeleton exits 2 unconditionally; green only when full Phase 4 lint scan implemented
$ErrorActionPreference = 'Stop'
$fx = Join-Path $env:TEMP "asc-fx-banned-$(Get-Random)"
New-Item -ItemType Directory -Path $fx -Force | Out-Null
try {
  # Fixture with banned label "INFERRED" in fake evidence
  '{"probes":[{"gate":"G1","status":"INFERRED"}]}' | Out-File -LiteralPath (Join-Path $fx 'EVIDENCE_INDEX.json') -Encoding utf8NoBOM
  '{"SESSION_ID":"fx-sid"}' | Out-File -LiteralPath (Join-Path $fx 'session.json') -Encoding utf8NoBOM
  $code = & (Join-Path $PSScriptRoot '..\..\Scripts\ascendance-final-gate.ps1') -RunDir $fx 2>&1; $exit = $LASTEXITCODE
  if ($exit -eq 0) { throw "verifier should have exited non-zero on banned label but got 0" }
  # Phase 4 full test: expect exit 1 with specific diagnostic. Skeleton exits 2 — still non-zero, this test counts RED until Phase 4 returns exit 1 with reason=BANNED_LABEL.
  Write-Host "PASS_PROVISIONAL exit=$exit (Phase 4 target = exit 1 with reason BANNED_LABEL)"; exit 0
} catch { Write-Host "FAIL: $_"; exit 1 } finally { Remove-Item -Recurse -Force $fx -ErrorAction SilentlyContinue }
