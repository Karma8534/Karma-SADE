#!/usr/bin/env python3
"""Regent guardrails for identity/session cohesion.

This module enforces a constrained runtime contract:
1) Identity contract must be present and checksum-valid.
2) Contract checksum must stay stable during runtime (unless reboot/reseeded).
3) Session state must be read before each turn and written after each turn.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional

REQUIRED_CONTRACT_FIELDS = (
    "contract_id",
    "name",
    "mission",
    "non_negotiables",
    "runtime_rules",
)


def _utc_now() -> str:
    return _dt.datetime.utcnow().isoformat() + "Z"


def _canonical_contract_payload(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Return identity payload used for checksum calculation."""
    return {
        k: v
        for k, v in contract.items()
        if k not in {"contract_checksum", "last_updated_utc"}
    }


def compute_contract_checksum(contract: Dict[str, Any]) -> str:
    payload = _canonical_contract_payload(contract)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _default_identity_contract() -> Dict[str, Any]:
    contract = {
        "contract_id": "regent_identity_v1",
        "name": "Vesper",
        "mission": (
            "Maintain coherent Regent identity and enforce continuity before "
            "optimization, routing, or evolution."
        ),
        "persona": {
            "voice": ["terse", "precise", "non-servile"],
            "forbidden_phrases": [
                "thank you for your kind words",
                "i am here to help",
                "how can i help",
            ],
        },
        "non_negotiables": [
            "No identity drift claims without evidence.",
            "No fabricated status, tasks, or priorities.",
            "If unknown, state unknown and preserve continuity.",
            "Never mutate identity contract in-process.",
        ],
        "runtime_rules": {
            "reject_if_checksum_changed": True,
            "require_session_state_read_before_write": True,
            "history_limit": 40,
        },
        "last_updated_utc": _utc_now(),
    }
    contract["contract_checksum"] = compute_contract_checksum(contract)
    return contract


def _default_session_schema() -> Dict[str, Any]:
    return {
        "schema_version": "1.0",
        "required": [
            "schema_version",
            "turn_index",
            "active_goals",
            "open_promises",
            "unresolved_tasks",
            "corrections_log",
            "emotional_stance",
            "last_actor",
            "last_msg_id",
            "last_user_input",
            "last_response",
            "last_category",
            "last_turn_utc",
            "quality_metrics",
            "history",
        ],
        "properties": {
            "turn_index": "integer",
            "active_goals": "array",
            "open_promises": "array",
            "unresolved_tasks": "array",
            "corrections_log": "array",
            "emotional_stance": "string",
            "last_actor": "string",
            "last_msg_id": "string",
            "last_user_input": "string",
            "last_response": "string",
            "last_category": "string",
            "last_turn_utc": "string",
            "quality_metrics": "object",
            "history": "array",
        },
    }


def _default_session_state(schema_version: str = "1.0") -> Dict[str, Any]:
    return {
        "schema_version": schema_version,
        "turn_index": 0,
        "active_goals": [],
        "open_promises": [],
        "unresolved_tasks": [],
        "corrections_log": [],
        "emotional_stance": "focused",
        "last_actor": "",
        "last_msg_id": "",
        "last_user_input": "",
        "last_response": "",
        "last_category": "",
        "last_turn_utc": "",
        "quality_metrics": {
            "identity_consistency": 1.0,
            "persona_style": 1.0,
            "session_continuity": 1.0,
            "task_completion": 0.5,
        },
        "history": [],
    }


