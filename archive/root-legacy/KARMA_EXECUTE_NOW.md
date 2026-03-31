# Tasks for Karma - Execute Now
**Date**: 2026-02-12
**Priority**: HIGH
**Method**: Use Ollama (LOCAL - FREE) for all tasks

---

## 🎯 Karma, Execute These 6 Tasks

### **Task 1: Health Check**
Run the health check script and report status:
```powershell
cd C:\Users\raest\Documents\Karma_SADE\Scripts
.\karma_health_check.ps1
```

**Report**: Overall status, which services are running, any errors

---

### **Task 2: Install Dependencies**
Install Python packages needed for new backend:
```bash
pip install fastapi uvicorn anthropic websockets python-multipart
```

**Report**: Success or any errors encountered

---

### **Task 3: Test Ollama Models**
Verify all Ollama models work:
```bash
ollama list
ollama run llama3.1 "Test - respond with OK"
ollama run deepseek-coder "Test - respond with OK"
```

**Report**: Which models are available and working

---

### **Task 4: Check API Keys**
Verify Claude API key is set:
```powershell
if ($env:ANTHROPIC_API_KEY) {
    Write-Host "API key is set (length: $($env:ANTHROPIC_API_KEY.Length))"
} else {
    Write-Host "WARNING: ANTHROPIC_API_KEY not set"
}
```

**Report**: Is API key configured?

---

### **Task 5: Resource Usage**
Check what's using resources:
```powershell
Get-Process | Where-Object {$_.WorkingSet -gt 100MB} |
    Select-Object ProcessName,@{Name="MemoryMB";Expression={[math]::Round($_.WorkingSet/1MB,2)}} |
    Sort-Object MemoryMB -Descending |
    Format-Table
```

**Report**: Top memory-using processes, total Karma memory usage

---

### **Task 6: Test New Backend**
Try starting the new backend (dry run):
```bash
python C:\Users\raest\Documents\Karma_SADE\Scripts\karma_backend.py &
# Let it run for 5 seconds
sleep 5
# Check if it's listening
curl http://localhost:9400/health
# Stop it
pkill -f karma_backend.py
```

**Report**: Did it start? Any errors? Health endpoint response?

---

## 📋 Deliverable

When all tasks complete, provide this summary:

```
KARMA TASK EXECUTION REPORT
Date: [timestamp]
Execution Time: [duration]
Model Used: Ollama (llama3.1 and deepseek-coder)

TASK RESULTS:
1. Health Check: [PASS/FAIL] - [details]
2. Dependencies: [PASS/FAIL] - [details]
3. Ollama Models: [PASS/FAIL] - [list of working models]
4. API Key: [CONFIGURED/NOT SET]
5. Resource Usage: [details - memory usage]
6. Backend Test: [PASS/FAIL] - [details]

ISSUES FOUND:
- [list any problems encountered]

RECOMMENDATIONS:
- [what should be done next]

NEXT STEPS:
- [based on results, what's ready to proceed]
```

---

## 💡 How to Execute

**Option 1: Manual (Recommended for first time)**
- Copy each task command
- Run in terminal
- Document results
- Compile final report

**Option 2: Automated (Future)**
- Run: `python Scripts/karma_execute_tasks.py`
- Karma executes all tasks automatically
- Generates report

---

## 🚫 Important Rules

1. **Use Ollama ONLY** - Save Claude API quota
2. **Document everything** - Record all outputs
3. **Report errors clearly** - Include full error messages
4. **Suggest fixes** - Use Ollama to analyze problems
5. **Be thorough** - Don't skip tasks

---

## ✅ Success Criteria

**Minimum to proceed**:
- ✅ Health check shows system is healthy
- ✅ Ollama models working
- ✅ No critical errors

**Ideal state**:
- ✅ All dependencies installed
- ✅ API key configured
- ✅ Backend starts successfully
- ✅ All systems green

---

**Cost for all 6 tasks**: $0.00 (100% Ollama)

**Start now and report back!** 🚀
