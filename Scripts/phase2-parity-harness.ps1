param(
  [string]$JulianExe='C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\target\release\julian.exe',
  [string]$EvidenceDir='C:\Users\raest\Documents\Karma_SADE\evidence',
  [string]$SessionId='',
  [string]$LocalBase='http://127.0.0.1:7891',
  [string]$RemoteBase='https://hub.arknexus.net'
)
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
$png=Join-Path $EvidenceDir 'phase2-parity.png'
$rt=Join-Path $EvidenceDir 'phase2-roundtrip.json'
$eq=Join-Path $EvidenceDir 'phase2-session-equality.txt'
$token=(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt").Trim()
$sid = $SessionId
if(-not $sid){ $sid=(Invoke-RestMethod -Uri "$LocalBase/memory/session" -TimeoutSec 8).session_id }
function HasProbe([string]$base,[string]$probe,[bool]$auth){ try{ $h=@{}; if($auth){$h.Authorization="Bearer $token"}; $r=Invoke-RestMethod -Uri "$base/v1/session/$sid" -Headers $h -TimeoutSec 10; foreach($x in @($r.history)){ $txt=''; if($x.text){$txt=$x.text}elseif($x.body.content){$txt=$x.body.content}; if($txt -like "*$probe*"){ return $true } } } catch {}; return $false }
function PostTurn([string]$base,[string]$txt,[bool]$auth){
  $h=@{'Content-Type'='application/json'}
  if($auth){$h.Authorization="Bearer $token"}
  $b=@{turn=$txt;role='user'}|ConvertTo-Json
  Invoke-RestMethod -Uri "$base/v1/session/$sid" -Method Post -Headers $h -Body $b -TimeoutSec 30 | Out-Null
}
$p1='PARITY-PROBE-'+(Get-Date).ToUniversalTime().ToString('o')
$sw1=[Diagnostics.Stopwatch]::StartNew(); PostTurn $LocalBase $p1 $false; $lr=-1; while($sw1.ElapsedMilliseconds -lt 30000){ if(HasProbe $RemoteBase $p1 $true){$lr=$sw1.ElapsedMilliseconds; break}; Start-Sleep -Milliseconds 400 }
$p2='PARITY-PROBE-REV-'+(Get-Date).ToUniversalTime().ToString('o')
$sw2=[Diagnostics.Stopwatch]::StartNew(); PostTurn $RemoteBase $p2 $true; $rl=-1; while($sw2.ElapsedMilliseconds -lt 30000){ if(HasProbe $LocalBase $p2 $false){$rl=$sw2.ElapsedMilliseconds; break}; Start-Sleep -Milliseconds 400 }
$lh=Invoke-RestMethod -Uri "$LocalBase/v1/session/$sid" -TimeoutSec 12
$rh=Invoke-RestMethod -Uri "$RemoteBase/v1/session/$sid" -Headers @{Authorization="Bearer $token"} -TimeoutSec 12
$ll=@(); foreach($h in @($lh.history|Select-Object -Last 20)){ $role=if($h.body.role){$h.body.role}else{''}; $txt=if($h.text){$h.text}elseif($h.body.content){$h.body.content}else{''}; $ll += "$role|$txt" }
$rr=@(); foreach($h in @($rh.history|Select-Object -Last 20)){ $role=if($h.body.role){$h.body.role}else{''}; $txt=if($h.text){$h.text}elseif($h.body.content){$h.body.content}else{''}; $rr += "$role|$txt" }
Get-Process julian,msedgewebview2 -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 1
$p=Start-Process -FilePath $JulianExe -PassThru
Start-Sleep -Seconds 6
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp=New-Object System.Drawing.Bitmap($b.Width,$b.Height)
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Left,$b.Top,0,0,$b.Size)
$g.Dispose(); $bmp.Save($png,[System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
@{timestamp=(Get-Date -Format o);session_id=$sid;probe_local_to_remote=$p1;probe_remote_to_local=$p2;local_to_remote_ms=$lr;remote_to_local_ms=$rl;deadline_ms=5000;local_to_remote_within_deadline=($lr -ge 0 -and $lr -lt 5000);remote_to_local_within_deadline=($rl -ge 0 -and $rl -lt 5000)} | ConvertTo-Json -Depth 5 | Set-Content -Path $rt -Encoding UTF8
$lines=@("session_id match: $([string]($lh.session_id -eq $rh.session_id))","history match: $([string](($ll -join "`n") -eq ($rr -join "`n")))",'','local:'); $lines+=$ll; $lines+='' ; $lines+='remote:'; $lines+=$rr; $lines | Set-Content -Path $eq -Encoding UTF8
