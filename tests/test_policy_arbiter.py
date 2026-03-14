import json
import pytest
from pathlib import Path
from Scripts.karma_policy_arbiter import PolicyArbiter


@pytest.fixture
def arbiter(tmp_path):
    boundary = {
        "hard_deny_paths": [
            "/run/secrets/**", "~/.ssh/**", "**/*token*", "**/*.key",
            "Config/governance_boundary_v1.json"
        ],
        "financial_files": ["hub.env", "spend-cap.json"]
    }
    critical = {
        "critical_paths": [
            "hub-bridge/app/server.js",
            "Memory/00-karma-system-prompt-live.md"
        ]
    }
    b = tmp_path / "boundary.json"
    c = tmp_path / "critical.json"
    b.write_text(json.dumps(boundary))
    c.write_text(json.dumps(critical))
    return PolicyArbiter(str(b), str(c))


def test_hard_deny_secret_path(arbiter):
    r = arbiter.evaluate("/run/secrets/api_key", "write", {})
    assert r.verdict == "DENY"
    assert r.reason_code == "HARD_DENY_PATH"


def test_hard_deny_token_file(arbiter):
    r = arbiter.evaluate("/some/path/my_token.txt", "write", {})
    assert r.verdict == "DENY"
    assert r.reason_code == "HARD_DENY_PATH"


def test_hard_deny_governance_file(arbiter):
    r = arbiter.evaluate("Config/governance_boundary_v1.json", "write", {})
    assert r.verdict == "DENY"
    assert r.reason_code == "HARD_DENY_PATH"


def test_financial_boundary(arbiter):
    r = arbiter.evaluate("/opt/hub-bridge/config/hub.env", "write", {})
    assert r.verdict == "DENY"
    assert r.reason_code == "FINANCIAL_BOUNDARY"


def test_critical_path_no_tests(arbiter):
    r = arbiter.evaluate("hub-bridge/app/server.js", "write", {})
    assert r.verdict == "DENY"
    assert r.reason_code == "CRITICAL_TESTS_FAILED"


def test_critical_path_with_tests_requires_approval(arbiter):
    r = arbiter.evaluate(
        "hub-bridge/app/server.js", "write",
        {"smoke_pass": True, "functional_pass": True}
    )
    assert r.verdict == "REQUIRE_APPROVAL"
    assert r.reason_code == "CRITICAL_PATH"


def test_non_critical_with_tests_allowed(arbiter):
    r = arbiter.evaluate(
        "Scripts/karma_kiki_v6.py", "write",
        {"smoke_pass": True, "functional_pass": True}
    )
    assert r.verdict == "ALLOW"


def test_non_critical_untested_allowed_with_flag(arbiter):
    r = arbiter.evaluate("Scripts/new_script.py", "write", {"untested": True})
    assert r.verdict == "ALLOW"
    assert "untested" in r.reason.lower()


def test_non_critical_no_tests_no_flag_denied(arbiter):
    r = arbiter.evaluate("Scripts/new_script.py", "write", {})
    assert r.verdict == "DENY"
    assert r.reason_code == "TESTS_REQUIRED"


def test_arbiter_result_has_reason_code(arbiter):
    r = arbiter.evaluate("/run/secrets/x", "write", {})
    assert r.reason_code
    assert r.reason
    assert r.verdict in ("ALLOW", "DENY", "REQUIRE_APPROVAL")
