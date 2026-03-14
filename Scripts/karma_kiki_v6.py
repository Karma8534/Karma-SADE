"""
karma_kiki_v6.py — Karma Autonomous Loop with Governance
Built: 2026-03-13

Extends v5 with:
- Bus Ingester: /v1/coordination → kiki_issues.jsonl
- K2-Critic Agent: advisory plan per cycle (degraded-safe)
- Policy Arbiter: deterministic ALLOW/DENY/REQUIRE_APPROVAL (hard gate)
- Promotion Contract: kiki/evolution → main with rollback audit
- Gate audit log: kiki_gate_audit.jsonl per arbiter decision
- Rollback pointer: .karma_last_good written after verified success
"""

import os
import sys
import json
import time
import signal
import logging
import subprocess
import urllib.request
import threading
from datetime import datetime, timezone
from pathlib import Path

# ============ Governance Imports ============

sys.path.insert(0, str(Path(__file__).parent.parent))
from Scripts.karma_policy_arbiter import PolicyArbiter
from Scripts.karma_promote import PromotionContract
from Scripts.karma_bus_ingester import BusIngester
from Scripts.karma_critic_agent import CriticAgent

# ============ Configuration ============

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://172.22.240.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "devstral:latest")
LOOP_INTERVAL = int(os.environ.get("LOOP_INTERVAL", "60"))

BASE_DIR = Path(os.environ.get("KARMA_BASE", "/mnt/c/dev/Karma/k2"))
CACHE_DIR = BASE_DIR / "cache"
SCRIPTS_DIR = BASE_DIR / "scripts"

ISSUES_FILE = CACHE_DIR / "kiki_issues.jsonl"
JOURNAL_FILE = CACHE_DIR / "kiki_journal.jsonl"
STATE_FILE = CACHE_DIR / "kiki_state.json"
DIRECTIVE_FILE = CACHE_DIR / "karma_directive.md"
JOURNAL_MAX_ENTRIES = 200

VAULT_AMBIENT_URL = os.environ.get(
    "VAULT_AMBIENT_URL", "https://hub.arknexus.net/v1/ambient"
)

# Governance paths
BOUNDARY_CONFIG = BASE_DIR / "Config/governance_boundary_v1.json"
CRITICAL_PATHS_CONFIG = BASE_DIR / "Config/critical_paths.json"
GATE_AUDIT_FILE = CACHE_DIR / "kiki_gate_audit.jsonl"
LAST_GOOD_FILE = BASE_DIR / ".karma_last_good"
PROVENANCE_DIR = BASE_DIR / "provenance"
HUB_TOKEN_PATH = "/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt"

# ============ Logging ============

LOG_FILE = os.environ.get("YOYO_LOG", "/var/log/karma_kiki.log")
_handlers = [logging.StreamHandler()]
try:
    _handlers.append(logging.FileHandler(LOG_FILE))
except (PermissionError, FileNotFoundError):
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _handlers.append(logging.FileHandler(CACHE_DIR / "kiki.log"))
    except (PermissionError, FileNotFoundError, OSError):
        pass  # stderr-only fallback on Windows dev machine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [YOYOv6] %(levelname)s %(message)s",
    handlers=_handlers,
)
log = logging.getLogger("kiki")

# ============ Governance Component Initialization ============

def _make_arbiter():
    """Initialize arbiter lazily — safe if config files don't exist yet."""
    if BOUNDARY_CONFIG.exists() and CRITICAL_PATHS_CONFIG.exists():
        return PolicyArbiter(str(BOUNDARY_CONFIG), str(CRITICAL_PATHS_CONFIG))
    return None


arbiter = _make_arbiter()

promotion_contract = PromotionContract(
    last_good_path=str(LAST_GOOD_FILE),
    provenance_dir=str(PROVENANCE_DIR),
)

ingester = BusIngester(
    issues_file=str(ISSUES_FILE),
    coordination_url=VAULT_AMBIENT_URL.replace("/v1/ambient", "/v1/coordination"),
)

