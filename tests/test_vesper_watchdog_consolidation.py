import datetime
import importlib
import json
import sys
from pathlib import Path


def _load_module():
    scripts_dir = Path(__file__).resolve().parents[1] / "Scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return importlib.import_module("Scripts.vesper_watchdog")


def test_vesper_watchdog_does_not_use_deprecated_utcnow():
    source = Path("Scripts/vesper_watchdog.py").read_text(encoding="utf-8")
    assert "datetime.datetime.utcnow(" not in source


def _iso(ts: datetime.datetime) -> str:
    return ts.astimezone(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def test_load_consolidation_state_defaults_when_missing(tmp_path, monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "CONSOLIDATION_STATE_FILE", tmp_path / "state.json")

    state = mod.load_consolidation_state()

    assert state["last_consolidated_at"] is None


def test_should_consolidate_short_circuits_before_entry_scan_when_time_gate_fails(tmp_path, monkeypatch):
    mod = _load_module()
    now = datetime.datetime(2026, 4, 5, 20, 0, tzinfo=datetime.timezone.utc)
    monkeypatch.setattr(mod, "CONSOLIDATION_STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(mod, "CONSOLIDATION_LOCK_FILE", tmp_path / "lock")
    monkeypatch.setattr(mod, "CONSOLIDATION_MIN_HOURS", 24.0)

    state = {"last_consolidated_at": _iso(now - datetime.timedelta(hours=1))}

    def fail_scan(_state):
        raise AssertionError("entry gate should not run when time gate fails")

    monkeypatch.setattr(mod, "entry_gate_passes", fail_scan)

    assert mod.should_consolidate(state=state, now=now) is False


def test_should_consolidate_requires_enough_new_entries_and_no_fresh_lock(tmp_path, monkeypatch):
    mod = _load_module()
    now = datetime.datetime(2026, 4, 5, 20, 0, tzinfo=datetime.timezone.utc)
    monkeypatch.setattr(mod, "EVOLUTION_LOG", tmp_path / "regent_evolution.jsonl")
    monkeypatch.setattr(mod, "CONSOLIDATION_STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(mod, "CONSOLIDATION_LOCK_FILE", tmp_path / "lock")
    monkeypatch.setattr(mod, "CONSOLIDATION_THRESHOLD", 3)
    monkeypatch.setattr(mod, "CONSOLIDATION_MIN_HOURS", 1.0)

    last = now - datetime.timedelta(hours=2)
    entries = [
        {"ts": _iso(last + datetime.timedelta(minutes=5)), "message": "a"},
        {"ts": _iso(last + datetime.timedelta(minutes=10)), "message": "b"},
        {"ts": _iso(last + datetime.timedelta(minutes=15)), "message": "c"},
    ]
    mod.EVOLUTION_LOG.write_text("\n".join(json.dumps(row) for row in entries) + "\n", encoding="utf-8")

    state = {"last_consolidated_at": _iso(last)}

    assert mod.should_consolidate(state=state, now=now) is True

    mod.CONSOLIDATION_LOCK_FILE.write_text("locked", encoding="utf-8")
    fresh = now.timestamp()
    import os
    os.utime(mod.CONSOLIDATION_LOCK_FILE, (fresh, fresh))

    assert mod.should_consolidate(state=state, now=now) is False


def test_stale_lock_does_not_block_consolidation(tmp_path, monkeypatch):
    mod = _load_module()
    now = datetime.datetime(2026, 4, 5, 20, 0, tzinfo=datetime.timezone.utc)
    monkeypatch.setattr(mod, "EVOLUTION_LOG", tmp_path / "regent_evolution.jsonl")
    monkeypatch.setattr(mod, "CONSOLIDATION_STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(mod, "CONSOLIDATION_LOCK_FILE", tmp_path / "lock")
    monkeypatch.setattr(mod, "CONSOLIDATION_THRESHOLD", 1)
    monkeypatch.setattr(mod, "CONSOLIDATION_MIN_HOURS", 1.0)

    last = now - datetime.timedelta(hours=2)
    mod.EVOLUTION_LOG.write_text(json.dumps({"ts": _iso(now - datetime.timedelta(minutes=1))}) + "\n", encoding="utf-8")
    state = {"last_consolidated_at": _iso(last)}

    mod.CONSOLIDATION_LOCK_FILE.write_text("locked", encoding="utf-8")
    stale = (now - datetime.timedelta(hours=2)).timestamp()
    import os
    os.utime(mod.CONSOLIDATION_LOCK_FILE, (stale, stale))

    assert mod.lock_gate_passes(now=now) is True
    assert mod.should_consolidate(state=state, now=now) is True


def test_mark_consolidation_complete_updates_state_and_releases_lock(tmp_path, monkeypatch):
    mod = _load_module()
    now = datetime.datetime(2026, 4, 5, 20, 0, tzinfo=datetime.timezone.utc)
    monkeypatch.setattr(mod, "CONSOLIDATION_STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(mod, "CONSOLIDATION_LOCK_FILE", tmp_path / "lock")

    mod.CONSOLIDATION_LOCK_FILE.write_text("locked", encoding="utf-8")

    mod.mark_consolidation_complete(now=now)

    state = json.loads(mod.CONSOLIDATION_STATE_FILE.read_text(encoding="utf-8"))
    assert state["last_consolidated_at"] == _iso(now)
    assert not mod.CONSOLIDATION_LOCK_FILE.exists()


def test_consolidate_memories_writes_record_marks_log_and_updates_state(tmp_path, monkeypatch):
    mod = _load_module()
    now = datetime.datetime(2026, 4, 5, 20, 0, tzinfo=datetime.timezone.utc)
    monkeypatch.setattr(mod, "EVOLUTION_LOG", tmp_path / "regent_evolution.jsonl")
    monkeypatch.setattr(mod, "CONSOLIDATION_FILE", tmp_path / "vesper_consolidations.jsonl")
    monkeypatch.setattr(mod, "CONSOLIDATION_STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(mod, "CONSOLIDATION_LOCK_FILE", tmp_path / "lock")
    monkeypatch.setattr(mod, "CONSOLIDATION_THRESHOLD", 2)
    monkeypatch.setattr(mod, "CONSOLIDATION_BATCH_SIZE", 2)
    monkeypatch.setattr(mod, "CONSOLIDATION_MIN_HOURS", 1.0)

    last = now - datetime.timedelta(hours=2)
    rows = [
        {"ts": _iso(last + datetime.timedelta(minutes=5)), "from": "colby", "source": "chat"},
        {"ts": _iso(last + datetime.timedelta(minutes=10)), "from": "colby", "source": "chat"},
    ]
    mod.EVOLUTION_LOG.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    mod.save_consolidation_state({"last_consolidated_at": _iso(last)})

    monkeypatch.setattr(
        mod,
        "_run_consolidation_model",
        lambda prompt: {
            "connections": "recent directives align around continuity",
            "insights": "keep the merged workspace stable",
            "importance": 0.8,
            "fix_skills": ["continuity"],
            "derived_skills": [],
            "captured_skills": [],
            "entities": ["Colby"],
            "topics": ["continuity"],
            "recommendation": "preserve the shared transcript substrate",
        },
    )

    changed = mod.consolidate_memories(now=now)

    assert changed == 2
    record = json.loads(mod.CONSOLIDATION_FILE.read_text(encoding="utf-8").splitlines()[0])
    assert record["entry_count"] == 2
    assert record["connections"] == "recent directives align around continuity"
    updated_rows = [json.loads(line) for line in mod.EVOLUTION_LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert all(row["consolidated"] is True for row in updated_rows)
    state = json.loads(mod.CONSOLIDATION_STATE_FILE.read_text(encoding="utf-8"))
    assert state["last_consolidated_at"] == _iso(now)
