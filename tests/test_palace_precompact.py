import sqlite3
from pathlib import Path

from Scripts.hooks import palace_precompact as hook


def test_precompact_respects_permission_gate(monkeypatch):
    monkeypatch.setattr(hook, "_permission_ok", lambda: (False, "blocked"))

    out = hook.handle({})

    assert out["permissionDecision"] == "deny"
    assert "blocked" in out["systemMessage"]


def test_precompact_trims_hall_events_only(tmp_path, monkeypatch):
    db = tmp_path / "claude-mem.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE observations (id INTEGER PRIMARY KEY, hall TEXT, created_at_epoch INTEGER)")
    for i in range(1, 8):
        hall = "hall_events" if i <= 5 else "hall_facts"
        conn.execute(
            "INSERT INTO observations (hall, created_at_epoch) VALUES (?, ?)",
            (hall, i),
        )
    conn.commit()
    conn.close()

    monkeypatch.setattr(hook, "DB_PATH", Path(db))
    monkeypatch.setattr(hook, "KEEP_EVENTS", 2)
    monkeypatch.setattr(hook, "_permission_ok", lambda: (True, "ok"))

    out = hook.handle({})

    conn = sqlite3.connect(db)
    events = conn.execute("SELECT count(*) FROM observations WHERE hall='hall_events'").fetchone()[0]
    facts = conn.execute("SELECT count(*) FROM observations WHERE hall='hall_facts'").fetchone()[0]
    remaining = [
        row[0]
        for row in conn.execute(
            "SELECT created_at_epoch FROM observations WHERE hall='hall_events' ORDER BY created_at_epoch DESC"
        ).fetchall()
    ]
    conn.close()

    assert "precompact removed 3 hall_events rows" in out["systemMessage"]
    assert events == 2
    assert facts == 2
    assert remaining == [5, 4]
