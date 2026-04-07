import importlib.util
from pathlib import Path


def _load_module():
    path = Path("Scripts/cc_bus_reader.py")
    spec = importlib.util.spec_from_file_location("cc_bus_reader_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_cc_bus_reader_uses_harness_not_direct_anthropic():
    source = Path("Scripts/cc_bus_reader.py").read_text(encoding="utf-8")
    assert "api.anthropic.com" not in source
    assert "ANTHROPIC_API_KEY" not in source
    assert "/v1/chat" in source
    assert "call_harness" in source


def test_complex_message_prefers_harness(monkeypatch, tmp_path):
    mod = _load_module()
    mod.TOKEN = "token"
    mod.WATERMARK_F = tmp_path / "wm.json"
    posted = []

    monkeypatch.setattr(
        mod,
        "fetch_bus_messages",
        lambda: [{"id": "m1", "from": "karma", "to": "cc", "content": "Please analyze this failure path and recommend next steps."}],
    )
    monkeypatch.setattr(mod, "call_harness", lambda msg: "HARNESS_OK")
    monkeypatch.setattr(mod, "call_cortex", lambda msg: "CORTEX_SHOULD_NOT_BE_USED")
    monkeypatch.setattr(mod, "post_to_bus", lambda content, to="colby": posted.append((content, to)) or {"ok": True, "id": "reply1"})

    mod.main()

    assert posted == [("HARNESS_OK", "karma")]


def test_simple_message_falls_back_to_harness_when_cortex_unavailable(monkeypatch, tmp_path):
    mod = _load_module()
    mod.TOKEN = "token"
    mod.WATERMARK_F = tmp_path / "wm.json"
    posted = []

    monkeypatch.setattr(
        mod,
        "fetch_bus_messages",
        lambda: [{"id": "m2", "from": "karma", "to": "cc", "content": "what is the current blocker?"}],
    )
    monkeypatch.setattr(mod, "call_cortex", lambda msg: None)
    monkeypatch.setattr(mod, "call_harness", lambda msg: "HARNESS_FALLBACK_OK")
    monkeypatch.setattr(mod, "post_to_bus", lambda content, to="colby": posted.append((content, to)) or {"ok": True, "id": "reply2"})

    mod.main()

    assert posted == [("HARNESS_FALLBACK_OK", "karma")]
