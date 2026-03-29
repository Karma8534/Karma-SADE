# Start-Karma.ps1 — Launch the Karma Electron desktop app
$karmaDir = Join-Path $env:USERPROFILE "Documents\Karma_SADE\karma-browser"
Set-Location $karmaDir
& npx electron . 2>&1 | Out-Null
