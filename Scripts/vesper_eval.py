#!/usr/bin/env python3
"""Vesper Eval Runner — evaluates pending candidates against eval gate thresholds.
Run by systemd timer every 30 minutes.

Uses Codex's regent_* modules. Fix applied: observational candidates
(proposed_change=None) use model_weight=1.0 since heuristics score 0.0
on numeric-only evidence dicts.
"""
import json
import os
import sys

sys.path.insert(0, "/mnt/c/dev/Karma/k2/Aria")

import regent_benchmarks as benchmarks
import regent_governance as governance
import regent_pipeline as pipeline
import regent_inference as inference

_ENV = {k: v for line in open("/etc/karma-regent.env").read().splitlines()
        if "=" in line for k, v in [line.split("=", 1)]}

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


def run_eval():
    pipeline.ensure_pipeline_dirs()
    suites = benchmarks.ensure_default_suites(pipeline.EVAL_ROOT)

    candidates = list(pipeline.list_candidate_files())
    if not candidates:
        print("[eval] no pending candidates")
        return 0, 0

    approved = rejected = 0

    for path in candidates:
        candidate = pipeline.read_json(path, {})
        if candidate.get("status") not in (None, "pending"):
            continue

        ctype = candidate.get("type", "")
        is_observational = candidate.get("proposed_change") is None

        # Heuristic scoring
        heuristic_scores = benchmarks.heuristic_metric_scores(candidate, suites)

        # Model scoring
        model_scores, model_source = _model_score(candidate, suites)

        # Fix: observational candidates get model_weight=1.0
        # (heuristics can't evaluate numeric-only evidence dicts)
        all_heuristic_zero = all(v == 0.0 for v in heuristic_scores.values())
        model_weight = 1.0 if (is_observational or all_heuristic_zero) else 0.6

        merged = benchmarks.merge_metric_scores(heuristic_scores, model_scores,
                                                model_weight=model_weight)

        gate_metrics = {k: merged.get(k, 0.0)
                        for k in ("identity_consistency", "persona_style",
                                  "session_continuity", "task_completion")}

        decision = governance.resolve_governor_decision(gate_metrics)

        eval_doc = {
            "eval_id": f"eval-{path.stem}",
            "candidate_id": candidate.get("candidate_id", path.stem),
            "candidate_path": str(path),
            "evaluated_utc": pipeline.iso_utc(),
            "heuristic_scores": heuristic_scores,
            "model_scores": model_scores,
            "model_source": model_source,
            "model_weight_used": model_weight,
            "merged_scores": merged,
            "gate_metrics": gate_metrics,
            "governor_decision": decision,
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
    return approved, rejected


if __name__ == "__main__":
    print(f"[vesper_eval] {pipeline.iso_utc()} — running")
    run_eval()
