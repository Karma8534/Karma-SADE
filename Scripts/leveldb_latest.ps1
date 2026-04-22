# leveldb_latest.ps1 - Return LATEST value for given key from Tauri WebView2 LevelDB
# HARNESS_GATE: support (G2 Phase1 cold-boot scraper)
# Tauri app identifier: net.arknexus.v6
# LevelDB dir: %LOCALAPPDATA%\net.arknexus.v6\EBWebView\Default\Local Storage\leveldb\
# Format: key-value sstable. LOG record format:
#   sequence(8) + type(1) + key_len(varint) + key + value_len(varint) + value (simplified)
# Our strategy: regex-scan .log files for UTF-8 key text; return last match's trailing value.
# For small value payloads (strings/JSON) this is sufficient. Fallback: return stored value map.
param(
  [Parameter(Mandatory=$true)][string]$Key,
  [string]$LevelDbDir,
  [string]$AppIdentifier = 'net.arknexus.v6'
)
$ErrorActionPreference = 'Stop'
if (-not $LevelDbDir) {
  $LevelDbDir = Join-Path $env:LOCALAPPDATA "$AppIdentifier\EBWebView\Default\Local Storage\leveldb"
}
if (-not (Test-Path -LiteralPath $LevelDbDir)) {
  Write-Host "ERR: leveldb_dir_missing $LevelDbDir"; exit 2
}

# Enumerate candidate files: *.log (active) + *.ldb (sst)
$files = Get-ChildItem -LiteralPath $LevelDbDir -File | Where-Object { $_.Name -like '*.log' -or $_.Name -like '*.ldb' } | Sort-Object LastWriteTime -Descending
if (-not $files) { Write-Host 'ERR: no_log_files'; exit 2 }

$latestValue = $null
$latestFile  = $null
$keyUtf8     = [Text.UTF8Encoding]::new($false).GetBytes($Key)
$keyPattern  = [regex]::Escape($Key)

foreach ($f in $files) {
  try {
    $bytes = [IO.File]::ReadAllBytes($f.FullName)
    # Leveldb Local Storage uses prefixed keys like `_http://host\x00\x01<key>`; find all occurrences
    $text = [Text.Encoding]::Latin1.GetString($bytes)
    $matches = [regex]::Matches($text, $keyPattern)
    if ($matches.Count -eq 0) { continue }
    $last = $matches[$matches.Count - 1]
    $afterIdx = $last.Index + $last.Length
    # Attempt to recover trailing JSON-like value (starts with `{` or `"`, bounded by non-printable)
    $tail = $text.Substring($afterIdx, [Math]::Min(8192, $text.Length - $afterIdx))
    # Strip leading varint/null bytes
    $valueMatch = [regex]::Match($tail, '(\{.*?\}|"[^"]*"|[^\x00-\x1f]{1,1024})', [Text.RegularExpressions.RegexOptions]::Singleline)
    if ($valueMatch.Success) {
      $latestValue = $valueMatch.Value
      $latestFile  = $f.Name
      break
    }
  } catch { continue }
}

if ($null -eq $latestValue) {
  Write-Host "ERR: key_not_found key=$Key files=$($files.Count)"
  exit 3
}

$result = [ordered]@{ key = $Key; value = $latestValue; source_file = $latestFile; scanned_files = $files.Count }
$result | ConvertTo-Json -Compress
exit 0
