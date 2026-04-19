$WshShell = New-Object -ComObject WScript.Shell
$ShortcutPath = Join-Path $env:USERPROFILE 'Desktop\ArkNexus.lnk'
$TargetPath   = Join-Path $env:USERPROFILE 'Desktop\Julian.exe'
$sc = $WshShell.CreateShortcut($ShortcutPath)
$sc.TargetPath       = $TargetPath
$sc.IconLocation     = "$TargetPath,0"
$sc.Description      = 'ArkNexus - Julian harness'
$sc.WorkingDirectory = Join-Path $env:USERPROFILE 'Desktop'
$sc.Save()
Get-Item $ShortcutPath | Format-List Name, Length, LastWriteTime
