# 🤖 Handoff Package for Karma
**Date**: 2026-02-12
**From**: Claude Code (Architecture Agent)
**To**: Karma (Execution Agent)
**Goal**: Execute system tasks using LOCAL models (Ollama) to save Claude API quota

---

## 🎯 Your Mission, Karma

Neo has upgraded to Claude MAX plan and needs to conserve API quota. You will execute these tasks using **Ollama** (local, FREE) instead of Claude API.

**Key Rule**: Use `ollama run llama3.1` or `ollama run deepseek-coder` for ALL tasks below. DO NOT use Claude API unless a task explicitly requires it.

---

## ✅ Task List (Execute with Ollama)

### **Task 1: System Health Check**
**Command**:
```powershell
cd C:\Users\raest\Documents\Karma_SADE\Scripts
.\karma_health_check.ps1
```

**What to report**:
- Overall system status (HEALTHY/WARNING/CRITICAL)
- Which services are running
- Any errors or warnings
- Memory usage of Karma SADE components

**Use Ollama to analyze**: If there are errors, ask Ollama to interpret them:
```bash
ollama run llama3.1 "Analyze this error and suggest fix: [paste error]"
```

---

### **Task 2: Install Backend Dependencies**
**Command**:
```bash
pip install fastapi uvicorn anthropic websockets python-multipart
```

**Expected output**: "Successfully installed..." for each package

**If errors**, use Ollama to troubleshoot:
```bash
ollama run llama3.1 "Python pip install failed with: [error]. How to fix?"
```

**Verify installation**:
```bash
pip list | grep -E "fastapi|uvicorn|anthropic|websockets"
```

---

### **Task 3: Test Ollama Models**
Verify all local models work:
```bash
ollama list
ollama run llama3.1 "Hello, test message"
ollama run deepseek-coder "Write a simple Python hello world"
ollama run qwen2.5-coder:3b "Explain async/await in Python"
```

**Report**:
- Which models are installed
- Which models respond correctly
- Any models that error

---

### **Task 4: Check API Key Configuration**
**Check if Claude API key is set**:
```powershell
$env:ANTHROPIC_API_KEY
```

**If NOT set**, check secrets manager:
```powershell
cd C:\Users\raest\Documents\Karma_SADE\Scripts
.\karma_secrets.ps1 -Action list
```

**Report**:
- Is ANTHROPIC_API_KEY set? (YES/NO)
- Are any keys stored in secrets manager?

**DO NOT reveal the actual key values!**

---

### **Task 5: Resource Usage Analysis**
**Get current resource usage**:
```powershell
# Memory usage of key processes
Get-Process | Where-Object {$_.WorkingSet -gt 100MB} |
    Select-Object Name,Id,@{Name="MemoryMB";Expression={[math]::Round($_.WorkingSet/1MB,2)}} |
    Sort-Object MemoryMB -Descending |
    Format-Table

# Check if Open WebUI is running
Get-Process | Where-Object {$_.ProcessName -like "*open-webui*"}

# Check if Cockpit is running
Get-Process python | Where-Object {$_.Id -eq 25096}
```

**Use Ollama to analyze**:
```bash
ollama run llama3.1 "Based on this process list, what's using the most resources: [paste output]"
```

**Report**:
- Total memory used by Karma SADE
- Is Open WebUI running? (we want to stop it)
- Is Cockpit running on PID 25096?
- Recommendations for optimization

---

### **Task 6: Test New Backend (Dry Run)**
**Try starting the new backend**:
```bash
cd C:\Users\raest\Documents\Karma_SADE\Scripts
python karma_backend.py
```

**Expected**:
```
Karma SADE Backend v2.0
Dashboard: http://localhost:9400
...
```

