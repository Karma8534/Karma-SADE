# Creates the "Talk to Karma" desktop shortcut
# Run once: powershell -ExecutionPolicy Bypass -File create-shortcut.ps1

$karmaDir = "C:\Users\raest\Documents\Karma_SADE\karma-core"
if (-not (Test-Path $karmaDir)) { New-Item -ItemType Directory -Path $karmaDir -Force | Out-Null }

# Copy files to stable location
$srcDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Copy-Item (Join-Path $srcDir "karma-icon.ico") $karmaDir -Force
Copy-Item (Join-Path $srcDir "karma-chat.ps1") $karmaDir -Force

$icoPath = Join-Path $karmaDir "karma-icon.ico"
$ps1Path = Join-Path $karmaDir "karma-chat.ps1"

# Create desktop shortcut
$shell = New-Object -ComObject WScript.Shell
$lnkPath = "C:\Users\raest\Desktop\Talk to Karma.lnk"
$shortcut = $shell.CreateShortcut($lnkPath)
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-ExecutionPolicy Bypass -NoProfile -File `"$ps1Path`""
$shortcut.IconLocation = "$icoPath,0"
$shortcut.WorkingDirectory = $karmaDir
$shortcut.WindowStyle = 1
$shortcut.Description = "Talk to Karma - AI peer terminal chat"
$shortcut.Save()

Write-Host "Shortcut created: $lnkPath" -ForegroundColor Green
Write-Host "Icon: $icoPath"
Write-Host "Launcher: $ps1Path"
