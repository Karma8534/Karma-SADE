from pathlib import Path

from Scripts.regent_inference import CascadeConfig, call_with_local_first


def _cfg():
    return CascadeConfig(
        ollama_url="http://k2:11434",
        p1_ollama_url="http://p1:11434",
        k2_primary_model="k2model",
        k2_fallback_model="",
        p1_model="p1model",
        groq_url="https://groq.example",
        groq_model="groq-m",
        groq_api_key="groq-key",
        openrouter_url="https://openrouter.example",
        openrouter_model="or-m",
        openrouter_api_key="or-key",
        zai_url="https://bigmodel.example",
        zai_model="zai-m",
        zai_api_key="zai-key",
    )


def test_karma_regent_uses_sovereign_harness_not_direct_anthropic():
    source = Path("Scripts/karma_regent.py").read_text(encoding="utf-8")
    assert "api.anthropic.com" not in source
    assert "ANTHROPIC_API_KEY" not in source
    assert "https://hub.arknexus.net/v1/chat" in source
    assert "fallback_fn=call_sovereign_harness" in source
    assert 'fallback_label="cc_harness"' in source


def test_regent_inference_uses_supplied_fallback_label(monkeypatch):
    monkeypatch.setattr("Scripts.regent_inference._call_ollama", lambda *args, **kwargs: None)
    monkeypatch.setattr("Scripts.regent_inference._call_openai_compat", lambda *args, **kwargs: None)

    result, source = call_with_local_first(
        messages=[{"role": "user", "content": "hello"}],
        system_prompt="sys",
        config=_cfg(),
        fallback_fn=lambda msgs: "fallback-ok",
        fallback_label="cc_harness",
    )

    assert result == "fallback-ok"
    assert source == "cc_harness"
