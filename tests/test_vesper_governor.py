import importlib
import json
import sys
from pathlib import Path


def _load_module():
    scripts_dir = Path(__file__).resolve().parents[1] / "Scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return importlib.import_module("Scripts.vesper_governor")


def test_update_candidate_artifact_from_promo_points_to_applied_artifact(tmp_path, monkeypatch):
    mod = _load_module()

    eval_dir = tmp_path / "evals"
    eval_dir.mkdir(parents=True)
    candidate_path = tmp_path / "candidates" / "candidate-example.json"
    candidate_path.parent.mkdir(parents=True)
    candidate_path.write_text(json.dumps({"candidate_id": "cand-1", "status": "approved"}), encoding="utf-8")

    eval_path = eval_dir / "eval-candidate-example.json"
    eval_path.write_text(
        json.dumps(
            {
                "eval_id": "eval-candidate-example",
                "candidate_path": str(candidate_path),
                "candidate_id": "cand-1",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(mod.pipeline, "EVAL_DIR", eval_dir)

    applied_artifact = tmp_path / "cache" / "regent_promotions_applied" / "promotion-candidate-example.json"
    result = mod._update_candidate_artifact_from_promo(
        {"eval_id": "eval-candidate-example", "candidate_id": "cand-1"},
        "applied",
        {"promotion_ref": str(applied_artifact), "applied_at": "2026-04-05T00:00:00Z"},
    )

    assert result == str(candidate_path)
    updated = json.loads(candidate_path.read_text(encoding="utf-8"))
    assert updated["status"] == "applied"
    assert updated["promotion_ref"] == str(applied_artifact)
    assert updated["applied_at"] == "2026-04-05T00:00:00Z"
    assert updated["eval_ref"] == str(eval_dir / "eval-candidate-example.json")
