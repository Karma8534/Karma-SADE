# TEST: leveldb format canary — Tauri profile path reachable + .log file readable
# RED_WHY: harness sanity check for Tauri LevelDB assumptions
$ErrorActionPreference = 'Stop'
try {
  $root = 'C:\Users\raest\AppData\Local\net.arknexus.julian\EBWebView\Default\Local Storage\leveldb'
  if (-not (Test-Path $root)) { throw "leveldb root absent: $root — Julian may need to run at least once" }
  $latest = Get-ChildItem $root -Filter '*.log' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if (-not $latest) { throw 'no .log files in leveldb dir' }
  if ($latest.Length -lt 100) { throw "leveldb log too small: $($latest.Length) bytes" }
  Write-Host "PASS latest=$($latest.Name) size=$($latest.Length)"; exit 0
} catch { Write-Host "FAIL: $_"; exit 1 }
