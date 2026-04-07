import importlib
import json


def _load_module():
    return importlib.import_module("Scripts.nexus_agent")


def test_append_transcript_writes_append_only_message_and_last_prompt_metadata(tmp_path, monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "TRANSCRIPT_DIR", str(tmp_path))

    mod.append_transcript("alpha", {"role": "user", "content": "remember this"})
    mod.append_transcript("alpha", {"role": "assistant", "content": "stored"})

    raw = (tmp_path / "alpha.jsonl").read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in raw]

    assert rows[0]["type"] == "user"
    assert rows[0]["session_id"] == "alpha"
    assert rows[1]["type"] == "last-prompt"
    assert rows[1]["last_prompt"] == "remember this"
    assert rows[2]["type"] == "assistant"


def test_load_transcript_filters_metadata_and_preserves_message_order(tmp_path, monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "TRANSCRIPT_DIR", str(tmp_path))

    mod.append_transcript("beta", {"role": "user", "content": "u1"})
    mod.append_transcript("beta", {"role": "assistant", "content": "a1"})
    mod.append_transcript("beta", {"role": "user", "content": "u2"})

    loaded = mod.load_transcript("beta")

    assert [entry["role"] for entry in loaded] == ["user", "assistant", "user"]
    assert [entry["content"] for entry in loaded] == ["u1", "a1", "u2"]


def test_load_transcript_supports_limit_without_rewriting_file(tmp_path, monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "TRANSCRIPT_DIR", str(tmp_path))

    for idx in range(5):
        mod.append_transcript("gamma", {"role": "user", "content": f"u{idx}"})

    path = tmp_path / "gamma.jsonl"
    before = path.read_text(encoding="utf-8")
    tail = mod.load_transcript("gamma", limit=2)
    after = path.read_text(encoding="utf-8")

    assert [entry["content"] for entry in tail] == ["u3", "u4"]
    assert before == after


def test_list_transcript_sessions_reads_last_prompt_summary(tmp_path, monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "TRANSCRIPT_DIR", str(tmp_path))

    mod.append_transcript("delta", {"role": "user", "content": "first prompt"})
    mod.append_transcript("delta", {"role": "assistant", "content": "ack"})

    sessions = mod.list_transcript_sessions(limit=5)

    assert sessions[0]["session_id"] == "delta"
    assert sessions[0]["last_prompt"] == "first prompt"
