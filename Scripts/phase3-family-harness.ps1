param(
  [string]$JulianExe='C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\target\release\julian.exe',
  [string]$EvidenceDir='C:\Users\raest\Documents\Karma_SADE\evidence',
  [string]$FrontendSrcDir='C:\Users\raest\Documents\Karma_SADE\frontend\src'
)
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
$a=Join-Path $EvidenceDir 'phase3-agents-sections.png'
$w=Join-Path $EvidenceDir 'phase3-whoami.png'
$g=Join-Path $EvidenceDir 'phase3-family-grep.txt'
Get-Process julian,msedgewebview2 -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 1
Start-Process -FilePath $JulianExe | Out-Null
Start-Sleep -Seconds 6
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp=New-Object System.Drawing.Bitmap($b.Width,$b.Height)
$gr=[System.Drawing.Graphics]::FromImage($bmp)
$gr.CopyFromScreen($b.Left,$b.Top,0,0,$b.Size)
$gr.Dispose(); $bmp.Save($a,[System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
$sid=(Invoke-RestMethod -Uri 'http://127.0.0.1:7891/memory/session' -TimeoutSec 8).session_id
$body=@{message='/whoami';session_id=$sid}|ConvertTo-Json
Invoke-RestMethod -Uri 'http://127.0.0.1:7891/v1/chat' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 120 | Out-Null
Start-Sleep -Seconds 2
$bmp2=New-Object System.Drawing.Bitmap($b.Width,$b.Height)
$gr2=[System.Drawing.Graphics]::FromImage($bmp2)
$gr2.CopyFromScreen($b.Left,$b.Top,0,0,$b.Size)
$gr2.Dispose(); $bmp2.Save($w,[System.Drawing.Imaging.ImageFormat]::Png); $bmp2.Dispose()
$patterns=@('TRUE FAMILY.*[Cc]odex','TRUE FAMILY.*\bKCC\b','Codex.*\(family\)','KCC.*\(family\)')
$hits=@()
$files=Get-ChildItem -Path $FrontendSrcDir -Recurse -File -Include *.ts,*.tsx
foreach($f in $files){ $content=Get-Content -Path $f.FullName -Raw; foreach($p in $patterns){ if($content -match $p){ $hits += "$($f.FullName):$p" } } }
if($hits.Count -eq 0){ 'PASS zero hits' | Set-Content -Path $g -Encoding UTF8 } else { $hits | Set-Content -Path $g -Encoding UTF8 }
