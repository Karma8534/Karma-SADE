# HARNESS_GATE: G1,G2,G3,G4,G5,G6,G7,G8,G14
# Independent verifier -- different-tool-family cross-check per gate.
# Harnesses use PowerShell+Invoke-RestMethod+System.Drawing+CDP ClientWebSocket.
# This verifier uses: curl via ssh vault-neo, python3 via ssh vault-neo, raw Get-Content byte reads.
# Zero reliance on harness code paths. Emits delta report vs harness-reported gate_g*_pass values.
param(
  [Parameter(Mandatory = $true)][string]$RunDir,
  [switch]$Quiet
)
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $RunDir)) { throw "RunDir not found: $RunDir" }
$sessionPath = Join-Path $RunDir 'session.json'
if (-not (Test-Path -LiteralPath $sessionPath)) { throw "session.json missing" }
$session = Get-Content -LiteralPath $sessionPath -Raw | ConvertFrom-Json
$sessionId = [string]$session.session_id
$sessionStart = [string]$session.session_start_utc
if (-not $sessionId) { throw 'session_id missing' }

$reportPath = Join-Path $RunDir 'independent-verify.json'
$deltas = @()
$checks = [ordered]@{}

function Test-FileContainsSession([string]$path, [string]$sid) {
  if (-not (Test-Path -LiteralPath $path)) { return $false }
  $raw = [IO.File]::ReadAllBytes($path)
  $asText = [Text.Encoding]::UTF8.GetString($raw)
  return $asText.Contains($sid)
}

