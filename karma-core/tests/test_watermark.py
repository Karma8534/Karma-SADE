import json
import os
import tempfile
import pytest
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from batch_ingest import read_watermark, write_watermark, read_new_episodes


def _make_ledger(tmp_path, entries):
    p = tmp_path / "memory.jsonl"
    with open(p, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    return str(p)


def _make_entry(user="hello", assistant="hi", provider="hub-chat"):
    return {
        "tags": ["hub", "chat"],
        "content": {
            "user_message": user,
            "assistant_text": assistant,
            "provider": provider,
        }
    }


class TestWatermark:
    def test_init_creates_watermark_at_current_line_count(self, tmp_path):
        ledger = _make_ledger(tmp_path, [_make_entry() for _ in range(5)])
        wm_path = str(tmp_path / ".watermark")
        result = read_watermark(wm_path, ledger)
        assert result == 5
        assert os.path.exists(wm_path)

    def test_read_watermark_returns_existing_value(self, tmp_path):
        ledger = _make_ledger(tmp_path, [_make_entry()])
        wm_path = str(tmp_path / ".watermark")
        write_watermark(wm_path, 42)
        assert read_watermark(wm_path, ledger) == 42

    def test_write_watermark_atomic(self, tmp_path):
        wm_path = str(tmp_path / ".watermark")
        write_watermark(wm_path, 99)
        with open(wm_path) as f:
            assert f.read().strip() == "99"
        assert not os.path.exists(wm_path + ".tmp")


class TestReadNewEpisodes:
    def test_reads_from_start_line(self, tmp_path):
        entries = [_make_entry(user=f"msg{i}") for i in range(10)]
        ledger = _make_ledger(tmp_path, entries)
        episodes, end_line = read_new_episodes(ledger, start_line=5, max_batch=200)
        assert len(episodes) == 5
        assert end_line == 10

    def test_respects_max_batch(self, tmp_path):
        entries = [_make_entry() for _ in range(50)]
        ledger = _make_ledger(tmp_path, entries)
        episodes, end_line = read_new_episodes(ledger, start_line=0, max_batch=20)
        assert len(episodes) == 20

    def test_skips_entries_without_required_fields(self, tmp_path):
        entries = [
            {"content": {"user_message": "hi"}},
            _make_entry(),
        ]
        ledger = _make_ledger(tmp_path, entries)
        episodes, _ = read_new_episodes(ledger, start_line=0, max_batch=200)
        assert len(episodes) == 1

    def test_empty_from_start_line_at_end(self, tmp_path):
        entries = [_make_entry() for _ in range(3)]
        ledger = _make_ledger(tmp_path, entries)
        episodes, end_line = read_new_episodes(ledger, start_line=3, max_batch=200)
        assert len(episodes) == 0
        assert end_line == 3
