"""
Step 3.2: Hooks Pipeline (P10)
Four hook points in Karma's invocation lifecycle.
All hooks are functions that accept context and return modified context.

session_start: blocking — runs before first LLM call
pre_tool_use: blocking — runs before each tool execution
post_tool_use: async — runs after each tool execution
session_end: async — runs when session closes
"""

import json
import sqlite3
import os
import traceback
from datetime import datetime, timezone

DB_PATH = os.getenv("MEMORY_DB_PATH", "/opt/seed-vault/memory_v1/memory.db")

# Import Phase 1+2 modules
try:
    from memory_tools import (
        admit_memory, retrieve_memory, load_last_session,
        load_pending_observations, save_session_context,
        auto_tag_category, assign_confidence
    )
    _MEM_AVAILABLE = True
except ImportError:
    _MEM_AVAILABLE = False

try:
    from observation_block import build_observation_block
    _OBS_AVAILABLE = True
except ImportError:
    _OBS_AVAILABLE = False

try:
    from budget_guard import check_budget, log_llm_call
    _BUDGET_AVAILABLE = True
except ImportError:
    _BUDGET_AVAILABLE = False

try:
    from capability_gate import check_access
    _GATE_AVAILABLE = True
except ImportError:
    _GATE_AVAILABLE = False

try:
    from session_briefing import generate_session_briefing
    _BRIEFING_AVAILABLE = True
except ImportError:
    _BRIEFING_AVAILABLE = False


# ─── Identity Spine Loader ────────────────────────────────────────────────

def load_identity_spine() -> str:
    """Load the identity spine from files. Returns text block for system prompt."""
    identity_paths = [
        "/opt/seed-vault/memory_v1/identity/identity.json",
        "/opt/seed-vault/memory_v1/identity/invariants.json",
        "/opt/seed-vault/memory_v1/identity/direction.md",
    ]
    parts = []
    for path in identity_paths:
        try:
            with open(path, "r") as f:
                content = f.read().strip()
                if content:
                    parts.append(content)
        except FileNotFoundError:
            pass
    
    # Also pull identity memories from SQLite
    if _MEM_AVAILABLE:
        try:
            identities = retrieve_memory("identity purpose values", top_k=5,
                                         category_filter="identity")
            if identities:
                parts.append("--- Identity Memories ---")
                for mem in identities:
                    parts.append(f"- {mem['content']}")
        except Exception:
            pass
    
    return "\n".join(parts) if parts else ""


# ─── Hook Implementations ─────────────────────────────────────────────────

def hook_session_start(session_id: str = None, user_message: str = "") -> dict:
    """
    Blocking hook: runs before first LLM call in a session.
    Returns context dict to inject into system prompt.
    
    Pipeline:
    1. load_identity_spine
    2. load_observations_since_last_session  
    3. retrieve_relevant_memories (P6: memory-before-prompt)
    4. build_session_context
    """
    context = {
        "identity_spine": "",
        "observation_block": "",
        "relevant_memories": [],
        "session_briefing": "",
        "last_session": None,
    }
    
    try:
        # 1. Identity spine
        context["identity_spine"] = load_identity_spine()
    except Exception as e:
        print(f"[HOOKS] identity_spine failed: {e}")

    try:
        # 2. Observation block (P3 stable prefix)
        if _OBS_AVAILABLE:
            context["observation_block"] = build_observation_block(session_id)
    except Exception as e:
        print(f"[HOOKS] observation_block failed: {e}")

    try:
        # 3. Memory-before-prompt (P6)
        if _MEM_AVAILABLE and user_message:
            memories = retrieve_memory(user_message, top_k=5)
            context["relevant_memories"] = memories
    except Exception as e:
        print(f"[HOOKS] retrieve_memory failed: {e}")

    try:
        # 4. Session context (P5)
        if _MEM_AVAILABLE:
            last = load_last_session()
            context["last_session"] = last
    except Exception as e:
        print(f"[HOOKS] load_last_session failed: {e}")

    try:
        # 5. Session briefing (Option C)
        if _BRIEFING_AVAILABLE:
            context["session_briefing"] = generate_session_briefing()
    except Exception as e:
        print(f"[HOOKS] session_briefing failed: {e}")

    return context


def hook_pre_tool_use(tool_name: str, tool_input: dict,
                      token: str = "", endpoint: str = "") -> dict:
    """
    Blocking hook: runs before each tool execution.
    Returns: {allowed: bool, reason: str}
    
    Pipeline:
    1. validate_tool_call
    2. gate_permissions (capability gate)
    3. check_budget (Decision #11)
    """
    ALLOWED_TOOLS = {"read_file", "write_file", "edit_file", "bash",
                     "shell_exec", "file_read", "file_write", "file_edit"}
    
    # 1. Validate tool name
    if tool_name not in ALLOWED_TOOLS:
        return {"allowed": False, "reason": f"Unknown tool: {tool_name}"}
    
    # 2. Validate dangerous patterns in bash commands
    if tool_name in ("bash", "shell_exec"):
        cmd = tool_input.get("command", "")
        dangerous = ["rm -rf /", "mkfs", "dd if=", "> /dev/", "chmod 777 /",
                      "curl | sh", "wget | sh", "shutdown", "reboot",
                      "kill -9 1", ":(){ :|:& };:"]
        for pattern in dangerous:
            if pattern in cmd:
                return {"allowed": False,
                        "reason": f"Blocked dangerous command pattern: {pattern}"}
    
    # 3. Capability gate
    if _GATE_AVAILABLE and token:
        access = check_access(token, "/v1/tools/execute", "POST")
        if not access["allowed"]:
            return {"allowed": False, "reason": access["reason"]}
    
    # 4. Budget check
    if _BUDGET_AVAILABLE:
        budget = check_budget()
        if not budget["allowed"]:
            return {"allowed": False,
                    "reason": budget.get("reason", "BUDGET_EXHAUSTED")}
    
    return {"allowed": True, "reason": "All checks passed"}


