#!/usr/bin/env python3
"""Vesper Governor — applies approved promotion artifacts to identity spine.
Run by systemd timer every 2 hours.

Uses Codex's regent_* modules.
Never mutates identity_contract.json directly.
"""
import json
import os
import subprocess
import time
import urllib.request

import regent_guardrails as guardrails
import regent_pipeline as pipeline

SAFE_TARGETS = {"persona.voice", "runtime_rules", "safe_exec", "behavioral_awareness", "gap_closure", "self_edit", None}

SAFE_EXEC_WHITELIST = {
    "systemctl restart karma-regent",
    "python3 /mnt/c/dev/Karma/k2/Aria/tools/vesper_truth_repair.py",
    "python3 /mnt/c/dev/Karma/k2/Aria/vesper_watchdog.py",
    "python3 /mnt/c/dev/Karma/k2/Aria/vesper_eval.py",
}


def _safe_exec(command: str) -> bool:
    """Execute a whitelisted governance command. Returns True on success."""
    import subprocess
    if command not in SAFE_EXEC_WHITELIST:
        print(f"[governor] BLOCKED safe_exec: not in whitelist: {command!r}")
        return False
    try:
        result = subprocess.run(
            command.split(), capture_output=True, text=True, timeout=30
        )
        print(f"[governor] safe_exec exit={result.returncode}: {command!r}")
        if result.stdout:
            print(f"[governor] stdout: {result.stdout[:200]}")
        return result.returncode == 0
    except Exception as e:
        print(f"[governor] safe_exec error: {e}")
        return False

IDENTITY_PATH = pipeline.IDENTITY_CONTRACT_FILE
_ENV_FILE = os.environ.get("REGENT_ENV_FILE", "/etc/karma-regent.env")
_SYNTHETIC_MARKERS = ("codex", "e2e", "pipeline_validation")


def _load_env_file() -> dict:
    path = _ENV_FILE
    if not os.path.exists(path):
        return {}
    out = {}
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                if "=" not in line or line.strip().startswith("#"):
                    continue
                key, value = line.split("=", 1)
                out[key.strip()] = value.strip()
    except Exception:
        return {}
    return out


_FILE_ENV = _load_env_file()


def _env_get(key: str, default: str = "") -> str:
    val = os.environ.get(key)
    if val is not None and str(val).strip() != "":
        return str(val).strip()
    return str(_FILE_ENV.get(key, default)).strip()


def _is_synthetic_candidate_id(candidate_id: str) -> bool:
    text = (candidate_id or "").lower()
    return any(token in text for token in _SYNTHETIC_MARKERS)


def _validate_contract():
    result = guardrails.load_identity_contract(IDENTITY_PATH)
    if not result.get("ok"):
        return False, result.get("error", "checksum validation failed")
    return True, result["checksum"]


def _find_eval_artifact(eval_id: str):
    if not eval_id:
        return None
    for path in pipeline.EVAL_DIR.glob("eval-*.json"):
        payload = pipeline.read_json(path, {})
        if payload.get("eval_id") == eval_id:
            return payload
    return None


def _promotion_governance_ok(promo: dict):
    """Strict gate: apply only if eval gate passed with non-override approval."""
    eval_id = promo.get("eval_id", "")
    ev = _find_eval_artifact(eval_id)
    if not ev:
        return False, "missing_eval_artifact"

    eval_candidate = ev.get("candidate_id")
    promo_candidate = promo.get("candidate_id")
    if eval_candidate and promo_candidate and eval_candidate != promo_candidate:
        return False, "candidate_id_mismatch"

    gate_passed = bool(ev.get("governor_decision", {}).get("gate", {}).get("passed", False))
    decision_kind = ev.get("governor_decision", {}).get("decision", "")
    if not gate_passed:
        return False, "eval_gate_not_passed"
    if decision_kind != "approve":
        return False, f"decision_kind_blocked:{decision_kind or 'unknown'}"

    # Snapshot integrity: prevent promo tampering between eval and apply.
    eval_sha = ev.get("candidate_snapshot_sha256", "")
    promo_sha = promo.get("candidate_snapshot_sha256", "")
    live_sha = pipeline.stable_fingerprint(promo.get("candidate_snapshot", {}))
    if eval_sha and eval_sha != live_sha:
        return False, "candidate_snapshot_sha_mismatch_eval"
    if promo_sha and promo_sha != live_sha:
        return False, "candidate_snapshot_sha_mismatch_promo"

    return True, "ok"


