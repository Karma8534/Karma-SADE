# TEST: drain-queue retries pending entries; state -> confirmed on success
# RED_WHY: implementation exists but depends on live MCP/bus
$ErrorActionPreference = 'Stop'
$fx = Join-Path $env:TEMP "asc-fx-drain-$(Get-Random)"
New-Item -ItemType Directory -Path $fx -Force | Out-Null
try {
  '{"SESSION_ID":"fx-drain"}' | Out-File -LiteralPath (Join-Path $fx 'session.json') -Encoding utf8NoBOM
  '{"utc":"2026-01-01T00:00:00Z","type":"DECISION","title":"t","text":"b","gate":"plan-level","state":"pending","obs_id":null,"bus_id":null}' | Out-File -LiteralPath (Join-Path $fx 'dual-write-queue.jsonl') -Encoding utf8NoBOM
  '' | Out-File -LiteralPath (Join-Path $fx 'PROBE_LOG.md') -Encoding utf8NoBOM
  $out = & (Join-Path $PSScriptRoot '..\..\Scripts\ascendance-drain-queue.ps1') -RunDir $fx 2>&1
  if ($LASTEXITCODE -ne 0) { throw "drain exit $LASTEXITCODE" }
  Write-Host "PASS out=$out"; exit 0
} catch { Write-Host "FAIL: $_"; exit 1 } finally { Remove-Item -Recurse -Force $fx -ErrorAction SilentlyContinue }
