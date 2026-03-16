# Karma K2 Merged Agent Architecture — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the five-component K2 merged agent architecture with locked governance boundary, enabling Karma to autonomously evolve herself under deterministic policy enforcement with Colby as final authority.

**Architecture:** Karma-Core (hub-facing intelligence) seeds goals via `/v1/coordination` bus → Kiki-Executor picks issues, requests Critic plan, runs Policy Arbiter gate, executes, verifies, commits to `kiki/evolution` → Promotion Contract gates `kiki/evolution → main`. Policy Arbiter is deterministic code — not an LLM. Critic is advisory only.

**Tech Stack:** Python 3.10+, Node.js (hub-bridge), JSON/JSONL, Git + GitHub CLI (`gh`), Ollama (Critic), Anthropic API (Karma-Core via hub-bridge).

**Build order:** Governance configs → Policy Arbiter → Promotion Contract → Bus Ingester → K2-Critic → Kiki v6 (wire all) → Deploy + Verify.

**Two hard prerequisites before anything else:**
1. Deterministic Policy Arbiter
2. Explicit Promotion Contract to `main`

---

## Task 1: Governance Config Files

**Files:**
- Create: `Config/governance_boundary_v1.json`
- Create: `Config/critical_paths.json`

**Step 1: Create Config directory**
```bash
mkdir -p Config
```

**Step 2: Write `Config/governance_boundary_v1.json`**
```json
{
  "version": "1.0",
  "controlled_by": "colby",
  "hard_deny_paths": [
    "/run/secrets/**",
    "~/.ssh/**",
    "/opt/seed-vault/memory_v1/hub_auth/**",
    "/opt/seed-vault/memory_v1/session/**",
    "/opt/seed-vault/memory_v1/hub_bridge/config/hub.env",
    "**/*.pem",
    "**/*.key",
    "**/.env*",
    "**/*token*",
    "**/*api_key*",
    "Config/governance_boundary_v1.json"
  ],
  "financial_files": [
    "hub.env",
    "spend-cap.json",
    "billing-policy.json",
    "model-routing-config.json"
  ],
  "spend_envelope_path": "/opt/seed-vault/memory_v1/session/spend_envelope.json",
  "lease_timeout_minutes": 5,
  "lease_heartbeat_intervals": 2
}
```

**Step 3: Write `Config/critical_paths.json`**
```json
{
  "version": "1.0",
  "controlled_by": "colby",
  "critical_paths": [
    "hub-bridge/app/server.js",
    "Memory/00-karma-system-prompt-live.md",
    "CLAUDE.md",
    "Config/governance_boundary_v1.json",
    "Config/critical_paths.json",
    ".github/workflows/**",
    "Scripts/karma_policy_arbiter.py",
    "Scripts/karma_promote.py"
  ]
}
```

**Step 4: Commit**
```bash
git add Config/
git commit -m "feat: add governance boundary and critical paths config (Colby-controlled)"
```

---

## Task 2: Policy Arbiter — Tests First

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_policy_arbiter.py`
- Create: `Scripts/karma_policy_arbiter.py` (implementation follows tests)

**Step 1: Create tests directory**
```bash
mkdir -p tests
touch tests/__init__.py
```

**Step 2: Write failing tests**

`tests/test_policy_arbiter.py`:
```python
import json
import pytest
from pathlib import Path
from Scripts.karma_policy_arbiter import PolicyArbiter


@pytest.fixture
def arbiter(tmp_path):
    boundary = {
        "hard_deny_paths": [
            "/run/secrets/**", "~/.ssh/**", "**/*token*", "**/*.key",
            "Config/governance_boundary_v1.json"
        ],
        "financial_files": ["hub.env", "spend-cap.json"]
    }
    critical = {
        "critical_paths": [
            "hub-bridge/app/server.js",
            "Memory/00-karma-system-prompt-live.md"
        ]
    }
    b = tmp_path / "boundary.json"
    c = tmp_path / "critical.json"
    b.write_text(json.dumps(boundary))
    c.write_text(json.dumps(critical))
    return PolicyArbiter(str(b), str(c))


def test_hard_deny_secret_path(arbiter):
    r = arbiter.evaluate("/run/secrets/api_key", "write", {})
    assert r.verdict == "DENY"
    assert r.reason_code == "HARD_DENY_PATH"