def _checkpoint(candidate: dict) -> dict:
    """Snapshot identity-critical files before apply."""
    import hashlib
    ckpt_id = f"ckpt-{pipeline.iso_utc().replace(':', '').replace('-', '')[:16]}-{pipeline.slugify(candidate.get('candidate_id', 'unknown'), 30)}"
    ckpt_dir = pipeline.CHECKPOINT_DIR / ckpt_id
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for src in (pipeline.SPINE_FILE, pipeline.SESSION_STATE_FILE, IDENTITY_PATH):
        if src.exists():
            content = src.read_bytes()
            dest = ckpt_dir / src.name
            dest.write_bytes(content)
            files.append({"path": str(dest), "sha256": hashlib.sha256(content).hexdigest()})
    return {"checkpoint_id": ckpt_id, "candidate_id": candidate.get("candidate_id"),
            "created_utc": pipeline.iso_utc(), "files": files}


def _http_json_post(url: str, payload: dict, headers: dict, timeout: int = 6) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="ignore")
            status = int(getattr(response, "status", 200))
            return {"ok": 200 <= status < 300, "status": status, "body": body}
    except Exception as exc:
        msg = str(exc)
        status = None
        if "HTTP Error " in msg:
            try:
                status = int(msg.split("HTTP Error ", 1)[1].split(":", 1)[0])
            except Exception:
                status = None
        return {"ok": False, "status": status, "error": msg[:240]}


def _falkor_http_targets() -> list:
    hub_base = (_env_get("HUB_BASE_URL", "") or "https://hub.arknexus.net").rstrip("/")
    token = _env_get("HUB_AUTH_TOKEN", "")
    aria_key = _env_get("ARIA_SERVICE_KEY", "")
    explicit = _env_get("FALKOR_WRITE_URL", "")

    targets = []
    if explicit:
        targets.append({"mode": "cypher", "url": explicit, "auth": "bearer"})
    targets.extend(
        [
            {"mode": "cypher", "url": f"{hub_base}/v1/cypher", "auth": "bearer"},
            {"mode": "tool", "url": f"{hub_base}/api/tools/execute", "auth": "aria"},
        ]
    )

    deduped = []
    seen = set()
    for item in targets:
        key = (item["mode"], item["url"])
        if key in seen:
            continue
        seen.add(key)
        item["token"] = token if item["auth"] == "bearer" else aria_key
        deduped.append(item)
    return deduped


def _write_pattern_to_falkor_http(cypher: str) -> dict:
    attempts = []
    for target in _falkor_http_targets():
        token = target.get("token", "")
        if not token:
            attempts.append(
                {
                    "url": target["url"],
                    "mode": target["mode"],
                    "ok": False,
                    "reason": "missing_token",
                }
            )
            continue
        if target["mode"] == "tool":
            headers = {"Content-Type": "application/json", "X-Aria-Service-Key": token}
            payload = {"tool": "graph_query", "input": {"cypher": cypher}}
        else:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }
            payload = {"query": cypher}
        result = _http_json_post(target["url"], payload, headers=headers, timeout=6)
        attempt = {"url": target["url"], "mode": target["mode"], **result}
        attempts.append(attempt)
        if result.get("ok"):
            if target["mode"] == "tool":
                try:
                    parsed = json.loads(result.get("body", "") or "{}")
                except Exception:
                    parsed = {}
                if not bool(parsed.get("ok")):
                    continue
            return {
                "attempted": True,
                "success": True,
                "channel": "http",
                "endpoint": target["url"],
                "attempts": attempts,
            }
    return {
        "attempted": bool(attempts),
        "success": False,
        "reason": "all_http_targets_failed",
        "attempts": attempts,
    }


