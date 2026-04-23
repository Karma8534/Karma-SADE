param([string]$RunDir, [string]$SessionId)
$ErrorActionPreference = 'Stop'
$qp = Join-Path $RunDir 'dual-write-queue.jsonl'
$lines = Get-Content -LiteralPath $qp
$new = foreach ($l in $lines) {
  if (-not $l.Trim()) { continue }
  $obj = $l | ConvertFrom-Json
  $obj | Add-Member -NotePropertyName session_id -NotePropertyValue $SessionId -Force
  $obj | ConvertTo-Json -Compress
}
$text = ($new -join "`n") + "`n"
[IO.File]::WriteAllText($qp, $text, [Text.UTF8Encoding]::new($false))
$newSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $qp).Hash.ToLowerInvariant()
Write-Host ("queue sha new: " + $newSha.Substring(0, 12))
$idxP = Join-Path $RunDir 'EVIDENCE_INDEX.json'
$obj = Get-Content -LiteralPath $idxP -Raw | ConvertFrom-Json
$queueAbs = (Resolve-Path -LiteralPath $qp).Path
foreach ($e in $obj) {
  if ($e.artifacts -and ($e.artifacts -contains $queueAbs)) {
    $e.sha256.$queueAbs = $newSha
  }
}
$obj | ConvertTo-Json -Depth 10 | Out-File -LiteralPath $idxP -Encoding utf8NoBOM
Write-Host "index sha updated"
