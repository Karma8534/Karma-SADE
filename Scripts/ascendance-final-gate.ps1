# HARNESS_GATE: verifier
# Ascendance final gate verifier -- plan v2 Phase 4.1 + directive v3 Section 9.2.
# Reads session.json, EVIDENCE_INDEX.json, GAP_MATRIX.md, PROBE_LOG.md, dual-write-queue.jsonl.
# Recomputes sha256; enforces SESSION_ID-in-artifact; banned-label scan (evidence/** + MEMORY.md Ascendance section);
# asserts harness_sha + settings_sha unchanged vs plan.session.json.snapshots;
# re-probes binary-fixed gates (G11 quarantine, G13 focus) live;
# directive_sha256 recheck vs canonical; queue drain check.
# Emits FINAL_GATE block. Exit 0 iff every field true.
param(
  [string]$RunDir,
  [string]$PlanRunId,
  [string]$GitRemote = 'origin',
  [switch]$Dry
)
$ErrorActionPreference = 'Stop'
$repoRoot = 'C:\Users\raest\Documents\Karma_SADE'
$evidenceRoot = Join-Path $repoRoot 'evidence'
$trackerStatePath = Join-Path $repoRoot '.claude\hooks\.arknexus-tracker-state.json'
$memoryPath = Join-Path $repoRoot 'MEMORY.md'

function Resolve-LatestRunDir {
  param([string]$Root, [string]$Prefix = 'ascendance-run-')
  $dirs = Get-ChildItem -LiteralPath $Root -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "$Prefix*" } |
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
    return ($actual -eq [string]$Expected.ToLowerInvariant())
  } catch { return $false }
}

