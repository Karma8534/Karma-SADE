import json
import pytest
from unittest.mock import patch
from Scripts.karma_critic_agent import CriticAgent


@pytest.fixture
def critic():
    return CriticAgent(dry_run=True)


def test_critic_returns_plan_structure(critic):
    issue = {"issue": "Fix the login bug", "details": "500 on /login"}
    plan = critic.get_plan(issue, context="")
    # In dry_run mode, returns a canned plan
    assert "plan" in plan
    assert "tests" in plan
    assert "risks" in plan
    assert "confidence" in plan


def test_critic_unavailable_returns_none_gracefully():
    critic_live = CriticAgent(dry_run=False)
    with patch.object(critic_live, '_call_ollama', side_effect=Exception("Ollama down")):
        result = critic_live.get_plan({"issue": "test"}, context="")
    # None signals degraded mode — caller continues without critic
    assert result is None


def test_critic_cannot_close_issues(critic):
    # Critic output has no close/commit/write fields
    plan = critic.get_plan({"issue": "test"}, context="")
    assert "close_issue" not in plan
    assert "commit" not in plan
    assert "write_file" not in plan
