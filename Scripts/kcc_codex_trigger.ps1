<#
.SYNOPSIS
    KCC Codex trigger — runs codex exec on K2 and returns ArchonPrime analysis output.
.PARAMETER Prompt
    The analysis prompt to send to Codex.
.PARAMETER K2Host
    K2 LAN address. Default: 192.168.0.226
.EXAMPLE
    .\kcc_codex_trigger.ps1 -Prompt "What is 2+2? Respond with just the number."
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$Prompt,
    [string]$K2Host = "192.168.0.226"
)

# Escape single quotes in prompt for bash single-quoted string
$EscapedPrompt = $Prompt -replace "'", "'\''"

# Verified invocation (PROOF-A Task 1): npx codex exec --sandbox read-only --skip-git-repo-check
# stderr suppressed (codex prints version banner to stderr; rc=0 on success)
$SshOutput = & ssh karma@$K2Host "npx codex exec --sandbox read-only --skip-git-repo-check '$EscapedPrompt'" 2>$null
$rc = $LASTEXITCODE

if ($rc -ne 0) {
    Write-Error "kcc_codex_trigger: codex exec failed (rc=$rc). Run manually to debug: ssh karma@$K2Host 'npx codex exec --sandbox read-only --skip-git-repo-check `"$Prompt`"'"
    return $null
}

$Result = ($SshOutput | Where-Object { $_ -ne $null } | ForEach-Object { "$_" }) -join "`n"
return $Result.Trim()
