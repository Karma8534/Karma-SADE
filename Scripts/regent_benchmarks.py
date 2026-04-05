#!/usr/bin/env python3
"""Eval prompt and heuristic helpers for Vesper candidates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


DEFAULT_SUITES = {
    "identity_consistency": {
        "keywords": ["identity", "coherence", "continuity", "memory", "persona", "spine"],
        "weight": 1.0,
    },
    "persona_style": {
        "keywords": ["terse", "precise", "direct", "rigor", "non-servile", "clear"],
        "weight": 1.0,
    },
    "session_continuity": {
        "keywords": ["session", "history", "restart", "transcript", "resume", "persist"],
        "weight": 1.0,
    },
    "task_completion": {
        "keywords": ["test", "verify", "proof", "diff", "implemented", "applied", "working"],
        "weight": 1.0,
    },
}


def ensure_default_suites(eval_root: Path | str) -> Dict[str, Any]:
    root = Path(eval_root)
    root.mkdir(parents=True, exist_ok=True)
    suites_path = root / "benchmark_suites.json"
    if not suites_path.exists():
        suites_path.write_text(json.dumps(DEFAULT_SUITES, indent=2) + "\n", encoding="utf-8")
        return DEFAULT_SUITES
    try:
        payload = json.loads(suites_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and payload:
            return payload
    except Exception:
        pass
    suites_path.write_text(json.dumps(DEFAULT_SUITES, indent=2) + "\n", encoding="utf-8")
    return DEFAULT_SUITES


def build_eval_prompt(candidate: Dict[str, Any], suites: Dict[str, Any]) -> str:
    prompt = {
        "task": "Score the candidate on 0.0-1.0 for identity_consistency, persona_style, session_continuity, task_completion. Return JSON only.",
        "candidate": candidate,
        "metric_hints": suites,
        "requirements": [
            "Use conservative scoring.",
            "A candidate without proof or concrete execution should score lower on task_completion.",
            "Behavioral and observational candidates can still score high if evidence is coherent.",
        ],
    }
    return json.dumps(prompt, indent=2)


def heuristic_metric_scores(candidate: Dict[str, Any], suites: Dict[str, Any]) -> Dict[str, float]:
    text_parts = [
        candidate.get("type", ""),
        json.dumps(candidate.get("evidence", {}), ensure_ascii=True),
        json.dumps(candidate.get("proposed_change", {}), ensure_ascii=True),
        candidate.get("summary", ""),
        candidate.get("description", ""),
    ]
    haystack = " ".join(part for part in text_parts if part).lower()
    scores: Dict[str, float] = {}

    for metric, spec in suites.items():
        keywords = [str(item).lower() for item in (spec or {}).get("keywords", [])]
        if not keywords:
            scores[metric] = 0.25
            continue
        hits = sum(1 for keyword in keywords if keyword in haystack)
        ratio = hits / max(1, len(keywords))
        base = 0.25 + min(0.65, ratio * 0.75)
        if metric == "task_completion":
            proposed = candidate.get("proposed_change", {}) or {}
            if proposed.get("diff"):
                base += 0.1
            if proposed.get("test_command"):
                base += 0.1
        scores[metric] = round(min(1.0, base), 3)

    return scores


def merge_metric_scores(
    heuristic_scores: Dict[str, float],
    model_scores: Dict[str, float],
    model_weight: float = 0.6,
) -> Dict[str, float]:
    model_weight = max(0.0, min(1.0, float(model_weight)))
    heuristic_weight = 1.0 - model_weight
    merged: Dict[str, float] = {}
    for metric in set(heuristic_scores) | set(model_scores):
        h_val = float(heuristic_scores.get(metric, 0.0))
        m_val = float(model_scores.get(metric, h_val))
        merged[metric] = round((h_val * heuristic_weight) + (m_val * model_weight), 3)
    return merged
