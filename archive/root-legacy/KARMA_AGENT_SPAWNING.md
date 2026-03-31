# Karma Agent Spawning System
**Goal**: Karma can create and manage sub-agents for parallel task execution
**Status**: Architecture designed, ready to implement

---

## 🎯 Vision: Karma as Agent Orchestrator

```
                    ┌─────────────────┐
                    │      YOU        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  KARMA (Main)   │
                    │  Orchestrator   │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    ┌─────────┐         ┌─────────┐        ┌─────────┐
    │ Agent 1 │         │ Agent 2 │        │ Agent 3 │
    │  Task:  │         │  Task:  │        │  Task:  │
    │ Monitor │         │ Backup  │        │ Deploy  │
    └─────────┘         └─────────┘        └─────────┘
```

---

## 🚀 How Karma Spawns Agents

### **Architecture: MCP Agent Framework**

Karma can spawn agents using:
1. **Claude Agent SDK** (for complex reasoning agents)
2. **Ollama Workers** (for simple execution agents - FREE)
3. **Playwright Agents** (for browser automation agents)

### **Example: Karma Spawns 3 Agents in Parallel**

```python
# In karma_backend.py

from claude_agent_sdk import Agent, AgentPool

class KarmaOrchestrator:
    """Main Karma that can spawn and manage sub-agents"""

    def __init__(self):
        self.agent_pool = AgentPool(max_workers=10)
        self.active_agents = {}

    async def handle_complex_task(self, task: str):
        """
        Analyze task and decide if it needs multiple agents
        """
        # Karma analyzes: "This needs 3 parallel tasks"
        subtasks = self.decompose_task(task)

        if len(subtasks) > 1:
            # Spawn multiple agents
            agents = []
            for i, subtask in enumerate(subtasks):
                agent = self.spawn_agent(
                    name=f"SubAgent-{i}",
                    task=subtask,
                    model="ollama:llama3.1"  # FREE for simple tasks
                )
                agents.append(agent)

            # Wait for all agents to complete
            results = await asyncio.gather(*[a.execute() for a in agents])

            # Karma synthesizes results
            return self.synthesize_results(results)
        else:
            # Single task, Karma handles directly
            return await self.execute(task)

    def spawn_agent(self, name: str, task: str, model: str):
        """
        Create a new agent instance
        """
        agent = Agent(
            name=name,
            model=model,
            tools=self.get_tools_for_task(task),
            system_prompt=f"You are {name}, focused on: {task}"
        )

        self.active_agents[name] = agent
        return agent

    def get_tools_for_task(self, task: str):
        """
        Give agent only the tools it needs
        """
        if "browser" in task.lower():
            return ["playwright_browser", "screenshot"]
        elif "file" in task.lower():
            return ["read_file", "write_file", "edit_file"]
        elif "system" in task.lower():
            return ["bash", "powershell"]
        else:
            return ["bash"]  # Default
```

---

## 🎬 Real-World Example

### **Scenario: You ask Karma to "Deploy the new dashboard"**

**Karma's Response:**
```
Karma: "I'll spawn 3 agents to handle this in parallel:
  - Agent-1: Run tests
  - Agent-2: Build production bundle
  - Agent-3: Backup current version

Spawning agents now..."
```

**What happens:**
```python
# Karma decomposes task
subtasks = [
    "Run pytest and report results",
    "Build dashboard with npm run build",
    "Backup current dashboard to ~/backups/"
]

# Spawn 3 agents using Ollama (FREE)
agent1 = karma.spawn_agent("TestRunner", subtasks[0], "ollama:llama3.1")
agent2 = karma.spawn_agent("Builder", subtasks[1], "ollama:deepseek-coder")
agent3 = karma.spawn_agent("BackupAgent", subtasks[2], "ollama:llama3.1")

# Execute in parallel
results = await asyncio.gather(
    agent1.execute(),
    agent2.execute(),
    agent3.execute()
)

# Karma reports back
Karma: """
✅ All agents completed:
  - TestRunner: All 47 tests passed
  - Builder: Production bundle created (2.3MB)
  - BackupAgent: Backup saved to ~/backups/dashboard-2026-02-12.tar.gz

Ready to deploy. Should I proceed?
"""
```

**Total Cost**: $0.00 (all agents used Ollama)

**Time Saved**: 3x faster (parallel execution)

---

## 🔧 Implementation Levels

### **Level 1: Simple Worker Pool** (Easiest - Start Here)
Karma uses Python `multiprocessing` to run tasks in parallel:

```python
# karma_workers.py
from multiprocessing import Pool
import subprocess

def run_task(task):
    """Execute a task using Ollama"""
    result = subprocess.run(
        ["ollama", "run", "llama3.1", task],
        capture_output=True,
        text=True
    )
    return result.stdout

# Karma spawns workers
with Pool(processes=3) as pool:
    tasks = [
        "Check disk usage",
        "Check memory usage",
        "Check running services"
    ]
    results = pool.map(run_task, tasks)

# All 3 tasks run in parallel, FREE
```

**Benefits**: Simple, no dependencies, works now
**Limitations**: No tool use, no complex reasoning

---

### **Level 2: Ollama Multi-Agent** (Medium Complexity)
Each agent is an Ollama instance with specific role:

```python
# karma_ollama_agents.py
import requests
import asyncio

class OllamaAgent:
    """Simple agent using Ollama"""

    def __init__(self, name, role, model="llama3.1"):
        self.name = name
        self.role = role
        self.model = model

    async def execute(self, task):
        """Execute task using Ollama"""
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": self.model,
                "prompt": f"Role: {self.role}\nTask: {task}",
                "stream": False
            }
        )
        return response.json()["response"]

# Karma creates specialized agents
monitor_agent = OllamaAgent("Monitor", "System monitoring expert")
backup_agent = OllamaAgent("Backup", "Backup and recovery specialist")
deploy_agent = OllamaAgent("Deploy", "Deployment automation expert")

# Run in parallel
tasks = [
    monitor_agent.execute("Check system health"),
    backup_agent.execute("Backup database"),
    deploy_agent.execute("Deploy new version")
]

results = await asyncio.gather(*tasks)
```

**Benefits**: Role specialization, parallel execution, FREE
**Limitations**: No tool use yet

---

### **Level 3: Claude Agent SDK** (Full Power - Recommended)
Use official Claude Agent SDK for full agent capabilities:

```python
# karma_claude_agents.py
from anthropic import Anthropic
import asyncio

class ClaudeSubAgent:
    """Full-featured agent using Claude SDK"""

    def __init__(self, name, tools, model="claude-sonnet-4"):
        self.name = name
        self.client = Anthropic()
        self.tools = tools
        self.model = model

    async def execute(self, task):
        """Execute task with tool use"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            tools=self.tools,
            messages=[
                {"role": "user", "content": task}
            ]
        )

        # Handle tool calls
        if response.stop_reason == "tool_use":
            # Execute tools and continue
            return await self.handle_tool_calls(response)

        return response.content[0].text

# Karma spawns agents with specific tools
browser_agent = ClaudeSubAgent(
    name="BrowserAgent",
    tools=[playwright_tool, screenshot_tool],
    model="claude-haiku-4"  # Cheaper for simple tasks
)

system_agent = ClaudeSubAgent(
    name="SystemAgent",
    tools=[bash_tool, read_file_tool],
    model="claude-haiku-4"
)

# Execute in parallel
results = await asyncio.gather(
    browser_agent.execute("Navigate to dashboard and screenshot"),
    system_agent.execute("Check system logs for errors")
)
```

**Benefits**: Full tool use, complex reasoning, proper error handling
**Cost**: Uses Claude API (but can use Haiku for cheaper)

---

## 💡 Smart Agent Spawning Strategy

### **Karma's Decision Tree:**

```
New Task Received
    │
    ├─ Can it be parallelized?
    │   ├─ YES → Spawn multiple agents
    │   └─ NO → Handle directly
    │
    ├─ Complexity level?
    │   ├─ Simple → Use Ollama agents (FREE)
    │   ├─ Medium → Use Haiku agents (CHEAP)
    │   └─ Complex → Use Sonnet agents (EXPENSIVE)
    │
    └─ Tools needed?
        ├─ Browser → Spawn Playwright agent
        ├─ System → Spawn Bash agent
        ├─ Files → Spawn File agent
        └─ Research → Spawn Research agent
```

---

## 📊 Cost Comparison

### **Without Agent Spawning:**
```
You: "Deploy dashboard, run tests, backup DB, check logs"

Karma (single agent):
  1. Run tests (2 min)
  2. Build (1 min)
  3. Backup (1 min)
  4. Check logs (1 min)

Total: 5 minutes sequential
Cost: $0.003 (one Claude call)
```

### **With Agent Spawning:**
```
You: "Deploy dashboard, run tests, backup DB, check logs"

Karma (spawns 4 agents):
  Agent-1: Run tests      } All
  Agent-2: Build          } in
  Agent-3: Backup DB      } parallel
  Agent-4: Check logs     }

Total: 2 minutes parallel (60% faster!)
Cost: $0.00 (all use Ollama)
```

