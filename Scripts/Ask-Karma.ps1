# Ask-Karma.ps1
# Quick way to delegate tasks to Karma using FREE Ollama instead of Claude Code
#
# Usage:
#   Ask-Karma "Check system health"
#   Ask-Karma "What's using the most memory?"
#   karma "List all Python files"  (if you create alias)

param(
    [Parameter(Mandatory=$true, Position=0, ValueFromRemainingArguments=$true)]
    [string[]]$Question,

    [Parameter(Mandatory=$false)]
    [string]$Model = "llama3.1"
)

$QuestionText = $Question -join " "

Write-Host "💬 Asking Karma (using $Model - FREE)..." -ForegroundColor Cyan
Write-Host "❓ Question: $QuestionText`n" -ForegroundColor Yellow

# Try Ollama directly
try {
    $response = ollama run $Model $QuestionText 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "🤖 Karma's Response:" -ForegroundColor Green
        Write-Host $response
        Write-Host "`n💰 Cost: `$0.00 (Local Ollama)" -ForegroundColor Green

        # Log interaction
        $logEntry = @{
            timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
            question = $QuestionText
            response = $response
            model = $Model
            cost = 0
        } | ConvertTo-Json -Compress

        Add-Content -Path "karma_interactions.jsonl" -Value $logEntry

        return $response
    } else {
        Write-Host "❌ Error from Ollama" -ForegroundColor Red
        return $null
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "`nMake sure Ollama is installed and running:" -ForegroundColor Yellow
    Write-Host "  Check with: ollama list" -ForegroundColor Yellow
    return $null
}

<#
.SYNOPSIS
Send a task to Karma using FREE local Ollama models instead of paid Claude API

.DESCRIPTION
This script delegates simple tasks to Karma, which uses local Ollama models.
This saves your Claude Code API quota for complex architectural tasks.

.PARAMETER Question
The question or task you want Karma to handle

.PARAMETER Model
Which Ollama model to use (default: llama3.1)
Options: llama3.1, deepseek-coder, qwen2.5-coder

.EXAMPLE
Ask-Karma "Check system health"

.EXAMPLE
Ask-Karma "List all running services" -Model deepseek-coder

.EXAMPLE
# Create alias for faster access
Set-Alias karma Ask-Karma
karma "What's the weather?"
#>