def hook_post_tool_use(tool_name: str, tool_input: dict,
                       tool_result: dict, session_id: str = "") -> None:
    """
    Async hook: runs after each tool execution.
    
    Pipeline:
    1. observe_tool_result (write to observations table)
    2. extract_memory_cells (admit learnings if any)
    """
    db = sqlite3.connect(DB_PATH)
    try:
        now = datetime.now(timezone.utc).timestamp()
        
        # 1. Write observation
        result_preview = str(tool_result).get("result", str(tool_result))[:200] if isinstance(tool_result, dict) else str(tool_result)[:200]
        description = f"Tool '{tool_name}' executed"
        if tool_name in ("bash", "shell_exec"):
            description += f": {tool_input.get('command', '')[:100]}"
        elif tool_name in ("read_file", "file_read"):
            description += f": {tool_input.get('path', '')}"
        
        success = tool_result.get("ok", True) if isinstance(tool_result, dict) else True
        outcome = "success" if success else f"error: {tool_result.get('error', 'unknown')}" if isinstance(tool_result, dict) else "completed"
        
        db.execute("""
            INSERT INTO observations (event_type, description, outcome, observed_at, reflected)
            VALUES (?, ?, ?, ?, 0)
        """, (f"tool_{tool_name}", description, outcome, now))
        db.commit()
        
    except Exception as e:
        print(f"[HOOKS] post_tool_use observation failed: {e}")
    finally:
        db.close()


def hook_session_end(session_id: str, task: str = "", goal: str = "",
                     approaches: str = "", decisions: str = "",
                     state: str = "", learnings: list = None) -> dict:
    """
    Async hook: runs when session closes.
    
    Pipeline:
    1. write_session_context (P5 5-field)
    2. extract_and_admit_memories (P4)
    3. update_observations (P3)
    4. generate_reflection (structured template)
    """
    results = {
        "session_saved": False,
        "memories_admitted": 0,
        "observations_marked": 0,
    }
    
    if not _MEM_AVAILABLE:
        return results
    
    try:
        # 1. Save session context (P5)
        save_session_context(
            session_id=session_id,
            task=task, goal=goal,
            approaches=approaches,
            decisions=decisions,
            state=state
        )
        results["session_saved"] = True
    except Exception as e:
        print(f"[HOOKS] session save failed: {e}")
    
    # 2. Admit learnings as memory cells
    if learnings:
        for learning in learnings:
            try:
                if isinstance(learning, str):
                    r = admit_memory(learning, source="reflection")
                elif isinstance(learning, dict):
                    r = admit_memory(
                        content=learning.get("content", ""),
                        category=learning.get("category"),
                        source="reflection",
                        confidence=learning.get("confidence")
                    )
                if r and r.get("action") in ("added", "updated"):
                    results["memories_admitted"] += 1
            except Exception as e:
                print(f"[HOOKS] admit learning failed: {e}")
    
    # 3. Admit decisions as pinned memory cells
    if decisions:
        for decision in decisions.split(";"):
            decision = decision.strip()
            if decision and len(decision) > 10:
                try:
                    r = admit_memory(
                        content=decision,
                        category="decision",
                        source="reflection",
                        confidence=1.0,
                        pinned=True
                    )
                except Exception:
                    pass
    
    # 4. Mark observations as reflected
    try:
        db = sqlite3.connect(DB_PATH)
        now = datetime.now(timezone.utc).timestamp()
        cursor = db.execute(
            "UPDATE observations SET reflected=1 WHERE reflected=0"
        )
        results["observations_marked"] = cursor.rowcount
        db.commit()
        db.close()
    except Exception as e:
        print(f"[HOOKS] mark observations failed: {e}")
    
    return results


# ─── Hook Registry ─────────────────────────────────────────────────────────

HOOKS = {
    "session_start": hook_session_start,
    "pre_tool_use": hook_pre_tool_use,
    "post_tool_use": hook_post_tool_use,
    "session_end": hook_session_end,
}


def run_hook(hook_name: str, **kwargs):
    """Execute a named hook with the given arguments."""
    hook_fn = HOOKS.get(hook_name)
    if not hook_fn:
        return {"error": f"Unknown hook: {hook_name}"}
    try:
        return hook_fn(**kwargs)
    except Exception as e:
        print(f"[HOOKS] {hook_name} failed: {traceback.format_exc()}")
        return {"error": str(e)}
