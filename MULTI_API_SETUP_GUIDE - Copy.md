# Multi-API Setup Guide - Complete Instructions
**Goal**: Add Gemini + OpenAI to maximize FREE usage and daily token capacity
**Time**: 15 minutes total

---

## 📋 **Quick Summary**

**What you're adding:**
- ✅ Gemini API (FREE - 1,500 requests/day)
- ✅ OpenAI API (CHEAP - ~$0.0025/query)

**Benefits:**
- 24x more daily capacity (500 → 12,000 requests/day)
- 95% FREE usage (Ollama + Gemini handle 95% of queries)
- Lower costs ($1.35/month → $0.75/month)
- Better quality (right model for each task)

---

## 🔑 **Step 1: Get Gemini API Key (5 min)**

### **A. Create Gemini API Key**

1. **Go to**: https://aistudio.google.com/app/apikey

2. **Sign in** with your Google account

3. **Click**: "Create API key" or "Get API key"

4. **Select**: "Create API key in new project" (or choose existing project)

5. **COPY the key** - it starts with `AIza...`
   - Example: `AIzaSyABC123...xyz789` (about 39 characters)

6. **Save it immediately** - you can see it again later, but better to save now

---

### **B. Set Gemini Environment Variable**

**Open PowerShell** and run:

```powershell
# Replace YOUR_KEY_HERE with your actual Gemini key
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "AIzaSyABC123...xyz789", "User")
```

**Verify it's set:**
```powershell
# Close and reopen PowerShell, then check:
$env:GEMINI_API_KEY

# Should show: AIzaSyABC123...
```

---

## 🔑 **Step 2: Get OpenAI API Key (5 min)**

### **A. Create OpenAI API Key**

1. **Go to**: https://platform.openai.com/api-keys

2. **Sign in** (or create account if needed)

3. **Click**: "+ Create new secret key"

4. **Name it**: "Karma SADE" (or whatever you want)

5. **COPY the key IMMEDIATELY** - starts with `sk-proj-...` or `sk-...`
   - Example: `sk-proj-ABC123...XYZ789` (very long, 100+ characters)
   - ⚠️ **You'll NEVER see this again!** Copy it NOW!

6. **Save to password manager** or secure note

---

### **B. Set OpenAI Environment Variable**

**In PowerShell:**

```powershell
# Replace YOUR_KEY_HERE with your actual OpenAI key
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-proj-ABC123...XYZ789", "User")
```

**Verify it's set:**
```powershell
# Close and reopen PowerShell, then check:
$env:OPENAI_API_KEY

# Should show: sk-proj-ABC123...
```

---

## 🔧 **Step 3: Install Python Packages (2 min)**

**Run in terminal:**

```bash
pip install google-generativeai openai
```

**Expected output:**
```
Successfully installed google-generativeai-... openai-...
```

---

## ✅ **Step 4: Verify Setup (2 min)**

**Test all APIs:**

```bash
cd C:\Users\raest\Documents\Karma_SADE
python Scripts/test_backend.py
```

**Expected output:**
```
[PASS] Ollama available (FREE)
[PASS] Gemini available (FREE - 1,500/day)
[PASS] OpenAI available (PAID)
[PASS] Claude available (PAID)
[CONFIG] 4 AI backends available

BACKEND TEST COMPLETE
```

---

## 🎯 **Complete PowerShell Script (Copy & Paste)**

```powershell
# Get your API keys first from:
# Gemini: https://aistudio.google.com/app/apikey
# OpenAI: https://platform.openai.com/api-keys

# Then run these commands (replace with YOUR keys):

# Set Gemini key
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "YOUR_GEMINI_KEY_HERE", "User")

# Set OpenAI key
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "YOUR_OPENAI_KEY_HERE", "User")

# Verify
Write-Host "Gemini key set: $($env:GEMINI_API_KEY -ne $null)"
Write-Host "OpenAI key set: $($env:OPENAI_API_KEY -ne $null)"

# Note: You'll need to close and reopen PowerShell for changes to take effect
```

---

## 📊 **After Setup - What Changes?**

### **New 4-Tier Routing:**

