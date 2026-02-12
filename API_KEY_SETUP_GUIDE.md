# API Key Setup Guide - Step by Step
**Goal**: Set ANTHROPIC_API_KEY permanently for Karma backend
**Time**: 2 minutes

---

## 🔑 Step-by-Step Instructions

### **Step 1: Open PowerShell**
- Press `Win + X`
- Click "Windows PowerShell" or "Terminal"

---

### **Step 2: Set the API Key (Choose ONE method)**

#### **Method A: Permanent User Variable (RECOMMENDED)**
```powershell
# Replace 'your-actual-api-key-here' with your real key
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "your-actual-api-key-here", "User")
```

**Pros**: Permanent, survives reboots, works for all future PowerShell sessions

---

#### **Method B: Current Session Only (Quick Test)**
```powershell
$env:ANTHROPIC_API_KEY = "your-actual-api-key-here"
```

**Pros**: Immediate, good for testing
**Cons**: Lost when you close PowerShell

---

### **Step 3: Verify It's Set**

```powershell
# Check the value (should show your key)
$env:ANTHROPIC_API_KEY

# Or check length (should show a number like 108)
$env:ANTHROPIC_API_KEY.Length
```

**Expected output**: Should show your API key or its length

---

### **Step 4: Restart PowerShell (if using Method A)**

```powershell
# Close and reopen PowerShell, then verify again:
$env:ANTHROPIC_API_KEY
```

If it shows your key → SUCCESS! ✅

---

### **Step 5: Test with Python**

```powershell
python -c "import os; print('API Key set:', 'ANTHROPIC_API_KEY' in os.environ)"
```

**Expected output**: `API Key set: True`

---

## 🔒 Security Notes

**DON'T**:
- ❌ Commit API key to Git
- ❌ Share in screenshots
- ❌ Paste in public channels

**DO**:
- ✅ Use environment variables (what we're doing)
- ✅ Keep backup in password manager
- ✅ Rotate periodically

---

## 🐛 Troubleshooting

### Problem: "Variable not found after restart"
**Solution**: Use Method A again, make sure to close ALL PowerShell windows

### Problem: "Python can't see the variable"
**Solution**: Restart PowerShell after setting the variable

### Problem: "I need to check if it's already set"
```powershell
# Check registry
Get-ItemProperty -Path "HKCU:\Environment" -Name ANTHROPIC_API_KEY
```

---

## 📋 Quick Reference

```powershell
# SET (permanent)
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")

# CHECK
$env:ANTHROPIC_API_KEY

# REMOVE (if needed)
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $null, "User")
```

---

## ✅ Next Steps After Setup

Once API key is configured:

1. **Test the backend**:
   ```bash
   python Scripts/karma_backend.py
   ```

2. **Verify health endpoint**:
   ```bash
   curl http://localhost:9400/health
   ```

3. **Proceed to unified dashboard** build

---

**Ready? Copy Method A command, replace with your key, paste in PowerShell!** 🚀
