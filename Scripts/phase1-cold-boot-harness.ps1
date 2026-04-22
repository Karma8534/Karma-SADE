param(
  [string]$JulianExe='C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\target\release\julian.exe',
  [string]$EvidenceDir='C:\Users\raest\Documents\Karma_SADE\evidence'
)
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
$png=Join-Path $EvidenceDir 'phase1-first-frame.png'
$tim=Join-Path $EvidenceDir 'phase1-timing.json'
$hist=Join-Path $EvidenceDir 'phase1-history-diff.txt'
$trace=Join-Path $EvidenceDir 'phase1-canonical-trace.txt'
Get-Process julian,msedgewebview2 -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 700
$sw=[Diagnostics.Stopwatch]::StartNew()
$p=Start-Process -FilePath $JulianExe -PassThru
$visible=-1
for($i=0;$i -lt 120;$i++){ Start-Sleep -Milliseconds 50; $p.Refresh(); if($p.MainWindowHandle -ne 0){$visible=$sw.ElapsedMilliseconds; break} }
Start-Sleep -Seconds 3
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp=New-Object System.Drawing.Bitmap($b.Width,$b.Height)
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Left,$b.Top,0,0,$b.Size)
$g.Dispose(); $bmp.Save($png,[System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
function P([string]$u){ try{$r=Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 8; [pscustomobject]@{url=$u;status=$r.StatusCode;lat=0;snippet=($r.Content.Substring(0,[Math]::Min(300,$r.Content.Length)) -replace '[\r\n]',' ')} } catch { [pscustomobject]@{url=$u;status=0;lat=0;snippet=$_.Exception.Message} } }
$w=P 'http://127.0.0.1:7891/memory/wakeup'
$s=P 'http://127.0.0.1:7891/memory/session'
$r=P 'http://127.0.0.1:7891/v1/runtime/truth'
$sid=''; try{$sid=((Invoke-RestMethod -Uri 'http://127.0.0.1:7891/memory/session' -TimeoutSec 6).session_id)}catch{}
if(-not $sid){$sid='unknown'}
$ss=P "http://127.0.0.1:7891/v1/session/$sid"
@($w,$s,$r,$ss) | ConvertTo-Json -Depth 5 | Set-Content -Path $trace -Encoding UTF8
$history=@()
try{ $sj=Invoke-RestMethod -Uri "http://127.0.0.1:7891/v1/session/$sid" -TimeoutSec 8; $history=@($sj.history | Select-Object -Last 3) }catch{}
$lines=@("session_id: $sid",'last 3 turns:')
if($history.Count -eq 0){$lines+='(none)'} else { foreach($h in $history){ $role=if($h.body.role){$h.body.role}else{'?'}; $txt=if($h.text){$h.text}elseif($h.body.content){$h.body.content}else{''}; $lines+="$role | $($txt -replace '[\r\n]',' ')" } }
$lines | Set-Content -Path $hist -Encoding UTF8
$tm=[pscustomobject]@{ timestamp=(Get-Date -Format o); window_visible_ms=$visible; wall_clock_ms=$sw.ElapsedMilliseconds; paint_deadline_ms=2000; paint_within_deadline=($visible -ge 0 -and $visible -lt 2000) }
$tm | ConvertTo-Json -Depth 5 | Set-Content -Path $tim -Encoding UTF8
