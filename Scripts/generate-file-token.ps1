$bytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$token = [System.Convert]::ToBase64String($bytes)
Set-Content -Path 'C:\Users\raest\Documents\Karma_SADE\.local-file-token' -Value $token -Encoding UTF8 -NoNewline
Write-Output "Token generated and saved to .local-file-token"
Write-Output "Token value: $token"
Write-Output "Copy this value - you will need it for hub.env on vault-neo in Task 5"
