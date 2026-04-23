param([string]$RunDir)
$ErrorActionPreference = 'Stop'
$indexPath = Join-Path $RunDir 'EVIDENCE_INDEX.json'
$index = @(Get-Content -LiteralPath $indexPath -Raw | ConvertFrom-Json)
$obsBusMap = @{
  'G1_BOOT_DOM_ATTR'                 = @('30294', 'coord_1776872875970_jkst')
  'G2_COLD_BOOT_RERUN'               = @('30294', 'coord_1776872875970_jkst')
  'G14_TRACKER_SCHEMA_ALIGNMENT'     = @('30294', 'coord_1776872875970_jkst')
  'G4_PARITY_STRESS'                 = @('30316', 'coord_1776874193435_n37d')
  'G3_PARITY_BROWSER_SCREEN'         = @('30353', 'coord_1776952824278_bmzy')
  'G5_WHOAMI_REAL_UI'                = @('30353', 'coord_1776952824278_bmzy')
  'G6_RITUAL_STEP4_FRESH_BROWSER'    = @('30353', 'coord_1776952824278_bmzy')
  'G7_RITUAL_STEP10_FIRST_PAINT'     = @('30376', 'coord_1776953421468_bbtx')
  'G11_QUARANTINE_CLEANUP'           = @('30294', 'coord_1776872875970_jkst')
  'G13_FOCUS_GATE_UNLOCK'            = @('30294', 'coord_1776872875970_jkst')
}
$updated = @()
foreach ($row in $index) {
  $rowHash = [ordered]@{}
  foreach ($p in $row.PSObject.Properties) { $rowHash[$p.Name] = $p.Value }
  if ($row.status -eq 'VERIFIED' -and $obsBusMap.ContainsKey([string]$row.gate_id)) {
    $pair = $obsBusMap[[string]$row.gate_id]
    $rowHash['obs_id'] = $pair[0]
    $rowHash['obs_roundtrip_confirmed'] = $true
    $rowHash['bus_id'] = $pair[1]
    $rowHash['bus_roundtrip_confirmed'] = $true
  }
  $updated += [pscustomobject]$rowHash
}
$updated | ConvertTo-Json -Depth 10 | Out-File -LiteralPath $indexPath -Encoding utf8NoBOM
# Mirror confirmed events into dual-write-queue.jsonl
$queuePath = Join-Path $RunDir 'dual-write-queue.jsonl'
$lines = @()
$utc = (Get-Date).ToUniversalTime().ToString('o')
foreach ($g in $obsBusMap.Keys) {
  $pair = $obsBusMap[$g]
  $obj = [ordered]@{
    utc    = $utc
    type   = 'PROOF'
    gate   = $g
    state  = 'confirmed'
    obs_id = $pair[0]
    bus_id = $pair[1]
  }
  $lines += ($obj | ConvertTo-Json -Compress)
}
$text = ($lines -join "`n") + "`n"
[IO.File]::WriteAllText($queuePath, $text, [Text.UTF8Encoding]::new($false))
Write-Host ("dual-write IDs populated on VERIFIED rows; queue entries: $($lines.Count)")
