$WScript = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$lnk = Join-Path $desktop 'Arknexus.lnk'
$sc = $WScript.CreateShortcut($lnk)
$sc.TargetPath = 'C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\target\release\nexus.exe'
$sc.WorkingDirectory = 'C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\target\release'
$sc.IconLocation = 'C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\icons\icon.ico,0'
$sc.Description = 'Arknexus - Tauri app'
$sc.Save()
Test-Path $lnk
(Get-Item $lnk).FullName
