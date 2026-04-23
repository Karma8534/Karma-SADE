param([Parameter(Mandatory = $true)][string]$RunDir)
$ErrorActionPreference = 'Continue'
$absRun = (Resolve-Path -LiteralPath $RunDir).Path
$session = Get-Content -LiteralPath (Join-Path $RunDir 'session.json') -Raw | ConvertFrom-Json
$sid = $session.SESSION_ID
$idx = Get-Content -LiteralPath (Join-Path $RunDir 'EVIDENCE_INDEX.json') -Raw | ConvertFrom-Json
$manPath = Join-Path $RunDir 'artifact_manifest.json'
$man = @(Get-Content -LiteralPath $manPath -Raw | ConvertFrom-Json)
$manPaths = @($man | ForEach-Object { $_.path })
foreach ($row in $idx) {
  foreach ($a in @($row.artifacts)) {
    $ap = [string]$a
    if (-not $ap -or -not (Test-Path -LiteralPath $ap)) { Write-Host "MISSING: $($row.gate_id) -> $ap"; continue }
    $expected = $null
    if ($row.sha256 -and $row.sha256.PSObject.Properties.Name -contains $ap) { $expected = [string]$row.sha256.$ap }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $ap).Hash.ToLowerInvariant()
    if ($expected -ne $actual) { Write-Host "SHA_MISMATCH: $($row.gate_id) -> $ap expected=$($expected.Substring(0,12)) actual=$($actual.Substring(0,12))" }
    $ext = [IO.Path]::GetExtension($ap).ToLowerInvariant()
    if ($ext -in @('.json', '.txt', '.md', '.log', '.ps1', '.ts', '.tsx', '.js', '.jsx', '.yml', '.yaml', '.csv', '.jsonl', '.marker')) {
      $raw = Get-Content -LiteralPath $ap -Raw
      if (-not ($raw -match [regex]::Escape($sid))) {
        if ($manPaths -notcontains $ap) { Write-Host "NO_SID_TEXT: $($row.gate_id) -> $ap" }
      }
    } else {
      if ($manPaths -notcontains $ap) { Write-Host "NO_MANIFEST_BINARY: $($row.gate_id) -> $ap" }
    }
  }
}