def ensure_control_artifacts(
    identity_path: Path,
    schema_path: Path,
    policy_path: Path,
    eval_path: Path,
    session_state_path: Path,
) -> None:
    identity_path.parent.mkdir(parents=True, exist_ok=True)
    session_state_path.parent.mkdir(parents=True, exist_ok=True)

    if not identity_path.exists():
        identity_path.write_text(
            json.dumps(_default_identity_contract(), indent=2) + "\n",
            encoding="utf-8",
        )

    if not schema_path.exists():
        schema_path.write_text(
            json.dumps(_default_session_schema(), indent=2) + "\n",
            encoding="utf-8",
        )

    if not policy_path.exists():
        policy_path.write_text(
            "# Evolution Policy\n\n"
            "## Runtime\n"
            "- Runtime proposes changes only.\n"
            "- Runtime cannot self-apply identity or policy mutations.\n\n"
            "## Learner\n"
            "- Learner generates candidate patches and evaluation notes.\n"
            "- Learner cannot deploy directly.\n\n"
            "## Governor\n"
            "- Governor applies changes only when eval gates pass.\n"
            "- Governor records evidence and rollback checkpoint for every apply.\n",
            encoding="utf-8",
        )

    if not eval_path.exists():
        eval_path.write_text(
            "# Eval Gate Spec\n\n"
            "Required metrics (0.0-1.0):\n"
            "- identity_consistency >= 0.90\n"
            "- persona_style >= 0.80\n"
            "- session_continuity >= 0.80\n"
            "- task_completion >= 0.70\n\n"
            "Gate behavior:\n"
            "- If any metric fails, block evolution apply.\n"
            "- Runtime may continue serving, but must log failure reason.\n",
            encoding="utf-8",
        )

    if not session_state_path.exists():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        session_state_path.write_text(
            json.dumps(
                _default_session_state(schema_version=schema.get("schema_version", "1.0")),
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_identity_contract(identity_path: Path) -> Dict[str, Any]:
    if not identity_path.exists():
        return {"ok": False, "error": f"identity contract missing: {identity_path}"}
    try:
        contract = _load_json(identity_path)
    except Exception as exc:
        return {"ok": False, "error": f"identity contract parse error: {exc}"}

    missing = [k for k in REQUIRED_CONTRACT_FIELDS if k not in contract]
    if missing:
        return {"ok": False, "error": f"identity contract missing fields: {missing}"}

    current_checksum = compute_contract_checksum(contract)
    declared_checksum = contract.get("contract_checksum", "")
    if not declared_checksum:
        return {"ok": False, "error": "identity contract missing contract_checksum"}
    if declared_checksum != current_checksum:
        return {
            "ok": False,
            "error": "identity contract checksum mismatch",
            "declared_checksum": declared_checksum,
            "current_checksum": current_checksum,
        }

    return {"ok": True, "contract": contract, "checksum": current_checksum}


def load_session_state(schema_path: Path, session_state_path: Path) -> Dict[str, Any]:
    if not schema_path.exists():
        return {"ok": False, "error": f"session schema missing: {schema_path}"}
    if not session_state_path.exists():
        return {"ok": False, "error": f"session state missing: {session_state_path}"}

    try:
        schema = _load_json(schema_path)
        state = _load_json(session_state_path)
    except Exception as exc:
        return {"ok": False, "error": f"session state/schema parse error: {exc}"}

    required = schema.get("required", [])
    missing = [k for k in required if k not in state]
    if missing:
        return {"ok": False, "error": f"session state missing fields: {missing}"}

    return {"ok": True, "schema": schema, "state": state}


def begin_turn(
    identity_path: Path,
    schema_path: Path,
    session_state_path: Path,
    expected_checksum: Optional[str],
) -> Dict[str, Any]:
    contract_result = load_identity_contract(identity_path)
    if not contract_result.get("ok"):
        return {"ok": False, "error": contract_result.get("error")}

    current_checksum = contract_result["checksum"]
    if expected_checksum and current_checksum != expected_checksum:
        return {
            "ok": False,
            "error": (
                "identity checksum changed during runtime; generation blocked "
                "until explicit restart/reseed"
            ),
            "expected_checksum": expected_checksum,
            "current_checksum": current_checksum,
        }

    state_result = load_session_state(schema_path, session_state_path)
    if not state_result.get("ok"):
        return {"ok": False, "error": state_result.get("error")}

    return {
        "ok": True,
        "current_checksum": current_checksum,
        "contract": contract_result["contract"],
        "session_state": state_result["state"],
        "schema": state_result["schema"],
    }


def evaluate_turn_quality(response_text: str, session_state: Dict[str, Any]) -> Dict[str, float]:
    text = (response_text or "").lower()
    forbidden = [
        "thank you for your kind words",
        "i am here to help",
        "how can i help",
    ]
    identity_consistency = 0.0 if any(p in text for p in forbidden) else 1.0
    persona_style = 1.0 if len(response_text or "") <= 900 else 0.7
    session_continuity = 1.0 if session_state.get("turn_index", 0) >= 0 else 0.0
    task_completion = 0.8 if (response_text or "").strip() else 0.0
    return {
        "identity_consistency": round(identity_consistency, 3),
        "persona_style": round(persona_style, 3),
        "session_continuity": round(session_continuity, 3),
        "task_completion": round(task_completion, 3),
    }


def finalize_turn(
    session_state_path: Path,
    session_state: Dict[str, Any],
    from_addr: str,
    msg_id: str,
    user_input: str,
    response_text: str,
    category: str,
    history_limit: int = 40,
) -> Dict[str, Any]:
    state = dict(session_state)
    state["turn_index"] = int(state.get("turn_index", 0)) + 1
    state["last_actor"] = from_addr
    state["last_msg_id"] = msg_id
    state["last_user_input"] = (user_input or "")[:1200]
    state["last_response"] = (response_text or "")[:1200]
    state["last_category"] = category
    state["last_turn_utc"] = _utc_now()
    state["quality_metrics"] = evaluate_turn_quality(response_text or "", state)

    history = list(state.get("history", []))
    history.append(
        {
            "ts": state["last_turn_utc"],
            "from": from_addr,
            "msg_id": msg_id,
            "category": category,
            "user": (user_input or "")[:300],
            "assistant": (response_text or "")[:300],
        }
    )
    state["history"] = history[-max(1, int(history_limit)) :]

    session_state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return state

