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
