#!/usr/bin/env python3
"""Vesper Eval Runner — evaluates pending candidates against eval gate thresholds.
Run by systemd timer every 30 minutes.

Uses Codex's regent_* modules. Fix applied: observational candidates
(proposed_change=None) use model_weight=1.0 since heuristics score 0.0
on numeric-only evidence dicts.
"""
import json
import os
import urllib.request
from pathlib import Path

import regent_benchmarks as benchmarks
import regent_governance as governance
import regent_pipeline as pipeline
import regent_inference as inference


def _load_env_file() -> dict:
    path = Path(os.environ.get("REGENT_ENV_FILE", "/etc/karma-regent.env"))
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" not in line or line.strip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        out[key.strip()] = value.strip()
    return out


_ENV = _load_env_file()

CASCADE_CFG = inference.CascadeConfig(
    ollama_url=_ENV.get("K2_OLLAMA_URL", "http://host.docker.internal:11434"),
    p1_ollama_url=_ENV.get("P1_OLLAMA_URL", "http://100.124.194.102:11434"),
    k2_primary_model=_ENV.get("K2_OLLAMA_PRIMARY_MODEL", "nemotron-mini:optimized"),
    k2_fallback_model=_ENV.get("K2_OLLAMA_FALLBACK_MODEL", "nemotron-mini:latest"),
    p1_model=_ENV.get("P1_OLLAMA_MODEL", "nemotron-mini:latest"),
    groq_url="https://api.groq.com/openai/v1/chat/completions",
    groq_model="llama-3.3-70b-versatile",
    groq_api_key=_ENV.get("GROQ_API_KEY", ""),
    openrouter_url="https://openrouter.ai/api/v1/chat/completions",
    openrouter_model=_ENV.get("OPENROUTER_MODEL", "deepseek/deepseek-r1"),
    openrouter_api_key=_ENV.get("OPENROUTER_API_KEY", ""),
    zai_api_key=_ENV.get("ZAI_API_KEY", ""),
)


def _candidate_snapshot_sha(candidate: dict) -> str:
    return pipeline.stable_fingerprint(candidate or {})


def _model_score(candidate: dict, suites: dict) -> tuple:
    prompt = benchmarks.build_eval_prompt(candidate, suites)
    messages = [{"role": "user", "content": prompt}]
    system = ("You are a strict JSON evaluator. Return only a valid JSON object "
              "with metric scores 0.0-1.0. No markdown, no explanation.")
    raw, source = inference.call_with_local_first(
        messages=messages,
        system_prompt=system,
        config=CASCADE_CFG,
        log_fn=lambda m: print(f"[eval:inference] {m}"),
    )
    if not raw:
        return {}, "none"
    # strip markdown fences if present
    clean = raw.strip().strip("```").strip()
    if clean.startswith("json"):
        clean = clean[4:].strip()
    try:
        scores = json.loads(clean)
        return {k: float(v) for k, v in scores.items() if isinstance(v, (int, float))}, source
    except Exception:
        # try to extract JSON object from response
        import re
        m = re.search(r"\{.*\}", clean, re.DOTALL)
        if m:
            try:
                scores = json.loads(m.group())
                return {k: float(v) for k, v in scores.items() if isinstance(v, (int, float))}, source
            except Exception:
                pass
        return {}, source




