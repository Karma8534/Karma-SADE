from pathlib import Path


def test_karma_regent_defaults_match_live_local_floor():
    source = Path("Scripts/karma_regent.py").read_text(encoding="utf-8")
    assert 'os.environ.get("K2_OLLAMA_URL", "http://host.docker.internal:11434")' in source
    assert 'os.environ.get("K2_OLLAMA_MODEL", "")' in source
    assert 'K2_OLLAMA_FALLBACK_MODEL = os.environ.get("K2_OLLAMA_FALLBACK_MODEL", "")' in source
    assert 'P1_OLLAMA_MODEL = os.environ.get("P1_OLLAMA_MODEL", "sam860/LFM2:350m")' in source

    mirror = Path("Vesper/karma_regent.py").read_text(encoding="utf-8")
    assert 'os.environ.get("K2_OLLAMA_URL", "http://host.docker.internal:11434")' in mirror


def test_vesper_eval_defaults_match_live_local_floor():
    source = Path("Scripts/vesper_eval.py").read_text(encoding="utf-8")
    assert 'ollama_url=_ENV.get("K2_OLLAMA_URL", "")' in source
    assert 'k2_primary_model=_ENV.get("K2_OLLAMA_PRIMARY_MODEL", "")' in source
    assert 'k2_fallback_model=_ENV.get("K2_OLLAMA_FALLBACK_MODEL", "")' in source
    assert 'p1_model=_ENV.get("P1_OLLAMA_MODEL", "sam860/LFM2:350m")' in source


def test_regent_triage_defaults_match_live_k2_inventory():
    source = Path("Scripts/regent_triage.py").read_text(encoding="utf-8")
    assert 'os.environ.get("K2_OLLAMA_URL", "http://host.docker.internal:11434")' in source
    assert 'os.environ.get("REGENT_TRIAGE_MODEL", "qwen3.5:4b")' in source

    mirror = Path("Vesper/regent_triage.py").read_text(encoding="utf-8")
    assert 'os.environ.get("K2_OLLAMA_URL", "http://host.docker.internal:11434")' in mirror
    assert 'os.environ.get("REGENT_TRIAGE_MODEL", "qwen3.5:4b")' in mirror


def test_session_review_defaults_match_live_review_floor():
    source = Path("Scripts/session_review.py").read_text(encoding="utf-8")
    assert 'os.environ.get("OLLAMA_URL", "http://100.75.109.92:11434")' in source
    assert 'os.environ.get("REVIEW_MODEL", "qwen3.5:4b")' in source
    assert 'LOCAL_OLLAMA_URL = "http://localhost:11434"' in source
    assert 'os.environ.get("REVIEW_FALLBACK_MODEL", "sam860/LFM2:350m")' in source

    task = Path("Scripts/Run-SessionIngest.ps1").read_text(encoding="utf-8")
    assert '$env:OLLAMA_URL = "http://100.75.109.92:11434"' in task
    assert '$env:REVIEW_MODEL = "qwen3.5:4b"' in task
    assert '$env:REVIEW_FALLBACK_MODEL = "sam860/LFM2:350m"' in task


def test_smart_router_defaults_match_live_local_floor():
    source = Path("Scripts/smart_router.py").read_text(encoding="utf-8")
    assert 'os.environ.get("K2_OLLAMA_URL", "http://100.75.109.92:11434")' in source
    assert 'os.environ.get("K2_OLLAMA_MODEL")' in source
    assert 'os.environ.get("K2_OLLAMA_PRIMARY_MODEL")' in source
    assert '"qwen3.5:4b"' in source
    assert 'os.environ.get("P1_OLLAMA_MODEL", "sam860/LFM2:350m")' in source


def test_k2_mcp_server_default_model_matches_live_k2_floor():
    source = Path("Scripts/k2_mcp_server.py").read_text(encoding="utf-8")
    assert '"default": "qwen3.5:4b"' in source
    assert 'arguments.get("model", "qwen3.5:4b")' in source
    assert "qwen3:8b" not in source


def test_k2_cortex_default_endpoint_matches_live_host_boundary():
    source = Path("k2/aria/julian_cortex.py").read_text(encoding="utf-8")
    assert 'os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434")' in source
