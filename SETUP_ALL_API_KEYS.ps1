# ============================================================================
# Karma SADE - Complete API Key Setup Script
# ============================================================================
# This script sets up ALL API keys for the 5-tier routing system
# Run this in PowerShell as Administrator (optional) or as your user
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Karma SADE - API Key Setup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to set API key
function Set-KarmaAPIKey {
    param(
        [string]$KeyName,
        [string]$KeyValue,
        [string]$Description
    )

    if ($KeyValue -and $KeyValue -ne "") {
        [System.Environment]::SetEnvironmentVariable($KeyName, $KeyValue, 'User')
        Write-Host "[OK] $Description set successfully" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] $Description - no value provided" -ForegroundColor Yellow
    }
}

# ============================================================================
# REQUIRED KEYS (At least one needed)
# ============================================================================

Write-Host "TIER 1: Ollama (FREE - Local)" -ForegroundColor Cyan
Write-Host "No API key needed - install Ollama from https://ollama.com" -ForegroundColor Gray
Write-Host ""

Write-Host "TIER 2: Z.ai GLM-4-Flash (FREE - Unlimited Cloud Backup)" -ForegroundColor Cyan
$ZAI_KEY = Read-Host "Enter your Z.ai API key (or press Enter to skip)"
Set-KarmaAPIKey -KeyName "ZAI_API_KEY" -KeyValue $ZAI_KEY -Description "Z.ai GLM"
Write-Host "Get key from: https://open.bigmodel.cn/" -ForegroundColor Gray
Write-Host ""

Write-Host "TIER 3: Google Gemini (FREE - 1,500 requests/day)" -ForegroundColor Cyan
$GEMINI_KEY = Read-Host "Enter your Gemini API key (or press Enter to skip)"
Set-KarmaAPIKey -KeyName "GEMINI_API_KEY" -KeyValue $GEMINI_KEY -Description "Google Gemini"
Write-Host "Get key from: https://aistudio.google.com/app/apikey" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# OPTIONAL PAID KEYS (For complex tasks)
# ============================================================================

Write-Host "TIER 4-5: OpenAI (PAID - ~`$0.0025/query)" -ForegroundColor Cyan
$OPENAI_KEY = Read-Host "Enter your OpenAI API key (or press Enter to skip)"
Set-KarmaAPIKey -KeyName "OPENAI_API_KEY" -KeyValue $OPENAI_KEY -Description "OpenAI"
Write-Host "Get key from: https://platform.openai.com/api-keys" -ForegroundColor Gray
Write-Host ""

Write-Host "TIER 6: Perplexity (PAID - ~`$0.001/query, research specialist)" -ForegroundColor Cyan
$PERPLEXITY_KEY = Read-Host "Enter your Perplexity API key (or press Enter to skip)"
Set-KarmaAPIKey -KeyName "PERPLEXITY_API_KEY" -KeyValue $PERPLEXITY_KEY -Description "Perplexity"
Write-Host "Get key from: https://www.perplexity.ai/" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# DISABLED KEYS
# ============================================================================

Write-Host "Claude (DISABLED - No credits available)" -ForegroundColor Red
Write-Host "Claude API is not configured due to insufficient credits" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# VERIFICATION
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$keys = @{
    "ZAI_API_KEY" = "Z.ai GLM"
    "GEMINI_API_KEY" = "Google Gemini"
    "OPENAI_API_KEY" = "OpenAI"
    "PERPLEXITY_API_KEY" = "Perplexity"
}

foreach ($key in $keys.Keys) {
    $value = [System.Environment]::GetEnvironmentVariable($key, 'User')
    if ($value) {
        $masked = $value.Substring(0, [Math]::Min(10, $value.Length)) + "..."
        Write-Host "[OK] $($keys[$key]): $masked" -ForegroundColor Green
    } else {
        Write-Host "[--] $($keys[$key]): Not set" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Close this PowerShell window" -ForegroundColor White
Write-Host "2. Double-click '⚡ Karma SADE' icon on your desktop" -ForegroundColor White
Write-Host "3. Check logs for backend availability:" -ForegroundColor White
Write-Host "   tail -f Logs\karma-backend.log" -ForegroundColor Gray
Write-Host ""
Write-Host "Expected output:" -ForegroundColor White
Write-Host "  [OK] Z.ai GLM available (FREE Flash + PAID GLM-5)" -ForegroundColor Gray
Write-Host "  [OK] Gemini available (FREE - 1,500/day)" -ForegroundColor Gray
Write-Host "  [OK] OpenAI available (PAID - ~`$0.0025/query)" -ForegroundColor Gray
Write-Host "  [OK] Perplexity available (PAID - research specialist)" -ForegroundColor Gray
Write-Host "  [CONFIG] 5 AI backends available" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
