# Create Desktop Shortcut for Karma SADE
# This script creates a desktop icon to launch Karma with one click

$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = "$DesktopPath\⚡ Karma SADE.lnk"

# Create the shortcut
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "C:\Windows\System32\wscript.exe"
$Shortcut.Arguments = '"C:\Users\raest\Documents\Karma_SADE\START_KARMA_HIDDEN.vbs"'
$Shortcut.WorkingDirectory = "C:\Users\raest\Documents\Karma_SADE"
$Shortcut.Description = "Launch Karma SADE Unified Dashboard (Hidden Backend)"
$Shortcut.IconLocation = "C:\Windows\System32\shell32.dll,277"  # Lightning bolt icon
$Shortcut.WindowStyle = 7  # Minimized window
$Shortcut.Save()

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Desktop Shortcut Created!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Shortcut location: $ShortcutPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "Double-click the '⚡ Karma SADE' icon on your desktop to:" -ForegroundColor White
Write-Host "  1. Start the multi-API backend (4 AI models)" -ForegroundColor Gray
Write-Host "  2. Open the unified dashboard in your browser" -ForegroundColor Gray
Write-Host "  3. Begin chatting with Karma!" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
