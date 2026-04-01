"""hooks_engine.py — 11-Event Hooks Engine for Karma Nexus (Sprint 3a).

Provides conditional hook evaluation, structured output, and audit trail.
11 event types: UserPromptSubmit, PreToolUse, PostToolUse, Stop, StopFailure,
SubagentStop, TaskCreated, CwdChanged, FileChanged, WorktreeCreate, SessionEnd.
"""
import json, os, time, subprocess, threading
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Optional, Union
from datetime import datetime, timezone

# ── Event types ──────────────────────────────────────────────────────────────
EVENTS = {
    "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop", "StopFailure",
    "SubagentStop", "TaskCreated", "CwdChanged", "FileChanged",
    "WorktreeCreate", "SessionEnd",
}

# ── Data classes ─────────────────────────────────────────────────────────────
@dataclass
class HookDef:
    name: str
    event: str  # one of EVENTS, or comma-separated for multi-event
    condition: str  # expression string, evaluated against context
    handler: Union[Callable, str]  # callable or path to .py/.sh script
    timeout_ms: int = 5000

    def __post_init__(self):
        for e in self.event.split(","):
            e = e.strip()
            if e and e not in EVENTS:
                raise ValueError(f"Unknown event type: {e}. Valid: {EVENTS}")


@dataclass
class HookOutput:
    systemMessage: Optional[str] = None
    updatedInput: Optional[Any] = None
    permissionDecision: str = "allow"  # allow, deny, ask


@dataclass
class HookResult:
    hook_name: str
    event: str
    duration_ms: int
    output: Optional[dict] = None
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ── Condition evaluator ──────────────────────────────────────────────────────
def _resolve_dot_path(obj: dict, path: str) -> Any:
    """Resolve dot-path like 'input.command' against a dict."""
    parts = path.strip().split(".")
    current = obj
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def evaluate_condition(condition_str: str, context: dict) -> bool:
    """Evaluate a condition string against context.

    Supports:
      - 'True' / 'False' literals
      - 'key == value'
      - 'key != value'
      - 'key > N' / 'key < N'
      - 'key in [a, b, c]'
      - 'expr1 AND expr2'
      - Dot-path access: 'input.command'
      - String values can be quoted or unquoted
    """
    condition_str = condition_str.strip()

    if condition_str == "True":
        return True
    if condition_str == "False":
        return False

    # AND compound
    if " AND " in condition_str:
        parts = condition_str.split(" AND ")
        return all(evaluate_condition(p.strip(), context) for p in parts)

    # 'key in [a, b, c]'
    if " in [" in condition_str:
        key, rest = condition_str.split(" in ", 1)
        key = key.strip()
        items_str = rest.strip().strip("[]")
        items = [s.strip().strip("'\"") for s in items_str.split(",")]
        val = _resolve_dot_path(context, key)
        return str(val) in items

    # 'key in value' (substring)
    if " in " in condition_str:
        key, val = condition_str.split(" in ", 1)
        key = key.strip().strip("'\"")
        resolved = _resolve_dot_path(context, val.strip())
        if isinstance(resolved, (list, set, tuple)):
            return key in resolved
        if isinstance(resolved, str):
            return key in resolved
        return False

    # Comparison operators
    for op in ("!=", "==", ">=", "<=", ">", "<"):
        if op in condition_str:
            left, right = condition_str.split(op, 1)
            left_val = _resolve_dot_path(context, left.strip())
            right_val = right.strip().strip("'\"")
            # Try numeric comparison
            try:
                left_num = float(left_val) if left_val is not None else 0
                right_num = float(right_val)
                if op == "==": return left_num == right_num
                if op == "!=": return left_num != right_num
                if op == ">":  return left_num > right_num
                if op == "<":  return left_num < right_num
                if op == ">=": return left_num >= right_num
                if op == "<=": return left_num <= right_num
            except (ValueError, TypeError):
                pass
            # String comparison
            left_str = str(left_val) if left_val is not None else ""
            if op == "==": return left_str == right_val
            if op == "!=": return left_str != right_val
            return False

    # Bare key — truthy check
    val = _resolve_dot_path(context, condition_str)
    return bool(val)


