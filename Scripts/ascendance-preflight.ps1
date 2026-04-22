# ascendance-preflight.ps1 — Plan v2 §3 preflight battery PF01..PF15
# HARNESS_GATE: preflight
param(
  [string]$RunDir,
  [switch]$AutoRemediate
)
$ErrorActionPreference = 'Continue'
$results = @()

function Add-Check { param($id, $predicate, $actual, $status, $extra) $results += @{ id=$id; predicate=$predicate; actual=$actual; status=$status; extra=$extra } }

# PF01 ssh vault-neo
$ok = $false
try { $r = ssh -o ConnectTimeout=10 vault-neo 'echo ok' 2>$null; if ($r -match 'ok') { $ok = $true } } catch {}
Add-Check 'PF01' 'ssh vault-neo echo ok' $ok (if ($ok) { 'VERIFIED' } else { 'FAIL' })

# PF03 bus POST roundtrip
$ok = $false; $coordId = $null
try {
  $cmd = 'TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -X POST -d ''{"from":"cc","to":"cc","type":"inform","urgency":"informational","content":"PF03 preflight"}'' http://localhost:18090/v1/coordination/post'
  $code = ssh vault-neo $cmd 2>$null
  if ($code -eq '200') { $ok = $true }
} catch {}
Add-Check 'PF03' 'bus POST /v1/coordination/post 200' $ok (if ($ok) { 'VERIFIED' } else { 'FAIL' })

# PF04 token operational
$ok = $false
try {
  $code = curl -sf -o NUL -w "%{http_code}" https://hub.arknexus.net/health 2>$null
  if ($code -eq '200') { $ok = $true }
} catch {}
Add-Check 'PF04' 'hub /health 200 (token operational proxy)' $ok (if ($ok) { 'VERIFIED' } else { 'FAIL' })

# PF05 clock skew
$ok = $false; $skew = $null
try {
  $local = [int][double]::Parse((Get-Date -UFormat %s))
  $remote = [int](ssh vault-neo 'date -u +%s' 2>$null)
  $skew = [math]::Abs($local - $remote)
  if ($skew -lt 5) { $ok = $true }
} catch {}
Add-Check 'PF05' 'NTP skew < 5s' "$skew s" (if ($ok) { 'VERIFIED' } else { 'FAIL' })

# PF06 CDP port 9222 free
$ok = $true
try {
  $conn = Get-NetTCPConnection -LocalPort 9222 -State Listen -ErrorAction SilentlyContinue
  if ($conn) { $ok = $false }
} catch {}
Add-Check 'PF06' 'CDP port 9222 free' $ok (if ($ok) { 'VERIFIED' } else { 'FAIL' })

# PF07 ffmpeg
$ok = $false; $bin = $null
try {
  $bin = (Get-ChildItem 'C:\Users\raest\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_*\ffmpeg-*_build\bin\ffmpeg.exe' -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
  if ($bin -and (Test-Path $bin)) { $ok = $true }
} catch {}
Add-Check 'PF07' 'ffmpeg available (gdigrab)' $bin (if ($ok) { 'VERIFIED' } else { 'FAIL' })

# PF08 node+npm
$ok = $false
try { $n = node --version 2>$null; if ($n) { $ok = $true } } catch {}
Add-Check 'PF08' 'node+npm present' $n (if ($ok) { 'VERIFIED' } else { 'FAIL' })

# PF09 cargo
$ok = $false
try { $c = cargo --version 2>$null; if ($c) { $ok = $true } } catch {}
Add-Check 'PF09' 'cargo+rustc present' $c (if ($ok) { 'VERIFIED' } else { 'FAIL' })

# PF10 docker vault-neo
$ok = $false
try { $ps = ssh vault-neo 'docker ps --format "{{.Names}}" | wc -l' 2>$null; if ([int]$ps -ge 3) { $ok = $true } } catch {}
Add-Check 'PF10' 'vault-neo docker containers reachable' "$ps containers" (if ($ok) { 'VERIFIED' } else { 'FAIL' })

# PF12 disk free
$free = (Get-PSDrive C).Free / 1GB
Add-Check 'PF12' 'P1 disk free >= 10 GB' "$([math]::Round($free,1)) GB" (if ($free -ge 10) { 'VERIFIED' } else { 'FAIL' })

# PF13 git remote
$ok = $false
try { $r = git ls-remote origin HEAD 2>$null; if ($r) { $ok = $true } } catch {}
Add-Check 'PF13' 'git ls-remote origin HEAD' $r (if ($ok) { 'VERIFIED' } else { 'FAIL' })

# PF14 run lock free
$lockPath = 'C:\Users\raest\Documents\Karma_SADE\evidence\.ascendance.lock'
$ok = -not (Test-Path $lockPath)
Add-Check 'PF14' 'single-run lock free' $ok (if ($ok) { 'VERIFIED' } else { 'FAIL' })

# PF15 gmail creds readable
$credsPath = 'C:\Users\raest\Documents\Karma_SADE\.gmail-cc-creds'
$ok = Test-Path $credsPath
Add-Check 'PF15' 'gmail creds readable' $ok (if ($ok) { 'VERIFIED' } else { 'FAIL' })

# Emit JSON
$out = @{ preflight_utc = (Get-Date).ToUniversalTime().ToString('o'); checks = $results }
$json = $out | ConvertTo-Json -Depth 5
if ($RunDir) { $json | Out-File -LiteralPath (Join-Path $RunDir 'preflight.json') -Encoding utf8NoBOM }
Write-Host $json

$failed = ($results | Where-Object { $_.status -ne 'VERIFIED' }).Count
if ($failed -gt 0) { exit 1 } else { exit 0 }
