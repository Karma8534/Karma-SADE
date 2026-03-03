# Karma SADE - Multi-Agent Task Routing
**Goal**: Use the right AI for each task to maximize efficiency and minimize costs

---

## 🎯 Agent Capabilities & Costs

| Agent | Cost | Speed | Best For | Quota |
|-------|------|-------|----------|-------|
| **Ollama** (Local) | FREE | Fast | Code, analysis, simple tasks | Unlimited |
| **Gemini CLI** | FREE | Very Fast | Research, quick answers | ~1500/day |
| **Perplexity** | FREE* | Medium | Web research, citations | ~300/day |
| **ChatGPT** | PAID | Fast | General tasks, code | Your plan |
| **Karma/Claude** | PAID | Medium | Complex reasoning, planning | 500/day MAX |
| **Claude Code** | PAID | Medium | Architecture, debugging | 500/day MAX |

*Free tier limits

---

## 🗺️ Task Routing Decision Tree

```
New Task
    │
    ├─ Needs web research?
    │   ├─ Yes → Perplexity (citations needed) or Gemini CLI (quick facts)
    │   └─ No → Continue
    │
    ├─ Complex architecture/planning?
    │   ├─ Yes → Claude Code (you + me)
    │   └─ No → Continue
    │
    ├─ Code generation/review?
    │   ├─ Yes → Ollama DeepSeek (local) → fallback: ChatGPT
    │   └─ No → Continue
    │
    ├─ System commands/automation?
    │   ├─ Yes → Karma + Ollama (local tools, no AI needed for execution)
    │   └─ No → Continue
    │
    ├─ Simple question/explanation?
    │   ├─ Yes → Ollama Llama3 (FREE) → fallback: Gemini CLI
    │   └─ No → Continue
    │
    └─ Complex reasoning/multi-step?
        └─ Yes → Karma with Claude Sonnet (careful quota use)
```

---

## 📋 Specific Task → Agent Mapping

### **Ollama (Local - ALWAYS TRY FIRST)**
- ✅ Code reviews
- ✅ Code generation (simple)
- ✅ Log analysis
- ✅ Text summarization
- ✅ Simple Q&A
- ✅ Data extraction
- ✅ JSON parsing

**Models to use**:
- `deepseek-coder:6.7b` - Code tasks
- `llama3.1:8b` - General tasks
- `qwen2.5-coder:3b` - Quick code analysis

**How to invoke**:
```bash
# Via Karma or directly
ollama run deepseek-coder "Review this code: [paste]"
ollama run llama3.1 "Explain Docker containers"
```

---

### **Gemini CLI (Free - Second Choice)**
- ✅ Quick research
- ✅ Fact-checking
- ✅ API documentation lookup
- ✅ Technology comparisons
- ✅ Troubleshooting guides

**How to invoke**:
```bash
# Already installed, v0.28.2
gemini "How to configure FastAPI WebSocket"
gemini "Best practices for Python async"
```

**Why use**: Google's knowledge cutoff is newer, free tier is generous

---

### **Perplexity (Research - Third Choice)**
- ✅ Deep research with citations
- ✅ Current events / latest tech
- ✅ Comparative analysis
- ✅ Technical documentation searches

**When to use**: Need authoritative sources with links

**How to use**: Via web interface (Perplexity.ai)

---

### **ChatGPT (Paid - Fourth Choice)**
- ✅ When Ollama can't handle complexity
- ✅ Creative tasks
- ✅ Code generation (medium complexity)
- ✅ Debugging assistance

**Why not first**: Uses your paid quota, Ollama is free and almost as good

---

### **Karma + Claude Sonnet (Expensive - Last Resort)**
- ✅ Complex multi-step reasoning
- ✅ Architectural decisions
- ✅ Advanced problem solving
- ✅ Tool use (browser, system commands)
- ✅ When all else fails

**Quota**: 500 requests/day (save for important tasks!)

---

### **Claude Code (You + Me - Architecture Only)**
- ✅ System architecture planning
- ✅ Complex debugging
- ✅ Multi-file refactoring
- ✅ Infrastructure setup
- ✅ When you need pair programming

**Quota**: 500 requests/day (shared with Karma!)

---

## 🎯 Example Workflows

### **Workflow 1: Code Review**
```
You: "Review this Python script"

Step 1: Ollama DeepSeek (FREE, local)
  → 80% of reviews handled here
  → If complex, proceed to Step 2

Step 2: ChatGPT (Paid but fast)
  → Handles edge cases Ollama misses
  → If STILL stuck, proceed to Step 3

Step 3: Karma + Claude Sonnet (Last resort)
  → Use only for truly complex architectural reviews
```

**Quota saved**: 80% reduction in Claude calls

---

