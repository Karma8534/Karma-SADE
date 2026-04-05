#!/usr/bin/env python3
"""Governor gate thresholds for candidate promotion."""

from __future__ import annotations

from typing import Dict


DEFAULT_THRESHOLDS = {
    "identity_consistency": 0.90,
    "persona_style": 0.80,
    "session_continuity": 0.80,
    "task_completion": 0.70,
}

OBSERVATIONAL_TYPES = {
    "behavioral_continuity",
    "tool_utilization_repair",
    "tool_utilization_strength",
    "research_skill_card",
    "ambient_observation",
    "verbosity_correction",
    "claude_dependency",
    "PITFALL",
}


def resolve_governor_decision(gate_metrics: Dict[str, float], candidate_type: str = "") -> Dict[str, object]:
    thresholds = dict(DEFAULT_THRESHOLDS)
    if candidate_type in OBSERVATIONAL_TYPES:
        thresholds["task_completion"] = 0.55

    failures = []
    for metric, minimum in thresholds.items():
        actual = float(gate_metrics.get(metric, 0.0))
        if actual < minimum:
            failures.append(
                {
                    "metric": metric,
                    "actual": round(actual, 3),
                    "minimum": round(minimum, 3),
                }
            )

    passed = not failures
    decision = "approve" if passed else "reject"
    if passed:
        reason = "gate_passed"
    else:
        reason = "gate_failed:" + ",".join(item["metric"] for item in failures)

    return {
        "approved": passed,
        "decision": decision,
        "reason": reason,
        "gate": {
            "passed": passed,
            "failures": failures,
            "metrics": {k: round(float(v), 3) for k, v in gate_metrics.items()},
            "thresholds": thresholds,
        },
        "override": {
            "active": False,
            "reason": "",
        },
    }
