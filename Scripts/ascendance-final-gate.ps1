param(
  [string]$RunDir,
  [string]$GitRemote = 'cxNexusv6'
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

function Get-ShaMatch {
  param([string]$Path, [string]$Expected)
  try {
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    return ($actual -eq [string]$Expected).ToLowerInvariant()
  } catch { return $false }
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
$gapPath = Join-Path $RunDir 'GAP_MATRIX.md'
$probePath = Join-Path $RunDir 'PROBE_LOG.md'
$manifestPath = Join-Path $RunDir 'artifact_manifest.json'

$sessionExists = Test-Path -LiteralPath $sessionPath
$indexExists = Test-Path -LiteralPath $indexPath
if (-not $sessionExists -or -not $indexExists) {
  Write-Host 'FINAL_GATE:'
  Write-Host '- verifier_exit_code:          1'
  Write-Host '- error:                       session_or_index_missing_or_invalid'
  exit 1
}

$session = Load-JsonFile -Path $sessionPath
$index = Load-JsonFile -Path $indexPath
$manifest = Load-JsonFile -Path $manifestPath
if ($null -eq $session) {
  Write-Host 'FINAL_GATE:'
  Write-Host '- verifier_exit_code:          1'
  Write-Host '- error:                       session_json_invalid'
  exit 1
}
if ($null -eq $index) { $index = @() }

$sessionId = [string]$session.session_id
$sessionStart = Get-Date ([string]$session.session_start_utc)
$now = (Get-Date).ToUniversalTime()

$expectedGateIds = @(
  'G1_BOOT_DOM_ATTR','G2_COLD_BOOT_RERUN','G3_PARITY_BROWSER_SCREEN','G4_PARITY_STRESS',
  'G5_WHOAMI_REAL_UI','G6_RITUAL_STEP4_FRESH_BROWSER','G7_RITUAL_STEP10_FIRST_PAINT',
  'G8_RITUAL_UNINTERRUPTED_RECORDING','G9_DUAL_WRITE_DISCIPLINE','G10_GIT_AND_MEMORY',
  'G11_QUARANTINE_CLEANUP','G12_VAULT_PARITY','G13_FOCUS_GATE_UNLOCK','G14_TRACKER_SCHEMA_ALIGNMENT'
)

$latest = @{}
foreach ($row in $index) {
  $gid = [string]$row.gate_id
  if (-not $gid) { continue }
  if (-not $latest.ContainsKey($gid)) {
    $latest[$gid] = $row
    continue
  }
  $prev = $latest[$gid]
  $prevAttempt = [int]($prev.attempt_n | ForEach-Object { $_ })
  $newAttempt = [int]($row.attempt_n | ForEach-Object { $_ })
  if ($newAttempt -ge $prevAttempt) {
    $latest[$gid] = $row
  }
}

$all14 = $true
$anyFail = $false
$anyBlocked = $false
$artifactComplete = $true
$sessionIdInArtifacts = $true
$dualWrites = $true
$harnessShaUnchanged = $true
$settingsShaUnchanged = $true
$memorySchemaValid = $false
$trackerShipped = $false
$vaultParityVerified = $false
$ritualRecordingValid = $false
$bannedHits = 0

foreach ($gid in $expectedGateIds) {
  if (-not $latest.ContainsKey($gid)) {
    $all14 = $false
    $anyBlocked = $true
    continue
  }
  $row = $latest[$gid]
  $status = [string]$row.status
  if ($status -ne 'VERIFIED') {
    $all14 = $false
  }
  if ($status -eq 'FAIL') { $anyFail = $true }
  if ($status -eq 'BLOCKED') { $anyBlocked = $true }

  if (-not $row.obs_roundtrip_confirmed -or -not $row.bus_roundtrip_confirmed) {
    $dualWrites = $false
  }

  $artifacts = @($row.artifacts)
  $sha = $row.sha256
  foreach ($a in $artifacts) {
    $ap = [string]$a
    if (-not $ap -or -not (Test-Path -LiteralPath $ap)) {
      $artifactComplete = $false
      continue
    }
    $expected = $null
    if ($sha -and $sha.PSObject.Properties.Name -contains $ap) {
      $expected = [string]$sha.$ap
    }
    if (-not $expected) {
      $artifactComplete = $false
      continue
    }
    if (-not (Get-ShaMatch -Path $ap -Expected $expected)) {
      $artifactComplete = $false
    }
    $isTextHit = Get-TextSessionHit -Path $ap -SessionId $sessionId
    if (-not $isTextHit) {
      $manifestHit = $false
      if ($manifest) {
        foreach ($m in $manifest) {
          if ([string]$m.path -eq $ap -and [string]$m.session_id -eq $sessionId -and [string]$m.sha256 -eq $expected) {
            $manifestHit = $true
            break
          }
        }
      }
      if (-not $manifestHit) { $sessionIdInArtifacts = $false }
    }
  }
}

# Banned label scan in verifier-owned outputs only.
$scanFiles = @($indexPath, $gapPath, $probePath)
if (Test-Path -LiteralPath $memoryPath) { $scanFiles += $memoryPath }
$bannedRegex = '(?i)\b(inferred|likely|should|probably|close enough|done-ish|implied|assumed|effectively|essentially|in practice|approximately|basically|mostly|seems|appears to|close to|near enough)\b'
foreach ($sf in $scanFiles) {
  try {
    $raw = Get-Content -LiteralPath $sf -Raw
    $hits = [regex]::Matches($raw, $bannedRegex).Count
    $bannedHits += $hits
  } catch {}
}

# Snapshot drift checks.
$snapshotMap = @{}
foreach ($s in @($session.snapshots)) {
  if ($s.path -and $s.sha256) { $snapshotMap[[string]$s.path] = [string]$s.sha256 }
}
foreach ($k in $snapshotMap.Keys) {
  if (-not (Test-Path -LiteralPath $k)) {
    if ($k -like '*settings.local.json') { $settingsShaUnchanged = $false } else { $harnessShaUnchanged = $false }
    continue
  }
  $ok = Get-ShaMatch -Path $k -Expected $snapshotMap[$k]
  if (-not $ok) {
    if ($k -like '*settings.local.json') { $settingsShaUnchanged = $false } else { $harnessShaUnchanged = $false }
  }
}

# Memory schema coarse validation.
if (Test-Path -LiteralPath $memoryPath) {
  try {
    $mraw = Get-Content -LiteralPath $memoryPath -Raw
    if ($mraw -match '##\s+Ascendance Run' -and $mraw -match [regex]::Escape($sessionId) -and $mraw -match 'commit_sha:') {
      $memorySchemaValid = $true
    }
  } catch {}
}

# Ritual artifact validity.
$mp4 = Join-Path $RunDir 'ascendance-ritual.mp4'
$ritualSubDir = Join-Path $RunDir 'ritual'
if (Test-Path -LiteralPath $mp4) {
  $ritualRecordingValid = $true
} elseif (Test-Path -LiteralPath $ritualSubDir) {
  $allSteps = $true
  for ($i = 1; $i -le 12; $i++) {
    $fn = ('step-{0:D2}.png' -f $i)
    if (-not (Test-Path -LiteralPath (Join-Path $ritualSubDir $fn))) { $allSteps = $false; break }
  }
  $ritualRecordingValid = $allSteps
}

# Git clean + pushed check.
$gitClean = ((git -C $repoRoot status --porcelain) -join '') -eq ''
$localHead = (git -C $repoRoot rev-parse HEAD).Trim()
$remoteHead = ''
try {
  $remoteLine = (git -C $repoRoot ls-remote $GitRemote refs/heads/main)
  if ($remoteLine) { $remoteHead = ($remoteLine -split '\s+')[0].Trim() }
} catch {}
$gitPushed = ($localHead -and $remoteHead -and ($localHead -eq $remoteHead))
$gitScopeCleanAndPushed = ($gitClean -and $gitPushed)

# Vault parity marker (to be emitted by deployment harness).
$vaultMarker = Join-Path $RunDir 'vault_parity_verified.json'
if (Test-Path -LiteralPath $vaultMarker) {
  $v = Load-JsonFile -Path $vaultMarker
  if ($v -and $v.verified -eq $true) { $vaultParityVerified = $true }
}

# Tracker shipped in-session check.
$trackerState = Load-JsonFile -Path $trackerStatePath
if ($trackerState) {
  try {
    $lastRunUtc = [datetime]::Parse([string]$trackerState.last_run).ToUniversalTime()
    $recent = (($now - $lastRunUtc).TotalSeconds -le 120)
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
  $sha = $row.sha256
  foreach ($p in @($row.artifacts)) {
    $path = [string]$p
    if ($sha -and $sha.PSObject.Properties.Name -contains $path) {
      $shaInputs += [string]$sha.$path
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
