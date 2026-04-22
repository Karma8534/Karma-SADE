param(
  [string]$RunDir,
  [string]$GitRemote = 'origin'
)

$ErrorActionPreference = 'Stop'
$repoRoot = 'C:\Users\raest\Documents\Karma_SADE'
$evidenceRoot = Join-Path $repoRoot 'evidence'
$trackerStatePath = Join-Path $repoRoot '.claude\hooks\.arknexus-tracker-state.json'
$memoryPath = Join-Path $repoRoot 'MEMORY.md'

function Resolve-LatestRunDir {
  param([string]$Root)
  $dirs = Get-ChildItem -LiteralPath $Root -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like 'ascendance-run-*' } |
    Sort-Object LastWriteTime -Descending
  if (-not $dirs -or $dirs.Count -eq 0) { return $null }
  return $dirs[0].FullName
}

function Load-JsonFile {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) { return $null }
  try {
    $raw = Get-Content -LiteralPath $Path -Raw
    if ($null -eq $raw) { return $null }
    $trim = $raw.Trim()
    if ($trim -eq '[]') { return @() }
    if ($trim -eq '{}') { return @{} }
    return ($raw | ConvertFrom-Json)
  } catch { return $null }
}

function Get-ShaMatch {
  param([string]$Path, [string]$Expected)
  try {
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    return ($actual -eq [string]$Expected).ToString().ToLowerInvariant()
  } catch { return $false }
}

function Get-TextSessionHit {
  param([string]$Path, [string]$SessionId)
  try {
    $ext = [IO.Path]::GetExtension($Path).ToLowerInvariant()
    if ($ext -in @('.json', '.txt', '.md', '.log', '.ps1', '.ts', '.tsx', '.js', '.jsx', '.yml', '.yaml', '.csv')) {
      $raw = Get-Content -LiteralPath $Path -Raw -ErrorAction Stop
      return ($raw -match [regex]::Escape($SessionId))
    }
  } catch {}
  return $false
}

function Get-AscendanceMemorySection {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) { return '' }
  $raw = Get-Content -LiteralPath $Path -Raw
  $m = [regex]::Matches($raw, '(?ms)^##\s+Ascendance Run.*?(?=^##\s+|\z)')
  if ($m.Count -eq 0) { return '' }
  return [string]$m[$m.Count - 1].Value
}

if (-not $RunDir) {
  $RunDir = Resolve-LatestRunDir -Root $evidenceRoot
}
if (-not $RunDir -or -not (Test-Path -LiteralPath $RunDir)) {
  Write-Host 'FINAL_GATE:'
  Write-Host '- verifier_exit_code:          1'
  Write-Host '- error:                       run_dir_missing'
  exit 1
}

$sessionPath = Join-Path $RunDir 'session.json'
$indexPath = Join-Path $RunDir 'EVIDENCE_INDEX.json'
$manifestPath = Join-Path $RunDir 'artifact_manifest.json'
$gapPath = Join-Path $RunDir 'GAP_MATRIX.md'
$probePath = Join-Path $RunDir 'PROBE_LOG.md'

$session = Load-JsonFile -Path $sessionPath
$index = Load-JsonFile -Path $indexPath
$manifest = Load-JsonFile -Path $manifestPath
if ($null -eq $session -or $null -eq $index) {
  Write-Host 'FINAL_GATE:'
  Write-Host '- verifier_exit_code:          1'
  Write-Host '- error:                       session_or_index_missing_or_invalid'
  exit 1
}

$sessionId = [string]$session.session_id
if (-not $sessionId) { $sessionId = [string]$session.SESSION_ID }
$now = (Get-Date).ToUniversalTime()

$expectedGateIds = @(
  'G1_BOOT_DOM_ATTR','G2_COLD_BOOT_RERUN','G3_PARITY_BROWSER_SCREEN','G4_PARITY_STRESS',
  'G5_WHOAMI_REAL_UI','G6_RITUAL_STEP4_FRESH_BROWSER','G7_RITUAL_STEP10_FIRST_PAINT',
  'G8_RITUAL_UNINTERRUPTED_RECORDING','G9_DUAL_WRITE_DISCIPLINE','G10_GIT_AND_MEMORY',
  'G11_QUARANTINE_CLEANUP','G12_VAULT_PARITY','G13_FOCUS_GATE_UNLOCK','G14_TRACKER_SCHEMA_ALIGNMENT'
)

$latest = @{}
foreach ($row in @($index)) {
  $gid = [string]$row.gate_id
  if (-not $gid) { continue }
  if (-not $latest.ContainsKey($gid)) {
    $latest[$gid] = $row
    continue
  }
  $prevAttempt = [int]$latest[$gid].attempt_n
  $newAttempt = [int]$row.attempt_n
  if ($newAttempt -ge $prevAttempt) { $latest[$gid] = $row }
}

$all14 = $true
$anyFail = $false
$anyBlocked = $false
$artifactComplete = $true
$sessionIdInArtifacts = $true
$dualWrites = $true