**If it starts**: Press Ctrl+C to stop it (we'll configure properly later)

**If errors**: Use Ollama to diagnose:
```bash
ollama run deepseek-coder "Python error when starting FastAPI: [paste error]. How to fix?"
```

**Report**:
- Did it start? (YES/NO)
- Any errors? (paste them)
- Port conflicts? (check if something is already on 9400)

---

### **Task 7: Analyze Dashboard Code**
**Use Ollama to review the dashboard**:
```bash
# Read the current dashboard
cat C:\Users\raest\Documents\Karma_SADE\Dashboard\index.html

# Ask Ollama to analyze it
ollama run deepseek-coder "Analyze this HTML dashboard code and suggest where to add a chat panel: [paste first 100 lines]"
```

**Report**:
- Current dashboard structure
- Ollama's suggestions for adding chat panel
- Any issues in existing code

---

### **Task 8: Test Cockpit Dashboard Endpoint**
**Check if dashboard loads**:
```bash
curl http://localhost:9400/dashboard
```

**Expected**: HTML content (the dashboard)

**If 404 or error**, check Cockpit logs:
```bash
tail -50 C:\Users\raest\Documents\Karma_SADE\Logs\cockpit-service.log
```

**Report**:
- Does dashboard load? (YES/NO)
- Any errors in logs?
- Current Cockpit status

---

## 📊 Final Report Format

When you complete all tasks, provide this summary:

```markdown
# Karma Task Completion Report
**Date**: [timestamp]
**Agent**: Karma (using Ollama local models)
**API Calls Used**: 0 Claude calls (all local!)

## Task Results

### ✅ Task 1: System Health
- Status: [HEALTHY/WARNING/CRITICAL]
- Services Running: [list]
- Issues: [list or "None"]

### ✅ Task 2: Dependencies
- Status: [INSTALLED/FAILED]
- Missing: [list or "None"]

### ✅ Task 3: Ollama Models
- Working Models: [list]
- Failed Models: [list or "None"]

### ✅ Task 4: API Keys
- Claude Key Set: [YES/NO]
- Secrets Configured: [YES/NO]

### ✅ Task 5: Resources
- Open WebUI: [RUNNING/STOPPED]
- Cockpit: [RUNNING/STOPPED]
- Total Memory: [X MB]

### ✅ Task 6: Backend Test
- Started: [YES/NO]
- Errors: [list or "None"]

### ✅ Task 7: Dashboard Analysis
- Ollama Suggestions: [summary]

### ✅ Task 8: Dashboard Endpoint
- Loads: [YES/NO]
- Issues: [list or "None"]

## 🎯 Recommendations

Based on analysis using Ollama (local AI):

1. [First recommendation]
2. [Second recommendation]
3. [Blockers or issues Neo needs to resolve]

## 📈 Next Steps

Suggested order:
1. [What to do first]
2. [What to do second]
3. [What can wait]

## 💰 Quota Impact

- Claude API calls used: **0** ✅
- Ollama calls used: ~20 (FREE, local)
- Total cost: **$0.00**

---

**Ready for next phase!** ✅
```

---

## 🔧 How to Execute This (Instructions for Karma)

### **Method 1: Via Open WebUI (Current)**
1. Open http://localhost:8080
2. Copy each task command
3. Execute using tools
4. Ask Ollama to analyze outputs
5. Compile final report

### **Method 2: Via Terminal (Direct)**
1. Open PowerShell
2. Run commands manually
3. Use Ollama CLI for analysis
4. Document results in report

### **Method 3: Via Script (Automated)**
Create a script that runs all tasks and uses Ollama to analyze results.

---

## ⚠️ Important Notes

1. **Use Ollama FIRST** - Don't use Claude API unless absolutely stuck
2. **Save outputs** - Copy all command outputs for the report
3. **Be thorough** - If something fails, investigate why
4. **Ask Ollama** - Use local AI to interpret errors and suggest fixes
5. **Document everything** - Neo needs the report to plan next steps

---

## 🎯 Success Criteria

You've succeeded when:
- ✅ All 8 tasks attempted
- ✅ Results documented in report format
- ✅ Used 0 Claude API calls (all Ollama)
- ✅ Identified any blockers for Neo
- ✅ Provided clear next steps

---

## 💡 Example Ollama Usage

**Good (use Ollama)**:
```bash
# Analyze error
ollama run llama3.1 "This error appeared: ModuleNotFoundError: No module named 'fastapi'. What does it mean?"

# Review code
ollama run deepseek-coder "Review this Python code for issues: [paste code]"

# Generate solution
ollama run llama3.1 "How to install FastAPI on Windows?"
```

**Bad (wastes quota)**:
```bash
# DON'T DO THIS - uses Claude API
Ask Karma via Open WebUI: "What does this error mean?"
```

---

## 🚀 Ready to Start?

Execute tasks **in order** and compile the final report. Use Ollama for ALL analysis to save Neo's Claude API quota.

**Go forth and automate!** 🤖