def _check_regression(cycle_metrics, window=20, threshold=0.05):
    """Rolling baseline comparison. Emits REGRESSION signal on >5% drop in key metrics."""
    if not cycle_metrics:
        return
    key = ["identity_consistency", "persona_style"]
    curr = {}
    for m in key:
        vals = [e.get(m, 0.0) for e in cycle_metrics if m in e]
        if vals:
            curr[m] = sum(vals) / len(vals)
    if not curr:
        return
    past = [e for e in pipeline.read_jsonl(pipeline.EVAL_AUDIT)
            if e.get("gate_metrics") and e.get("type") != "REGRESSION"]
    baseline = past[-window:] if len(past) >= window else past
    if len(baseline) < 3:
        print(f"[eval] regression check: only {len(baseline)} baseline entries, skipping")
        return
    base = {}
    for m in key:
        vals = [e["gate_metrics"].get(m, 0.0) for e in baseline if m in e.get("gate_metrics", {})]
        if vals:
            base[m] = sum(vals) / len(vals)
    drops = {}
    for m in key:
        if m in base and m in curr and base[m] > 0:
            drop_frac = (base[m] - curr[m]) / base[m]
            if drop_frac > threshold:
                drops[m] = {
                    "baseline": round(base[m], 4),
                    "current": round(curr[m], 4),
                    "drop_pct": round(100 * drop_frac, 2),
                }
    if not drops:
        print(f"[eval] regression check: no drops above {threshold*100:.0f}% threshold")
        return
    msg = "REGRESSION: " + ", ".join(
        f"{m}: {v['drop_pct']}% drop ({v['baseline']:.3f}->{v['current']:.3f})"
        for m, v in drops.items()
    )
    print(f"[eval] {msg}")
    pipeline.append_jsonl(pipeline.EVAL_AUDIT, {
        "ts": pipeline.iso_utc(),
        "type": "REGRESSION",
        "regressions": drops,
        "baseline_window": len(baseline),
        "cycle_count": len(cycle_metrics),
        "message": msg,
    })
    token = os.environ.get("HUB_AUTH_TOKEN", "")
    if token:
        try:
            payload = json.dumps({
                "from": "vesper-eval", "to": "all",
                "type": "alert", "urgency": "important",
                "content": msg,
            }).encode()
            req = urllib.request.Request(
                "https://hub.arknexus.net/v1/coordination/post",
                data=payload,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=10)
            print("[eval] REGRESSION posted to coordination bus")
        except Exception as e:
            print(f"[eval] bus post failed: {e}")