### **Workflow 2: Research**
```
You: "How to implement WebSockets in FastAPI?"

Step 1: Gemini CLI (FREE, fast)
  → gemini "FastAPI WebSocket tutorial"
  → Gets official docs + examples

Step 2 (if needed): Perplexity (FREE, deep)
  → Search: "FastAPI WebSocket best practices 2026"
  → Get latest articles with citations

Step 3 (if still stuck): Karma + Claude
  → Ask for specific implementation help
  → Uses Claude quota ONLY if needed
```

**Quota saved**: 95% of research uses FREE tools

---

### **Workflow 3: System Automation**
```
You: "Create a script to monitor disk usage"

Step 1: Karma with Ollama (FREE)
  → Karma uses local Ollama to generate script
  → Tests locally
  → Deploys if works

Step 2 (if fails): Karma with ChatGPT
  → More robust generation
  → Still cheaper than Claude

Step 3 (only if needed): Claude Code
  → Complex multi-step automation
  → Architectural guidance
```

**Quota saved**: 90% handled without Claude

---

## 🔧 Implementation: Karma Routing Logic

Add to `karma_backend.py`:

```python
# Model routing based on task complexity
def route_to_model(task_description: str, complexity: str = "auto"):
    """
    Route to appropriate model based on task.

    complexity: "simple", "medium", "complex", "auto"
    """

    # Auto-detect complexity
    if complexity == "auto":
        complexity = detect_complexity(task_description)

    if complexity == "simple":
        # Try Ollama first
        models = ["ollama:llama3.1", "gemini-cli", "chatgpt"]

    elif complexity == "medium":
        # Skip Ollama, use faster paid options
        models = ["gemini-cli", "chatgpt", "claude:haiku"]

    elif complexity == "complex":
        # Go straight to Claude
        models = ["claude:sonnet"]

    # Try each model in order
    for model in models:
        try:
            response = call_model(model, task_description)
            if response.quality_check():
                return response
        except:
            continue

    # Fallback to Claude Sonnet
    return call_claude_sonnet(task_description)


def detect_complexity(task: str) -> str:
    """Simple heuristic for task complexity."""

    # Simple keywords
    simple_keywords = ["explain", "what is", "how to", "define", "list"]

    # Complex keywords
    complex_keywords = ["architect", "design", "multi-step", "integrate", "optimize"]

    task_lower = task.lower()

    if any(kw in task_lower for kw in complex_keywords):
        return "complex"
    elif any(kw in task_lower for kw in simple_keywords):
        return "simple"
    else:
        return "medium"
```

---

## 📊 Expected Quota Distribution

### **Before Optimization**
```
Claude Sonnet: 100% of tasks = 50 requests/day
Quota used: 50/500 (10%)
```

### **After Optimization**
```
Ollama:        70% of tasks = 35 tasks (FREE)
Gemini CLI:    15% of tasks = 7.5 tasks (FREE)
ChatGPT:       10% of tasks = 5 tasks (Your plan)
Perplexity:    2% of tasks = 1 task (FREE)
Claude Sonnet: 3% of tasks = 1.5 tasks (PAID)

Quota used: 1.5/500 (0.3%!)
```

**Result**: You can scale up **30x** before hitting limits!

---

## ✅ Quick Setup Checklist

To enable multi-agent routing:

- [ ] Verify Ollama is running: `ollama list`
- [ ] Test Gemini CLI: `gemini "test"`
- [ ] Configure Karma to try Ollama first
- [ ] Add routing logic to karma_backend.py
- [ ] Create shortcut commands for each agent
- [ ] Document which agent for which task type
- [ ] Monitor actual usage patterns
- [ ] Adjust routing based on results

---

## 🎯 Smart Shortcuts

Create these commands for quick access:

```powershell
# Scripts\quick_ai.ps1

function Ask-Ollama {
    param([string]$Question)
    ollama run llama3.1 $Question
}

function Ask-Gemini {
    param([string]$Question)
    gemini $Question
}

function Ask-Karma {
    param([string]$Question)
    # Send to Karma via API
    curl -X POST http://localhost:9400/api/chat -d "{\"message\": \"$Question\"}"
}

# Usage:
# Ask-Ollama "Explain async/await"      # FREE, local
# Ask-Gemini "Latest Python 3.13"       # FREE, Google
# Ask-Karma "Complex architecture Q"    # PAID, use sparingly
```

---

## 🚀 Next Steps

1. **Immediate**: Have Karma execute tasks from `KARMA_TASKS.md` using **Ollama**
2. **Today**: Set up routing logic in karma_backend.py
3. **This week**: Monitor actual usage patterns
4. **Ongoing**: Refine routing based on what works best

**Start with Karma + Ollama for system tasks** → Report results → Optimize from there!

Ready to delegate to Karma? 🎯
