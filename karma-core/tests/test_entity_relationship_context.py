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


def test_query_relevant_relationships_returns_cooccurrence_dicts():
    """query_relevant_relationships returns from/relationship/to dicts using MENTIONS co-occurrence count."""
    import server

    # New row format: [from_entity, to_entity, cocount(int)]
    mock_result = [
        ["header"],
        [["Karma", "FalkorDB", 21],
         ["Colby", "Karma", 123]]
    ]

    with patch.object(server, "get_falkor") as mock_get_falkor:
        mock_r = MagicMock()
        mock_r.execute_command.return_value = mock_result
        mock_get_falkor.return_value = mock_r

        result = server.query_relevant_relationships(["Karma", "Colby"])

    assert len(result) == 2
    assert result[0]["from"] == "Karma"
    assert result[0]["to"] == "FalkorDB"
    assert "21" in result[0]["relationship"]
    assert "episode" in result[0]["relationship"]
    assert result[1]["from"] == "Colby"
    assert result[1]["to"] == "Karma"
    assert "123" in result[1]["relationship"]


def test_query_relevant_relationships_graceful_on_error():
    """query_relevant_relationships returns [] on FalkorDB failure."""
    import server
    with patch.object(server, "get_falkor") as mock_get_falkor:
        mock_get_falkor.side_effect = Exception("timeout")
        result = server.query_relevant_relationships(["Karma"])
    assert result == []


def test_query_relevant_relationships_uses_mentions_not_relates_to():
    """query_relevant_relationships queries MENTIONS co-occurrence, not frozen RELATES_TO edges.

    RELATES_TO edges are permanently frozen at 2026-03-04 (pre-skip-dedup era).
    MENTIONS co-occurrence is live and grows with every batch_ingest run.
    Row format from new Cypher: [from_entity, to_entity, cocount(int)]
    """
    import server

    mock_result = [
        ["header"],
        [["Karma", "FalkorDB", 21],
         ["Karma", "Colby", 123]],
    ]

    with patch.object(server, "get_falkor") as mock_get_falkor:
        mock_r = MagicMock()
        mock_r.execute_command.return_value = mock_result
        mock_get_falkor.return_value = mock_r

        result = server.query_relevant_relationships(["Karma"])

        # The Cypher issued must use MENTIONS, not RELATES_TO
        call_args = mock_r.execute_command.call_args[0]
        cypher_issued = call_args[2]
        assert "MENTIONS" in cypher_issued, "Cypher must use MENTIONS edges"
        assert "RELATES_TO" not in cypher_issued, "Cypher must NOT use stale RELATES_TO edges"

    assert len(result) == 2
    assert result[0]["from"] == "Karma"
    assert result[0]["to"] == "FalkorDB"
    assert "21" in result[0]["relationship"]


def test_query_relevant_relationships_formats_cooccurrence_label():
    """relationship label is human-readable co-occurrence string, not a raw edge fact."""
    import server

    mock_result = [
        ["header"],
        [["User", "Karma", 100]],
    ]

    with patch.object(server, "get_falkor") as mock_get_falkor:
        mock_r = MagicMock()
        mock_r.execute_command.return_value = mock_result
        mock_get_falkor.return_value = mock_r

        result = server.query_relevant_relationships(["User"])

    assert len(result) == 1
    assert result[0]["from"] == "User"
    assert result[0]["to"] == "Karma"
    assert "100" in result[0]["relationship"]
    assert "episode" in result[0]["relationship"]


def test_build_karma_context_includes_relationship_section():
    """build_karma_context includes Entity Relationships section when edges exist."""
    import server

    # Mock entity query to return known entities
    mock_entities = [{"name": "Karma", "summary": "AI system"}, {"name": "FalkorDB", "summary": "graph DB"}]
    # Mock relationship query to return edges
    mock_rels = [{"from": "Karma", "relationship": "stores data in", "to": "FalkorDB"}]

    with patch.object(server, "query_knowledge_graph", return_value=mock_entities), \
         patch.object(server, "query_relevant_relationships", return_value=mock_rels), \
         patch.object(server, "_pattern_cache", []), \
         patch.object(server, "query_identity_facts", return_value=""), \
         patch.object(server, "query_recent_episodes", return_value=[]), \
         patch.object(server, "query_recent_ingest_episodes", return_value=[]), \
         patch.object(server, "query_pending_cc_proposals", return_value=[]), \
         patch.object(server, "query_preferences", return_value=[]):
        ctx = server.build_karma_context("test message")

    assert "## Entity Relationships" in ctx
    assert "Karma → stores data in → FalkorDB" in ctx


def test_build_karma_context_includes_recurring_topics():
    """build_karma_context includes Recurring Topics section when pattern cache has data."""
    import server

    mock_entities = [{"name": "Karma", "summary": "AI system"}]
    mock_pattern = [{"entity": "Karma", "mentions": 47}, {"entity": "FalkorDB", "mentions": 31}]

    with patch.object(server, "query_knowledge_graph", return_value=mock_entities), \
         patch.object(server, "query_relevant_relationships", return_value=[]), \
         patch.object(server, "_pattern_cache", mock_pattern), \
         patch.object(server, "query_identity_facts", return_value=""), \
         patch.object(server, "query_recent_episodes", return_value=[]), \
         patch.object(server, "query_recent_ingest_episodes", return_value=[]), \
         patch.object(server, "query_pending_cc_proposals", return_value=[]), \
         patch.object(server, "query_preferences", return_value=[]):
        ctx = server.build_karma_context("test message")

    assert "## Recurring Topics" in ctx
    assert "1. Karma (47 episodes)" in ctx
    assert "2. FalkorDB (31 episodes)" in ctx


def test_build_karma_context_omits_sections_when_empty():
    """build_karma_context omits both sections when no data available."""
    import server

    with patch.object(server, "query_knowledge_graph", return_value=[]), \
         patch.object(server, "query_relevant_relationships", return_value=[]), \
         patch.object(server, "_pattern_cache", []), \
         patch.object(server, "query_identity_facts", return_value=""), \
         patch.object(server, "query_recent_episodes", return_value=[]), \
         patch.object(server, "query_recent_ingest_episodes", return_value=[]), \
         patch.object(server, "query_pending_cc_proposals", return_value=[]), \
         patch.object(server, "query_preferences", return_value=[]):
        ctx = server.build_karma_context("test message")

    assert "## Entity Relationships" not in ctx
    assert "## Recurring Topics" not in ctx
