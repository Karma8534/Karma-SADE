#!/usr/bin/env python3
"""Vesper Governor — applies approved promotion artifacts to identity spine.
Run by systemd timer every 2 hours.

Uses Codex's regent_* modules.
Never mutates identity_contract.json directly.
"""
import json
import sys

sys.path.insert(0, "/mnt/c/dev/Karma/k2/Aria")

import regent_guardrails as guardrails
import regent_pipeline as pipeline

SAFE_TARGETS = {"persona.voice", "runtime_rules", None}

IDENTITY_PATH = pipeline.Path("/mnt/c/dev/Karma/k2/Aria/docs/regent/identity_contract.json")


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
        pattern = {
            "type":            candidate.get("type"),
            "candidate_id":    candidate.get("candidate_id"),
            "promoted_at":     pipeline.iso_utc(),
            "evidence":        candidate.get("evidence", candidate.get("candidate_snapshot", {}).get("evidence", {})),
            "proposed_change": candidate.get("candidate_snapshot", {}).get("proposed_change"),
            "confidence":      candidate.get("candidate_snapshot", {}).get("confidence", 0),
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


def run_governor():
    pipeline.ensure_pipeline_dirs()
    done_dir = pipeline.CACHE_DIR / "regent_promotions_applied"
    done_dir.mkdir(parents=True, exist_ok=True)

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
            total = pipeline.read_json(pipeline.STATE_FILE, {}).get("total_promotions", 0)
        except Exception:
            total = 0
        _update_state(total)
        return 0

    applied = skipped = 0

    for path in pending:
        promo = pipeline.read_json(path, {})
        if not promo.get("approved"):
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
            path.unlink()
            applied += 1

            spine_ver = pipeline.read_json(pipeline.SPINE_FILE, {}).get("evolution", {}).get("version", "?")
            pipeline.append_jsonl(pipeline.GOVERNOR_AUDIT,
                                  {"ts": pipeline.iso_utc(), "event": "applied",
                                   "candidate_id": promo.get("candidate_id"),
                                   "spine_version": spine_ver, "checksum": checksum_or_err})
            print(f"[governor] APPLIED {promo.get('candidate_id', '?')} → spine v{spine_ver}")
        else:
            skipped += 1

    try:
        total = pipeline.read_json(pipeline.STATE_FILE, {}).get("total_promotions", 0) + applied
    except Exception:
        total = applied

    _update_state(total)
    print(f"[governor] done: {applied} applied, {skipped} skipped "
          f"(total_promotions={total}, self_improving={total > 0})")
    return applied


if __name__ == "__main__":
    print(f"[vesper_governor] {pipeline.iso_utc()} — running")
    run_governor()