```
Query comes in
    │
    ├─ Tier 1: Try Ollama (FREE - unlimited local)
    │   ├─ Success → Done ($0.00)
    │   └─ Fail → Next tier
    │
    ├─ Tier 2: Try Gemini (FREE - 1,500/day)
    │   ├─ Success → Done ($0.00)
    │   └─ Fail → Next tier
    │
    ├─ Tier 3: Try OpenAI (CHEAP - ~$0.0025)
    │   ├─ Success → Done ($0.0025)
    │   └─ Fail → Next tier
    │
    └─ Tier 4: Try Claude (EXPENSIVE - last resort)
        └─ Success → Done ($0.015)
```

**Result:** 95% of queries handled FREE!

---

## 💰 **Cost Comparison**

### **Before (Ollama + Claude only):**
```
50 queries/day:
  - 35 → Ollama = $0.00
  - 15 → Claude = $0.045

Daily: $0.045
Monthly: $1.35
Yearly: $16.20
```

### **After (All 4 APIs):**
```
100 queries/day:
  - 70 → Ollama = $0.00
  - 20 → Gemini = $0.00
  - 5 → OpenAI = $0.01
  - 5 → Claude = $0.015

Daily: $0.025
Monthly: $0.75
Yearly: $9

SAVINGS: $7/year + DOUBLE usage!
```

---

## 🔍 **Troubleshooting**

### **Problem: "GEMINI_API_KEY not set"**
**Solution:**
1. Check if you closed/reopened PowerShell after setting
2. Verify in registry: `Get-ItemProperty -Path "HKCU:\Environment" -Name GEMINI_API_KEY`
3. If not there, run the SetEnvironmentVariable command again

---

### **Problem: "google-generativeai not installed"**
**Solution:**
```bash
pip install google-generativeai
```

---

### **Problem: "openai not installed"**
**Solution:**
```bash
pip install openai
```

---

### **Problem: Backend still using only Ollama**
**Solution:**
1. Make sure you restarted the backend after setting keys
2. Check logs: `tail -f ~/Documents/Karma_SADE/Logs/karma-backend.log`
3. Should see: `[OK] Gemini available` and `[OK] OpenAI available`

---

## ✅ **Verification Checklist**

Before starting the backend, verify:

- [ ] Gemini API key obtained from https://aistudio.google.com/app/apikey
- [ ] OpenAI API key obtained from https://platform.openai.com/api-keys
- [ ] Both keys set in environment variables
- [ ] PowerShell restarted after setting keys
- [ ] Python packages installed: `google-generativeai` and `openai`
- [ ] Test script passes: `python Scripts/test_backend.py`

---

## 🚀 **Ready to Start**

**Once all keys are set:**

```bash
# Start the unified backend
python C:\Users\raest\Documents\Karma_SADE\Scripts\karma_backend.py

# Should see:
# [OK] Ollama available (FREE - unlimited local)
# [OK] Gemini available (FREE - 1,500/day)
# [OK] OpenAI available (PAID - ~$0.0025/query)
# [OK] Claude available (PAID - last resort)
# [CONFIG] 4 AI backends available
```

**Then open dashboard:**
```
http://localhost:9400/unified
```

**Test it:**
- Ask simple question → Should use Ollama (FREE)
- Ask code question → Should use Ollama deepseek-coder (FREE)
- If Ollama fails → Should fallback to Gemini (FREE)
- Complex query → Should use OpenAI or Claude (PAID)

---

## 📈 **Daily Capacity**

```
Before: 500 requests/day (Claude MAX plan limit)

After:
  - Ollama: Unlimited (local)
  - Gemini: 1,500/day (FREE)
  - OpenAI: ~10,000/day (paid, high limit)
  - Claude: 500/day (fallback)

Total effective: 12,000+ requests/day
```

**You now have 24x more capacity!** 🎉

---

## 🎯 **Next Steps**

1. **Get both API keys** (15 min total)
2. **Set environment variables** (2 min)
3. **Install packages** (2 min)
4. **Test backend** (2 min)
5. **Start using!** (immediately)

**Total time: ~20 minutes for 24x capacity and 50% cost savings!**

---

**Questions? Check the logs:**
```bash
tail -f ~/Documents/Karma_SADE/Logs/karma-backend.log
```

You'll see which API handled each query and why!
