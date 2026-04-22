# TEST: final-gate flags stale verified_utc (>600s old for non-binary-fixed gates)
# RED_WHY: Phase 4 implements verified_utc freshness check
$ErrorActionPreference = 'Stop'
$fx = Join-Path $env:TEMP "asc-fx-stale-$(Get-Random)"
New-Item -ItemType Directory -Path $fx -Force | Out-Null
try {
  $oldTs = (Get-Date).AddHours(-2).ToUniversalTime().ToString('o')
  "[{`"gate_id`":`"G1`",`"status`":`"VERIFIED`",`"verified_utc`":`"$oldTs`",`"artifacts`":[],`"sha256`":{}}]" | Out-File -LiteralPath (Join-Path $fx 'EVIDENCE_INDEX.json') -Encoding utf8NoBOM
  '{"SESSION_ID":"fx","session_start_utc":"'+(Get-Date).ToUniversalTime().ToString('o')+'"}' | Out-File -LiteralPath (Join-Path $fx 'session.json') -Encoding utf8NoBOM
  & (Join-Path $PSScriptRoot '..\..\Scripts\ascendance-final-gate.ps1') -RunDir $fx 2>&1 | Out-Null
  if ($LASTEXITCODE -eq 0) { throw "should reject stale verified_utc but exited 0" }
  Write-Host "PASS_PROVISIONAL exit=$LASTEXITCODE"; exit 0
} catch { Write-Host "FAIL: $_"; exit 1 } finally { Remove-Item -Recurse -Force $fx -ErrorAction SilentlyContinue }