foreach ($gid in $expectedGateIds) {
  if (-not $latest.ContainsKey($gid)) {
    $all14 = $false
    $anyBlocked = $true
    continue
  }
  $row = $latest[$gid]
  $status = [string]$row.status
  if ($status -ne 'VERIFIED') { $all14 = $false }
  if ($status -eq 'FAIL') { $anyFail = $true }
  if ($status -eq 'BLOCKED') { $anyBlocked = $true }

  if (-not $row.obs_roundtrip_confirmed -or -not $row.bus_roundtrip_confirmed) {
    $dualWrites = $false
  }

  foreach ($ap in @($row.artifacts)) {
    $p = [string]$ap
    if (-not $p -or -not (Test-Path -LiteralPath $p)) {
      $artifactComplete = $false
      continue
    }
    $expected = $null
    if ($row.sha256 -and $row.sha256.PSObject.Properties.Name -contains $p) {
      $expected = [string]$row.sha256.$p
    }
    if (-not $expected) {
      $artifactComplete = $false
      continue
    }
    if (-not (Get-ShaMatch -Path $p -Expected $expected)) {
      $artifactComplete = $false
    }

    $isTextHit = Get-TextSessionHit -Path $p -SessionId $sessionId
    if (-not $isTextHit) {
      $manifestHit = $false
      foreach ($m in @($manifest)) {
        if ([string]$m.path -eq $p -and [string]$m.session_id -eq $sessionId -and [string]$m.sha256 -eq $expected) {
          $manifestHit = $true
          break
        }
      }
      if (-not $manifestHit) { $sessionIdInArtifacts = $false }
    }
  }
}

$memorySection = Get-AscendanceMemorySection -Path $memoryPath
$bannedRegex = '(?i)\b(inferred|likely|should|probably|close enough|done-ish|implied|assumed|effectively|essentially|in practice|approximately|basically|mostly|seems|appears to|close to|near enough)\b'
$bannedHits = 0
foreach ($sf in @($indexPath, $gapPath, $probePath)) {
  if (-not (Test-Path -LiteralPath $sf)) { continue }
  try {
    $raw = Get-Content -LiteralPath $sf -Raw
    $bannedHits += [regex]::Matches($raw, $bannedRegex).Count
  } catch {}
}
if ($memorySection) {
  $bannedHits += [regex]::Matches($memorySection, $bannedRegex).Count
}

$harnessShaUnchanged = $true
$settingsShaUnchanged = $true
$snapshotMap = @{}
$sNode = $session.snapshots
if ($sNode -and $sNode -is [System.Collections.IDictionary]) {
  foreach ($k in $sNode.Keys) { $snapshotMap[[string]$k] = [string]$sNode[$k] }
} else {
  foreach ($s in @($sNode)) {
    if ($s.path -and $s.sha256) { $snapshotMap[[string]$s.path] = [string]$s.sha256 }
  }
}
foreach ($k in $snapshotMap.Keys) {
  $p = $k
  if (-not [IO.Path]::IsPathRooted($p)) { $p = Join-Path $repoRoot $p }
  if (-not (Test-Path -LiteralPath $p)) {
    if ($p -like '*settings.local.json') { $settingsShaUnchanged = $false } else { $harnessShaUnchanged = $false }
    continue
  }
  $ok = Get-ShaMatch -Path $p -Expected $snapshotMap[$k]
  if (-not $ok) {
    if ($p -like '*settings.local.json') { $settingsShaUnchanged = $false } else { $harnessShaUnchanged = $false }
  }
}

$memorySchemaValid = $false
if ($memorySection -and $memorySection -match [regex]::Escape($sessionId) -and $memorySection -match 'commit_sha:') {
  $memorySchemaValid = $true
}

$ritualRecordingValid = $false
$mp4 = Join-Path $RunDir 'ascendance-ritual.mp4'
$ritualSubDir = Join-Path $RunDir 'ritual'
if (Test-Path -LiteralPath $mp4) {
  $ritualRecordingValid = $true
} elseif (Test-Path -LiteralPath $ritualSubDir) {
  $allSteps = $true
  for ($i = 1; $i -le 12; $i++) {
    if (-not (Test-Path -LiteralPath (Join-Path $ritualSubDir ('step-{0:D2}.png' -f $i)))) { $allSteps = $false; break }
  }
  $ritualRecordingValid = $allSteps
}

$gitClean = ((git -C $repoRoot status --porcelain) -join '') -eq ''
$localHead = (git -C $repoRoot rev-parse HEAD).Trim()
$remoteHead = ''
$remotesToTry = @($GitRemote, 'origin', 'cxNexusv6') | Select-Object -Unique
foreach ($r in $remotesToTry) {
  if (-not $r) { continue }
  try {
    $line = (git -C $repoRoot ls-remote $r refs/heads/main)
    if ($line) { $remoteHead = ($line -split '\s+')[0].Trim(); break }
  } catch {}
}
$gitPushed = ($localHead -and $remoteHead -and ($localHead -eq $remoteHead))
$gitScopeCleanAndPushed = ($gitClean -and $gitPushed)