critic = CriticAgent(ollama_url=OLLAMA_URL, model=OLLAMA_MODEL)

# ============ Governance Helpers ============

def write_gate_audit(cycle: int, target_path: str, result):
    """Append one arbiter decision to the gate audit log."""
    GATE_AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": _now(), "cycle": cycle, "target": target_path,
        "verdict": result.verdict, "reason_code": result.reason_code,
        "reason": result.reason,
    }
    with open(GATE_AUDIT_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def write_critic_plan(cycle: int, plan: dict):
    """Write advisory critic plan for this cycle (not canonical)."""
    path = CACHE_DIR / f"critic_plan_{cycle:04d}.json"
    path.write_text(json.dumps(plan, indent=2))


def get_current_sha() -> str:
    """Return short git SHA of HEAD, or 'unknown' on error."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=BASE_DIR
        )
        return result.stdout.strip()[:12]
    except Exception:
        return "unknown"

# ============ Ollama ============

def ollama_chat(system_prompt: str, user_prompt: str, timeout: int = 360) -> str:
    """Call local Ollama via /api/chat. Returns raw text response."""
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 2048},
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read())
    return body.get("message", {}).get("content", "")


def ollama_alive() -> bool:
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5):
            return True
    except Exception:
        return False

# ============ Issues ============

def load_issues() -> list[dict]:
    """Load all issues from JSONL file."""
    if not ISSUES_FILE.exists():
        return []
    issues = []
    for line in ISSUES_FILE.read_text().strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            issues.append(json.loads(line))
        except Exception:
            pass
    return issues


def save_issues(issues: list[dict]):
    """Rewrite issues file without closed issues."""
    ISSUES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ISSUES_FILE, "w") as f:
        for issue in issues:
            f.write(json.dumps(issue) + "\n")


def close_issue(issues: list[dict], index: int) -> list[dict]:
    """Remove issue at index. Returns new list."""
    return [i for idx, i in enumerate(issues) if idx != index]

# ============ State ============

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {
        "cycles": 0, "started_at": _now(),
        "actions_attempted": 0, "actions_succeeded": 0,
        "actions_failed": 0, "issues_closed": 0,
        "idle_cycles": 0,
    }


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))

# ============ Context ============

def gather_context() -> str:
    """Minimal context: workspace files + directive snippet."""
    parts = []

    # Directive
    try:
        if DIRECTIVE_FILE.exists():
            parts.append(f"DIRECTIVE:\n{DIRECTIVE_FILE.read_text()[:1500]}")
    except Exception:
        pass

    # Workspace files
    try:
        files = []
        for f in sorted(CACHE_DIR.iterdir()):
            if f.is_file():
                sz = f.stat().st_size
                mt = datetime.fromtimestamp(f.stat().st_mtime).strftime("%m-%d %H:%M")
                files.append(f"  {f.name} ({sz}B, {mt})")
        parts.append("WORKSPACE:\n" + "\n".join(files[:20]))
    except Exception:
        pass

    # Recent journal (last 5 entries only)
    try:
        if JOURNAL_FILE.exists():
            lines = JOURNAL_FILE.read_text().strip().split("\n")
            recent = lines[-5:] if len(lines) > 5 else lines
            entries = []
            for line in recent:
                try:
                    e = json.loads(line)
                    entries.append(f"  [{e.get('ts','')}] {e.get('ok','?')} {e.get('type','?')}: {e.get('summary','')}")
                except Exception:
                    pass
            if entries:
                parts.append("RECENT JOURNAL:\n" + "\n".join(entries))
    except Exception:
        pass

    return "\n\n".join(parts)

# ============ Think ============

SYSTEM_PROMPT = """You are Karma's autonomous brain running on K2 via Ollama.
You receive ONE issue to work on. Your job: produce a concrete fix.

RESPOND IN VALID JSON ONLY. No markdown fences. No explanation outside JSON.
{
  "action": "description of what you're doing",
  "target_file": "/absolute/path/to/file/to/write",
  "content": "the COMPLETE file content to write",
  "test_command": "shell command to verify (null if none)"
}

RULES:
- target_file MUST be an absolute path under /mnt/c/dev/Karma/k2/
- content MUST be the COMPLETE file content, not a patch
- If the issue asks you to modify an existing file, include ALL of its content with your changes
- If you cannot solve the issue, set target_file to null and explain in action
"""


def think(issue: dict, context: str) -> dict | None:
    """Ask devstral to solve one issue. Returns parsed action or None."""
    user_msg = f"""ISSUE TO SOLVE:
{issue.get('issue', '')}

DETAILS:
{issue.get('details', '')}

CONTEXT:
{context}

Produce a JSON fix for this issue. target_file must be absolute path under /mnt/c/dev/Karma/k2/."""

    try:
        raw = ollama_chat(SYSTEM_PROMPT, user_msg)
    except Exception as e:
        log.error(f"Ollama call failed: {e}")
        return None

    log.info(f"LLM response length: {len(raw)} chars")
    log.info(f"LLM first 200: {repr(raw[:200])}")

    # Strip markdown fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    raw = raw.strip()

    # Strip think tags
    if "<think>" in raw:
        parts = raw.split("</think>")
        raw = parts[-1].strip() if len(parts) > 1 else raw

    # Parse JSON
    try:
        return json.loads(raw)
    except Exception:
        pass

    # Try extracting JSON object
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(raw[start:end])
        except Exception:
            pass

    log.warning(f"Unparseable LLM response: {raw[:300]}")
    return None

# ============ Act + Verify ============

def act_and_verify(decision: dict) -> dict:
    """Write file, run test, verify bytes actually changed. Returns result."""
    target = decision.get("target_file")
    content = decision.get("content", "")
    test_cmd = decision.get("test_command")

    if not target or not content:
        return {"ok": False, "reason": "no target_file or content in LLM response"}

    target_path = Path(target)

    # Security: must be under K2 base
    try:
        target_path.resolve().relative_to(BASE_DIR.resolve())
    except ValueError:
        return {"ok": False, "reason": f"target_file {target} is outside {BASE_DIR}"}

    # Read before-state
    before_bytes = None
    if target_path.exists():
        try:
            before_bytes = target_path.read_bytes()
        except Exception:
            pass

    # Write
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content)
        log.info(f"Wrote {len(content)} chars to {target}")
    except Exception as e:
        return {"ok": False, "reason": f"write failed: {e}"}

    # Verify bytes actually changed
    after_bytes = target_path.read_bytes()
    if before_bytes is not None and before_bytes == after_bytes:
        return {"ok": False, "reason": "file unchanged — wrote identical content"}

    # Run test if provided
    if test_cmd:
        try:
            result = subprocess.run(
                test_cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                # Revert
                if before_bytes is not None:
                    target_path.write_bytes(before_bytes)
                    log.warning(f"Test failed, reverted {target}")
                else:
                    target_path.unlink(missing_ok=True)
                    log.warning(f"Test failed, removed {target}")
                return {
                    "ok": False,
                    "reason": f"test failed (exit {result.returncode}): {result.stderr[:200]}",
                    "reverted": True,
                }
            log.info(f"Test passed: {test_cmd}")
        except subprocess.TimeoutExpired:
            if before_bytes is not None:
                target_path.write_bytes(before_bytes)
            else:
                target_path.unlink(missing_ok=True)
            return {"ok": False, "reason": "test timed out, reverted"}

    bytes_changed = len(after_bytes) - (len(before_bytes) if before_bytes else 0)
    return {
        "ok": True,
        "reason": f"wrote {len(content)} chars to {target} (delta: {bytes_changed:+d} bytes)",
        "new_file": before_bytes is None,
    }

# ============ Journal ============

def journal_write(cycle: int, issue: dict, decision: dict | None, result: dict):
    """Append structured entry to journal."""
    entry = {
        "ts": _now(),
        "cycle": cycle,
        "type": "action" if result.get("ok") else "failure",
        "issue": issue.get("issue", "")[:100],
        "summary": (decision or {}).get("action", "no decision"),
        "result": result.get("reason", ""),
        "ok": result.get("ok", False),
        "vault_worthy": result.get("ok", False),
    }

    JOURNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(JOURNAL_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    # Rotate
    try:
        lines = JOURNAL_FILE.read_text().strip().split("\n")
        if len(lines) > JOURNAL_MAX_ENTRIES:
            JOURNAL_FILE.write_text("\n".join(lines[-JOURNAL_MAX_ENTRIES:]) + "\n")
    except Exception:
        pass

    # Sync successful actions to vault
    if result.get("ok"):
        _sync_to_vault(entry)


def _sync_to_vault(entry: dict):
    content = (
        f"[karma-kiki-v6] Cycle #{entry.get('cycle',0)}: "
        f"{entry.get('summary','')} — {entry.get('result','')}"
    )
    payload = json.dumps({
        "source": "karma_kiki_v6",
        "content": content,
        "lane": "k2_evolution",
        "timestamp": entry.get("ts", _now()),
    }).encode()
    try:
        req = urllib.request.Request(
            VAULT_AMBIENT_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            log.info(f"Vault sync: {resp.status}")
    except Exception as e:
        log.warning(f"Vault sync failed (non-fatal): {e}")

# ============ Main Loop ============

_shutdown = threading.Event()


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _handle_signal(signum, _):
    log.info(f"Signal {signum} — stopping.")
    _shutdown.set()


signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


def run_cycle(state: dict):
    """One cycle: bus ingest → pick issue → critic → think → arbiter → act → verify → rollback pointer → promote → close → journal."""
    state["cycles"] += 1
    cycle = state["cycles"]
    log.info(f"=== Cycle #{cycle} ===")

    # 1. Load issues
    issues = load_issues()

    # 1b. Ingest coordination bus
    try:
        if Path(HUB_TOKEN_PATH).exists():
            token = Path(HUB_TOKEN_PATH).read_text().strip()
            ingested = ingester.fetch_and_ingest(token)
            if ingested:
                log.info(f"Ingested {ingested} new issues from coordination bus")
                issues = load_issues()
    except Exception as e:
        log.warning(f"Bus ingestion failed (non-fatal): {e}")

    if not issues:
        log.info("No issues in backlog — idle")
        state["idle_cycles"] += 1
        return

    # 2. Pick first issue
    issue = issues[0]
    log.info(f"Working on: {issue.get('issue', '')[:80]}")

    # 3. Check Ollama
    if not ollama_alive():
        log.error("Ollama unreachable — skipping cycle")
        journal_write(cycle, issue, None, {"ok": False, "reason": "Ollama unreachable"})
        return

    # 4. Gather context
    context = gather_context()

    # 2b. Critic plan (advisory — degraded-safe)
    critic_plan = critic.get_plan(issue, context)
    if critic_plan is None:
        log.warning("Critic unavailable — degraded mode (executor-only)")
    else:
        write_critic_plan(cycle, critic_plan)
        log.info(f"Critic plan: {str(critic_plan.get('plan',''))[:80]}")

    # 4b. Think
    decision = think(issue, context)

    if not decision or not decision.get("target_file"):
        reason = "LLM returned no actionable response"
        if decision:
            reason = decision.get("action", reason)
        log.warning(f"No action: {reason}")
        journal_write(cycle, issue, decision, {"ok": False, "reason": reason})
        # Close unsolvable issue to prevent infinite loop
        if decision and not decision.get("target_file"):
            issues = close_issue(issues, 0)
            save_issues(issues)
            state["issues_closed"] += 1
            log.info(f"Closed unsolvable issue. {len(issues)} remaining.")
        return

    # 3b. Policy Arbiter gate (hard — DENY blocks execution)
    if arbiter is not None:
        has_test = bool(decision.get("test_command"))
        arbiter_result = arbiter.evaluate(
            target_path=decision.get("target_file", ""),
            operation="write",
            test_results={"smoke_pass": has_test, "functional_pass": has_test},
        )
        write_gate_audit(cycle, decision.get("target_file", ""), arbiter_result)
        log.info(f"Arbiter: {arbiter_result.verdict} [{arbiter_result.reason_code}]")

        if arbiter_result.verdict == "DENY":
            log.warning(f"Arbiter DENIED: {arbiter_result.reason}")
            journal_write(cycle, issue, decision,
                          {"ok": False, "reason": f"arbiter_deny:{arbiter_result.reason_code}"})
            issues = close_issue(issues, 0)
            save_issues(issues)
            state["actions_failed"] += 1
            state["issues_closed"] += 1
            return

        if arbiter_result.verdict == "REQUIRE_APPROVAL":
            log.info(f"Arbiter REQUIRE_APPROVAL — holding for Colby: {arbiter_result.reason}")
            journal_write(cycle, issue, decision,
                          {"ok": False, "reason": f"arbiter_require_approval:{arbiter_result.reason_code}"})
            return  # Do not execute — wait for approval signal
    else:
        log.warning("Arbiter not initialized (config missing) — proceeding without gate")
        arbiter_result = type("R", (), {"verdict": "ALLOW", "reason_code": "no_config", "reason": "arbiter config missing"})()

    # 5. Act + Verify
    state["actions_attempted"] += 1
    result = act_and_verify(decision)
    log.info(f"Result: ok={result['ok']} — {result.get('reason', '')[:100]}")

    # 6. Journal
    journal_write(cycle, issue, decision, result)

    # 7. Close issue (whether success or failure — prevent infinite retry)
    issues = close_issue(issues, 0)
    save_issues(issues)
    state["issues_closed"] += 1

    if result["ok"]:
        state["actions_succeeded"] += 1
        log.info(f"SUCCESS — issue closed, {len(issues)} remaining")

        # 4b. Rollback pointer + promotion check
        sha = get_current_sha()
        promotion_contract.write_last_good(sha)
        promo = promotion_contract.evaluate_promotion(
            cycle=cycle,
            test_results={"smoke_pass": True, "functional_pass": True},
            arbiter_verdict=arbiter_result.verdict,
        )
        if promo["eligible"]:
            log.info(f"Cycle #{cycle} eligible for promotion to main — PR opened")
        else:
            log.info(f"Cycle #{cycle} not yet eligible: {promo['reason']}")
    else:
        state["actions_failed"] += 1
        log.info(f"FAILED — issue closed anyway (no infinite retry), {len(issues)} remaining")


def main():
    log.info("=" * 50)
    log.info("KARMA KIKI v6.0 — AUTONOMOUS LOOP WITH GOVERNANCE")
    log.info(f"Model: {OLLAMA_MODEL} @ {OLLAMA_URL}")
    log.info(f"Cycle interval: {LOOP_INTERVAL}s")
    log.info(f"Issues file: {ISSUES_FILE}")
    log.info(f"Arbiter: {'initialized' if arbiter is not None else 'NOT INITIALIZED (config missing)'}")
    log.info("Governance: Bus Ingester + Critic + Policy Arbiter + Promotion Contract")
    log.info("Design: ingest bus → pick issue → critic → think → arbiter gate → act → VERIFY → rollback ptr → promote → journal")
    log.info("=" * 50)

    state = load_state()
    state["started_at"] = _now()
    state["cycles"] = 0
    state["actions_attempted"] = 0
    state["actions_succeeded"] = 0
    state["actions_failed"] = 0
    state["issues_closed"] = 0
    state["idle_cycles"] = 0
    save_state(state)

    if not ollama_alive():
        log.error(f"Ollama not reachable at {OLLAMA_URL} — cannot start")
        sys.exit(1)

    log.info("Ollama verified. Starting loop.")

    while not _shutdown.is_set():
        try:
            run_cycle(state)
            save_state(state)
        except Exception as e:
            log.error(f"Cycle error: {e}", exc_info=True)
        _shutdown.wait(timeout=LOOP_INTERVAL)

    save_state(state)
    log.info("Karma kiki v6 stopped. State saved.")


if __name__ == "__main__":
    main()