def _write_pattern_to_falkor_ssh(cypher: str) -> dict:
    target = _env_get("REGENT_FALKOR_SSH_TARGET", "neo@64.225.13.144")
    if not target:
        return {"attempted": False, "success": False, "reason": "missing_ssh_target"}

    connect_timeout = max(4, int(_env_get("REGENT_FALKOR_SSH_CONNECT_TIMEOUT", "8")))
    remote_py = (
        "import json, urllib.request\n"
        "payload={'tool_name':'graph_query','tool_input':{'cypher':"
        + repr(cypher)
        + "}}\n"
        "req=urllib.request.Request('http://127.0.0.1:8340/v1/tools/execute',\n"
        "    data=json.dumps(payload).encode('utf-8'),\n"
        "    headers={'Content-Type':'application/json'}, method='POST')\n"
        "with urllib.request.urlopen(req, timeout=8) as r:\n"
        "    print(r.read().decode('utf-8','ignore'))\n"
    )
    remote_cmd = f"python3 - <<'PY'\n{remote_py}PY"
    cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={connect_timeout}",
        target,
        remote_cmd,
    ]
    try:
        run = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=connect_timeout + 12,
        )
        if run.returncode != 0:
            return {
                "attempted": True,
                "success": False,
                "reason": f"ssh_exit_{run.returncode}",
                "stderr": (run.stderr or "")[:240],
            }
        output = (run.stdout or "").strip()
        if not output:
            return {
                "attempted": True,
                "success": False,
                "reason": "ssh_empty_response",
            }
        try:
            payload = json.loads(output)
        except Exception:
            payload = {}
        if bool(payload.get("ok")) and bool((payload.get("result") or {}).get("ok")):
            return {
                "attempted": True,
                "success": True,
                "channel": "ssh_tool",
                "endpoint": "ssh://neo@64.225.13.144 -> http://127.0.0.1:8340/v1/tools/execute",
            }
        return {
            "attempted": True,
            "success": False,
            "reason": "ssh_tool_error",
            "response_excerpt": output[:240],
        }
    except Exception as exc:
        return {
            "attempted": True,
            "success": False,
            "reason": f"ssh_exception:{str(exc)[:180]}",
        }


def _queue_falkor_outbox(pattern: dict, cypher: str, status: dict) -> str:
    payload = {
        "queued_utc": pipeline.iso_utc(),
        "candidate_id": pattern.get("candidate_id"),
        "type": pattern.get("type"),
        "confidence": pattern.get("confidence"),
        "cypher": cypher,
        "status": status,
    }
    path = (
        pipeline.FALKOR_OUTBOX_DIR
        / f"falkor-{pipeline.slugify(pattern.get('candidate_id', 'unknown'))}-{pipeline.iso_utc().replace(':', '').replace('-', '')}.json"
    )
    pipeline.write_json(path, payload)
    return str(path)


def _write_pattern_to_falkor(pattern: dict, allow_queue: bool = True) -> dict:
    """Best-effort Falkor write with explicit status for auditability."""
    try:
        cid = (pattern.get("candidate_id") or "unknown")[:60].replace("'", "")
        ctype = (pattern.get("type") or "behavioral")[:40].replace("'", "")
        conf = float(pattern.get("confidence") or 0)
        cat = "stable" if conf >= 0.7 else "candidate"
        ts = pipeline.iso_utc()
        cypher = (
            f"MERGE (p:Pattern {{candidate_id: '{cid}'}}) "
            f"SET p.type='{ctype}', p.confidence={conf}, "
            f"p.promoted_at='{ts}', p.category='{cat}'"
        )
        http_status = _write_pattern_to_falkor_http(cypher)
        if http_status.get("success"):
            return http_status

        ssh_status = _write_pattern_to_falkor_ssh(cypher)
        if ssh_status.get("success"):
            return {
                "attempted": True,
                "success": True,
                "channel": ssh_status.get("channel", "ssh_tool"),
                "endpoint": ssh_status.get("endpoint", ""),
                "http_attempts": http_status.get("attempts", []),
            }

        combined = {
            "attempted": True,
            "success": False,
            "reason": "falkor_write_failed",
            "http": http_status,
            "ssh": ssh_status,
        }
        if allow_queue:
            outbox_path = _queue_falkor_outbox(pattern, cypher, combined)
            combined["queued"] = True
            combined["outbox_path"] = outbox_path
        return combined
    except Exception as e:
        return {"attempted": True, "success": False, "reason": str(e)[:240]}


def _drain_falkor_outbox(max_items: int = 10) -> dict:
    replayed = 0
    failed = 0
    outbox_files = sorted(pipeline.FALKOR_OUTBOX_DIR.glob("falkor-*.json"))[: max(0, max_items)]
    for path in outbox_files:
        payload = pipeline.read_json(path, {})
        pattern = {
            "candidate_id": payload.get("candidate_id", ""),
            "type": payload.get("type", "behavioral"),
            "confidence": payload.get("confidence", 0.0),
        }
        status = _write_pattern_to_falkor(pattern, allow_queue=False)
        if status.get("success"):
            path.unlink(missing_ok=True)
            replayed += 1
            pipeline.append_jsonl(
                pipeline.GOVERNOR_AUDIT,
                {
                    "ts": pipeline.iso_utc(),
                    "event": "outbox_replayed",
                    "candidate_id": pattern.get("candidate_id"),
                    "outbox_file": str(path),
                    "status": status,
                },
            )
            continue

        payload["last_retry_utc"] = pipeline.iso_utc()
        payload["last_retry_status"] = status
        pipeline.write_json(path, payload)
        failed += 1
    return {"replayed": replayed, "failed": failed, "checked": len(outbox_files)}



