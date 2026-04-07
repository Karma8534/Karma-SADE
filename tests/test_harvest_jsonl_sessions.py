import importlib


def _load_module():
    return importlib.import_module("Scripts.harvest_jsonl_sessions")


def test_ingest_observations_saves_each_new_observation(monkeypatch):
    mod = _load_module()
    saved = []

    monkeypatch.setattr(mod, "save_observation", lambda obs: saved.append(obs) or True)

    observations = [
        {"title": "Obs 1", "text": "alpha", "project": "Karma_SADE", "type": "proof"},
        {"title": "Obs 2", "text": "beta", "project": "Karma_SADE", "type": "decision"},
    ]

    count = mod.ingest_observations(observations)

    assert count == 2
    assert [obs["title"] for obs in saved] == ["Obs 1", "Obs 2"]