# ── Hooks Service ────────────────────────────────────────────────────────────
class HooksService:
    def __init__(self, audit_path: str = None):
        self._registry: dict[str, list[HookDef]] = {}  # event -> list[HookDef]
        self._audit_path = audit_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "tmp", "hooks_audit.jsonl"
        )
        os.makedirs(os.path.dirname(self._audit_path), exist_ok=True)

    def register(self, hook_def: HookDef):
        """Register a hook for one or more events (comma-separated)."""
        for event in hook_def.event.split(","):
            event = event.strip()
            if event not in self._registry:
                self._registry[event] = []
            self._registry[event].append(hook_def)

    def fire(self, event: str, context: dict) -> list[HookResult]:
        """Fire all hooks registered for this event. Returns results."""
        if event not in EVENTS:
            raise ValueError(f"Unknown event: {event}")
        hooks = self._registry.get(event, [])
        results = []
        for hook_def in hooks:
            t0 = time.time()
            try:
                if not evaluate_condition(hook_def.condition, context):
                    continue
                output = self._execute(hook_def, context)
                duration = int((time.time() - t0) * 1000)
                result = HookResult(
                    hook_name=hook_def.name, event=event,
                    duration_ms=duration, output=output,
                )
            except Exception as e:
                duration = int((time.time() - t0) * 1000)
                result = HookResult(
                    hook_name=hook_def.name, event=event,
                    duration_ms=duration, error=str(e),
                )
            results.append(result)
            self._audit(result)
        return results

    def _execute(self, hook_def: HookDef, context: dict) -> dict:
        """Execute a hook handler (callable or script)."""
        handler = hook_def.handler
        timeout_s = hook_def.timeout_ms / 1000.0

        if callable(handler):
            return handler(context)

        # Script path
        path = str(handler)
        if path.endswith(".py"):
            return self._run_python_hook(path, context, timeout_s)
        elif path.endswith(".sh"):
            return self._run_bash_hook(path, context, timeout_s)
        else:
            raise ValueError(f"Unknown handler type: {path}")

    def _run_python_hook(self, path: str, context: dict, timeout: float) -> dict:
        """Run a Python hook script. Sends context as JSON on stdin, reads JSON from stdout."""
        proc = subprocess.run(
            ["python", path],
            input=json.dumps(context),
            capture_output=True, text=True, timeout=timeout,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Hook {path} failed (exit {proc.returncode}): {proc.stderr[:500]}")
        stdout = proc.stdout.strip()
        if not stdout:
            return {}
        # Find last JSON line (skip any print statements)
        for line in reversed(stdout.splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
        return {}

    def _run_bash_hook(self, path: str, context: dict, timeout: float) -> dict:
        """Run a Bash hook script. Context passed as env vars."""
        env = os.environ.copy()
        for k, v in context.items():
            if isinstance(v, (str, int, float, bool)):
                env[f"HOOK_{k.upper()}"] = str(v)
        env["HOOK_CONTEXT_JSON"] = json.dumps(context)
        proc = subprocess.run(
            ["bash", path],
            capture_output=True, text=True, timeout=timeout, env=env,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Hook {path} failed: {proc.stderr[:500]}")
        stdout = proc.stdout.strip()
        if stdout and stdout.startswith("{"):
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                pass
        return {"stdout": stdout}

    def _audit(self, result: HookResult):
        """Append result to audit log (fire-and-forget)."""
        try:
            entry = asdict(result)
            with open(self._audit_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass  # Never fail on audit

    def list_hooks(self) -> dict:
        """List all registered hooks by event."""
        return {event: [h.name for h in hooks] for event, hooks in self._registry.items()}
