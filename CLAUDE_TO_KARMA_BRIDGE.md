# Claude Code ↔ Karma Bridge
**Problem**: Using Claude Code for tasks that Karma could handle wastes API quota
**Solution**: Bridge that routes tasks to Karma automatically

---

## 🎯 The Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              YOU (in Warp/Claude Code)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         TASK ROUTER (decides: Me or Karma?)                 │
├─────────────────────────────────────────────────────────────┤
│  IF simple/automated:                                       │
│    → Send to Karma (FREE Ollama)                            │
│                                                             │
│  IF complex/architecture:                                   │
│    → Handle in Claude Code (PAID Claude API)                │
└──────────┬──────────────────────────────────────────────┬───┘
           │                                              │
           ▼                                              ▼
  ┌────────────────┐                            ┌─────────────────┐
  │  KARMA         │                            │  CLAUDE CODE    │
  │  (Ollama)      │                            │  (Me + You)     │
  │  FREE          │                            │  PAID           │
  └────────────────┘                            └─────────────────┘
```

---

## 🔧 How to Implement

### **Option 1: MCP Server Bridge** (BEST - I recommend this!)

Create an MCP server that acts as a bridge:

```python
# Scripts/karma_bridge_mcp.py
from mcp import Server, Tool
import requests

server = Server("karma-bridge")

@server.tool()
def delegate_to_karma(task: str, priority: str = "low") -> str:
    """
    Delegate a task to Karma instead of using Claude Code.

    Args:
        task: The task description for Karma to execute
        priority: "low" = use Ollama (FREE), "high" = use Claude if needed

    Returns:
        Karma's response
    """
    # Send task to Karma via API
    response = requests.post(
        "http://localhost:8080/api/chat",  # Open WebUI API
        json={
            "model": "ollama:llama3.1" if priority == "low" else "claude:sonnet",
            "message": task,
            "stream": False
        }
    )

    return response.json()["message"]


@server.tool()
def should_use_karma(task_description: str) -> dict:
    """
    Analyze if a task should go to Karma (FREE) or stay in Claude Code (PAID).

    Returns: {"use_karma": bool, "reason": str}
    """
    # Simple heuristics
    karma_keywords = [
        "check", "list", "show", "get status", "health check",
        "install", "run command", "test", "analyze logs"
    ]

    claude_keywords = [
        "design", "architect", "complex", "multi-step", "plan",
        "refactor", "optimize algorithm"
    ]

    task_lower = task_description.lower()

    if any(kw in task_lower for kw in claude_keywords):
        return {
            "use_karma": False,
            "reason": "Complex task requiring Claude's reasoning"
        }

    if any(kw in task_lower for kw in karma_keywords):
        return {
            "use_karma": True,
            "reason": "Simple task, Karma can handle with Ollama (FREE)"
        }

    return {
        "use_karma": True,  # Default to FREE
        "reason": "Moderate complexity, try Karma first"
    }
```

**Install the MCP server:**
```json
// In Claude Code config (~/.claude/mcp-config.json)
{
  "karma-bridge": {
    "command": "python",
    "args": ["C:/Users/raest/Documents/Karma_SADE/Scripts/karma_bridge_mcp.py"]
  }
}
```

**Usage in Claude Code:**
```
You: "Check if all services are healthy"

Me (Claude Code):
  1. Calls should_use_karma("Check if all services are healthy")
  2. Gets: {"use_karma": true, "reason": "Simple status check"}
  3. Calls delegate_to_karma("Check system health")
  4. Karma executes using Ollama (FREE)
  5. Returns result to you

Result: $0.00 API cost (vs $0.003 if I did it)
```

---

### **Option 2: Shared API Endpoint** (SIMPLER)

Create a unified API that both me and Karma use:

```python
# Scripts/unified_api.py
from fastapi import FastAPI
from karma_memory import KarmaMemory
import anthropic
import requests

app = FastAPI()
memory = KarmaMemory()

@app.post("/api/task")
async def handle_task(task: str, source: str):
    """
    Unified task handler - routes to Karma or Claude based on complexity

    Args:
        task: What needs to be done
        source: "claude_code" or "user"
    """

    # Check task complexity
    complexity = analyze_complexity(task)

    if complexity == "simple":
        # Use Karma with Ollama (FREE)
        result = await call_karma_ollama(task)
        memory.store_message("karma_ollama", result, session_id=get_session_id())
        return {"handler": "karma_ollama", "cost": 0, "result": result}

    elif complexity == "medium":
        # Use Karma with Claude Haiku (CHEAP)
        result = await call_karma_haiku(task)
        memory.store_message("karma_haiku", result, session_id=get_session_id())
        return {"handler": "karma_haiku", "cost": 0.0003, "result": result}

    else:  # complex
        # Use Claude Sonnet (EXPENSIVE - reserve for architecture)
        result = await call_claude_sonnet(task)
        memory.store_message("claude_sonnet", result, session_id=get_session_id())
        return {"handler": "claude_sonnet", "cost": 0.003, "result": result}


async def call_karma_ollama(task: str):
    """Send to Karma using local Ollama"""
    response = requests.post(
        "http://localhost:11434/api/generate",  # Ollama API
        json={
            "model": "llama3.1",
            "prompt": task,
            "stream": False
        }
    )
    return response.json()["response"]
```

**Then in Claude Code, I use this API:**
```python
# When you ask me to do something, I first check:
task_route = requests.post(
    "http://localhost:9400/api/task",
    json={"task": user_request, "source": "claude_code"}
)