function Get-TextSessionHit {
  param([string]$Path, [string]$SessionId)
  try {
    $ext = [IO.Path]::GetExtension($Path).ToLowerInvariant()
    if ($ext -in @('.json', '.txt', '.md', '.log', '.ps1', '.ts', '.tsx', '.js', '.jsx', '.yml', '.yaml', '.csv', '.jsonl', '.marker')) {
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

function Scan-BannedLabels {
  param([string[]]$Texts)
  $bannedRegex = '(?i)\b(inferred|likely|should|probably|close enough|done-ish|implied|assumed|effectively|essentially|in practice|approximately|basically|mostly|seems|appears to|close to|near enough)\b'
  $hits = 0
  foreach ($t in $Texts) {
    if ($t) { $hits += [regex]::Matches($t, $bannedRegex).Count }
  }
  return $hits
}

if (-not $RunDir) {
  $RunDir = Resolve-LatestRunDir -Root $evidenceRoot -Prefix 'ascendance-run-'
  if (-not $RunDir) { $RunDir = Resolve-LatestRunDir -Root $evidenceRoot -Prefix 'plan-run-' }
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
$queuePath = Join-Path $RunDir 'dual-write-queue.jsonl'
$planSessionPath = Join-Path $RunDir 'plan.session.json'

$session = Load-JsonFile -Path $sessionPath
if (-not $session) { $session = Load-JsonFile -Path $planSessionPath }
$index = Load-JsonFile -Path $indexPath
$manifest = Load-JsonFile -Path $manifestPath
if ($null -eq $session) {
  Write-Host 'FINAL_GATE:'
  Write-Host '- verifier_exit_code:          1'
  Write-Host '- error:                       session_missing_or_invalid'
  exit 1
}
if ($null -eq $index) { $index = @() }

$sessionId = [string]$session.session_id
if (-not $sessionId) { $sessionId = [string]$session.SESSION_ID }
$sessionStartUtc = [string]$session.session_start_utc
if (-not $sessionStartUtc) { $sessionStartUtc = [string]$session.started_utc }
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
  if (-not $latest.ContainsKey($gid)) { $latest[$gid] = $row; continue }
  $prevAttempt = [int]$latest[$gid].attempt_n
  $newAttempt = [int]$row.attempt_n
  if ($newAttempt -ge $prevAttempt) { $latest[$gid] = $row }
}

$all14 = $true; $anyFail = $false; $anyBlocked = $false
$artifactComplete = $true; $sessionIdInArtifacts = $true; $dualWrites = $true
foreach ($gid in $expectedGateIds) {
  if (-not $latest.ContainsKey($gid)) { $all14 = $false; $anyBlocked = $true; continue }
  $row = $latest[$gid]
  $status = [string]$row.status
  if ($status -ne 'VERIFIED') { $all14 = $false }
  if ($status -eq 'FAIL') { $anyFail = $true }
  if ($status -eq 'BLOCKED') { $anyBlocked = $true }
  if (-not $row.obs_roundtrip_confirmed -or -not $row.bus_roundtrip_confirmed) { $dualWrites = $false }
  foreach ($ap in @($row.artifacts)) {
    $p = [string]$ap
    if (-not $p -or -not (Test-Path -LiteralPath $p)) { $artifactComplete = $false; continue }
    $expected = $null
    if ($row.sha256 -and $row.sha256.PSObject.Properties.Name -contains $p) { $expected = [string]$row.sha256.$p }
    if (-not $expected) { $artifactComplete = $false; continue }
    if (-not (Get-ShaMatch -Path $p -Expected $expected)) { $artifactComplete = $false }
    $isTextHit = Get-TextSessionHit -Path $p -SessionId $sessionId
    if (-not $isTextHit) {
      $manifestHit = $false
      foreach ($m in @($manifest)) {
        if ([string]$m.path -eq $p -and [string]$m.session_id -eq $sessionId -and [string]$m.sha256 -eq $expected) { $manifestHit = $true; break }
      }
      if (-not $manifestHit) { $sessionIdInArtifacts = $false }
    }
  }
}

$memorySection = Get-AscendanceMemorySection -Path $memoryPath
$bannedTexts = @()
foreach ($sf in @($indexPath, $gapPath, $probePath, $queuePath)) {
  if (Test-Path -LiteralPath $sf) {
    try { $bannedTexts += (Get-Content -LiteralPath $sf -Raw) } catch {}
  }
}
$bannedTexts += $memorySection
$bannedHits = Scan-BannedLabels -Texts $bannedTexts

$harnessShaUnchanged = $true
$settingsShaUnchanged = $true
$snapshotMap = @{}
$sNode = $session.snapshots
if ($sNode) {
  if ($sNode.harness_ps1_sha256) {
    foreach ($prop in $sNode.harness_ps1_sha256.PSObject.Properties) { $snapshotMap[[string]$prop.Name] = [string]$prop.Value }
  }
  if ($sNode.settings_local_sha256) { $snapshotMap['.claude/settings.local.json'] = [string]$sNode.settings_local_sha256 }
  if ($sNode.pre_commit_sha256) { $snapshotMap['.git/hooks/pre-commit'] = [string]$sNode.pre_commit_sha256 }
  if ($sNode.cc_scope_index_sha256) { $snapshotMap['Karma2/cc-scope-index.md'] = [string]$sNode.cc_scope_index_sha256 }
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

$directiveMatch = $true
$directivePath = Join-Path $repoRoot 'docs\ForColby\ascendance-directive-v3.md'
if ($session.directive_sha256 -and (Test-Path -LiteralPath $directivePath)) {
  $directiveMatch = Get-ShaMatch -Path $directivePath -Expected ([string]$session.directive_sha256)
}

$planMatch = $true
$planPath = Join-Path $repoRoot '.gsd\phase-ascendance-build-PLAN.md'
if ($session.plan_sha256_at_snapshot -and (Test-Path -LiteralPath $planPath)) {
  $planMatch = Get-ShaMatch -Path $planPath -Expected ([string]$session.plan_sha256_at_snapshot)
}

$memorySchemaValid = $false
if ($memorySection -and $memorySection -match [regex]::Escape($sessionId) -and $memorySection -match 'commit_sha:') { $memorySchemaValid = $true }

$ritualRecordingValid = $false
$ritualSubDir = Join-Path $RunDir 'ritual'
$mp4File = Get-ChildItem -LiteralPath $ritualSubDir -Filter '*.mp4' -ErrorAction SilentlyContinue | Select-Object -First 1
if ($mp4File -and $mp4File.Length -gt 0) {
  $ritualRecordingValid = $true
} elseif (Test-Path -LiteralPath $ritualSubDir) {
  $allSteps = $true
  for ($i = 1; $i -le 12; $i++) {
    if (-not (Test-Path -LiteralPath (Join-Path $ritualSubDir ('step-{0:D2}.png' -f $i)))) { $allSteps = $false; break }
  }
  $ritualRecordingValid = $allSteps
}

$queueDrained = $true
if (Test-Path -LiteralPath $queuePath) {
  $queueLines = Get-Content -LiteralPath $queuePath -ErrorAction SilentlyContinue
  foreach ($line in @($queueLines)) {
    if (-not $line.Trim()) { continue }
    try {
      $entry = $line | ConvertFrom-Json
      if ([string]$entry.state -ne 'confirmed') { $queueDrained = $false }
    } catch { $queueDrained = $false }
  }
}

$gitClean = ((git -C $repoRoot status --porcelain) -join '') -eq ''
$localHead = (git -C $repoRoot rev-parse HEAD).Trim()
$remoteHead = ''
foreach ($r in @($GitRemote, 'origin') | Select-Object -Unique) {
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
$trackerScriptPath = Join-Path $repoRoot '.claude\hooks\arknexus-tracker.py'
if (Test-Path -LiteralPath $trackerScriptPath) {
  try {
    & python $trackerScriptPath | Out-Null
  } catch {}
}
$trackerState = Load-JsonFile -Path $trackerStatePath
if ($trackerState) {
  try {
    $lastRunUtc = [datetime]::Parse([string]$trackerState.last_run).ToUniversalTime()
    $recent = (($now - $lastRunUtc).TotalSeconds -le 600)
    if ([string]$trackerState.overall -match 'ASCENDANCE = 100 \(SHIPPED\)' -and $recent) { $trackerShipped = $true }
  } catch {}
}

$reshipAllTrue = $false
$reshipPath = Join-Path $RunDir 're-ship-checklist.json'
if (Test-Path -LiteralPath $reshipPath) {
  $rs = Load-JsonFile -Path $reshipPath
  if ($rs -and $rs.checks) {
    $requiredReshipChecks = @(
      'get_routes_200',
      'post_routes_auth_200',
      'static_assets_present',
      'watcher_recent_success_10m',
      'mounted_volume_sha_expected',
      'e2e_chat_prompt_to_text',
      'e2e_memory_write_restart_readback',
      'e2e_slash_command_ui',
      'hostile_red_team_separate_tool_family'
    )
    $reshipAllTrue = $true
    foreach ($rk in $requiredReshipChecks) {
      $rv = $rs.checks.$rk
      if (-not ($rv -eq $true)) { $reshipAllTrue = $false; break }
    }
  }
}

$g11Live = (-not (Test-Path -LiteralPath (Join-Path $repoRoot 'config\permission_rules.json.broken-bak'))) -and `
           (-not (Test-Path -LiteralPath (Join-Path $repoRoot 'evidence\invalidated-synthetic-s174')))
$g13Live = -not (Test-Path -LiteralPath (Join-Path $repoRoot '.claude\hooks\.arknexus-focus-lock.json'))

$probeLogRaw = ''
if (Test-Path -LiteralPath $probePath) { $probeLogRaw = Get-Content -LiteralPath $probePath -Raw }
$probeHasProof = ($probeLogRaw -match '\bPROOF\b')
$probeHasDecision = ($probeLogRaw -match '\bDECISION\b')

$fields = [ordered]@{
  all_14_verified              = $all14
  any_fail_remaining           = $anyFail
  any_blocked_remaining        = $anyBlocked
  banned_label_hits            = $bannedHits
  artifacts_complete           = $artifactComplete
  session_id_in_all_artifacts  = $sessionIdInArtifacts
  dual_writes_confirmed        = $dualWrites
  queue_drained                = $queueDrained
  ritual_recording_valid       = $ritualRecordingValid
  git_clean_and_pushed         = $gitScopeCleanAndPushed
  vault_parity_verified        = $vaultParityVerified
  harness_sha_unchanged        = $harnessShaUnchanged
  settings_sha_unchanged       = $settingsShaUnchanged
  directive_sha256_match       = $directiveMatch
  plan_sha256_match            = $planMatch
  memory_md_schema_valid       = $memorySchemaValid
  tracker_shipped_in_session   = $trackerShipped
  reship_checklist_all_true    = $reshipAllTrue
  g11_live_reprobe             = $g11Live
  g13_live_reprobe             = $g13Live
  probe_log_has_proof          = $probeHasProof
  probe_log_has_decision       = $probeHasDecision
}

$shaInputs = @((Get-FileHash -Algorithm SHA256 -LiteralPath $sessionPath).Hash.ToLowerInvariant())
foreach ($gid in $expectedGateIds) {
  if (-not $latest.ContainsKey($gid)) { continue }
  $row = $latest[$gid]
  foreach ($p in @($row.artifacts)) {
    $path = [string]$p
    if ($row.sha256 -and $row.sha256.PSObject.Properties.Name -contains $path) { $shaInputs += [string]$row.sha256.$path }
  }
}
$joined = ($shaInputs | Sort-Object) -join ''
$sessionDigest = if ($joined) {
  $bytes = [Text.Encoding]::UTF8.GetBytes($joined)
  $shaObj = [Security.Cryptography.SHA256]::Create()
  ($shaObj.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join ''
} else { '' }

$trueRequired = @('all_14_verified','artifacts_complete','session_id_in_all_artifacts','dual_writes_confirmed','queue_drained','ritual_recording_valid','git_clean_and_pushed','vault_parity_verified','harness_sha_unchanged','settings_sha_unchanged','directive_sha256_match','plan_sha256_match','memory_md_schema_valid','tracker_shipped_in_session','reship_checklist_all_true','g11_live_reprobe','g13_live_reprobe','probe_log_has_proof','probe_log_has_decision')
$allTrue = $true
foreach ($k in $trueRequired) { if (-not $fields[$k]) { $allTrue = $false } }
if ($fields.any_fail_remaining -or $fields.any_blocked_remaining -or $fields.banned_label_hits -gt 0) { $allTrue = $false }
$exitCode = if ($allTrue) { 0 } else { 1 }

Write-Host 'FINAL_GATE:'
foreach ($k in $fields.Keys) {
  $v = $fields[$k]
  $vs = if ($v -is [bool]) { $v.ToString().ToLowerInvariant() } else { [string]$v }
  Write-Host ("- {0,-30} {1}" -f ($k + ':'), $vs)
}
Write-Host ("- {0,-30} {1}" -f 'session_digest:', $sessionDigest)
Write-Host ("- {0,-30} {1}" -f 'directive_sha256:', ([string]$session.directive_sha256))
Write-Host ("- {0,-30} {1}" -f 'verifier_exit_code:', $exitCode)
exit $exitCode
