from pathlib import Path


def test_regent_watchdog_uses_openrouter_not_direct_anthropic():
    source = Path("Scripts/regent_watchdog.py").read_text(encoding="utf-8")
    assert "api.anthropic.com" not in source
    assert "ANTHROPIC_API_KEY" not in source
    assert "OPENROUTER_API_KEY" in source
    assert "openrouter.ai/api/v1/chat/completions" in source
