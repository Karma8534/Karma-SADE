param()
$ErrorActionPreference = 'Stop'
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) { Write-Host "ERROR: Must run as Administrator" -ForegroundColor Red; exit 1 }

Write-Host "Adding URL ACL for http://+:7771/ ..." -ForegroundColor Cyan
$result = netsh http add urlacl url=http://+:7771/ user="$env:USERDOMAIN\$env:USERNAME" 2>&1
Write-Host $result
Write-Host "Done." -ForegroundColor Green