def run_eval():
    pipeline.ensure_pipeline_dirs()
    suites = benchmarks.ensure_default_suites(pipeline.EVAL_ROOT)

    candidates = list(pipeline.list_candidate_files())
    if not candidates:
        print("[eval] no pending candidates")
        return 0, 0

    approved = rejected = 0
    cycle_metrics = []  # regression baseline feed

    for path in candidates:
        candidate = pipeline.read_json(path, {})
        if candidate.get("status") not in (None, "pending", "new"):
            continue

        ctype = candidate.get("type", "")
        is_observational = candidate.get("proposed_change") is None

        # HARD GATE (Phase 0): reject non-observational candidates missing
        # target_files, test_command, or a real diff. No promotion without evidence.
        if not is_observational:
            proposed = candidate.get("proposed_change", {}) or {}
            has_target_files = bool(proposed.get("target_files"))
            has_test_command = bool(proposed.get("test_command"))
            has_diff = bool(proposed.get("diff", "").strip())
            missing = []
            if not has_target_files:
                missing.append("target_files")
            if not has_test_command:
                missing.append("test_command")
            if not has_diff:
                missing.append("diff")
            if missing:
                reason = f"HARD_GATE_REJECT: missing {', '.join(missing)}"
                print(f"[eval] {reason} — {path.stem}")
                pipeline.update_candidate_status(path, "rejected", {"gate_reason": reason})
                rejected += 1
                continue

        # PITFALL_FAST_PATH: awareness candidates from CC sessions are pre-evaluated.
        # Bypass model/heuristic gate — approve directly on confidence.
        AWARENESS_TYPES = {"PITFALL", "verbosity_correction", "claude_dependency", "ambient_observation"}  # K-3: ambient is observational, no task completion applicable
        if ctype in AWARENESS_TYPES:
            conf = float(candidate.get("confidence", 0.0))
            conf_threshold = 0.60
            fast_approved = conf >= conf_threshold
            fast_decision = "approve" if fast_approved else "reject"
            fast_reason = f"PITFALL_FAST_PATH: confidence={conf:.2f} {'>='+str(conf_threshold)+' approved' if fast_approved else '<'+str(conf_threshold)+' rejected'}"
            fake_gate = {"passed": fast_approved, "failures": [] if fast_approved else [{"metric": "confidence", "actual": conf, "minimum": conf_threshold}], "metrics": {"identity_consistency": conf, "persona_style": conf, "session_continuity": conf, "task_completion": conf}, "thresholds": {"identity_consistency": conf_threshold, "persona_style": conf_threshold, "session_continuity": conf_threshold, "task_completion": conf_threshold}}
            fast_gov_decision = {"approved": fast_approved, "decision": fast_decision, "reason": fast_reason, "gate": fake_gate, "override": {"active": False, "reason": "fast_path"}}
            eval_doc = {
                "eval_id": f"eval-{path.stem}", "candidate_id": candidate.get("candidate_id", path.stem),
                "candidate_path": str(path), "candidate_snapshot_sha256": _candidate_snapshot_sha(candidate),
                "evaluated_utc": pipeline.iso_utc(), "heuristic_scores": {}, "model_scores": {},
                "model_source": "fast_path", "model_weight_used": 0.0, "merged_scores": {},
                "gate_metrics": {}, "governor_decision": fast_gov_decision,
                "gate_passed": fast_approved, "decision_kind": fast_decision,
                "status": "evaluated", "governor_status": fast_decision + "d",
            }
            out = pipeline.EVAL_DIR / f"eval-{path.stem}.json"
            out.write_text(json.dumps(eval_doc, indent=2))
            if fast_approved:
                approved += 1
                print(f"[eval] PITFALL fast-path APPROVED: {path.stem} (conf={conf:.2f})")
                # Write promotion artifact so governor can pick it up
                promo = {
                    "promotion_id": f"promotion-{pipeline.slugify(path.stem)}-{pipeline.iso_utc().replace(':','').replace('-','')[:16]}",
                    "candidate_id": eval_doc["candidate_id"],
                    "eval_id": eval_doc["eval_id"],
                    "decision": "approve",
                    "approved": True,
                    "decision_reason": fast_reason,
                    "decision_utc": pipeline.iso_utc(),
                    "gate_metrics": {},
                    "gate_passed": True,
                    "decision_kind": "approve",
                    "candidate_snapshot_sha256": eval_doc["candidate_snapshot_sha256"],
                    "candidate_snapshot": candidate,
                    "status": "approved",
                }
                promo_path = pipeline.PROMOTION_DIR / f"promotion-{path.name}"
                pipeline.write_json(promo_path, promo)
                pipeline.update_candidate_status(path, "approved", {"eval_ref": str(out), "promotion_ref": str(promo_path)})
            else:
                rejected += 1
                print(f"[eval] PITFALL fast-path rejected: {path.stem} (conf={conf:.2f})")
            continue

        # Heuristic scoring
        heuristic_scores = benchmarks.heuristic_metric_scores(candidate, suites)

        # Model scoring
        model_scores, model_source = _model_score(candidate, suites)

        # Fix: observational + heuristic-blind types get model_weight=1.0.
        # Heuristics return fixed low scores (0.25) for behavioral/structural candidates
        # that don't have keyword-matchable content -- dragging merged scores below gate.
        HEURISTIC_BLIND_TYPES = {"behavioral_continuity", "tool_utilization_repair",
                                  "tool_utilization_strength", "research_skill_card",
                                  "PITFALL", "verbosity_correction", "claude_dependency",
                                  "ambient_observation"}  # K-3: no keyword heuristics for ambient
        all_heuristic_zero = all(v == 0.0 for v in heuristic_scores.values())
        heuristic_unreliable = ctype in HEURISTIC_BLIND_TYPES or all_heuristic_zero
        model_weight = 1.0 if (is_observational or heuristic_unreliable) else 0.6

        merged = benchmarks.merge_metric_scores(heuristic_scores, model_scores,
                                                model_weight=model_weight)

        gate_metrics = {k: merged.get(k, 0.0)
                        for k in ("identity_consistency", "persona_style",
                                  "session_continuity", "task_completion")}

        cycle_metrics.append(gate_metrics)  # regression detection
        decision = governance.resolve_governor_decision(gate_metrics, candidate_type=ctype)

        eval_doc = {
            "eval_id": f"eval-{path.stem}",
            "candidate_id": candidate.get("candidate_id", path.stem),
            "candidate_path": str(path),
            "candidate_snapshot_sha256": _candidate_snapshot_sha(candidate),
            "evaluated_utc": pipeline.iso_utc(),
            "heuristic_scores": heuristic_scores,
            "model_scores": model_scores,
            "model_source": model_source,
            "model_weight_used": model_weight,
            "merged_scores": merged,
            "gate_metrics": gate_metrics,
            "governor_decision": decision,
            "gate_passed": bool(decision.get("gate", {}).get("passed", False)),
            "decision_kind": decision.get("decision", ""),
            "status": "evaluated",
            "governor_status": "approved" if decision["approved"] else "rejected",
        }

        eval_path = pipeline.EVAL_DIR / f"eval-{path.name}"
        pipeline.write_json(eval_path, eval_doc)
        pipeline.append_jsonl(pipeline.EVAL_AUDIT, {
            "ts": pipeline.iso_utc(),
            "candidate_id": eval_doc["candidate_id"],
            "type": ctype,
            "gate_metrics": gate_metrics,
            "decision": "approved" if decision["approved"] else "rejected",
            "model_weight": model_weight,
        })

        if decision["approved"]:
            # Write promotion artifact
            promo = {
                "promotion_id": f"promotion-{pipeline.slugify(path.stem)}-{pipeline.iso_utc().replace(':', '').replace('-', '')[:16]}",
                "candidate_id": eval_doc["candidate_id"],
                "eval_id": eval_doc["eval_id"],
                "decision": "approve",
                "approved": True,
                "decision_reason": decision.get("reason", ""),
                "decision_utc": pipeline.iso_utc(),
                "gate_metrics": gate_metrics,
                "gate_passed": bool(decision.get("gate", {}).get("passed", False)),
                "decision_kind": decision.get("decision", ""),
                "candidate_snapshot_sha256": eval_doc["candidate_snapshot_sha256"],
                "candidate_snapshot": candidate,
                "status": "approved",
            }
            promo_path = pipeline.PROMOTION_DIR / f"promotion-{path.name}"
            pipeline.write_json(promo_path, promo)
            pipeline.update_candidate_status(path, "approved",
                                             {"eval_ref": str(eval_path),
                                              "promotion_ref": str(promo_path)})
            approved += 1
            print(f"[eval] APPROVED {ctype} (weight={model_weight:.1f} "
                  f"ic={gate_metrics['identity_consistency']:.2f} "
                  f"ps={gate_metrics['persona_style']:.2f})")
        else:
            failures = [f["metric"] for f in decision.get("gate", {}).get("failures", [])]
            pipeline.update_candidate_status(path, "rejected",
                                             {"eval_ref": str(eval_path),
                                              "gate_failures": failures})
            rejected += 1
            print(f"[eval] REJECTED {ctype}: {', '.join(failures)}")

    print(f"[eval] done: {approved} approved, {rejected} rejected")
    _check_regression(cycle_metrics)

    # Autoresearch primitive: log composite quality score each eval cycle
    try:
        import subprocess
        result = subprocess.run(
            ["python3", "/mnt/c/dev/Karma/k2/aria/karma_quality_score.py"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"[eval] {result.stdout.strip().splitlines()[0]}")
    except Exception as e:
        print(f"[eval] quality score failed: {e}")

    return approved, rejected


if __name__ == "__main__":
    print(f"[vesper_eval] {pipeline.iso_utc()} — running")
    run_eval()