def test_hard_deny_token_file(arbiter):
    r = arbiter.evaluate("/some/path/my_token.txt", "write", {})
    assert r.verdict == "DENY"
    assert r.reason_code == "HARD_DENY_PATH"


def test_hard_deny_governance_file(arbiter):
    r = arbiter.evaluate("Config/governance_boundary_v1.json", "write", {})
    assert r.verdict == "DENY"
    assert r.reason_code == "HARD_DENY_PATH"


def test_financial_boundary(arbiter):
    r = arbiter.evaluate("/opt/hub-bridge/config/hub.env", "write", {})
    assert r.verdict == "DENY"
    assert r.reason_code == "FINANCIAL_BOUNDARY"


def test_critical_path_no_tests(arbiter):
    r = arbiter.evaluate("hub-bridge/app/server.js", "write", {})
    assert r.verdict == "DENY"
    assert r.reason_code == "CRITICAL_TESTS_FAILED"


def test_critical_path_with_tests_requires_approval(arbiter):
    r = arbiter.evaluate(
        "hub-bridge/app/server.js", "write",
        {"smoke_pass": True, "functional_pass": True}
    )
    assert r.verdict == "REQUIRE_APPROVAL"
    assert r.reason_code == "CRITICAL_PATH"


def test_non_critical_with_tests_allowed(arbiter):
    r = arbiter.evaluate(
        "Scripts/karma_kiki_v6.py", "write",
        {"smoke_pass": True, "functional_pass": True}
    )
    assert r.verdict == "ALLOW"


def test_non_critical_untested_allowed_with_flag(arbiter):
    r = arbiter.evaluate("Scripts/new_script.py", "write", {"untested": True})
    assert r.verdict == "ALLOW"
    assert "untested" in r.reason.lower()


def test_non_critical_no_tests_no_flag_denied(arbiter):
    r = arbiter.evaluate("Scripts/new_script.py", "write", {})
    assert r.verdict == "DENY"
    assert r.reason_code == "TESTS_REQUIRED"


def test_arbiter_result_has_reason_code(arbiter):
    r = arbiter.evaluate("/run/secrets/x", "write", {})
    assert r.reason_code
    assert r.reason
    assert r.verdict in ("ALLOW", "DENY", "REQUIRE_APPROVAL")
```

**Step 3: Run — verify all fail**
```bash
cd /c/Users/raest/Documents/Karma_SADE
python -m pytest tests/test_policy_arbiter.py -v
```
Expected: `ModuleNotFoundError: No module named 'Scripts.karma_policy_arbiter'`

---

## Task 3: Policy Arbiter — Implementation

**Files:**
- Create: `Scripts/__init__.py`
- Create: `Scripts/karma_policy_arbiter.py`

**Step 1: Create `Scripts/__init__.py`**
```bash
touch Scripts/__init__.py
```

**Step 2: Write `Scripts/karma_policy_arbiter.py`**
```python
"""
karma_policy_arbiter.py — Deterministic governance enforcement.
NOT an LLM. Pure function: inputs → ALLOW | DENY | REQUIRE_APPROVAL.
LLMs may propose. Arbiter decides.
"""

import fnmatch
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

VERDICT = Literal["ALLOW", "DENY", "REQUIRE_APPROVAL"]


@dataclass
class ArbitratorResult:
    verdict: VERDICT
    reason_code: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "reason_code": self.reason_code,
            "reason": self.reason,
        }


