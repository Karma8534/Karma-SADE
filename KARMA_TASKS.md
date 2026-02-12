# Tasks for Karma to Execute
**Date**: 2026-02-12
**Purpose**: Offload work from Warp Claude to Karma to save API quota

---

## 🎯 Immediate Tasks for Karma

### Task 1: Install Backend Dependencies
```bash
pip install fastapi uvicorn anthropic websockets python-multipart
```

**Why**: Need these for the new unified backend

**Check success**: Run `pip list | grep fastapi`

---

### Task 2: Test Current System Health
Run the health check script:
```powershell
cd C:\Users\raest\Documents\Karma_SADE\Scripts
.\karma_health_check.ps1
```

**Report back**:
- Which services are healthy?
- Any warnings or errors?
- What's the overall status?

---

### Task 3: Check API Key Configuration
Verify your Claude API key is set:
```powershell
$env:ANTHROPIC_API_KEY
# or
$env:CLAUDE_API_KEY
```

**If not set**, set it:
```powershell
# Option 1: Use secrets manager
.\karma_secrets.ps1 -Action store -Key "anthropic_api_key"

# Option 2: Set environment variable
$env:ANTHROPIC_API_KEY = "your-key-here"
```

---

### Task 4: Test New Backend (Dry Run)
Try starting the new backend to see if it works:
```bash
python C:\Users\raest\Documents\Karma_SADE\Scripts\karma_backend.py
```

**Expected output**:
```
Karma SADE Backend v2.0
Dashboard: http://localhost:9400
API Docs: http://localhost:9400/docs
```

**If it starts successfully**, press Ctrl+C to stop it (we'll configure it properly next)

**If errors**, report them back to Neo

---

### Task 5: Monitor Current Resource Usage
Check what's using resources:
```powershell
Get-Process | Where-Object {$_.WorkingSet -gt 100MB} | Select-Object Name,Id,@{Name="MemoryMB";Expression={[math]::Round($_.WorkingSet/1MB,2)}} | Sort-Object MemoryMB -Descending | Format-Table
```

**Report**:
- Which processes are using the most memory?
- Is Open WebUI running? (we might not need it anymore)
- Total memory used by Karma SADE components?

---

### Task 6: Analyze Dashboard Performance
Open the dashboard and check:
```
http://localhost:9400/dashboard
```

**Questions to answer**:
- Does it load?
- Are all tabs working?
- Any errors in browser console (F12)?
- Does auto-refresh work?

---

## 📊 Information to Collect for Neo

When you complete these tasks, provide a summary:

```
Task Completion Report
======================
Date: [date/time]

Task 1 (Dependencies): ✅ DONE / ⚠️ PARTIAL / ❌ FAILED
  - Details: [what happened]

Task 2 (Health Check): ✅ DONE / ⚠️ PARTIAL / ❌ FAILED
  - Overall status: [HEALTHY/WARNING/CRITICAL]
  - Issues found: [list]

Task 3 (API Keys): ✅ CONFIGURED / ❌ NOT SET
  - Method used: [secrets/env var]

Task 4 (Backend Test): ✅ WORKS / ❌ ERRORS
  - Port: [9400 or other]
  - Errors: [if any]

Task 5 (Resources):
  - Open WebUI: [running/stopped]
  - Total Karma memory: [XMB]
  - Recommendation: [any]

Task 6 (Dashboard):
  - Status: [working/broken]
  - Issues: [list]

Recommendations for Next Steps:
1. [what should Neo do next?]
2. [any blockers?]
3. [optimization opportunities?]
```

---

## 🚀 Why This Approach

**Benefits**:
- ✅ Karma learns by doing these tasks
- ✅ Saves Neo's Claude API quota (Karma uses its own calls)
- ✅ Karma builds context about the system
- ✅ Parallel work: Karma investigates while Neo plans

**After Karma reports back**, we'll know:
1. What's working
2. What needs fixing
3. Whether we can proceed with unified dashboard
4. Resource usage and optimization opportunities

---

## 💡 Tips for Karma

**Be thorough**: Run each command and check the output
**Be precise**: Copy exact error messages if something fails
**Be proactive**: If you see an issue, suggest a fix
**Ask for help**: If stuck, tell Neo what you tried

You've got this! 🚀
