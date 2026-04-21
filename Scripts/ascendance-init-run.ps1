param(
  [switch]$Real,
  [string]$RunId
)

$ErrorActionPreference = 'Stop'

$repoRoot = 'C:\Users\raest\Documents\Karma_SADE'
$evidenceRoot = Join-Path $repoRoot 'evidence'
$planFile = Join-Path $repoRoot 'docs\For Colby\cxArkNexusv4Prop1.md'
$trackerState = Join-Path $repoRoot '.claude\hooks\.arknexus-tracker-state.json'

if (-not (Test-Path -LiteralPath $evidenceRoot)) {
  New-Item -ItemType Directory -Path $evidenceRoot -Force | Out-Null
}

$sessionId = [Guid]::NewGuid().ToString()
$sessionStartUtc = (Get-Date).ToUniversalTime().ToString('o')
if (-not $RunId) {
  $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
  $RunId = "$stamp-$($sessionId.Substring(0,8))"
}

$runDir = Join-Path $evidenceRoot ("ascendance-run-" + $RunId)
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

# Global ritual evidence precondition reset.
$ritualDir = Join-Path $evidenceRoot 'ritual'
if (Test-Path -LiteralPath $ritualDir) {
  Get-ChildItem -LiteralPath $ritualDir -Force -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
} else {
  New-Item -ItemType Directory -Path $ritualDir -Force | Out-Null
}

if (Test-Path -LiteralPath $trackerState) {
  Remove-Item -LiteralPath $trackerState -Force -ErrorAction SilentlyContinue
}

$snapshotGlobs = @(
  'Scripts\phase*-harness.ps1',
  'Scripts\ascendance-*.ps1',
  '.claude\settings.local.json',
  '.git\hooks\pre-commit'
)

$snapshotFiles = @()
foreach ($g in $snapshotGlobs) {
  $matches = Get-ChildItem -Path (Join-Path $repoRoot $g) -File -ErrorAction SilentlyContinue
  foreach ($m in $matches) {
    $snapshotFiles += $m.FullName
  }
}
$snapshotFiles = $snapshotFiles | Sort-Object -Unique

$snapshots = @()
foreach ($f in $snapshotFiles) {
  try {
    $h = (Get-FileHash -Algorithm SHA256 -LiteralPath $f).Hash.ToLowerInvariant()
    $snapshots += [ordered]@{
      path = $f
      sha256 = $h
    }
  } catch {}
}

$planSha = $null
if (Test-Path -LiteralPath $planFile) {
  $planSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $planFile).Hash.ToLowerInvariant()
}

$session = [ordered]@{
  run_id = $RunId
  mode = if ($Real) { 'real' } else { 'dry' }
  session_id = $sessionId
  session_start_utc = $sessionStartUtc
  plan_file = $planFile
  plan_sha256 = $planSha
  snapshots = $snapshots
}

$sessionPath = Join-Path $runDir 'session.json'
$indexPath = Join-Path $runDir 'EVIDENCE_INDEX.json'
$gapPath = Join-Path $runDir 'GAP_MATRIX.md'
$probePath = Join-Path $runDir 'PROBE_LOG.md'
$manifestPath = Join-Path $runDir 'artifact_manifest.json'

$session | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $sessionPath -Encoding UTF8
'[]' | Set-Content -LiteralPath $indexPath -Encoding UTF8
'[]' | Set-Content -LiteralPath $manifestPath -Encoding UTF8

$gates = 1..14 | ForEach-Object { "G$_" }
$gapLines = @(
  '# GAP_MATRIX',
  '',
  '| gate_id | status | attempt_n | verified_utc | artifact |',
  '|---|---|---:|---|---|'
)
foreach ($g in $gates) {
  $gapLines += "| $g | BLOCKED | 0 | - | - |"
}
$gapLines | Set-Content -LiteralPath $gapPath -Encoding UTF8

$probeLines = @(
  '# PROBE_LOG',
  '',
  '| utc | type | gate | obs_id | bus_id | title | hashes |',
  '|---|---|---|---|---|---|---|'
)
$probeLines | Set-Content -LiteralPath $probePath -Encoding UTF8

[ordered]@{
  ok = $true
  run_id = $RunId
  run_dir = $runDir
  session_path = $sessionPath
  evidence_index_path = $indexPath
  gap_matrix_path = $gapPath
  probe_log_path = $probePath
  artifact_manifest_path = $manifestPath
  snapshots = $snapshots.Count
} | ConvertTo-Json -Depth 6
