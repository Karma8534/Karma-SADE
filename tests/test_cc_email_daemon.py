import importlib.util
import json
from pathlib import Path


def load_module():
    path = Path("Scripts/cc_email_daemon.py")
    spec = importlib.util.spec_from_file_location("cc_email_daemon_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_status_interval_is_30_minutes_and_check_interval_is_15_minutes():
    mod = load_module()
    assert mod.CHECK_INTERVAL_MIN == 15
    assert mod.STATUS_INTERVAL_MIN == 30


def test_email_ollama_defaults_match_live_p1_floor():
    mod = load_module()
    assert mod.OLLAMA_URL == "http://localhost:11434/v1/chat/completions"
    assert mod.OLLAMA_MODEL == "sam860/LFM2:350m"


def test_sovereign_sender_detection_accepts_colby_address():
    mod = load_module()
    assert mod.is_sovereign_sender("Colby <rae.steele76@gmail.com>")
    assert mod.is_sovereign_sender("rae.steele76@gmail.com")
    assert not mod.is_sovereign_sender("someone@example.com")


def test_queue_sovereign_directive_writes_pending_json(tmp_path):
    mod = load_module()
    mod.DIRECTIVE_QUEUE_DIR = tmp_path
    message = {
        "from": "Colby <rae.steele76@gmail.com>",
        "subject": "Directive: Fix the bridge",
        "date": "Sat, 05 Apr 2026 12:00:00 -0400",
        "body": "Repair the bridge path and report back.",
    }
    out = mod.queue_sovereign_directive(message, received_at="2026-04-05T16:30:00Z")
    payload = json.loads(Path(out).read_text(encoding="utf-8"))
    assert payload["kind"] == "sovereign_email_directive"
    assert payload["state"] == "pending"
    assert payload["from"] == "rae.steele76@gmail.com"
    assert payload["subject"] == "Directive: Fix the bridge"
    assert "Repair the bridge path" in payload["body"]


def test_process_new_messages_queues_and_acks_sovereign_email(tmp_path):
    mod = load_module()
    mod.DIRECTIVE_QUEUE_DIR = tmp_path
    sent = []
    bus = []

    def fake_send(subject, body):
        sent.append((subject, body))
        return {"ok": True}

    def fake_bus(content):
        bus.append(content)

    messages = [
        {
            "from": "Colby <rae.steele76@gmail.com>",
            "subject": "Directive: tighten the harness",
            "date": "Sat, 05 Apr 2026 12:00:00 -0400",
            "body": "Tighten the harness and verify it.",
        }
    ]

    result = mod.process_new_messages(messages, send_email=fake_send, bus_post=fake_bus)
    assert result["sovereign_count"] == 1
    assert len(result["queued"]) == 1
    assert sent and sent[0][0] == "Re: Directive: tighten the harness"
    assert "My understanding" in sent[0][1]
    assert bus and "SOVEREIGN EMAIL DIRECTIVE" in bus[0]


def test_state_blocker_summary_only_lists_open_items(tmp_path):
    mod = load_module()
    gsd = tmp_path / ".gsd"
    gsd.mkdir()
    state = gsd / "STATE.md"
    state.write_text(
        "# STATE\n\n## Active Blockers\n\n"
        "1. ~~Broken thing~~ ✅ RESOLVED\n"
        "2. **Open thing** -- still pending\n"
        "3. ~~False alarm~~ ✅ FALSE POSITIVE\n",
        encoding="utf-8",
    )
    mod.REPO = tmp_path
    summary = mod._read_state_blockers()
    assert "Open blockers: 1" in summary
    assert "B2: Open thing -- still pending" in summary
    assert "Broken thing" not in summary
    assert "False alarm" not in summary
    assert "~~" not in summary
    assert "**" not in summary


def test_status_email_body_uses_clean_digest_not_raw_markdown():
    mod = load_module()
    body = mod.build_status_email_body(
        "2026-04-05 20:05 UTC",
        "Snapshot generated: 2026-04-05T15:50:12Z\nCurrent focus: Repair status email formatting.\nThe One Thing: Make cc_server real.",
        "Open blockers: 2\n- B17: dead code\n- B18: proof pending",
    )
    assert "CC Ascendant - Status Report" in body
    assert "Current focus: Repair status email formatting." in body
    assert "Open blockers: 2" in body
    assert "~~" not in body
    assert "**" not in body
    assert "???" not in body
    assert '??"' not in body
    assert "??" not in body
    assert "## Active Blockers" not in body


def test_cmd_check_is_time_gated(tmp_path):
    mod = load_module()
    mod.CHECK_LAST_FILE = tmp_path / "cc_email_check_last.txt"
    mod.CHECK_LAST_FILE.write_text(datetime_now_iso())
    result = mod.cmd_check()
    assert "skipped (" in result
    assert "threshold=15m" in result


def test_cmd_status_is_time_gated_every_30_minutes(tmp_path):
    mod = load_module()
    mod.STATUS_SENT_FILE = tmp_path / "cc_email_status_last.txt"
    mod.STATUS_SENT_FILE.write_text(datetime_now_iso())
    result = mod.cmd_status()
    assert "skipped (" in result
    assert "threshold=30m" in result


def datetime_now_iso():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
