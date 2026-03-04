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


def test_query_relevant_relationships_empty_list():
    """query_relevant_relationships([]) returns [] without hitting FalkorDB."""
    import server
    with patch.object(server, "get_falkor") as mock_get_falkor:
        result = server.query_relevant_relationships([])
    mock_get_falkor.assert_not_called()
    assert result == []


def test_query_relevant_relationships_returns_facts():
    """query_relevant_relationships returns from/relationship/to dicts using r.fact."""
    import server

    mock_result = [
        ["header"],
        [["Karma", "uses for memory storage", "FalkorDB"],
         ["Colby", "is building", "Karma"]]
    ]

    with patch.object(server, "get_falkor") as mock_get_falkor:
        mock_r = MagicMock()
        mock_r.execute_command.return_value = mock_result
        mock_get_falkor.return_value = mock_r

        result = server.query_relevant_relationships(["Karma", "Colby"])

    assert len(result) == 2
    assert result[0] == {"from": "Karma", "relationship": "uses for memory storage", "to": "FalkorDB"}
    assert result[1] == {"from": "Colby", "relationship": "is building", "to": "Karma"}


def test_query_relevant_relationships_graceful_on_error():
    """query_relevant_relationships returns [] on FalkorDB failure."""
    import server
    with patch.object(server, "get_falkor") as mock_get_falkor:
        mock_get_falkor.side_effect = Exception("timeout")
        result = server.query_relevant_relationships(["Karma"])
    assert result == []
