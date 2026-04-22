# ascendance-init-run.ps1 — Create run dir + session.json + skeleton artifacts per directive v3 §10
# HARNESS_GATE: init
param(
  [switch]$Real,
  [switch]$Dry,
  [string]$RunId
)
$ErrorActionPreference = 'Stop'
$repoRoot = 'C:\Users\raest\Documents\Karma_SADE'
$evidenceRoot = Join-Path $repoRoot 'evidence'
$directivePath = Join-Path $repoRoot 'docs\ForColby\ascendance-directive-v3.md'
$planPath      = Join-Path $repoRoot '.gsd\phase-ascendance-build-PLAN.md'
$launcherPath  = Join-Path $repoRoot 'docs\ForColby\ascendance-launcher-v3-hardened.md'
$trackerState  = Join-Path $repoRoot '.claude\hooks\.arknexus-tracker-state.json'
$ritualDir     = Join-Path $evidenceRoot 'ritual'

if (-not (Test-Path $evidenceRoot)) { New-Item -ItemType Directory -Path $evidenceRoot -Force | Out-Null }

$sessionId      = [Guid]::NewGuid().ToString()
$sessionStartUtc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
if (-not $RunId) {
  $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
  $RunId = "$stamp-$($sessionId.Substring(0,8))"
}
$prefix = if ($Real) { 'ascendance-run-' } elseif ($Dry) { 'ascendance-dry-run-' } else { 'ascendance-run-' }
$runDir = Join-Path $evidenceRoot "$prefix$RunId"
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

# G8 precondition: wipe ritual dir
if (Test-Path $ritualDir) {
  Get-ChildItem -Path $ritualDir -Force -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
} else { New-Item -ItemType Directory -Path $ritualDir -Force | Out-Null }

# Tracker state is runtime truth and should never be deleted by init.
# Keep it intact so final-gate/tracker checks remain stable across runs.

$directiveSha = (Get-FileHash -Path $directivePath -Algorithm SHA256).Hash
$planSha      = (Get-FileHash -Path $planPath -Algorithm SHA256).Hash
$launcherSha  = (Get-FileHash -Path $launcherPath -Algorithm SHA256).Hash

$snapshotPaths = @(
  'Scripts\phase1-cold-boot-harness.ps1',
  'Scripts\phase2-parity-harness.ps1',
  'Scripts\phase3-family-harness.ps1',
  'Scripts\ascendance-ritual-harness.ps1',
  'Scripts\ascendance-init-run.ps1',
  'Scripts\ascendance-final-gate.ps1',
  'Scripts\ascendance-dual-write.ps1',
  'Scripts\ascendance-drain-queue.ps1',
  'Scripts\ascendance-preflight.ps1',
  '.claude\settings.local.json',
  '.git\hooks\pre-commit'
)
$snapshots = @{}
foreach ($p in $snapshotPaths) {
  $full = Join-Path $repoRoot $p
  if (Test-Path $full) { $snapshots[$p] = (Get-FileHash $full -Algorithm SHA256).Hash }
}

$sessionJson = @{
  SESSION_ID = $sessionId
  session_start_utc = $sessionStartUtc
  run_id = $RunId
  mode = if ($Real) { 'real' } elseif ($Dry) { 'dry' } else { 'real' }
  directive_path = 'docs/ForColby/ascendance-directive-v3.md'
  directive_sha256 = $directiveSha
  plan_path = '.gsd/phase-ascendance-build-PLAN.md'
  plan_sha256 = $planSha
  launcher_path = 'docs/ForColby/ascendance-launcher-v3-hardened.md'
  launcher_sha256 = $launcherSha
  operator = 'CC (Ascendant)'
  snapshots = $snapshots
}
$sessionJson | ConvertTo-Json -Depth 5 | Out-File -LiteralPath (Join-Path $runDir 'session.json') -Encoding utf8NoBOM

'[]' | Out-File -LiteralPath (Join-Path $runDir 'EVIDENCE_INDEX.json') -Encoding utf8NoBOM
"# GAP_MATRIX - $RunId`n`n| gate_id | status | attempt_n | verified_utc | artifact |`n|---|---|---|---|---|`n" | Out-File -LiteralPath (Join-Path $runDir 'GAP_MATRIX.md') -Encoding utf8NoBOM
"# PROBE_LOG - $RunId`n`nstarted_utc: $sessionStartUtc`nSESSION_ID: $sessionId`n`n## Log`n`n$sessionStartUtc | DIRECTION | init | obs=pending | bus=pending | run initialized | art_sha=none`n" | Out-File -LiteralPath (Join-Path $runDir 'PROBE_LOG.md') -Encoding utf8NoBOM
'' | Out-File -LiteralPath (Join-Path $runDir 'dual-write-queue.jsonl') -Encoding utf8NoBOM

Write-Host "run_dir: $runDir"
Write-Host "SESSION_ID: $sessionId"
Write-Host "run_id: $RunId"
exit 0
