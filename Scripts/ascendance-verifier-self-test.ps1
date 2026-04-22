# Verifier self-test -- plan v2 Phase 4.4.
# Synthetic PASS fixture + 5 synthetic FAIL fixtures (each targeting a distinct verifier check).
# FAIL reasons: banned-label, missing session_id, sha mismatch, missing gate, dual_write unconfirmed.
param(
  [string]$FixtureRoot,
  [switch]$KeepFixtures
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$verifier = Join-Path $PSScriptRoot 'ascendance-final-gate.ps1'
if (-not (Test-Path -LiteralPath $verifier)) { throw "verifier missing: $verifier" }
if (-not $FixtureRoot) { $FixtureRoot = Join-Path $env:TEMP ("ark-verifier-selftest-" + [Guid]::NewGuid().ToString('N')) }
New-Item -ItemType Directory -Force -Path $FixtureRoot | Out-Null

$expectedGateIds = @(
  'G1_BOOT_DOM_ATTR','G2_COLD_BOOT_RERUN','G3_PARITY_BROWSER_SCREEN','G4_PARITY_STRESS',
  'G5_WHOAMI_REAL_UI','G6_RITUAL_STEP4_FRESH_BROWSER','G7_RITUAL_STEP10_FIRST_PAINT',
  'G8_RITUAL_UNINTERRUPTED_RECORDING','G9_DUAL_WRITE_DISCIPLINE','G10_GIT_AND_MEMORY',
  'G11_QUARANTINE_CLEANUP','G12_VAULT_PARITY','G13_FOCUS_GATE_UNLOCK','G14_TRACKER_SCHEMA_ALIGNMENT'
)

function Sha256Of([string]$p) { (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLowerInvariant() }

function New-PassFixture {
  param([string]$Root, [string]$Label)
  $sid = "SELFTEST-$Label-$([Guid]::NewGuid().ToString('N').Substring(0,8))"
  $runDir = Join-Path $Root $Label
  New-Item -ItemType Directory -Force -Path $runDir | Out-Null
  New-Item -ItemType Directory -Force -Path (Join-Path $runDir 'ritual') | Out-Null

  $minimalPng = [byte[]](0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A,0x00,0x00,0x00,0x0D,0x49,0x48,0x44,0x52,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,0x08,0x02,0x00,0x00,0x00,0x90,0x77,0x53,0xDE,0x00,0x00,0x00,0x0C,0x49,0x44,0x41,0x54,0x08,0x99,0x63,0xF8,0xCF,0xC0,0x00,0x00,0x00,0x03,0x00,0x01,0x5B,0xE2,0x9B,0xB2,0x00,0x00,0x00,0x00,0x49,0x45,0x4E,0x44,0xAE,0x42,0x60,0x82)
  for ($i = 1; $i -le 12; $i++) {
    $p = Join-Path $runDir ('ritual\step-{0:D2}.png' -f $i)
    [IO.File]::WriteAllBytes($p, $minimalPng)
    (Get-Item -LiteralPath $p).LastWriteTime = (Get-Date).AddSeconds(-(13 - $i) * 10)
  }

  $indexEntries = @()
  $utc = (Get-Date).ToUniversalTime().ToString('o')
  foreach ($gid in $expectedGateIds) {
    $artPath = Join-Path $runDir ("art-$gid.txt")
    "gate=$gid session_id=$sid utc=$utc" | Set-Content -LiteralPath $artPath -Encoding UTF8
    $sha = Sha256Of $artPath
    $indexEntries += [ordered]@{
      attempt_id = ([Guid]::NewGuid().ToString('N'))
      gate_id = $gid
      attempt_n = 1
      status = 'VERIFIED'
      probe_command = "echo probe-$gid"
      independent_verify_command = "echo verify-$gid"
      predicate = 'synthetic==ok'
      expected = 'ok'
      actual = 'ok'
      artifacts = @($artPath)
      sha256 = @{ $artPath = $sha }
      session_id_present_in_artifact = $true
      verified_utc = $utc
      obs_id = "obs-$gid"
      obs_roundtrip_confirmed = $true
      bus_id = "bus-$gid"
      bus_roundtrip_confirmed = $true
      reason_if_not_pass = $null
    }
  }
  $indexEntries | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $runDir 'EVIDENCE_INDEX.json') -Encoding UTF8

  $gapLines = @('# GAP Matrix (synthetic)','| gate | status | attempt | utc | artifact |','|------|--------|---------|-----|----------|')
  foreach ($gid in $expectedGateIds) { $gapLines += "| $gid | VERIFIED | 1 | $utc | art-$gid.txt |" }
  $gapLines | Set-Content -LiteralPath (Join-Path $runDir 'GAP_MATRIX.md') -Encoding UTF8

  @(
    "$utc | DIRECTION | selftest | obs=obs-dir | bus=bus-dir | synthetic direction",
    "$utc | DECISION | selftest | obs=obs-dec | bus=bus-dec | synthetic decision",
    "$utc | PROOF | selftest | obs=obs-proof | bus=bus-proof | synthetic proof"
  ) | Set-Content -LiteralPath (Join-Path $runDir 'PROBE_LOG.md') -Encoding UTF8

  $queueText = '{"utc":"' + $utc + '","type":"PROOF","state":"confirmed","obs_id":"obs-proof","bus_id":"bus-proof"}' + "`n" + '{"utc":"' + $utc + '","type":"DECISION","state":"confirmed","obs_id":"obs-dec","bus_id":"bus-dec"}' + "`n"
  [IO.File]::WriteAllText((Join-Path $runDir 'dual-write-queue.jsonl'), $queueText, [Text.UTF8Encoding]::new($false))

  [ordered]@{
    session_id = $sid
    session_start_utc = $utc
    started_utc = $utc
    directive_sha256 = ''
    plan_sha256_at_snapshot = ''
    snapshots = @{ harness_ps1_sha256 = @{}; settings_local_sha256 = ''; pre_commit_sha256 = ''; cc_scope_index_sha256 = '' }
  } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $runDir 'session.json') -Encoding UTF8

  return @{ runDir = $runDir; sid = $sid }
}

