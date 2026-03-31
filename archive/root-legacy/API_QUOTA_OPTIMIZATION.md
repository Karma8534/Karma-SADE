# Claude API Quota Optimization Guide
**Plan**: MAX - Daily Limits
**Goal**: Stay under limits while maximizing Karma's capabilities

---

## 📊 Your Current MAX Plan Limits (Estimated)

| Model | Daily Limit | Token Estimate |
|-------|-------------|----------------|
| Claude Sonnet 4 | ~500 requests | ~2M tokens/day |
| Claude Opus 4 | ~100 requests | ~500K tokens/day |
| Claude Haiku 4 | ~2000 requests | ~5M tokens/day |

**Current Usage Split**:
- 🔴 **You + Me** (Warp/Claude Code): Uses Sonnet 4
- 🔴 **Karma** (Open WebUI): Uses Sonnet 4
- **Problem**: We're both using the same pool!

---

## 🎯 Optimization Strategy

### **1. Agent Division of Labor**

```
┌─────────────────────────────────────────────────────┐
│              TASK ROUTING LOGIC                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Simple/Repetitive → Karma (Ollama local)          │
│  Research/Analysis → Karma (Haiku - cheaper)       │
│  Code Generation   → Karma (Sonnet)                │
│  Complex Planning  → Claude Code (You + me)        │
│  Architecture      → Claude Code (You + me)        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### **2. Use Local Models First**

You already have **Ollama with 6 models**:
- `llama3.1:8b` - Good for general tasks
- `qwen2.5-coder:3b` - Code analysis
- `deepseek-coder:6.7b` - Code generation
- `llama3-groq-tool-use:8b` - Tool calling

**Strategy**:
```python
# Configure Karma to try local first
karma_config = {
    "model_fallback": [
        "ollama:llama3.1",      # Try local first (FREE)
        "groq:llama3-groq",     # Groq API (FREE tier)
        "claude:haiku",         # Cheap Claude (if needed)
        "claude:sonnet"         # Expensive (last resort)
    ]
}
```

### **3. Conversation Caching**

Enable prompt caching in `karma_backend.py`:
```python
# Add to Claude API calls
response = claude_client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=messages,
    system=[{
        "type": "text",
        "text": system_prompt,
        "cache_control": {"type": "ephemeral"}  # Cache this!
    }]
)
```

**Savings**: Up to 90% on repeated system prompts

### **4. Smart Context Management**

```python
# Don't send full conversation every time
# Only send last N messages + summary

def prepare_context(conversation, max_recent=10):
    if len(conversation) <= max_recent:
        return conversation

    # Summarize old messages
    old_messages = conversation[:-max_recent]
    summary = summarize(old_messages)  # Use cheap model

    recent = conversation[-max_recent:]

    return [
        {"role": "system", "content": f"Previous context: {summary}"},
        *recent
    ]
```

**Savings**: 50-70% reduction in input tokens

---

## 🚀 Immediate Actions to Save Quota

### **Action 1: Configure Karma to Use Ollama**

Edit Karma's model in Open WebUI:
1. Go to Settings → Models
2. Add Ollama models as primary
3. Set Claude as fallback only

**OR** if using new backend:
```python
# karma_backend.py - line ~80
# Add model routing logic

async def get_response(message, priority="low"):
    if priority == "low":
        # Try Ollama first
        try:
            return await ollama_client.generate(message)
        except:
            pass

    # Fallback to Claude
    return await claude_client.messages.create(...)
```

### **Action 2: Batch Non-Urgent Tasks**

Instead of asking Karma questions one-by-one:
```
❌ BAD (10 API calls):
You: "Check service 1"
Karma: [response]
You: "Check service 2"
Karma: [response]
...
```

Do this:
```
✅ GOOD (1 API call):
You: "Check all services and give me a summary report"
Karma: [comprehensive response]
```

### **Action 3: Enable Response Streaming + Stop**

```javascript
// In dashboard, add "Stop" button
let currentStream = null;

function stopGeneration() {
    if (currentStream) {
        currentStream.abort();  // Stop mid-response if you got enough
    }
}
```

**Savings**: Don't pay for tokens you don't need

### **Action 4: Use Groq for Speed Tasks**

Groq API is **FREE** and **blazing fast**:
```python
# Add to karma_backend.py
from groq import Groq

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# For quick tasks
def quick_response(message):
    return groq_client.chat.completions.create(
        model="llama3-groq-70b-8192-tool-use-preview",
        messages=[{"role": "user", "content": message}]
    )
```

**Use for**:
- Code reviews
- Summarization
- Simple Q&A
- Log analysis

---

## 📈 Monitoring Quota Usage

### **Create Daily Usage Dashboard**

```python
# Scripts/quota_monitor.py
import anthropic
import json
from datetime import datetime

client = anthropic.Anthropic()

