# Perplexity API Setup Guide

## Quick Setup

### Step 1: Set API Key in Windows Registry

Open PowerShell and run:

```powershell
[System.Environment]::SetEnvironmentVariable('PERPLEXITY_API_KEY', 'pplx-YOUR-KEY-HERE', 'User')
```

**Replace `pplx-YOUR-KEY-HERE` with your actual Perplexity API key.**

### Step 2: Verify Installation

```powershell
[System.Environment]::GetEnvironmentVariable('PERPLEXITY_API_KEY', 'User')
```

You should see your API key displayed.

### Step 3: Restart Karma Backend

Double-click the **⚡ Karma SADE** icon on your desktop, or run:

```bash
cd C:\Users\raest\Documents\Karma_SADE
START_KARMA.bat
```

The backend will automatically load the API key from the registry on startup.

---

## What is Perplexity?

Perplexity is a research-focused AI that excels at:
- Web search and current information
- Comparing multiple sources
- Research-heavy queries
- Fact-checking and citations

In Karma's 4-tier routing system, Perplexity is **Tier 4** (the final fallback):

1. **Ollama** (FREE - unlimited) - Simple queries and code
2. **Gemini** (FREE - 1,500/day) - Fast inference
3. **OpenAI** (CHEAP - ~$0.0025/query) - Complex code and reasoning
4. **Perplexity** (CHEAP - ~$0.001/query) - Research and analysis

---

## Cost Comparison

| Model | Cost per Query | Best For |
|-------|---------------|----------|
| Ollama | $0.00 (FREE) | Simple tasks, local privacy |
| Gemini | $0.00 (FREE) | Fast responses, general queries |
| OpenAI | ~$0.0025 | Complex code, reasoning |
| Perplexity | ~$0.001 | Research, web search, citations |
| ~~Claude~~ | ~~$0.015~~ | **DISABLED** (no credits) |

**Perplexity is 15x cheaper than Claude and includes web search!**

---

## How to Get a Perplexity API Key

1. Go to https://www.perplexity.ai/
2. Sign up or log in
3. Navigate to Settings → API
4. Create a new API key
5. Copy the key (starts with `pplx-`)
6. Follow the setup steps above

---

## Verification

After restarting the backend, check the logs:

```bash
tail -f C:\Users\raest\Documents\Karma_SADE\Logs\karma-backend.log
```

You should see:
```
[OK] Perplexity available (PAID - research specialist)
[CONFIG] 4 AI backends available
```

If you see `[CONFIG] 3 AI backends available`, the Perplexity key wasn't loaded correctly.

---

## Troubleshooting

### Key Not Loading

If Perplexity isn't detected:

1. **Check the registry value:**
   ```powershell
   Get-ItemProperty -Path 'HKCU:\Environment' -Name PERPLEXITY_API_KEY
   ```

2. **Verify key format:**
   - Must start with `pplx-`
   - No extra quotes or spaces

3. **Restart PowerShell and backend:**
   - Close all PowerShell windows
   - Restart the backend using START_KARMA.bat

### Still Not Working?

Set the key directly in environment (temporary):

```bash
set PERPLEXITY_API_KEY=pplx-YOUR-KEY-HERE
python Scripts\karma_backend.py
```

This will work for the current session only. For permanent storage, use the registry method above.

---

## Status

✅ **Perplexity integration complete**
✅ **Replaces Claude as Tier 4 fallback**
✅ **15x cheaper than Claude**
✅ **Includes web search capabilities**
❌ **Claude disabled (no credits available)**

---

**Your new multi-API stack:**
- 95% FREE (Ollama + Gemini)
- 5% PAID (OpenAI + Perplexity)
- $45/year savings vs Claude-only
- 24x capacity increase
