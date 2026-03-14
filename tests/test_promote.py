import json
import pytest
from unittest.mock import patch, MagicMock
from Scripts.karma_promote import PromotionContract


@pytest.fixture
def contract(tmp_path):
    last_good = tmp_path / ".karma_last_good"
    provenance_dir = tmp_path / "provenance"
    return PromotionContract(
        last_good_path=str(last_good),
        provenance_dir=str(provenance_dir),
        dry_run=True  # no real git/gh calls in tests
    )


def test_promote_fails_without_rollback_pointer(contract):
    result = contract.evaluate_promotion(
        cycle=1,
        test_results={"smoke_pass": True, "functional_pass": True},
        arbiter_verdict="ALLOW"
    )
    assert result["eligible"] is False
    assert result["reason"] == "no_rollback_pointer"


def test_promote_fails_without_smoke_test(contract, tmp_path):
    (tmp_path / ".karma_last_good").write_text("abc123")
    result = contract.evaluate_promotion(
        cycle=1,
        test_results={"smoke_pass": False, "functional_pass": True},
        arbiter_verdict="ALLOW"
    )
    assert result["eligible"] is False
    assert result["reason"] == "smoke_test_failed"


def test_promote_fails_without_functional_test(contract, tmp_path):
    (tmp_path / ".karma_last_good").write_text("abc123")
    result = contract.evaluate_promotion(
        cycle=1,
        test_results={"smoke_pass": True, "functional_pass": False},
        arbiter_verdict="ALLOW"
    )
    assert result["eligible"] is False
    assert result["reason"] == "functional_test_failed"


def test_promote_fails_on_arbiter_deny(contract, tmp_path):
    (tmp_path / ".karma_last_good").write_text("abc123")
    result = contract.evaluate_promotion(
        cycle=1,
        test_results={"smoke_pass": True, "functional_pass": True},
        arbiter_verdict="DENY"
    )
    assert result["eligible"] is False
    assert "arbiter" in result["reason"]


def test_promote_eligible_when_all_gates_pass(contract, tmp_path):
    (tmp_path / ".karma_last_good").write_text("abc123")
    result = contract.evaluate_promotion(
        cycle=1,
        test_results={"smoke_pass": True, "functional_pass": True},
        arbiter_verdict="ALLOW"
    )
    assert result["eligible"] is True


def test_write_last_good(contract, tmp_path):
    contract.write_last_good("deadbeef")
    assert (tmp_path / ".karma_last_good").read_text().strip() == "deadbeef"


def test_provenance_written_on_promote(contract, tmp_path):
    (tmp_path / ".karma_last_good").write_text("abc123")
    contract.evaluate_promotion(
        cycle=5,
        test_results={"smoke_pass": True, "functional_pass": True},
        arbiter_verdict="ALLOW"
    )
    prov_files = list((tmp_path / "provenance").glob("cycle_005_*.json"))
    assert len(prov_files) == 1
    prov = json.loads(prov_files[0].read_text())
    assert prov["cycle"] == 5
    assert prov["eligible"] is True


def test_rollback_rejects_unapproved_actor(contract):
    result = contract.rollback("rando", "testing")
    assert result["rolled_back"] is False
    assert "not approved" in result["reason"]


def test_rollback_dry_run_returns_sha(contract, tmp_path):
    (tmp_path / ".karma_last_good").write_text("deadbeef")
    result = contract.rollback("colby", "testing rollback")
    assert result["rolled_back"] is True
    assert result["sha"] == "deadbeef"
    assert result["dry_run"] is True