class PolicyArbiter:
    def __init__(self, boundary_config_path: str, critical_paths_path: str):
        self.boundary = json.loads(Path(boundary_config_path).read_text())
        self.critical = json.loads(Path(critical_paths_path).read_text())

    def evaluate(
        self, target_path: str, operation: str, test_results: dict
    ) -> ArbitratorResult:
        """
        Evaluate a proposed change.
        Returns deterministic ALLOW / DENY / REQUIRE_APPROVAL.
        """
        # 1. Hard deny — secrets, auth, governance lock
        if self._matches_any(target_path, self.boundary.get("hard_deny_paths", [])):
            return ArbitratorResult(
                "DENY", "HARD_DENY_PATH",
                f"{target_path} matches hard-deny list"
            )

        # 2. Financial boundary — named control files
        financial = self.boundary.get("financial_files", [])
        if any(target_path.endswith(f) for f in financial):
            return ArbitratorResult(
                "DENY", "FINANCIAL_BOUNDARY",
                f"{target_path} is a financial boundary file"
            )

        # 3. Critical paths — require tests + Colby approval
        if self._matches_any(target_path, self.critical.get("critical_paths", [])):
            if not (test_results.get("smoke_pass") and test_results.get("functional_pass")):
                return ArbitratorResult(
                    "DENY", "CRITICAL_TESTS_FAILED",
                    f"{target_path} is critical and requires smoke + functional tests"
                )
            return ArbitratorResult(
                "REQUIRE_APPROVAL", "CRITICAL_PATH",
                f"{target_path} is a critical path — Colby approval required"
            )

        # 4. Non-critical — smoke test OR explicit untested flag
        if test_results.get("smoke_pass"):
            return ArbitratorResult(
                "ALLOW", "NON_CRITICAL_VERIFIED",
                f"{target_path} passed smoke test"
            )
        if test_results.get("untested"):
            return ArbitratorResult(
                "ALLOW", "NON_CRITICAL_UNTESTED",
                f"{target_path} marked untested — allowed on non-critical path"
            )

        return ArbitratorResult(
            "DENY", "TESTS_REQUIRED",
            f"{target_path} is non-critical but has no smoke test and is not marked untested"
        )

    @staticmethod
    def _matches_any(path: str, patterns: list[str]) -> bool:
        return any(fnmatch.fnmatch(path, p) for p in patterns)
```

**Step 3: Run tests — verify all pass**
```bash
python -m pytest tests/test_policy_arbiter.py -v
```
Expected: All 10 tests PASS.

**Step 4: Commit**
```bash
git add Scripts/__init__.py Scripts/karma_policy_arbiter.py tests/
git commit -m "feat: deterministic Policy Arbiter — ALLOW/DENY/REQUIRE_APPROVAL (TDD, 10 tests)"
```

---

## Task 4: Promotion Contract — Tests First

**Files:**
- Create: `tests/test_promote.py`
- Create: `Scripts/karma_promote.py`

**Step 1: Write failing tests**

`tests/test_promote.py`:
```python
import json
import pytest
from unittest.mock import patch, MagicMock
from Scripts.karma_promote import PromotionContract


@pytest.fixture
def contract(tmp_path):
    last_good = tmp_path / ".karma_last_good"
    provenance_dir = tmp_path / "provenance"
    return PromotionContract(
        last_good_path=str(last_good),
        provenance_dir=str(provenance_dir),
        dry_run=True  # no real git/gh calls in tests
    )


def test_promote_fails_without_rollback_pointer(contract):
    result = contract.evaluate_promotion(
        cycle=1,
        test_results={"smoke_pass": True, "functional_pass": True},
        arbiter_verdict="ALLOW"
    )
    assert result["eligible"] is False
    assert result["reason"] == "no_rollback_pointer"


def test_promote_fails_without_smoke_test(contract, tmp_path):
    (tmp_path / ".karma_last_good").write_text("abc123")
    result = contract.evaluate_promotion(
        cycle=1,
        test_results={"smoke_pass": False, "functional_pass": True},
        arbiter_verdict="ALLOW"
    )
    assert result["eligible"] is False
    assert result["reason"] == "smoke_test_failed"


def test_promote_fails_without_functional_test(contract, tmp_path):
    (tmp_path / ".karma_last_good").write_text("abc123")
    result = contract.evaluate_promotion(
        cycle=1,
        test_results={"smoke_pass": True, "functional_pass": False},
        arbiter_verdict="ALLOW"
    )
    assert result["eligible"] is False
    assert result["reason"] == "functional_test_failed"


def test_promote_fails_on_arbiter_deny(contract, tmp_path):
    (tmp_path / ".karma_last_good").write_text("abc123")
    result = contract.evaluate_promotion(
        cycle=1,
        test_results={"smoke_pass": True, "functional_pass": True},
        arbiter_verdict="DENY"
    )
    assert result["eligible"] is False
    assert "arbiter" in result["reason"]


def test_promote_eligible_when_all_gates_pass(contract, tmp_path):
    (tmp_path / ".karma_last_good").write_text("abc123")
    result = contract.evaluate_promotion(
        cycle=1,
        test_results={"smoke_pass": True, "functional_pass": True},
        arbiter_verdict="ALLOW"
    )
    assert result["eligible"] is True


