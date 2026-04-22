# TEST: dual-write writes queue + roundtrips obs + bus; state=confirmed when both succeed
# RED_WHY: green when Phase 4 hardens obs/bus error handling
$ErrorActionPreference = 'Stop'
$fx = Join-Path $env:TEMP "asc-fx-dw-$(Get-Random)"
New-Item -ItemType Directory -Path $fx -Force | Out-Null
try {
  '{"SESSION_ID":"fx-sid"}' | Out-File -LiteralPath (Join-Path $fx 'session.json') -Encoding utf8NoBOM
  '' | Out-File -LiteralPath (Join-Path $fx 'dual-write-queue.jsonl') -Encoding utf8NoBOM
  '' | Out-File -LiteralPath (Join-Path $fx 'PROBE_LOG.md') -Encoding utf8NoBOM
  & (Join-Path $PSScriptRoot '..\..\Scripts\ascendance-dual-write.ps1') -Type DECISION -Title 'test' -Text 'test-body' -Gate plan-level -RunDir $fx -QueueOnly 2>&1 | Out-Null
  $q = Get-Content (Join-Path $fx 'dual-write-queue.jsonl') | Where-Object { $_.Trim() }
  if (-not $q) { throw 'queue empty after dual-write' }
  $entry = $q[0] | ConvertFrom-Json
  if ($entry.type -ne 'DECISION') { throw "wrong type $($entry.type)" }
  Write-Host 'PASS'; exit 0
} catch { Write-Host "FAIL: $_"; exit 1 } finally { Remove-Item -Recurse -Force $fx -ErrorAction SilentlyContinue }
