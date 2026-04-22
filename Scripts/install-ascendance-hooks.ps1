# Install ascendance hooks -- plan v2 Phase 4.3. Idempotent.
param(
  [switch]$Uninstall
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$srcHook = Join-Path $PSScriptRoot 'ascendance-pre-commit.sh'
$dstHook = Join-Path $repoRoot '.git\hooks\pre-commit'
$backupHook = Join-Path $repoRoot '.git\hooks\pre-commit.pre-ascendance.bak'

if ($Uninstall) {
  if (Test-Path -LiteralPath $backupHook) {
    Copy-Item -LiteralPath $backupHook -Destination $dstHook -Force
    Remove-Item -LiteralPath $backupHook -Force
    Write-Host "uninstall: restored pre-ascendance pre-commit hook"
  } else {
    Write-Host "uninstall: no backup found; nothing to restore"
  }
  exit 0
}

if (-not (Test-Path -LiteralPath $srcHook)) { throw "source hook missing: $srcHook" }

if ((Test-Path -LiteralPath $dstHook) -and -not (Test-Path -LiteralPath $backupHook)) {
  $existingRaw = Get-Content -LiteralPath $dstHook -Raw
  if ($existingRaw -notmatch 'Ascendance pre-commit hook') {
    Copy-Item -LiteralPath $dstHook -Destination $backupHook -Force
    Write-Host "backup: saved existing pre-commit to $backupHook"
  }
}

Copy-Item -LiteralPath $srcHook -Destination $dstHook -Force

try { git -C $repoRoot update-index --chmod=+x .git/hooks/pre-commit 2>$null } catch {}

$installedSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $dstHook).Hash
$srcSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $srcHook).Hash
$match = ($installedSha -eq $srcSha)
Write-Host ("installed pre-commit sha256={0} matches_src={1}" -f $installedSha.Substring(0, 12), $match)
if (-not $match) { throw "pre-commit install sha mismatch" }