def _retire_stale_patterns() -> int:
    """F-3: Adaptive forgetting — decay and retire patterns unreinforced for 30+ days."""
    import datetime
    try:
        spine = pipeline.read_json(pipeline.SPINE_FILE, {})
        evo = spine.get("evolution", {})
        stable = evo.get("stable_identity", [])
        if not stable:
            return 0
        now = datetime.datetime.utcnow()
        updated = []
        retired = 0
        for p in stable:
            reinforced_at = p.get("reinforced_at") or p.get("promoted_at", "")
            try:
                ref_dt = datetime.datetime.fromisoformat(reinforced_at.rstrip("Z"))
                days_silent = (now - ref_dt).days
            except Exception:
                updated.append(p)
                continue
            if days_silent >= 30:
                weeks_over = max(0, (days_silent - 30) // 7)
                cur_momentum = float(p.get("momentum", 1.0))
                decayed = round(cur_momentum * (0.9 ** weeks_over), 3)
                p["momentum"] = decayed
                if decayed < 0.3:
                    pipeline.append_jsonl(pipeline.GOVERNOR_AUDIT, {
                        "ts": pipeline.iso_utc(), "event": "retired",
                        "candidate_id": p.get("candidate_id"),
                        "pattern_type": p.get("type"),
                        "reason": f"momentum_decayed:{decayed}",
                        "days_silent": days_silent,
                        "momentum": decayed,
                    })
                    retired += 1
                    continue
            updated.append(p)
        if retired > 0:
            evo["stable_identity"] = updated
            evo["version"] = evo.get("version", 1) + 1
            spine["evolution"] = evo
            pipeline.write_json(pipeline.SPINE_FILE, spine)
            print(f"[governor] retired {retired} stale patterns (F-3)")
        return retired
    except Exception as e:
        print(f"[governor] _retire_stale_patterns error: {e}")
        return 0


def _smoke_test_promotion(promo: dict) -> tuple:
    """Run test_command from candidate if present. Returns (passed: bool, detail: str)."""
    candidate_snap = promo.get("candidate_snapshot", {})
    proposed = candidate_snap.get("proposed_change", {}) or {}
    test_cmd = proposed.get("test_command", "").strip()
    if not test_cmd:
        return True, "no_test_command"  # observational candidates pass by default
    try:
        result = subprocess.run(
            test_cmd, shell=True, capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return True, f"test_passed: {test_cmd}"
        return False, f"test_failed (exit {result.returncode}): {(result.stderr or result.stdout or '')[:200]}"
    except subprocess.TimeoutExpired:
        return False, f"test_timeout (60s): {test_cmd}"
    except Exception as e:
        return False, f"test_error: {e}"


def _apply_to_spine(candidate: dict):
    try:
        spine = pipeline.read_json(pipeline.SPINE_FILE, {})
        if "evolution" not in spine:
            spine["evolution"] = {"version": 1, "stable_identity": [], "candidate_patterns": []}

        evo = spine["evolution"]
        candidate_snap = candidate.get("candidate_snapshot", {})
        pattern = {
            "type":            candidate_snap.get("type", candidate.get("type")),
            "candidate_id":    candidate.get("candidate_id"),
            "promoted_at":     pipeline.iso_utc(),
            "evidence":        candidate_snap.get("evidence", candidate.get("evidence", {})),
            "proposed_change": candidate_snap.get("proposed_change"),
            "confidence":      candidate_snap.get("confidence", candidate.get("confidence", 0)),
            "momentum":        1.0,  # F-4: initial momentum at promotion
        }

        if _is_synthetic_candidate_id(pattern.get("candidate_id", "")):
            return (
                False,
                {
                    "attempted": False,
                    "success": False,
                    "reason": "synthetic_candidate_blocked",
                },
            )

        if pattern["confidence"] >= 0.7:
            evo["stable_identity"].append(pattern)
            # Diversity cap: max 5 of any single type, total max 20
            # Prevents PITFALL monoculture (P0-F F-1 TITANS type-diversity gate)
            from collections import Counter
            type_counts = Counter(s.get("type") for s in evo["stable_identity"])
            ctype = pattern.get("type")
            if type_counts[ctype] > 5:
                # Remove oldest entry of this type to make room
                for i, s in enumerate(evo["stable_identity"]):
                    if s.get("type") == ctype:
                        evo["stable_identity"].pop(i)
                        break
            evo["stable_identity"] = evo["stable_identity"][-20:]
        else:
            evo["candidate_patterns"].append(pattern)
            evo["candidate_patterns"] = evo["candidate_patterns"][-10:]

        evo["version"] = evo.get("version", 1) + 1
        # PROOF-B: save pre-promotion backup for regression rollback
        try:
            backup_path = pipeline.CACHE_DIR / "regent_control" / "spine_backup_pre_promote.json"
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            if pipeline.SPINE_FILE.exists():
                shutil.copy2(pipeline.SPINE_FILE, backup_path)
        except Exception as _bk_err:
            print(f"[governor] spine backup error: {_bk_err}")
        pipeline.write_json(pipeline.SPINE_FILE, spine)
        # P0-B: retry queue — 3 attempts, 5s backoff, audit every failure
        falkor_status = {"attempted": False, "success": False, "reason": "not_attempted"}
        for _attempt in range(1, 4):
            falkor_status = _write_pattern_to_falkor(pattern)
            if falkor_status.get("success"):
                if _attempt > 1:
                    pipeline.append_jsonl(
                        pipeline.GOVERNOR_AUDIT,
                        {
                            "ts": pipeline.iso_utc(),
                            "event": "falkor_write_recovery",
                            "attempt": _attempt,
                            "candidate_id": pattern.get("candidate_id"),
                        },
                    )
                break
            pipeline.append_jsonl(
                pipeline.GOVERNOR_AUDIT,
                {
                    "ts": pipeline.iso_utc(),
                    "event": "falkor_write_retry",
                    "attempt": _attempt,
                    "candidate_id": pattern.get("candidate_id"),
                    "reason": falkor_status.get("reason", ""),
                },
            )
            if _attempt < 3:
                time.sleep(5)
        else:
            pipeline.append_jsonl(
                pipeline.GOVERNOR_AUDIT,
                {
                    "ts": pipeline.iso_utc(),
                    "event": "PITFALL_falkor_write_exhausted",
                    "attempts": 3,
                    "candidate_id": pattern.get("candidate_id"),
                    "final_status": falkor_status,
                },
            )
        return True, falkor_status
    except Exception as e:
        print(f"[governor] spine write error: {e}")
        return False, {"attempted": False, "success": False, "reason": f"spine_write_error:{e}"}


def _update_state(total_applied: int):
    """Write governor status to dedicated control file.

    Avoids clobbering regent_state.json which the daemon heartbeat owns.
    """
    try:
        status_path = pipeline.CONTROL_DIR / "vesper_pipeline_status.json"
        existing = pipeline.read_json(status_path, {})
        existing["self_improving"]    = total_applied > 0
        existing["last_governor_run"] = pipeline.iso_utc()
        existing["total_promotions"]  = total_applied
        existing["pipeline_status"]   = {
            "watchdog": "active",
            "eval":     "active",
            "governor": "active",
        }
        pipeline.write_json(status_path, existing)
    except Exception as e:
        print(f"[governor] state update error: {e}")


def _read_total_promotions(done_dir):
    """Cumulative applied count from status file, with artifact-count fallback."""
    status_path = pipeline.CONTROL_DIR / "vesper_pipeline_status.json"
    status_total = pipeline.read_json(status_path, {}).get("total_promotions", 0)
    if not isinstance(status_total, int):
        status_total = 0

    applied_count = 0
    for artifact in done_dir.glob("promotion-*.json"):
        payload = pipeline.read_json(artifact, {})
        if payload.get("status") == "applied":
            applied_count += 1
    return max(status_total, applied_count)


def _hyperagent_threshold_check():
    """Hyperagent (primitive #16): meta-agent adjusts task-agent thresholds.
    Reads recent eval outcomes. If rejection > 80%, recommends loosening.
    If promoted candidates were noise, recommends tightening."""
    try:
        audit_entries = list(pipeline.read_jsonl(pipeline.EVAL_AUDIT))[-50:]
        if len(audit_entries) < 10:
            return  # not enough data

        approved = sum(1 for e in audit_entries if e.get("decision") == "approved")
        rejected = sum(1 for e in audit_entries if e.get("decision") == "rejected")
        total = approved + rejected
        if total == 0:
            return

        rejection_rate = rejected / total
        recommendation = None

        if rejection_rate > 0.80:
            recommendation = {
                "action": "loosen",
                "reason": f"Rejection rate {rejection_rate:.0%} > 80%. Consider lowering thresholds.",
                "rejection_rate": round(rejection_rate, 2),
                "sample_size": total,
            }
        elif rejection_rate < 0.20 and total > 20:
            recommendation = {
                "action": "tighten",
                "reason": f"Rejection rate {rejection_rate:.0%} < 20%. Quality gate may be too loose.",
                "rejection_rate": round(rejection_rate, 2),
                "sample_size": total,
            }

        if recommendation:
            pipeline.append_jsonl(pipeline.GOVERNOR_AUDIT, {
                "ts": pipeline.iso_utc(),
                "event": "hyperagent_threshold_recommendation",
                **recommendation,
            })
            print(f"[governor] HYPERAGENT: {recommendation['action']} — {recommendation['reason']}")
    except Exception as e:
        print(f"[governor] hyperagent check error: {e}")


def run_governor():
    pipeline.ensure_pipeline_dirs()
    done_dir = pipeline.CACHE_DIR / "regent_promotions_applied"
    done_dir.mkdir(parents=True, exist_ok=True)
    run_started = pipeline.iso_utc()
    pipeline.append_jsonl(
        pipeline.GOVERNOR_AUDIT, {"ts": run_started, "event": "run_started"}
    )
    _hyperagent_threshold_check()  # Primitive #16: meta-agent reviews task-agent performance
    outbox = _drain_falkor_outbox(max_items=10)
    _retire_stale_patterns()  # F-3: decay stale patterns before promoting new ones
    if outbox["checked"] > 0:
        pipeline.append_jsonl(
            pipeline.GOVERNOR_AUDIT,
            {
                "ts": pipeline.iso_utc(),
                "event": "outbox_replay_summary",
                **outbox,
            },
        )

    # Gate 1: identity contract valid
    ok, checksum_or_err = _validate_contract()
    if not ok:
        print(f"[governor] BLOCKED — {checksum_or_err}")
        pipeline.append_jsonl(pipeline.GOVERNOR_AUDIT,
                              {"ts": pipeline.iso_utc(), "event": "blocked",
                               "reason": checksum_or_err})
        return 0

    pending = sorted(pipeline.PROMOTION_DIR.glob("promotion-*.json"))
    if not pending:
        print("[governor] no approved promotions pending")
        try:
            total = _read_total_promotions(done_dir)
        except Exception:
            total = 0
        _update_state(total)
        pipeline.append_jsonl(
            pipeline.GOVERNOR_AUDIT,
            {
                "ts": pipeline.iso_utc(),
                "event": "run_completed",
                "applied": 0,
                "skipped": 0,
                "pending_count": 0,
                "total_promotions": total,
            },
        )
        return 0

    applied = skipped = 0

    for path in pending:
        promo = pipeline.read_json(path, {})
        if not promo.get("approved"):
            promo["status"] = promo.get("status", "rejected")
            promo["handled_at"] = pipeline.iso_utc()
            pipeline.write_json(done_dir / path.name, promo)
            path.unlink(missing_ok=True)
            skipped += 1
            continue

        gov_ok, gov_reason = _promotion_governance_ok(promo)
        if not gov_ok:
            promo["status"] = "blocked_governance"
            promo["handled_at"] = pipeline.iso_utc()
            promo["governance_reason"] = gov_reason
            pipeline.write_json(done_dir / path.name, promo)
            path.unlink(missing_ok=True)
            pipeline.append_jsonl(
                pipeline.GOVERNOR_AUDIT,
                {
                    "ts": pipeline.iso_utc(),
                    "event": "blocked_governance",
                    "candidate_id": promo.get("candidate_id"),
                    "eval_id": promo.get("eval_id"),
                    "reason": gov_reason,
                },
            )
            skipped += 1
            continue

        # Gate 2: re-validate before each apply
        ok2, _ = _validate_contract()
        if not ok2:
            print("[governor] BLOCKED mid-run — checksum drifted")
            pipeline.append_jsonl(pipeline.GOVERNOR_AUDIT,
                                  {"ts": pipeline.iso_utc(), "event": "mid_run_block",
                                   "candidate_id": promo.get("candidate_id")})
            break

        candidate_snap = promo.get("candidate_snapshot", {})
        proposed = candidate_snap.get("proposed_change")
        target = proposed.get("target") if proposed else None

        if target not in SAFE_TARGETS:
            print(f"[governor] SKIP unsafe target={target}")
            promo["status"] = "blocked_unsafe_target"
            promo["handled_at"] = pipeline.iso_utc()
            promo["unsafe_target"] = target
            pipeline.write_json(done_dir / path.name, promo)
            path.unlink(missing_ok=True)
            pipeline.append_jsonl(pipeline.GOVERNOR_AUDIT,
                                  {"ts": pipeline.iso_utc(), "event": "skipped_unsafe_target",
                                   "candidate_id": promo.get("candidate_id"), "target": target})
            skipped += 1
            continue

        ckpt = _checkpoint(promo)

        if target == "self_edit":
            # Beyond-preclaw1: Vesper proposes code changes via self-edit pipeline
            patch = (proposed.get("patch") or {})
            file_path = patch.get("file_path", "")
            new_content = patch.get("new_content", "")
            description = patch.get("description", candidate_snap.get("type", "vesper improvement"))
            risk_level = patch.get("risk_level", "medium")
            if file_path and new_content:
                try:
                    p1_url = _env_get("P1_HARNESS_URL", "http://100.124.194.102:7891")
                    payload = json.dumps({
                        "file_path": file_path,
                        "new_content": new_content,
                        "description": f"[Vesper] {description}",
                        "risk_level": risk_level,
                    }).encode()
                    req = urllib.request.Request(
                        f"{p1_url}/self-edit/propose", data=payload,
                        headers={"Content-Type": "application/json"}, method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=10) as r:
                        result = json.loads(r.read())
                    if result.get("ok"):
                        promo["status"] = "proposed_self_edit"
                        promo["applied_at"] = pipeline.iso_utc()
                        promo["self_edit_id"] = result.get("id")
                        pipeline.write_json(done_dir / path.name, promo)
                        path.unlink(missing_ok=True)
                        applied += 1
                        pipeline.append_jsonl(pipeline.GOVERNOR_AUDIT,
                                              {"ts": pipeline.iso_utc(), "event": "self_edit_proposed",
                                               "candidate_id": promo.get("candidate_id"),
                                               "file_path": file_path, "proposal_id": result.get("id")})
                        print(f"[governor] SELF-EDIT PROPOSED: {file_path} (id={result.get('id')})")
                    else:
                        promo["status"] = "self_edit_failed"
                        promo["handled_at"] = pipeline.iso_utc()
                        pipeline.write_json(done_dir / path.name, promo)
                        path.unlink(missing_ok=True)
                        skipped += 1
                except Exception as se_err:
                    print(f"[governor] self-edit propose error: {se_err}")
                    promo["status"] = "self_edit_error"
                    promo["handled_at"] = pipeline.iso_utc()
                    pipeline.write_json(done_dir / path.name, promo)
                    path.unlink(missing_ok=True)
                    skipped += 1
            else:
                promo["status"] = "self_edit_incomplete"
                promo["handled_at"] = pipeline.iso_utc()
                pipeline.write_json(done_dir / path.name, promo)
                path.unlink(missing_ok=True)
                skipped += 1
            continue

        if target == "safe_exec":
            command = (proposed.get("patch") or {}).get("command", "")
            if _safe_exec(command):
                promo["status"]     = "applied"
                promo["applied_at"] = pipeline.iso_utc()
                promo["checkpoint"] = ckpt
                pipeline.write_json(done_dir / path.name, promo)
                path.unlink(missing_ok=True)
                applied += 1
                pipeline.append_jsonl(pipeline.GOVERNOR_AUDIT,
                                      {"ts": pipeline.iso_utc(), "event": "safe_exec_applied",
                                       "candidate_id": promo.get("candidate_id"),
                                       "command": command})
                print(f"[governor] SAFE_EXEC APPLIED: {command!r}")
            else:
                promo["status"] = "safe_exec_failed"
                promo["handled_at"] = pipeline.iso_utc()
                pipeline.write_json(done_dir / path.name, promo)
                path.unlink(missing_ok=True)
                skipped += 1
            continue

        applied_ok, falkor_status = _apply_to_spine(promo)
        if applied_ok:
            # SMOKE TEST GATE (Phase 0): run test_command before finalizing
            smoke_passed, smoke_detail = _smoke_test_promotion(promo)
            if not smoke_passed:
                # Rollback: restore spine from checkpoint
                import shutil
                for f_info in ckpt.get("files", []):
                    ckpt_path = pipeline.Path(f_info["path"])
                    orig_name = ckpt_path.name
                    restore_target = pipeline.SPINE_FILE if orig_name == pipeline.SPINE_FILE.name else None
                    if restore_target and ckpt_path.exists():
                        shutil.copy2(ckpt_path, restore_target)
                promo["status"] = "smoke_test_failed"
                promo["handled_at"] = pipeline.iso_utc()
                promo["smoke_test"] = smoke_detail
                pipeline.write_json(done_dir / path.name, promo)
                path.unlink(missing_ok=True)
                pipeline.append_jsonl(pipeline.GOVERNOR_AUDIT,
                                      {"ts": pipeline.iso_utc(), "event": "smoke_test_failed",
                                       "candidate_id": promo.get("candidate_id"),
                                       "detail": smoke_detail})
                print(f"[governor] SMOKE TEST FAILED: {promo.get('candidate_id', '?')} — {smoke_detail}")
                skipped += 1
                continue

            promo["status"]     = "applied"
            promo["applied_at"] = pipeline.iso_utc()
            promo["checkpoint"] = ckpt
            promo["falkor_write"] = falkor_status
            promo["smoke_test"] = smoke_detail

            pipeline.write_json(done_dir / path.name, promo)
            path.unlink(missing_ok=True)
            applied += 1

            spine_ver = pipeline.read_json(pipeline.SPINE_FILE, {}).get("evolution", {}).get("version", "?")

            # Phase 0 Edit 10: If this is a gap_closure promotion, update the gap map atomically
            gap_update_result = None
            if target == "gap_closure":
                gap_feature = (proposed.get("patch") or {}).get("feature_name", "")
                gap_new_status = (proposed.get("patch") or {}).get("new_status", "HAVE")
                gap_evidence = f"Promoted spine v{spine_ver}, {pipeline.iso_utc()}"
                if gap_feature:
                    try:
                        # Import gap_map from Scripts/ (P1 path)
                        import importlib.util
                        gm_path = os.path.join(os.path.dirname(__file__), "gap_map.py")
                        spec = importlib.util.spec_from_file_location("gap_map", gm_path)
                        gm = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(gm)
                        gap_update_result = gm.update_gap_status(gap_feature, gap_new_status, evidence=gap_evidence)
                        if gap_update_result.get("updated"):
                            print(f"[governor] GAP MAP UPDATED: {gap_feature} -> {gap_new_status}")
                        else:
                            print(f"[governor] gap map update skipped: {gap_update_result.get('error')}")
                    except Exception as gm_err:
                        print(f"[governor] gap map update error: {gm_err}")
                        gap_update_result = {"updated": False, "error": str(gm_err)}

            pipeline.append_jsonl(pipeline.GOVERNOR_AUDIT,
                                  {"ts": pipeline.iso_utc(), "event": "applied",
                                   "candidate_id": promo.get("candidate_id"),
                                   "spine_version": spine_ver, "checksum": checksum_or_err,
                                   "falkor_write": falkor_status,
                                   "smoke_test": smoke_detail,
                                   "gap_map_update": gap_update_result})
            print(f"[governor] APPLIED {promo.get('candidate_id', '?')} -> spine v{spine_ver}")
        else:
            promo["status"] = "apply_failed"
            promo["handled_at"] = pipeline.iso_utc()
            promo["falkor_write"] = falkor_status
            pipeline.write_json(done_dir / path.name, promo)
            path.unlink(missing_ok=True)
            pipeline.append_jsonl(
                pipeline.GOVERNOR_AUDIT,
                {
                    "ts": pipeline.iso_utc(),
                    "event": "apply_failed",
                    "candidate_id": promo.get("candidate_id"),
                    "reason": falkor_status.get("reason", "unknown"),
                },
            )
            skipped += 1

    try:
        total = _read_total_promotions(done_dir) + applied
    except Exception:
        total = applied

    _update_state(total)
    pipeline.append_jsonl(
        pipeline.GOVERNOR_AUDIT,
        {
            "ts": pipeline.iso_utc(),
            "event": "run_completed",
            "applied": applied,
            "skipped": skipped,
            "pending_count": len(pending),
            "total_promotions": total,
        },
    )
    print(f"[governor] done: {applied} applied, {skipped} skipped "
          f"(total_promotions={total}, self_improving={total > 0})")
    return applied


if __name__ == "__main__":
    print(f"[vesper_governor] {pipeline.iso_utc()} — running")
    run_governor()
