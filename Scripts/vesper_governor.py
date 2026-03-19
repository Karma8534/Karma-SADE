#!/usr/bin/env python3
"""Vesper Governor — applies approved promotion artifacts to identity spine.
Run by systemd timer every 2 hours.

Uses Codex's regent_* modules.
Never mutates identity_contract.json directly.
"""
import json

import regent_guardrails as guardrails
import regent_pipeline as pipeline

SAFE_TARGETS = {"persona.voice", "runtime_rules", None}

IDENTITY_PATH = pipeline.IDENTITY_CONTRACT_FILE


def _validate_contract():
    result = guardrails.load_identity_contract(IDENTITY_PATH)
    if not result.get("ok"):
        return False, result.get("error", "checksum validation failed")
    return True, result["checksum"]


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


def _apply_to_spine(candidate: dict) -> bool:
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
        }

        if pattern["confidence"] >= 0.7:
            evo["stable_identity"].append(pattern)
            evo["stable_identity"] = evo["stable_identity"][-20:]
        else:
            evo["candidate_patterns"].append(pattern)
            evo["candidate_patterns"] = evo["candidate_patterns"][-10:]

        evo["version"] = evo.get("version", 1) + 1
        pipeline.write_json(pipeline.SPINE_FILE, spine)
        return True
    except Exception as e:
        print(f"[governor] spine write error: {e}")
        return False


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


def run_governor():
    pipeline.ensure_pipeline_dirs()
    done_dir = pipeline.CACHE_DIR / "regent_promotions_applied"
    done_dir.mkdir(parents=True, exist_ok=True)
    run_started = pipeline.iso_utc()
    pipeline.append_jsonl(
        pipeline.GOVERNOR_AUDIT, {"ts": run_started, "event": "run_started"}
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

        if _apply_to_spine(promo):
            promo["status"]     = "applied"
            promo["applied_at"] = pipeline.iso_utc()
            promo["checkpoint"] = ckpt

            pipeline.write_json(done_dir / path.name, promo)
            path.unlink(missing_ok=True)
            applied += 1

            spine_ver = pipeline.read_json(pipeline.SPINE_FILE, {}).get("evolution", {}).get("version", "?")
            pipeline.append_jsonl(pipeline.GOVERNOR_AUDIT,
                                  {"ts": pipeline.iso_utc(), "event": "applied",
                                   "candidate_id": promo.get("candidate_id"),
                                   "spine_version": spine_ver, "checksum": checksum_or_err})
            print(f"[governor] APPLIED {promo.get('candidate_id', '?')} -> spine v{spine_ver}")
        else:
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