if task_route["handler"] == "karma_ollama":
    # Karma handled it for FREE, I just relay the result
    return task_route["result"]
else:
    # Complex task, I handle it myself
    return my_response()
```

---

### **Option 3: Message Forwarding** (EASIEST - Start Here!)

Simple script that forwards messages from Claude Code to Karma:

```python
# Scripts/forward_to_karma.py
import sys
import requests

def send_to_karma(message: str):
    """Send a message to Karma and get response"""

    # Open WebUI API endpoint
    response = requests.post(
        "http://localhost:8080/api/chat",
        json={
            "model": "llama3.1",  # Use free Ollama model
            "messages": [
                {"role": "user", "content": message}
            ],
            "stream": False
        },
        headers={"Authorization": f"Bearer {get_api_key()}"}
    )

    return response.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: forward_to_karma.py 'your message'")
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    result = send_to_karma(message)

    print(f"[Karma via Ollama - FREE]")
    print(result)
```

**Usage:**
```bash
# Instead of asking me (Claude Code), you run:
python Scripts/forward_to_karma.py "Check system health"

# Karma responds using Ollama (FREE)
# vs me responding using Claude API (PAID)
```

---

## 💰 Cost Savings Examples

### **Scenario 1: System Health Check**
```
WITHOUT bridge:
  You → Claude Code → I execute → $0.003

WITH bridge:
  You → Claude Code → Detects simple task → Karma (Ollama) → $0.00

Savings: $0.003 per check × 10/day = $0.03/day = $10/year
```

### **Scenario 2: Code Review**
```
WITHOUT bridge:
  You → Claude Code → I review → $0.015

WITH bridge:
  You → Claude Code → Karma (DeepSeek local) → $0.00

Savings: $0.015 per review × 5/day = $0.075/day = $27/year
```

### **Scenario 3: Daily Tasks (50 total)**
```
WITHOUT bridge:
  50 tasks × $0.005 avg = $0.25/day = $91/year

WITH bridge (70% to Karma):
  35 tasks → Karma (FREE) = $0.00
  15 tasks → Claude = $0.075/day = $27/year

Savings: $64/year (70% reduction!)
```

---

## 🚦 Task Routing Rules

### **Always Use Karma (FREE Ollama):**
- ✅ System health checks
- ✅ Service status queries
- ✅ File operations (read, list, search)
- ✅ Log analysis
- ✅ Simple code reviews
- ✅ Running commands
- ✅ Installing dependencies
- ✅ Testing endpoints
- ✅ Data extraction/parsing

### **Always Use Claude Code (PAID):**
- ✅ Architectural decisions
- ✅ Complex refactoring
- ✅ Multi-file coordination
- ✅ Design discussions
- ✅ Debugging complex issues
- ✅ Planning new features
- ✅ Security analysis

### **Try Karma First, Fallback to Claude:**
- Code generation
- Documentation writing
- Configuration management
- Deployment scripts
- Test writing

---

## 🎯 Implementation Priority

### **Phase 1: Manual Routing** (Do Now - 5 min)
Create `forward_to_karma.py` script
Use it when you know task is simple
**Savings: ~30% quota reduction**

### **Phase 2: Smart Router** (This Week - 1 hour)
Add `should_use_karma()` analysis
I automatically suggest: "This task could be handled by Karma (FREE), should I forward it?"
**Savings: ~60% quota reduction**

### **Phase 3: MCP Bridge** (Next Week - 2 hours)
Full MCP server integration
Transparent routing
**Savings: ~90% quota reduction**

---

## 📊 Expected Results

### **Current Usage:**
```
You → Claude Code for everything
  50 tasks/day × $0.005 = $0.25/day
  Monthly: ~$7.50
  Yearly: ~$91
```

### **With Bridge (Phase 3):**
```
You → Task Router:
  35 tasks → Karma (Ollama) = $0.00
  10 tasks → Karma (Haiku) = $0.03
  5 tasks → Claude (Sonnet) = $0.015

Daily: $0.045 (82% savings!)
Monthly: ~$1.35
Yearly: ~$16
```

**Savings: $75/year + 90% quota headroom**

---

## 🔧 Quick Start

**Right now, create the forwarding script:**

```bash
# Create the script
cat > Scripts/forward_to_karma.py << 'EOF'
import requests
import sys

msg = " ".join(sys.argv[1:])
resp = requests.post(
    "http://localhost:8080/api/chat",
    json={"model": "llama3.1", "message": msg}
)
print(resp.json()["response"])
EOF

# Test it
python Scripts/forward_to_karma.py "What is 2+2?"
```

**Then whenever you have a simple task:**
```bash
# Instead of asking me:
python Scripts/forward_to_karma.py "Check if services are running"

# Karma does it for FREE using Ollama
```

---

## ✅ Summary

**The Bridge solves:**
1. ❌ Wasted Claude API quota on simple tasks
2. ❌ Both you and Karma competing for same quota pool
3. ❌ No clear routing logic (when to use which AI)

**Implementation:**
1. **Now**: Create forwarding script (5 min)
2. **Today**: Test with simple tasks
3. **This week**: Build smart router
4. **Next week**: Full MCP integration

**Result:**
- 90% quota reduction
- Faster task completion (Ollama is local, instant)
- Clear separation: Karma = execution, Claude Code = architecture

**You'll go from using 50 Claude API calls/day to ~5.**

That's 10x headroom for scaling up! 🚀