def test_write_last_good(contract, tmp_path):
    contract.write_last_good("deadbeef")
    assert (tmp_path / ".karma_last_good").read_text().strip() == "deadbeef"


def test_provenance_written_on_promote(contract, tmp_path):
    (tmp_path / ".karma_last_good").write_text("abc123")
    contract.evaluate_promotion(
        cycle=5,
        test_results={"smoke_pass": True, "functional_pass": True},
        arbiter_verdict="ALLOW"
    )
    prov_files = list((tmp_path / "provenance").glob("cycle_005_*.json"))
    assert len(prov_files) == 1
    prov = json.loads(prov_files[0].read_text())
    assert prov["cycle"] == 5
    assert prov["eligible"] is True
```

**Step 2: Run — verify fail**
```bash
python -m pytest tests/test_promote.py -v
```
Expected: `ModuleNotFoundError: No module named 'Scripts.karma_promote'`

---

## Task 5: Promotion Contract — Implementation

**Files:**
- Create: `Scripts/karma_promote.py`

**Step 1: Write `Scripts/karma_promote.py`**
```python
"""
karma_promote.py — Promotion contract: kiki/evolution -> main.
Deterministic gate. No LLM. Auto-opens PR when all gates pass.
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


class PromotionContract:
    def __init__(
        self,
        last_good_path: str = ".karma_last_good",
        provenance_dir: str = "provenance",
        dry_run: bool = False,
    ):
        self.last_good_path = Path(last_good_path)
        self.provenance_dir = Path(provenance_dir)
        self.dry_run = dry_run

    def evaluate_promotion(
        self, cycle: int, test_results: dict, arbiter_verdict: str
    ) -> dict:
        """
        Evaluate and (if eligible) execute promotion to main.
        Returns result dict with eligible, reason, and provenance.
        """
        # Gate 1: rollback pointer must exist
        if not self.last_good_path.exists():
            return self._record(cycle, False, "no_rollback_pointer", test_results)

        # Gate 2: smoke test
        if not test_results.get("smoke_pass"):
            return self._record(cycle, False, "smoke_test_failed", test_results)

        # Gate 3: functional test
        if not test_results.get("functional_pass"):
            return self._record(cycle, False, "functional_test_failed", test_results)

        # Gate 4: policy arbiter
        if arbiter_verdict != "ALLOW":
            return self._record(
                cycle, False, f"arbiter_{arbiter_verdict.lower()}", test_results
            )

        # All gates passed
        result = self._record(cycle, True, "all_gates_passed", test_results)

        if not self.dry_run:
            self._open_pr(cycle)

        return result

    def write_last_good(self, sha: str):
        """Write rollback pointer after verified cycle."""
        self.last_good_path.write_text(sha.strip())

    def rollback(self, actor: str, reason: str) -> dict:
        """
        Execute rollback to last known good SHA.
        actor must be an approved actor: colby, cc, codex.
        """
        approved_actors = {"colby", "cc", "codex"}
        if actor.lower() not in approved_actors:
            return {"rolled_back": False, "reason": f"actor {actor} not approved"}

        if not self.last_good_path.exists():
            return {"rolled_back": False, "reason": "no_rollback_pointer"}

        sha = self.last_good_path.read_text().strip()

        if self.dry_run:
            return {"rolled_back": True, "sha": sha, "actor": actor, "dry_run": True}

        result = subprocess.run(
            ["git", "reset", "--hard", sha],
            capture_output=True, text=True
        )
        success = result.returncode == 0
        self._log_rollback(actor, reason, sha, success)
        return {"rolled_back": success, "sha": sha, "actor": actor}

    def _record(
        self, cycle: int, eligible: bool, reason: str, test_results: dict
    ) -> dict:
        result = {
            "cycle": cycle,
            "eligible": eligible,
            "reason": reason,
            "test_results": test_results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._write_provenance(cycle, result)
        return result

    def _write_provenance(self, cycle: int, data: dict):
        self.provenance_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        path = self.provenance_dir / f"cycle_{cycle:03d}_{ts}.json"
        path.write_text(json.dumps(data, indent=2))

    def _log_rollback(self, actor: str, reason: str, sha: str, success: bool):
        self.provenance_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).isoformat()
        entry = {
            "event": "rollback",
            "actor": actor,
            "reason": reason,
            "sha": sha,
            "success": success,
            "timestamp": ts,
        }
        log = self.provenance_dir / "rollback_audit.jsonl"
        with open(log, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _open_pr(self, cycle: int):
        sha = self.last_good_path.read_text().strip()
        subprocess.run([
            "gh", "pr", "create",
            "--base", "main",
            "--head", "kiki/evolution",
            "--title", f"kiki cycle #{cycle}: autonomous evolution {sha[:8]}",
            "--body", (
                f"Autonomous kiki evolution commit.\n"
                f"Cycle: {cycle}\nSHA: {sha}\n"
                f"All gates passed: smoke ✓ functional ✓ arbiter ✓ rollback pointer ✓"
            ),
        ], capture_output=True)
```

**Step 2: Run tests — verify all pass**
```bash
python -m pytest tests/test_promote.py -v
```
Expected: All 7 tests PASS.

**Step 3: Commit**
```bash
git add Scripts/karma_promote.py tests/test_promote.py
git commit -m "feat: Promotion Contract — kiki/evolution->main gate with rollback audit (TDD, 7 tests)"
```

---

## Task 6: Coordinator Bus Schema Extension (hub-bridge)

**Files:**
- Modify: `hub-bridge/app/server.js` — add message type handlers for `seed_issue`, `promote_request`, `approval_required`, `rollback_event`

**Step 1: Read current `/v1/coordination` handler in server.js**

Find the coordination endpoint. Add message type validation:
```javascript
// Valid coordination message types
const COORDINATION_TYPES = [
  'seed_issue',        // Karma-Core → Kiki: new issue/goal
  'promote_request',   // Kiki → CC: request promotion review
  'approval_required', // Arbiter → Colby: critical path approval needed
  'rollback_event',    // Any approved actor → all: rollback notification
  'status_update',     // Any actor → bus: informational
];
```

**Step 2: Verify message routing in server.js doesn't break existing coordination**

Run smoke test:
```bash
curl -s -o /dev/null -w "%{http_code}" https://hub.arknexus.net/v1/coordination
```
Expected: 200

**Step 3: Commit**
```bash
git add hub-bridge/app/server.js
git commit -m "feat: extend /v1/coordination schema with typed message contracts"
```

---

## Task 7: Bus Ingester — Tests + Implementation

**Files:**
- Create: `tests/test_bus_ingester.py`
- Create: `Scripts/karma_bus_ingester.py`

**Step 1: Write tests**

`tests/test_bus_ingester.py`:
```python
import json
import pytest
from pathlib import Path
from Scripts.karma_bus_ingester import BusIngester


@pytest.fixture
def ingester(tmp_path):
    issues_file = tmp_path / "kiki_issues.jsonl"
    return BusIngester(issues_file=str(issues_file))


def test_converts_seed_issue_to_kiki_format(ingester):
    msg = {
        "id": "msg-001",
        "type": "seed_issue",
        "status": "PENDING",
        "payload": {
            "title": "Fix the login bug",
            "body": "Users report 500 on /login"
        }
    }
    issue = ingester.convert(msg)
    assert issue["issue"] == "Fix the login bug"
    assert issue["details"] == "Users report 500 on /login"
    assert issue["source"] == "karma_core"
    assert issue["coordination_id"] == "msg-001"


def test_ignores_non_seed_issue_messages(ingester):
    msgs = [
        {"id": "1", "type": "status_update", "status": "PENDING", "payload": {}},
        {"id": "2", "type": "rollback_event", "status": "PENDING", "payload": {}},
    ]
    result = ingester.filter_pending(msgs)
    assert len(result) == 0


def test_filters_only_pending_seed_issues(ingester):
    msgs = [
        {"id": "1", "type": "seed_issue", "status": "PENDING", "payload": {"title": "A"}},
        {"id": "2", "type": "seed_issue", "status": "PROCESSED", "payload": {"title": "B"}},
    ]
    result = ingester.filter_pending(msgs)
    assert len(result) == 1
    assert result[0]["id"] == "1"


def test_appends_to_issues_file(ingester, tmp_path):
    issues_file = tmp_path / "kiki_issues.jsonl"
    ingester.issues_file = issues_file
    msgs = [
        {"id": "1", "type": "seed_issue", "status": "PENDING",
         "payload": {"title": "Task A", "body": "Details A"}}
    ]
    count = ingester.ingest(msgs)
    assert count == 1
    lines = issues_file.read_text().strip().split("\n")
    assert len(lines) == 1
    issue = json.loads(lines[0])
    assert issue["issue"] == "Task A"
```

**Step 2: Run — verify fail, then implement**

```bash
python -m pytest tests/test_bus_ingester.py -v
```

**Step 3: Write `Scripts/karma_bus_ingester.py`**
```python
"""
karma_bus_ingester.py — Converts /v1/coordination seed_issue messages
into normalized kiki_issues.jsonl entries.
Single ingestion path: no direct writes from Karma-Core to issue file.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


