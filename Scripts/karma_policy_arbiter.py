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
