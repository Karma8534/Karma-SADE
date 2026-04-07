#!/usr/bin/env python3
"""Workspace-local pipeline utilities for Vesper eval/governor flows."""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator

import regent_guardrails as guardrails

Path = Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
VESPER_ROOT = WORKSPACE_ROOT / "Vesper"
DEFAULT_RUNTIME_ROOT = VESPER_ROOT / "runtime"
EVAL_ROOT = Path(os.environ.get("REGENT_EVAL_ROOT", str(DEFAULT_RUNTIME_ROOT))).resolve()

CONTROL_DIR = EVAL_ROOT / "control"
CHECKPOINT_DIR = EVAL_ROOT / "checkpoints"
CACHE_DIR = EVAL_ROOT / "cache"
CANDIDATE_DIR = EVAL_ROOT / "candidates"
EVAL_DIR = EVAL_ROOT / "evals"
PROMOTION_DIR = EVAL_ROOT / "promotions"
FALKOR_OUTBOX_DIR = EVAL_ROOT / "falkor_outbox"

IDENTITY_CONTRACT_FILE = CONTROL_DIR / "identity_contract.json"
SESSION_SCHEMA_FILE = CONTROL_DIR / "session_schema.json"
EVOLUTION_POLICY_FILE = CONTROL_DIR / "evolution_policy.md"
EVAL_SPEC_FILE = CONTROL_DIR / "eval_gate_spec.md"
SESSION_STATE_FILE = CONTROL_DIR / "regent_session_state.json"
SPINE_FILE = CONTROL_DIR / "identity_spine.json"
GOVERNOR_AUDIT = CONTROL_DIR / "governor_audit.jsonl"
EVAL_AUDIT = CONTROL_DIR / "eval_audit.jsonl"


def iso_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_fingerprint(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def slugify(value: Any, max_length: int = 64) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    text = re.sub(r"-{2,}", "-", text)
    return (text[:max_length] or "item").strip("-") or "item"


def read_json(path: Path | str, default: Any = None) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path | str, payload: Any) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return p


def read_jsonl(path: Path | str) -> Iterator[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return iter(())

    def _iter() -> Iterator[Dict[str, Any]]:
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            text = line.strip()
            if not text:
                continue
            try:
                payload = json.loads(text)
            except Exception:
                continue
            if isinstance(payload, dict):
                yield payload

    return _iter()


def append_jsonl(path: Path | str, payload: Dict[str, Any]) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
    return p


def _default_spine() -> Dict[str, Any]:
    return {
        "schema_version": "1.0",
        "updated_utc": iso_utc(),
        "evolution": {
            "version": 1,
            "stable_identity": [],
            "candidate_patterns": [],
        },
    }


def ensure_pipeline_dirs() -> None:
    for directory in (
        EVAL_ROOT,
        CONTROL_DIR,
        CHECKPOINT_DIR,
        CACHE_DIR,
        CANDIDATE_DIR,
        EVAL_DIR,
        PROMOTION_DIR,
        FALKOR_OUTBOX_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    guardrails.ensure_control_artifacts(
        IDENTITY_CONTRACT_FILE,
        SESSION_SCHEMA_FILE,
        EVOLUTION_POLICY_FILE,
        EVAL_SPEC_FILE,
        SESSION_STATE_FILE,
    )

    if not SPINE_FILE.exists():
        write_json(SPINE_FILE, _default_spine())

    for audit_path in (GOVERNOR_AUDIT, EVAL_AUDIT):
        if not audit_path.exists():
            audit_path.write_text("", encoding="utf-8")


def list_candidate_files() -> Iterable[Path]:
    ensure_pipeline_dirs()
    return sorted(CANDIDATE_DIR.glob("candidate-*.json"))


def update_candidate_status(path: Path | str, status: str, extra: Dict[str, Any] | None = None) -> Path:
    p = Path(path)
    payload = read_json(p, {}) or {}
    payload["status"] = status
    payload["updated_utc"] = iso_utc()
    if extra:
        payload.update(extra)
    return write_json(p, payload)