function Invoke-Verifier([string]$RunDir) {
  $out = & powershell -NoProfile -ExecutionPolicy Bypass -File $verifier -RunDir $RunDir 2>&1
  $exit = $LASTEXITCODE
  return @{ Output = ($out -join "`n"); Exit = $exit }
}

$results = @()

# FAIL-1: banned-label in PROBE_LOG
$f = New-PassFixture -Root $FixtureRoot -Label 'fail1-banned'
$probeFile = Join-Path $f.runDir 'PROBE_LOG.md'
Add-Content -LiteralPath $probeFile -Value "`n$(Get-Date -Format o) | NOTE | synthetic | This is likely OK."
$r = Invoke-Verifier $f.runDir
$ok = ($r.Exit -ne 0) -and ($r.Output -match 'banned_label_hits:\s*[1-9]')
$results += @{ test = 'fail1-banned-label'; ok = $ok; exit = $r.Exit }

# FAIL-2: missing SESSION_ID in artifact
$f = New-PassFixture -Root $FixtureRoot -Label 'fail2-missing-sid'
$someArt = Join-Path $f.runDir 'art-G1_BOOT_DOM_ATTR.txt'
'no session content here' | Set-Content -LiteralPath $someArt -Encoding UTF8
$idx = Get-Content -LiteralPath (Join-Path $f.runDir 'EVIDENCE_INDEX.json') -Raw | ConvertFrom-Json
$newSha = Sha256Of $someArt
foreach ($e in $idx) { if ($e.artifacts -contains $someArt) { $e.sha256 = @{ $someArt = $newSha } } }
$idx | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $f.runDir 'EVIDENCE_INDEX.json') -Encoding UTF8
$r = Invoke-Verifier $f.runDir
$ok = ($r.Exit -ne 0) -and ($r.Output -match 'session_id_in_all_artifacts:\s*false')
$results += @{ test = 'fail2-missing-session-id'; ok = $ok; exit = $r.Exit }