$vaultParityVerified = $false
$vaultMarker = Join-Path $RunDir 'vault_parity_verified.json'
if (Test-Path -LiteralPath $vaultMarker) {
  $v = Load-JsonFile -Path $vaultMarker
  if ($v -and $v.verified -eq $true) { $vaultParityVerified = $true }
}

$trackerShipped = $false
$trackerState = Load-JsonFile -Path $trackerStatePath
if ($trackerState) {
  try {
    $lastRunUtc = [datetime]::Parse([string]$trackerState.last_run).ToUniversalTime()
    $recent = (($now - $lastRunUtc).TotalSeconds -le 600)
    if ([string]$trackerState.overall -match 'ASCENDANCE = 100 \(SHIPPED\)' -and $recent) {
      $trackerShipped = $true
    }
  } catch {}
}

$fields = [ordered]@{
  all_14_verified = $all14
  any_fail_remaining = $anyFail
  any_blocked_remaining = $anyBlocked
  banned_label_hits = $bannedHits
  artifacts_complete = $artifactComplete
  session_id_in_all_artifacts = $sessionIdInArtifacts
  dual_writes_confirmed = $dualWrites
  ritual_recording_valid = $ritualRecordingValid
  git_clean_and_pushed = $gitScopeCleanAndPushed
  vault_parity_verified = $vaultParityVerified
  harness_sha_unchanged = $harnessShaUnchanged
  settings_sha_unchanged = $settingsShaUnchanged
  memory_md_schema_valid = $memorySchemaValid
  tracker_shipped_in_session = $trackerShipped
}

$shaInputs = @()
$shaInputs += (Get-FileHash -Algorithm SHA256 -LiteralPath $sessionPath).Hash.ToLowerInvariant()
foreach ($gid in $expectedGateIds) {
  if (-not $latest.ContainsKey($gid)) { continue }
  $row = $latest[$gid]
  foreach ($p in @($row.artifacts)) {
    $path = [string]$p
    if ($row.sha256 -and $row.sha256.PSObject.Properties.Name -contains $path) {
      $shaInputs += [string]$row.sha256.$path
    }
  }
}
$joined = ($shaInputs | Sort-Object) -join ''
$sessionDigest = if ($joined) {
  $bytes = [Text.Encoding]::UTF8.GetBytes($joined)
  $shaObj = [Security.Cryptography.SHA256]::Create()
  ($shaObj.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join ''
} else { '' }

$allTrue = $true
foreach ($k in @('all_14_verified','artifacts_complete','session_id_in_all_artifacts','dual_writes_confirmed','ritual_recording_valid','git_clean_and_pushed','vault_parity_verified','harness_sha_unchanged','settings_sha_unchanged','memory_md_schema_valid','tracker_shipped_in_session')) {
  if (-not $fields[$k]) { $allTrue = $false }
}
if ($fields.any_fail_remaining -or $fields.any_blocked_remaining -or $fields.banned_label_hits -gt 0) {
  $allTrue = $false
}
$exitCode = if ($allTrue) { 0 } else { 1 }

Write-Host 'FINAL_GATE:'
Write-Host ("- all_14_verified:             " + ($fields.all_14_verified.ToString().ToLowerInvariant()))
Write-Host ("- any_fail_remaining:          " + ($fields.any_fail_remaining.ToString().ToLowerInvariant()))
Write-Host ("- any_blocked_remaining:       " + ($fields.any_blocked_remaining.ToString().ToLowerInvariant()))
Write-Host ("- banned_label_hits:           " + $fields.banned_label_hits)
Write-Host ("- artifacts_complete:          " + ($fields.artifacts_complete.ToString().ToLowerInvariant()))
Write-Host ("- session_id_in_all_artifacts: " + ($fields.session_id_in_all_artifacts.ToString().ToLowerInvariant()))
Write-Host ("- dual_writes_confirmed:       " + ($fields.dual_writes_confirmed.ToString().ToLowerInvariant()))
Write-Host ("- ritual_recording_valid:      " + ($fields.ritual_recording_valid.ToString().ToLowerInvariant()))
Write-Host ("- git_clean_and_pushed:        " + ($fields.git_clean_and_pushed.ToString().ToLowerInvariant()))
Write-Host ("- vault_parity_verified:       " + ($fields.vault_parity_verified.ToString().ToLowerInvariant()))
Write-Host ("- harness_sha_unchanged:       " + ($fields.harness_sha_unchanged.ToString().ToLowerInvariant()))
Write-Host ("- settings_sha_unchanged:      " + ($fields.settings_sha_unchanged.ToString().ToLowerInvariant()))
Write-Host ("- memory_md_schema_valid:      " + ($fields.memory_md_schema_valid.ToString().ToLowerInvariant()))
Write-Host ("- tracker_shipped_in_session:  " + ($fields.tracker_shipped_in_session.ToString().ToLowerInvariant()))
Write-Host ("- session_digest:              " + $sessionDigest)
Write-Host ("- verifier_exit_code:          " + $exitCode)

exit $exitCode
