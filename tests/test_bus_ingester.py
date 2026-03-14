import json
import pytest
from pathlib import Path
from Scripts.karma_bus_ingester import BusIngester


@pytest.fixture
def ingester(tmp_path):
    issues_file = tmp_path / "kiki_issues.jsonl"
    return BusIngester(issues_file=str(issues_file))


def test_converts_seed_issue_to_kiki_format(ingester):
    msg = {
        "id": "msg-001",
        "type": "seed_issue",
        "status": "PENDING",
        "payload": {
            "title": "Fix the login bug",
            "body": "Users report 500 on /login"
        }
    }
    issue = ingester.convert(msg)
    assert issue["issue"] == "Fix the login bug"
    assert issue["details"] == "Users report 500 on /login"
    assert issue["source"] == "karma_core"
    assert issue["coordination_id"] == "msg-001"


def test_ignores_non_seed_issue_messages(ingester):
    msgs = [
        {"id": "1", "type": "status_update", "status": "PENDING", "payload": {}},
        {"id": "2", "type": "rollback_event", "status": "PENDING", "payload": {}},
    ]
    result = ingester.filter_pending(msgs)
    assert len(result) == 0


def test_filters_only_pending_seed_issues(ingester):
    msgs = [
        {"id": "1", "type": "seed_issue", "status": "PENDING", "payload": {"title": "A"}},
        {"id": "2", "type": "seed_issue", "status": "PROCESSED", "payload": {"title": "B"}},
    ]
    result = ingester.filter_pending(msgs)
    assert len(result) == 1
    assert result[0]["id"] == "1"


def test_appends_to_issues_file(ingester, tmp_path):
    issues_file = tmp_path / "kiki_issues.jsonl"
    ingester.issues_file = issues_file
    msgs = [
        {"id": "1", "type": "seed_issue", "status": "PENDING",
         "payload": {"title": "Task A", "body": "Details A"}}
    ]
    count = ingester.ingest(msgs)
    assert count == 1
    lines = issues_file.read_text().strip().split("\n")
    assert len(lines) == 1
    issue = json.loads(lines[0])
    assert issue["issue"] == "Task A"