---

## 🎯 Implementation Roadmap

### **Phase 1: Simple Workers** (This Week)
- ✅ Multi-process task execution
- ✅ Parallel command running
- ✅ Basic result aggregation

**File**: `Scripts/karma_workers.py` (create now)

### **Phase 2: Ollama Agents** (Next Week)
- ✅ Role-based agents
- ✅ Specialized prompts
- ✅ Agent coordination

**File**: `Scripts/karma_ollama_agents.py`

### **Phase 3: Claude SDK Agents** (Week 3)
- ✅ Full tool use
- ✅ Complex reasoning
- ✅ Error recovery

**File**: `Scripts/karma_claude_agents.py`

### **Phase 4: Agent Marketplace** (Future)
- ✅ Pre-built agent templates
- ✅ Agent sharing/loading
- ✅ Agent performance tracking

**File**: `Scripts/karma_agent_marketplace.py`

---

## 🚀 Quick Start: Enable Agent Spawning NOW

**Step 1: Create simple worker system** (I'll do this now)

```python
# Scripts/karma_spawn_workers.py
from multiprocessing import Pool
import subprocess
import time

def execute_task(task_data):
    """Execute a single task"""
    task_id, task_description = task_data

    print(f"[Agent-{task_id}] Starting: {task_description}")

    # Use Ollama for execution
    result = subprocess.run(
        ["ollama", "run", "llama3.1", task_description],
        capture_output=True,
        text=True,
        timeout=60
    )

    print(f"[Agent-{task_id}] Completed!")
    return {
        "agent_id": task_id,
        "task": task_description,
        "result": result.stdout,
        "success": result.returncode == 0
    }

def karma_spawn_agents(tasks):
    """Karma spawns multiple agents to handle tasks in parallel"""

    print(f"🤖 Karma: Spawning {len(tasks)} agents...")
    start_time = time.time()

    # Create worker pool
    with Pool(processes=len(tasks)) as pool:
        # Execute all tasks in parallel
        results = pool.map(execute_task, enumerate(tasks))

    duration = time.time() - start_time

    print(f"\n✅ All agents completed in {duration:.2f} seconds")
    print(f"💰 Total cost: $0.00 (Ollama agents)")

    return results

# Usage example
if __name__ == "__main__":
    tasks = [
        "Check disk usage on C: drive",
        "List all Python processes",
        "Check if port 9400 is listening"
    ]

    results = karma_spawn_agents(tasks)

    for r in results:
        print(f"\n[Agent-{r['agent_id']}] Result:")
        print(r['result'][:200])  # First 200 chars
```

**Step 2: Integrate with Karma backend**

```python
# In karma_backend.py, add:

from karma_spawn_workers import karma_spawn_agents

@app.post("/api/spawn-agents")
async def spawn_agents(tasks: List[str]):
    """Endpoint for Karma to spawn multiple agents"""
    results = karma_spawn_agents(tasks)
    return {"agents": len(tasks), "results": results, "cost": 0}
```

---

## 🎭 Agent Personality System

**Future Enhancement**: Each agent has personality traits

```python
agent_templates = {
    "fast_and_loose": {
        "model": "llama3.1",
        "temperature": 0.9,
        "personality": "Quick, approximate answers"
    },
    "careful_and_thorough": {
        "model": "deepseek-coder",
        "temperature": 0.1,
        "personality": "Detailed, verified results"
    },
    "creative_problem_solver": {
        "model": "llama3.1",
        "temperature": 1.2,
        "personality": "Innovative solutions"
    }
}

# Karma chooses agent type based on task
karma.spawn_agent("DebugAgent", task, template="careful_and_thorough")
karma.spawn_agent("IdeaAgent", task, template="creative_problem_solver")
```

---

## ✅ Summary

**YES, Karma can spawn agents - here's how:**

1. **Level 1 (Ready Now)**: Python multiprocessing workers
2. **Level 2 (This Week)**: Ollama-based agents with roles
3. **Level 3 (Next Week)**: Full Claude SDK agents with tools

**Benefits:**
- ✅ Parallel task execution (3-5x faster)
- ✅ Role specialization (better results)
- ✅ Cost optimization (FREE Ollama for 90% of agents)
- ✅ Scalability (spawn 10+ agents for complex tasks)

**The architecture is already designed and ready to implement!**

Want me to create the worker system now so Karma can start spawning agents?