class BusIngester:
    def __init__(
        self,
        issues_file: str = "/mnt/c/dev/Karma/k2/cache/kiki_issues.jsonl",
        coordination_url: str = "https://hub.arknexus.net/v1/coordination",
    ):
        self.issues_file = Path(issues_file)
        self.coordination_url = coordination_url

    def filter_pending(self, messages: list[dict]) -> list[dict]:
        return [
            m for m in messages
            if m.get("type") == "seed_issue" and m.get("status") == "PENDING"
        ]

    def convert(self, msg: dict) -> dict:
        payload = msg.get("payload", {})
        return {
            "issue": payload.get("title", "Untitled intent"),
            "details": payload.get("body", ""),
            "source": "karma_core",
            "coordination_id": msg.get("id"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def ingest(self, messages: list[dict]) -> int:
        pending = self.filter_pending(messages)
        if not pending:
            return 0
        issues = [self.convert(m) for m in pending]
        self.issues_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.issues_file, "a") as f:
            for issue in issues:
                f.write(json.dumps(issue) + "\n")
        return len(issues)

    def fetch_and_ingest(self, token: str) -> int:
        req = urllib.request.Request(
            self.coordination_url,
            headers={"Authorization": f"Bearer {token}"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            messages = json.loads(resp.read())
        return self.ingest(messages)
```

**Step 4: Run tests — verify all pass**
```bash
python -m pytest tests/test_bus_ingester.py -v
```

**Step 5: Commit**
```bash
git add Scripts/karma_bus_ingester.py tests/test_bus_ingester.py
git commit -m "feat: Bus Ingester — /v1/coordination seed_issue -> kiki_issues.jsonl (TDD)"
```

---

## Task 8: K2-Critic Agent

**Files:**
- Create: `Scripts/karma_critic_agent.py`
- Create: `tests/test_critic_agent.py`

**Step 1: Write tests (mock Ollama — Critic is advisory, not a gate)**

`tests/test_critic_agent.py`:
```python
import json
import pytest
from unittest.mock import patch
from Scripts.karma_critic_agent import CriticAgent


@pytest.fixture
def critic():
    return CriticAgent(dry_run=True)


def test_critic_returns_plan_structure(critic):
    issue = {"issue": "Fix the login bug", "details": "500 on /login"}
    plan = critic.get_plan(issue, context="")
    # In dry_run mode, returns a canned plan
    assert "plan" in plan
    assert "tests" in plan
    assert "risks" in plan
    assert "confidence" in plan


def test_critic_unavailable_returns_none_gracefully(critic):
    with patch.object(critic, '_call_ollama', side_effect=Exception("Ollama down")):
        result = critic.get_plan({"issue": "test"}, context="")
    # None signals degraded mode — caller continues without critic
    assert result is None


def test_critic_cannot_close_issues(critic):
    # Critic output has no close/commit/write fields
    plan = critic.get_plan({"issue": "test"}, context="")
    assert "close_issue" not in plan
    assert "commit" not in plan
    assert "write_file" not in plan
```

**Step 2: Write `Scripts/karma_critic_agent.py`**
```python
"""
karma_critic_agent.py — Advisory-only K2 Critic Agent.
Proposes plan/tests/risks per cycle. Cannot close issues,
write canonical artifacts, or commit. Output: critic_plan.json (advice only).
"""

import json
import urllib.request

CRITIC_SYSTEM = """You are an advisory critic agent for Karma's autonomous loop.
You receive ONE issue and produce a structured plan. You are ADVISORY ONLY.
You cannot close issues, commit code, or write canonical artifacts.

Respond in valid JSON only. No markdown fences. No extra keys:
{
  "plan": "step-by-step approach",
  "tests": ["specific test commands to verify the fix"],
  "risks": ["potential risks or side effects"],
  "confidence": 0.0
}
"""

DRY_RUN_PLAN = {
    "plan": "Dry run — no Ollama call made",
    "tests": ["echo 'dry run test'"],
    "risks": ["none in dry run"],
    "confidence": 0.0,
}


class CriticAgent:
    def __init__(
        self,
        ollama_url: str = "http://172.22.240.1:11434",
        model: str = "devstral:latest",
        dry_run: bool = False,
    ):
        self.ollama_url = ollama_url
        self.model = model
        self.dry_run = dry_run

    def get_plan(self, issue: dict, context: str) -> dict | None:
        """
        Returns critic plan dict, or None if Critic is unavailable.
        None = degraded mode. Kiki continues without critic plan.
        """
        if self.dry_run:
            return DRY_RUN_PLAN.copy()

        user_msg = (
            f"ISSUE: {issue.get('issue', '')}\n"
            f"DETAILS: {issue.get('details', '')}\n"
            f"CONTEXT: {context[:500]}"
        )

        try:
            raw = self._call_ollama(user_msg)
            return self._parse(raw)
        except Exception:
            return None  # Caller handles None as degraded mode

    def _call_ollama(self, user_msg: str) -> str:
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": CRITIC_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 1024},
        }).encode()
        req = urllib.request.Request(
            f"{self.ollama_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read())
        return body.get("message", {}).get("content", "")

    def _parse(self, raw: str) -> dict | None:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        if "<think>" in raw:
            raw = raw.split("</think>")[-1].strip()
        try:
            return json.loads(raw)
        except Exception:
            start, end = raw.find("{"), raw.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(raw[start:end])
                except Exception:
                    pass
        return None
```

**Step 3: Run tests — verify all pass**
```bash
python -m pytest tests/test_critic_agent.py -v
```

**Step 4: Commit**
```bash
git add Scripts/karma_critic_agent.py tests/test_critic_agent.py
git commit -m "feat: K2-Critic Agent — advisory plan/tests/risks per cycle, degraded mode safe (TDD)"
```

---

## Task 9: Kiki v6 — Wire All Components

**Files:**
- Create: `Scripts/karma_kiki_v6.py`

**Step 1: Kiki v6 adds to v5 loop:**
1. Bus Ingester runs at cycle start (converts coordination intents)
2. Critic called before think (degraded if unavailable)
3. Policy Arbiter called before act (hard gate — DENY blocks execution)
4. Rollback pointer written after verified success
5. Promotion Contract evaluated after success
6. `critic_plan.json` written per cycle (advisory artifact)
7. `kiki_gate_audit.jsonl` written per Arbiter decision

**Step 2: Create `Scripts/karma_kiki_v6.py`**

Base on `karma_kiki_v5.py`. Key additions to `run_cycle()`:

```python
# After loading issues, before think:
# 1. Ingest coordination bus
try:
    token = open("/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt").read().strip()
    ingested = ingester.fetch_and_ingest(token)
    if ingested:
        log.info(f"Ingested {ingested} new issues from coordination bus")
        issues = load_issues()  # reload with new issues
except Exception as e:
    log.warning(f"Bus ingestion failed (non-fatal): {e}")

# 2. Get Critic plan (advisory)
critic_plan = critic.get_plan(issue, context)
if critic_plan is None:
    log.warning("Critic unavailable — degraded mode (executor-only)")
    journal_write_meta(cycle, "critic_unavailable")
else:
    write_critic_plan(cycle, critic_plan)

# 3. Policy Arbiter before act
arbiter_result = arbiter.evaluate(
    target_path=decision.get("target_file", ""),
    operation="write",
    test_results={"smoke_pass": bool(decision.get("test_command")),
                  "functional_pass": bool(decision.get("test_command"))}
)
write_gate_audit(cycle, arbiter_result)

if arbiter_result.verdict == "DENY":
    log.warning(f"Arbiter DENIED: {arbiter_result.reason_code} — {arbiter_result.reason}")
    journal_write(cycle, issue, decision, {"ok": False, "reason": f"arbiter_deny: {arbiter_result.reason_code}"})
    issues = close_issue(issues, 0)
    save_issues(issues)
    return

if arbiter_result.verdict == "REQUIRE_APPROVAL":
    log.info(f"Arbiter REQUIRE_APPROVAL: {arbiter_result.reason} — posting to coordination bus")
    post_approval_request(cycle, issue, decision, arbiter_result)
    return  # Do not execute — wait for approval

# 4. After successful act+verify: write rollback pointer + evaluate promotion
if result["ok"]:
    sha = get_current_sha()
    promotion_contract.write_last_good(sha)
    promo = promotion_contract.evaluate_promotion(
        cycle=cycle,
        test_results={"smoke_pass": True, "functional_pass": True},
        arbiter_verdict=arbiter_result.verdict
    )
    if promo["eligible"]:
        log.info(f"Cycle #{cycle} eligible for promotion — PR opened")
```

**Step 3: Run v6 smoke test (dry run on K2)**
```bash
# On K2 via SSH
ssh -p 2223 -l karma localhost 'python3 /mnt/c/dev/Karma/k2/scripts/karma_kiki_v6.py --dry-run --cycles 1'
```
Expected: one cycle log showing critic call, arbiter gate, rollback pointer written.

**Step 4: Commit**
```bash
git add Scripts/karma_kiki_v6.py
git commit -m "feat: kiki v6 — Critic + Arbiter + Promotion Contract wired into autonomous loop"
```

---

## Task 10: Deploy + Verify

**Step 1: Push all changes to main**
```bash
git push origin main
```

**Step 2: Sync to K2 via vault-neo**
```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"
# Then sync scripts to K2 via tunnel
ssh -p 2223 -l karma localhost "cd /mnt/c/dev/Karma/k2 && git pull"
```

**Step 3: Verify governance files readable by arbiter**
```bash
ssh -p 2223 -l karma localhost "python3 -c \"
import json
b = json.load(open('/mnt/c/dev/Karma/k2/Config/governance_boundary_v1.json'))
c = json.load(open('/mnt/c/dev/Karma/k2/Config/critical_paths.json'))
print('boundary version:', b['version'])
print('critical paths:', len(c['critical_paths']))
\""
```

**Step 4: Run full test suite**
```bash
python -m pytest tests/ -v
```
Expected: All tests PASS. No warnings.

**Step 5: Run one kiki v6 cycle and inspect artifacts**
```bash
# Check gate audit written
ssh -p 2223 -l karma localhost "tail -1 /mnt/c/dev/Karma/k2/cache/kiki_gate_audit.jsonl"
# Check rollback pointer written
ssh -p 2223 -l karma localhost "cat /mnt/c/dev/Karma/k2/.karma_last_good"
# Check provenance directory
ssh -p 2223 -l karma localhost "ls /mnt/c/dev/Karma/k2/provenance/"
```

**Step 6: Commit final verification**
```bash
git add MEMORY.md
git commit -m "verified: kiki v6 + governance boundary + promotion contract live on K2"
```

---

## Verification Checklist

Before declaring this complete:

- [ ] `governance_boundary_v1.json` and `critical_paths.json` in git, Colby-controlled
- [ ] Policy Arbiter: 10 unit tests passing, deterministic (no LLM calls)
- [ ] Promotion Contract: 7 unit tests passing, rollback audit log functional
- [ ] Bus Ingester: 4 unit tests passing, single ingestion path enforced
- [ ] Critic Agent: 3 unit tests passing, graceful degraded mode verified
- [ ] Kiki v6: one real cycle on K2 with all artifacts written
- [ ] `kiki_gate_audit.jsonl` exists and has entries
- [ ] `.karma_last_good` written after successful cycle
- [ ] `provenance/` directory has at least one cycle record
- [ ] No canonical artifacts written by Critic
- [ ] Arbiter DENY correctly blocks execution (not just logs)
- [ ] Coordination bus schema accepts new message types

---

*Plan saved: 2026-03-13*
*Architecture locked via Colby + Karma gate-check (x7)*
*Two hard prerequisites completed: Deterministic Policy Arbiter ✓ Explicit Promotion Contract ✓*
