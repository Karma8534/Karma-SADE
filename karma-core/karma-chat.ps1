# Karma Terminal Chat Launcher
# Double-click to talk to Karma

$Host.UI.RawUI.WindowTitle = "Karma Chat"
$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "White"
Clear-Host

Write-Host ""
Write-Host "   Connecting to Karma..." -ForegroundColor DarkMagenta
Write-Host ""

# SSH into vault-neo and launch Karma's CLI inside the Docker container
ssh -t vault-neo "docker exec -it karma-server python3 /app/cli.py chat"

# If SSH exits, show message
Write-Host ""
Write-Host "   Session ended." -ForegroundColor DarkGray
Write-Host "   Press any key to close..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
