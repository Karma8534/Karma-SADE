<#
.SYNOPSIS
    Karma SADE — Secrets Manager v1.0.0
.DESCRIPTION
    Encrypts/decrypts API keys using Windows DPAPI (Data Protection API).
    Keys are encrypted per-user — only the Windows account that encrypted
    them can decrypt them. No master password, no external dependencies.

    Secrets are stored in: ~\karma\secrets.json
    Each value is a DPAPI-encrypted base64 string.

    Usage:
      # Store a secret interactively
      .\karma_secrets.ps1 -Action store -Key "openai_api_key"

      # Store a secret non-interactively (for scripting)
      .\karma_secrets.ps1 -Action store -Key "groq_api_key" -Value "gsk_..."

      # Retrieve a secret (outputs plaintext)
      .\karma_secrets.ps1 -Action get -Key "openai_api_key"

      # List all stored key names (not values)
      .\karma_secrets.ps1 -Action list

      # Delete a secret
      .\karma_secrets.ps1 -Action delete -Key "openai_api_key"

      # Export as environment variables (for use in startup scripts)
      .\karma_secrets.ps1 -Action env

.NOTES
    Security model:
    - DPAPI encryption is tied to the Windows user account (raest)
    - If the user password is reset by an admin (not changed by user), keys are LOST
    - Backup: keep a copy of your API keys in a password manager (1Password, etc.)
    - The secrets.json file is useless without the user's Windows credentials
    - secrets.json should NOT be committed to git (add to .gitignore)
#>

param(
    [Parameter(Mandatory)]
    [ValidateSet("store", "get", "list", "delete", "env")]
    [string]$Action,

    [string]$Key,
    [string]$Value
)

Add-Type -AssemblyName System.Security

$SecretsDir  = Join-Path $env:USERPROFILE "karma"
$SecretsFile = Join-Path $SecretsDir "secrets.json"

# ─── Helpers ──────────────────────────────────────────────────────────────────

function Protect-String {
    param([string]$Plaintext)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Plaintext)
    $encrypted = [System.Security.Cryptography.ProtectedData]::Protect(
        $bytes, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser
    )
    return [Convert]::ToBase64String($encrypted)
}

function Unprotect-String {
    param([string]$EncryptedBase64)
    $encrypted = [Convert]::FromBase64String($EncryptedBase64)
    $bytes = [System.Security.Cryptography.ProtectedData]::Unprotect(
        $encrypted, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser
    )
    return [System.Text.Encoding]::UTF8.GetString($bytes)
}

function Get-Secrets {
    if (Test-Path $SecretsFile) {
        try {
            return Get-Content $SecretsFile -Raw | ConvertFrom-Json
        }
        catch {
            Write-Error "Corrupted secrets file: $SecretsFile"
            exit 1
        }
    }
    return @{}
}

function Save-Secrets {
    param($Secrets)
    if (-not (Test-Path $SecretsDir)) {
        New-Item -ItemType Directory -Path $SecretsDir -Force | Out-Null
    }
    $Secrets | ConvertTo-Json -Depth 2 | Set-Content -Path $SecretsFile -Encoding UTF8

    # Lock down file permissions — owner only
    $acl = Get-Acl $SecretsFile
    $acl.SetAccessRuleProtection($true, $false)
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $env:USERNAME, "FullControl", "Allow"
    )
    $acl.AddAccessRule($rule)
    Set-Acl -Path $SecretsFile -AclObject $acl
}

# ─── Actions ──────────────────────────────────────────────────────────────────

switch ($Action) {
    "store" {
        if (-not $Key) {
            Write-Error "Usage: -Action store -Key <name> [-Value <secret>]"
            exit 1
        }
        if (-not $Value) {
            $secure = Read-Host "Enter value for '$Key'" -AsSecureString
            $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
            $Value = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
        if (-not $Value) {
            Write-Error "No value provided"
            exit 1
        }

        $secrets = Get-Secrets
        $encrypted = Protect-String -Plaintext $Value

        # ConvertFrom-Json returns PSCustomObject, handle both types
        if ($secrets -is [PSCustomObject]) {
            $secrets | Add-Member -NotePropertyName $Key -NotePropertyValue $encrypted -Force
        }
        else {
            $secrets[$Key] = $encrypted
        }

        Save-Secrets -Secrets $secrets
        Write-Host "[OK] Stored '$Key' (encrypted with DPAPI)" -ForegroundColor Green
    }

    "get" {
        if (-not $Key) {
            Write-Error "Usage: -Action get -Key <name>"
            exit 1
        }
        $secrets = Get-Secrets
        $val = $null
        if ($secrets -is [PSCustomObject]) {
            $val = $secrets.$Key
        }
        else {
            $val = $secrets[$Key]
        }
        if (-not $val) {
            Write-Error "Key '$Key' not found in secrets store"
            exit 1
        }
        # Output plaintext (can be captured by calling script)
        Unprotect-String -EncryptedBase64 $val
    }

    "list" {
        $secrets = Get-Secrets
        if ($secrets -is [PSCustomObject]) {
            $secrets.PSObject.Properties | ForEach-Object { Write-Host $_.Name }
        }
        else {
            $secrets.Keys | ForEach-Object { Write-Host $_ }
        }
    }

    "delete" {
        if (-not $Key) {
            Write-Error "Usage: -Action delete -Key <name>"
            exit 1
        }
        $secrets = Get-Secrets
        if ($secrets -is [PSCustomObject]) {
            $props = @{}
            $secrets.PSObject.Properties | Where-Object { $_.Name -ne $Key } | ForEach-Object {
                $props[$_.Name] = $_.Value
            }
            $secrets = [PSCustomObject]$props
        }
        else {
            $secrets.Remove($Key)
        }
        Save-Secrets -Secrets $secrets
        Write-Host "[OK] Deleted '$Key'" -ForegroundColor Green
    }

    "env" {
        # Output secrets as environment variable assignments
        # Usage in startup: . .\karma_secrets.ps1 -Action env
        $secrets = Get-Secrets
        $envMap = @{
            "openai_api_key"  = "OPENAI_API_KEY"
            "groq_api_key"    = "GROQ_API_KEY"
            "gemini_api_key"  = "GEMINI_API_KEY"
        }

        $props = @()
        if ($secrets -is [PSCustomObject]) {
            $props = $secrets.PSObject.Properties
        }

        foreach ($prop in $props) {
            $envName = if ($envMap.ContainsKey($prop.Name)) { $envMap[$prop.Name] } else { $prop.Name.ToUpper() }
            try {
                $plaintext = Unprotect-String -EncryptedBase64 $prop.Value
                [Environment]::SetEnvironmentVariable($envName, $plaintext, "Process")
                Write-Host "[OK] Set `$env:$envName" -ForegroundColor Green
            }
            catch {
                Write-Host "[ERROR] Failed to decrypt '$($prop.Name)': $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
}