# FAIL-3: sha mismatch
$f = New-PassFixture -Root $FixtureRoot -Label 'fail3-sha-mismatch'
$someArt = Join-Path $f.runDir 'art-G2_COLD_BOOT_RERUN.txt'
"tampered session_id=$($f.sid)" | Set-Content -LiteralPath $someArt -Encoding UTF8
$r = Invoke-Verifier $f.runDir
$ok = ($r.Exit -ne 0) -and ($r.Output -match 'artifacts_complete:\s*false')
$results += @{ test = 'fail3-sha-mismatch'; ok = $ok; exit = $r.Exit }

# FAIL-4: missing gate entry
$f = New-PassFixture -Root $FixtureRoot -Label 'fail4-missing-gate'
$idx = Get-Content -LiteralPath (Join-Path $f.runDir 'EVIDENCE_INDEX.json') -Raw | ConvertFrom-Json
$idx = @($idx | Where-Object { $_.gate_id -ne 'G14_TRACKER_SCHEMA_ALIGNMENT' })
$idx | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $f.runDir 'EVIDENCE_INDEX.json') -Encoding UTF8
$r = Invoke-Verifier $f.runDir
$ok = ($r.Exit -ne 0) -and ($r.Output -match 'all_14_verified:\s*false')
$results += @{ test = 'fail4-missing-gate'; ok = $ok; exit = $r.Exit }

# FAIL-5: dual-write unconfirmed
$f = New-PassFixture -Root $FixtureRoot -Label 'fail5-dualwrite'
$idx = Get-Content -LiteralPath (Join-Path $f.runDir 'EVIDENCE_INDEX.json') -Raw | ConvertFrom-Json
foreach ($e in $idx) { $e.obs_roundtrip_confirmed = $false }
$idx | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $f.runDir 'EVIDENCE_INDEX.json') -Encoding UTF8
$r = Invoke-Verifier $f.runDir
$ok = ($r.Exit -ne 0) -and ($r.Output -match 'dual_writes_confirmed:\s*false')
$results += @{ test = 'fail5-dualwrite'; ok = $ok; exit = $r.Exit }

# PASS-like: logic-testable fields TRUE in synthetic sandbox.
# Env-dependent fields (git_clean_and_pushed, vault_parity_verified, memory_md_schema_valid, tracker_shipped) cannot be true in sandbox -- excluded from self-test scope.
$f = New-PassFixture -Root $FixtureRoot -Label 'passlike'
$r = Invoke-Verifier $f.runDir
$passFields = ($r.Output -match 'all_14_verified:\s*true') -and `
              ($r.Output -match 'artifacts_complete:\s*true') -and `
              ($r.Output -match 'session_id_in_all_artifacts:\s*true') -and `
              ($r.Output -match 'dual_writes_confirmed:\s*true') -and `
              ($r.Output -match 'banned_label_hits:\s*0') -and `
              ($r.Output -match 'queue_drained:\s*true') -and `
              ($r.Output -match 'ritual_recording_valid:\s*true') -and `
              ($r.Output -match 'harness_sha_unchanged:\s*true') -and `
              ($r.Output -match 'settings_sha_unchanged:\s*true') -and `
              ($r.Output -match 'directive_sha256_match:\s*true') -and `
              ($r.Output -match 'plan_sha256_match:\s*true') -and `
              ($r.Output -match 'probe_log_has_proof:\s*true') -and `
              ($r.Output -match 'probe_log_has_decision:\s*true')
$results += @{ test = 'pass-fixture-logic-fields'; ok = $passFields; exit = $r.Exit; note = 'logic-testable fields only; env-dependent (git/vault/memory/tracker) excluded from sandbox scope' }

$summary = [ordered]@{
  fixture_root = $FixtureRoot
  verifier = $verifier
  results = $results
  all_pass = (@($results | Where-Object { -not $_.ok }).Count -eq 0)
}
$summary | ConvertTo-Json -Depth 6 | Write-Output

if (-not $KeepFixtures) {
  try { Remove-Item -LiteralPath $FixtureRoot -Recurse -Force } catch {}
}
if (-not $summary.all_pass) { exit 1 } else { exit 0 }
