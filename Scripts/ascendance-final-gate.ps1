# ascendance-final-gate.ps1 — Directive v3 §9 FINAL_GATE computation
# HARNESS_GATE: final
# Phase 1 SKELETON — exits 2 (not implemented). Full body lands in Phase 4.
param(
  [string]$RunDir,
  [switch]$Dry
)
$ErrorActionPreference = 'Stop'
$repoRoot = 'C:\Users\raest\Documents\Karma_SADE'
if (-not $RunDir) {
  $evidenceRoot = Join-Path $repoRoot 'evidence'
  $latest = Get-ChildItem -Path $evidenceRoot -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like 'ascendance-run-*' -or $_.Name -like 'ascendance-dry-run-*' } |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if ($latest) { $RunDir = $latest.FullName }
}
if (-not $RunDir -or -not (Test-Path $RunDir)) {
  Write-Host "FINAL_GATE: no run dir found"
  exit 2
}
Write-Host "FINAL_GATE: skeleton only - full implementation Phase 4"
Write-Host "run_dir: $RunDir"
# Phase 4 will: sha256 recompute, banned-label scan (scope evidence/** + MEMORY.md Ascendance section),
# harness_sha unchanged, settings_sha unchanged, G11/G13 re-probe, tracker in-session check,
# emit FINAL_GATE block per directive v3 §9.2, exit 0 only if all-true.
exit 2