def check_usage():
    # Get usage from Anthropic dashboard API
    # (if available, otherwise track locally)

    usage_log = {
        "date": datetime.now().date().isoformat(),
        "requests_today": get_request_count(),
        "tokens_today": get_token_count(),
        "limit": 500,  # Your daily limit
        "remaining": 500 - get_request_count()
    }

    # Save to file
    with open("~/karma/usage.json", "w") as f:
        json.dump(usage_log, f)

    # Alert if > 80%
    if usage_log["remaining"] < 100:
        print("⚠️  WARNING: Only 100 requests left today!")

if __name__ == "__main__":
    check_usage()
```

Run via scheduled task:
```powershell
# Every hour
schtasks /create /tn "KarmaSADE-QuotaCheck" /tr "python Scripts\quota_monitor.py" /sc hourly
```

### **Add Quota Display to Dashboard**

In your dashboard HTML, add:
```javascript
// Fetch and display current usage
fetch('/api/quota')
    .then(r => r.json())
    .then(data => {
        document.getElementById('quota').innerHTML = `
            ${data.remaining}/${data.limit} requests left today
            (${Math.round(data.remaining/data.limit*100)}%)
        `;
    });
```

---

## 🎛️ Model Selection Strategy

| Task Type | First Try | Fallback | Last Resort |
|-----------|-----------|----------|-------------|
| Code review | Ollama DeepSeek | Groq Llama3 | Claude Haiku |
| Simple Q&A | Ollama Llama3 | Groq | Claude Haiku |
| Code generation | Ollama DeepSeek | Claude Haiku | Claude Sonnet |
| Complex reasoning | Groq Llama3 | Claude Sonnet | Claude Opus |
| System commands | Local (no LLM) | N/A | N/A |
| Log parsing | Ollama Qwen | Groq | Claude Haiku |
| Architecture planning | Claude Sonnet | Claude Opus | (skip task) |

**Key Insight**: 80% of tasks can be done with **FREE** models (Ollama + Groq)

---

## 💰 Cost Breakdown (Estimated)

### **Current Usage (Before Optimization)**
```
Assumptions:
- 50 conversations/day
- Average 500 tokens per request
- All using Sonnet 4

Cost:
- Input: 50 * 200 tokens = 10K tokens = $0.03
- Output: 50 * 500 tokens = 25K tokens = $0.15
Total: ~$0.18/day = $5.40/month
```

### **Optimized Usage (After)**
```
Split:
- 30 tasks → Ollama (FREE)
- 15 tasks → Groq (FREE)
- 5 tasks → Claude Haiku ($0.01)
- 2 tasks → Claude Sonnet ($0.10)

Total: ~$0.11/day = $3.30/month

Savings: 40% reduction
```

### **Request Count Optimization**
```
Before: 50 Claude requests/day
After: 7 Claude requests/day (86% reduction!)

Remaining quota: 493/500 per day
You can scale up 70x before hitting limits!
```

---

## 🔥 Emergency Quota Management

If you hit 80% of daily limit:

### **Fallback Plan**
```python
# Auto-switch to cheaper models
def get_model_for_quota(remaining_requests):
    if remaining_requests < 50:
        return "ollama:llama3.1"  # FREE
    elif remaining_requests < 100:
        return "groq:llama3-groq"  # FREE
    elif remaining_requests < 200:
        return "claude-haiku"  # Cheap
    else:
        return "claude-sonnet"  # Normal
```

### **Pause Non-Essential**
```python
# Disable auto-features when quota low
if quota_remaining < 100:
    disable_proactive_monitoring()
    disable_auto_suggestions()
    # Only respond to direct queries
```

---

## 🎯 Recommended Configuration

Create `~/karma/config.json`:
```json
{
  "model_routing": {
    "primary": "ollama:llama3.1",
    "code": "ollama:deepseek-coder",
    "fast": "groq:llama3-groq",
    "smart": "claude:sonnet",
    "fallback": "claude:haiku"
  },
  "quota_management": {
    "daily_limit": 500,
    "alert_threshold": 0.8,
    "emergency_mode_at": 0.9,
    "cache_responses": true,
    "max_context_messages": 10
  },
  "features": {
    "proactive_monitoring": true,
    "auto_suggestions": true,
    "disable_when_quota_low": true
  }
}
```

---

## ✅ Action Checklist

To maximize your MAX plan:

- [ ] Configure Karma to use Ollama as primary model
- [ ] Add Groq API as secondary fallback
- [ ] Enable prompt caching in Claude calls
- [ ] Implement conversation context windowing
- [ ] Set up quota monitoring dashboard
- [ ] Create model routing logic (local → Groq → Claude)
- [ ] Batch related queries together
- [ ] Add "Stop generation" button to UI
- [ ] Configure auto-fallback when quota low
- [ ] Schedule hourly quota checks
- [ ] Document which tasks should use which models

---

## 🚀 Bottom Line

**With optimization**:
- Use Claude API for **<10% of tasks**
- Use FREE models for **90% of tasks**
- Stay at **~15% of daily quota** for normal usage
- **6-7x headroom** for burst activity

**Your MAX plan becomes** effectively unlimited for your personal use!

---

**Next Step**: Have Karma execute the tasks in `KARMA_TASKS.md` using **Ollama** (not Claude) to test the optimization. Report back results here.