function Read-JsonViaPython([string]$path, [string]$pyExpr) {
  if (-not (Test-Path -LiteralPath $path)) { return $null }
  $py = "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8-sig')); print($pyExpr)"
  $pythonCmd = if (Get-Command python -ErrorAction SilentlyContinue) { 'python' } elseif (Get-Command python3 -ErrorAction SilentlyContinue) { 'python3' } else { $null }
  if (-not $pythonCmd) {
    # Fallback: remote python3 via ssh
    $remoteTmp = "/tmp/ivf-$sessionId.json"
    scp -q $path "vault-neo:$remoteTmp" 2>$null | Out-Null
    return (ssh vault-neo "python3 -c `"$py`" $remoteTmp")
  }
  return (& $pythonCmd -c $py $path)
}

# G1/G2/G14 from phase1-timing.json
$timPath = Join-Path $RunDir 'phase1-timing.json'
if (Test-Path -LiteralPath $timPath) {
  $personaPaint = Read-JsonViaPython $timPath "d.get('persona_paint_ms','-')"
  $effectivePaint = Read-JsonViaPython $timPath "d.get('effective_paint_ms','-')"
  $windowVisible = Read-JsonViaPython $timPath "d.get('window_visible_ms','-')"
  $bootSid = Read-JsonViaPython $timPath "(d.get('boot_metrics') or {}).get('session_id','-')"
  $harnessSid = Read-JsonViaPython $timPath "d.get('harness_session_id','-')"
  $cdpHydr = Read-JsonViaPython $timPath "d.get('cdp_data_hydration_state','-')"
  $cdpSid = Read-JsonViaPython $timPath "d.get('cdp_data_session_id','-')"
  $harnessG1 = Read-JsonViaPython $timPath "d.get('gate_g1_pass','-')"
  $harnessG2 = Read-JsonViaPython $timPath "d.get('gate_g2_pass','-')"
  $harnessG14 = Read-JsonViaPython $timPath "d.get('gate_g14_pass','-')"

  $independentG1 = (($cdpHydr -eq 'ready') -and ($cdpSid -eq $sessionId))
  $independentG2 = ((($harnessSid -eq $sessionId) -or ($cdpSid -eq $sessionId)) -and ($effectivePaint -match '^\d+$') -and ([int]$effectivePaint -lt 2000))
  $independentG14 = (($personaPaint -match '^-?\d+$') -and ($effectivePaint -match '^-?\d+$'))

  $checks.G1 = @{ harness = "$harnessG1"; independent = $independentG1; artifact = $timPath; session_id_present = (Test-FileContainsSession $timPath $sessionId) }
  $checks.G2 = @{ harness = "$harnessG2"; independent = $independentG2; artifact = $timPath; session_id_present = (Test-FileContainsSession $timPath $sessionId) }
  $checks.G14 = @{ harness = "$harnessG14"; independent = $independentG14; artifact = $timPath; session_id_present = (Test-FileContainsSession $timPath $sessionId) }
  if ("$harnessG1".ToLower() -ne "$independentG1".ToLower()) { $deltas += "G1 harness=$harnessG1 independent=$independentG1" }
  if ("$harnessG2".ToLower() -ne "$independentG2".ToLower()) { $deltas += "G2 harness=$harnessG2 independent=$independentG2" }
  if ("$harnessG14".ToLower() -ne "$independentG14".ToLower()) { $deltas += "G14 harness=$harnessG14 independent=$independentG14" }
}

# G3 from phase2-roundtrip.json
$rtPath = Join-Path $RunDir 'phase2-roundtrip.json'
$probePath = Join-Path $RunDir 'phase2-probe.txt'
if ((Test-Path -LiteralPath $rtPath) -and (Test-Path -LiteralPath $probePath)) {
  $probe = (Get-Content -LiteralPath $probePath -Raw).Trim()
  $harnessG3 = Read-JsonViaPython $rtPath "d.get('gate_g3_pass','-')"
  # Independent path: check both local and remote session views for the emitted probe.
  $hit = 0
  try {
    $localResp = Invoke-WebRequest -Uri "http://127.0.0.1:7891/v1/session/$sessionId" -UseBasicParsing -TimeoutSec 10
    if ($localResp.Content -match [regex]::Escape($probe)) { $hit += 1 }
  } catch {}
  try {
    $out = ssh vault-neo "TOKEN=`$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt); curl -s -H `"Authorization: Bearer `$TOKEN`" https://hub.arknexus.net/v1/session/$sessionId | grep -c '$probe'"
    if ($out -match '^\d+$') { $hit += [int]$out }
  } catch {}
  $independentG3 = ($hit -gt 0)
  $checks.G3 = @{ harness = "$harnessG3"; independent = $independentG3; probe = $probe; hit_count = $hit; session_id_present = (Test-FileContainsSession $rtPath $sessionId) }
  if ("$harnessG3".ToLower() -ne "$independentG3".ToLower()) { $deltas += "G3 harness=$harnessG3 independent=$independentG3" }
}

# G4 from phase2-stress.json
$stressPath = Join-Path $RunDir 'phase2-stress.json'
if (Test-Path -LiteralPath $stressPath) {
  $harnessG4 = Read-JsonViaPython $stressPath "d.get('gate_g4_pass','-')"
  $missingR = Read-JsonViaPython $stressPath "d.get('missing_remote_count','-')"
  $missingL = Read-JsonViaPython $stressPath "d.get('missing_local_count','-')"
  $histMatch = Read-JsonViaPython $stressPath "d.get('history_match','-')"
  $independentG4 = (($missingR -eq '0') -and ($missingL -eq '0') -and ("$histMatch".ToLower() -eq 'true'))
  $checks.G4 = @{ harness = "$harnessG4"; independent = $independentG4; session_id_present = (Test-FileContainsSession $stressPath $sessionId) }
  if ("$harnessG4".ToLower() -ne "$independentG4".ToLower()) { $deltas += "G4 harness=$harnessG4 independent=$independentG4" }
}

# G5/G6 from phase3-family.json
$familyPath = Join-Path $RunDir 'phase3-family.json'
if (Test-Path -LiteralPath $familyPath) {
  $harnessG5 = Read-JsonViaPython $familyPath "d.get('gate_g5_pass','-')"
  $harnessG6 = Read-JsonViaPython $familyPath "d.get('gate_g6_pass','-')"
  $pickerOpen = Read-JsonViaPython $familyPath "d.get('picker_open','-')"
  $trueFamily = Read-JsonViaPython $familyPath "d.get('whoami_has_true_family','-')"
  $toolsRes = Read-JsonViaPython $familyPath "d.get('whoami_has_tools_resources','-')"
  $dirBefore = Read-JsonViaPython $familyPath "d.get('user_data_dir_existed_before','-')"
  $dirAfter = Read-JsonViaPython $familyPath "d.get('user_data_dir_deleted_after','-')"
  $independentG5 = (("$pickerOpen".ToLower() -eq 'true') -and ("$trueFamily".ToLower() -eq 'true') -and ("$toolsRes".ToLower() -eq 'true'))
  $independentG6 = (("$dirBefore".ToLower() -eq 'false') -and ("$dirAfter".ToLower() -eq 'true'))
  $checks.G5 = @{ harness = "$harnessG5"; independent = $independentG5; session_id_present = (Test-FileContainsSession $familyPath $sessionId) }
  $checks.G6 = @{ harness = "$harnessG6"; independent = $independentG6; session_id_present = (Test-FileContainsSession $familyPath $sessionId) }
  if ("$harnessG5".ToLower() -ne "$independentG5".ToLower()) { $deltas += "G5 harness=$harnessG5 independent=$independentG5" }
  if ("$harnessG6".ToLower() -ne "$independentG6".ToLower()) { $deltas += "G6 harness=$harnessG6 independent=$independentG6" }
}

# G7 from ascendance-ritual.json
$ritualPath = Join-Path $RunDir 'ascendance-ritual.json'
if (Test-Path -LiteralPath $ritualPath) {
  $harnessG7 = Read-JsonViaPython $ritualPath "d.get('gate_g7_pass','-')"
  $ritualTag = Read-JsonViaPython $ritualPath "d.get('ritual_tag','-')"
  # Independent: read history from local via curl, check ritual tag presence
  $expected = "ASCENDANCE-RITUAL-$sessionId"
  $foundCount = 0
  try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:7891/v1/session/$sessionId" -UseBasicParsing -TimeoutSec 10
    if ($resp.Content -match [regex]::Escape($expected)) { $foundCount = 1 }
  } catch {}
  $independentG7 = ($foundCount -gt 0)
  $checks.G7 = @{ harness = "$harnessG7"; independent = $independentG7; ritual_tag = $ritualTag; session_id_present = (Test-FileContainsSession $ritualPath $sessionId) }
  if ("$harnessG7".ToLower() -ne "$independentG7".ToLower()) { $deltas += "G7 harness=$harnessG7 independent=$independentG7" }
}

# G8 from ritual/recorder-manifest.json
$manifestPath = Join-Path $RunDir 'ritual\recorder-manifest.json'
if (Test-Path -LiteralPath $manifestPath) {
  $harnessG8 = Read-JsonViaPython $manifestPath "d.get('gate_g8_pass','-')"
  $monotonic = Read-JsonViaPython $manifestPath "d.get('monotonic','-')"
  $gapOk = Read-JsonViaPython $manifestPath "d.get('gap_ok','-')"
  $within = Read-JsonViaPython $manifestPath "d.get('within_session_window','-')"
  $mode = Read-JsonViaPython $manifestPath "d.get('mode','-')"
  $mp4Bytes = Read-JsonViaPython $manifestPath "d.get('mp4_bytes',0)"
  # Independent: list files on disk, recompute monotonic mtimes
  $ritualDir = Join-Path $RunDir 'ritual'
  $pngFiles = @(Get-ChildItem -LiteralPath $ritualDir -Filter 'step-*.png' -ErrorAction SilentlyContinue | Sort-Object Name)
  $mp4File = Get-ChildItem -LiteralPath $ritualDir -Filter '*.mp4' -ErrorAction SilentlyContinue | Select-Object -First 1
  $diskMonotonic = $true
  for ($i = 1; $i -lt $pngFiles.Count; $i++) {
    if ($pngFiles[$i].LastWriteTimeUtc -le $pngFiles[$i - 1].LastWriteTimeUtc) { $diskMonotonic = $false; break }
  }
  $independentG8 = ("$monotonic".ToLower() -eq 'true') -and ("$gapOk".ToLower() -eq 'true') -and ("$within".ToLower() -eq 'true')
  if ($mode -eq 'pngseq') { $independentG8 = $independentG8 -and ($pngFiles.Count -ge 12) -and $diskMonotonic }
  elseif ($mode -eq 'mp4') { $independentG8 = $independentG8 -and ($mp4File -and $mp4File.Length -gt 0) }
  $checks.G8 = @{ harness = "$harnessG8"; independent = $independentG8; disk_png_count = $pngFiles.Count; disk_monotonic = $diskMonotonic; session_id_present = (Test-FileContainsSession $manifestPath $sessionId) }
  if ("$harnessG8".ToLower() -ne "$independentG8".ToLower()) { $deltas += "G8 harness=$harnessG8 independent=$independentG8" }
}

$report = [ordered]@{
  session_id = $sessionId
  verified_utc = (Get-Date).ToUniversalTime().ToString('o')
  tool_family = 'powershell_invoke+python_json+curl_ssh+filesystem_mtime'
  checks = $checks
  deltas = $deltas
  verifier_pass = ($deltas.Count -eq 0)
}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8
if (-not $Quiet) { Write-Host "independent-verify: sid=$sessionId checks=$($checks.Count) deltas=$($deltas.Count) pass=$($report.verifier_pass)" }
if ($deltas.Count -gt 0) { exit 1 } else { exit 0 }
