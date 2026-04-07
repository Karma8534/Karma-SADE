import importlib


def _load_module():
    return importlib.import_module("Scripts.session_review")


def test_call_review_model_falls_back_to_groq(monkeypatch):
    mod = _load_module()
    calls = []

    monkeypatch.setattr(mod, "call_ollama_once", lambda prompt, url, model: calls.append(("ollama", url, model)) or None)
    monkeypatch.setattr(mod, "call_groq", lambda prompt: calls.append(("groq", None, None)) or "[]")

    result = mod.call_review_model("review this")

    assert result == "[]"
    assert calls[-1][0] == "groq"


def test_call_review_model_tries_k2_then_local_then_groq(monkeypatch):
    mod = _load_module()
    calls = []

    def fake_ollama(prompt, url, model):
        calls.append((url, model))
        return None

    monkeypatch.setattr(mod, "call_ollama_once", fake_ollama)
    monkeypatch.setattr(mod, "call_groq", lambda prompt: "[]")

    result = mod.call_review_model("review this")

    assert result == "[]"
    assert calls == [
        (mod.OLLAMA_URL, mod.MODEL),
        (mod.LOCAL_OLLAMA_URL, mod.LOCAL_OLLAMA_MODEL),
    ]
