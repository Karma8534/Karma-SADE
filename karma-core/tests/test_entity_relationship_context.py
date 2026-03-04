"""Tests for entity relationship context features."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock


def test_pattern_cache_starts_empty():
    """_pattern_cache is empty list on module import."""
    import importlib
    import server
    importlib.reload(server)
    assert server._pattern_cache == []


def test_refresh_pattern_cache_populates_cache():
    """_refresh_pattern_cache() stores results from FalkorDB query."""
    import server

    mock_result = [
        ["header"],                        # index 0: column names (ignored)
        [["Karma", 47], ["FalkorDB", 31]]  # index 1: rows
    ]

    with patch.object(server, "get_falkor") as mock_get_falkor:
        mock_r = MagicMock()
        mock_r.execute_command.return_value = mock_result
        mock_get_falkor.return_value = mock_r

        server._refresh_pattern_cache()

    assert len(server._pattern_cache) == 2
    assert server._pattern_cache[0] == {"entity": "Karma", "mentions": 47}
    assert server._pattern_cache[1] == {"entity": "FalkorDB", "mentions": 31}


def test_refresh_pattern_cache_graceful_on_error():
    """_refresh_pattern_cache() does not raise on FalkorDB failure."""
    import server
    server._pattern_cache = [{"entity": "OldData", "mentions": 5}]

    with patch.object(server, "get_falkor") as mock_get_falkor:
        mock_get_falkor.side_effect = Exception("FalkorDB unavailable")
        server._refresh_pattern_cache()  # must not raise

    # Cache preserved on error
    assert server._pattern_cache == [{"entity": "OldData", "mentions": 5}]
