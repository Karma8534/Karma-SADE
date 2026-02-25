"""
Tests for remove_duplicates.py script.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add karma-core to path so we can import the scripts module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the functions to test
from scripts.remove_duplicates import find_and_mark_duplicates, get_canonical_entity


def test_find_and_mark_duplicates_returns_structure():
    """Test that function returns correct dict structure with keep/delete keys."""
    # Mock the Redis connection and result
    mock_redis = MagicMock()

    # Simulate FalkorDB response: header + data rows
    # Each row: [entity_id, name, entity_type, created_at]
    mock_redis.execute_command.return_value = [
        ['e.id', 'e.name', 'e.entity_type', 'e.created_at'],  # header
        [
            ('e1', 'Alice', 'person', '2026-01-01T00:00:00Z'),
            ('e2', 'Alice', 'person', '2026-01-02T00:00:00Z'),  # duplicate
            ('e3', 'Bob', 'person', '2026-01-03T00:00:00Z'),
        ]
    ]

    with patch('redis.Redis', return_value=mock_redis):
        result = find_and_mark_duplicates()

    # Should have 'keep' and 'delete' keys
    assert isinstance(result, dict)
    assert 'keep' in result
    assert 'delete' in result
    assert isinstance(result['keep'], list)
    assert isinstance(result['delete'], list)

    # Should have one entity to keep (lowest ID) and one to delete
    assert len(result['keep']) > 0
    assert len(result['delete']) > 0


def test_get_canonical_entity_picks_lowest_id():
    """Test that canonical selection keeps entity with lowest ID."""
    entities = [
        {'id': 'e5', 'name': 'Alice', 'type': 'person', 'created_at': '2026-01-05T00:00:00Z'},
        {'id': 'e3', 'name': 'Alice', 'type': 'person', 'created_at': '2026-01-03T00:00:00Z'},
        {'id': 'e8', 'name': 'Alice', 'type': 'person', 'created_at': '2026-01-08T00:00:00Z'},
    ]

    canonical = get_canonical_entity(entities)

    # Should pick the one with lowest ID (lexicographically)
    assert canonical['id'] == 'e3'


def test_get_canonical_entity_single_entity():
    """Test that canonical selection works with single entity."""
    entities = [
        {'id': 'e1', 'name': 'Bob', 'type': 'person', 'created_at': '2026-01-01T00:00:00Z'},
    ]

    canonical = get_canonical_entity(entities)

    # Should return the only entity
    assert canonical['id'] == 'e1'


def test_find_and_mark_duplicates_groups_by_normalized_name():
    """Test that function correctly groups entities by normalized (lowercase) name."""
    mock_redis = MagicMock()

    # Same name with different cases and whitespace
    mock_redis.execute_command.return_value = [
        ['e.id', 'e.name', 'e.entity_type', 'e.created_at'],
        [
            ('e1', 'Alice Smith', 'person', '2026-01-01T00:00:00Z'),
            ('e2', 'alice smith', 'person', '2026-01-02T00:00:00Z'),
            ('e3', 'ALICE SMITH', 'person', '2026-01-03T00:00:00Z'),
            ('e4', 'Bob Johnson', 'person', '2026-01-04T00:00:00Z'),
        ]
    ]

    with patch('redis.Redis', return_value=mock_redis):
        result = find_and_mark_duplicates()

    # Should group all variations of "Alice Smith"
    # and keep only one, with the rest for deletion
    # Total: 3 duplicates of Alice Smith, 1 Bob (no duplicate)
    assert len(result['delete']) == 2  # 2 copies of Alice to delete
    assert len(result['keep']) == 2    # 1 Alice canonical + 1 Bob


def test_find_and_mark_duplicates_no_duplicates():
    """Test that function handles case with no duplicates."""
    mock_redis = MagicMock()

    mock_redis.execute_command.return_value = [
        ['e.id', 'e.name', 'e.entity_type', 'e.created_at'],
        [
            ('e1', 'Alice', 'person', '2026-01-01T00:00:00Z'),
            ('e2', 'Bob', 'person', '2026-01-02T00:00:00Z'),
            ('e3', 'Charlie', 'person', '2026-01-03T00:00:00Z'),
        ]
    ]

    with patch('redis.Redis', return_value=mock_redis):
        result = find_and_mark_duplicates()

    # No duplicates, so delete list should be empty
    assert len(result['delete']) == 0
    assert len(result['keep']) == 3


def test_find_and_mark_duplicates_empty_result():
    """Test that function handles empty FalkorDB result."""
    mock_redis = MagicMock()

    # Empty result
    mock_redis.execute_command.return_value = [
        ['e.id', 'e.name', 'e.entity_type', 'e.created_at'],
    ]

    with patch('redis.Redis', return_value=mock_redis):
        result = find_and_mark_duplicates()

    # Should return empty lists
    assert len(result['delete']) == 0
    assert len(result['keep']) == 0


def test_canonical_has_required_fields():
    """Test that canonical entity has all required fields."""
    mock_redis = MagicMock()

    mock_redis.execute_command.return_value = [
        ['e.id', 'e.name', 'e.entity_type', 'e.created_at'],
        [
            ('e1', 'Alice', 'person', '2026-01-01T00:00:00Z'),
            ('e2', 'Alice', 'person', '2026-01-02T00:00:00Z'),
        ]
    ]

    with patch('redis.Redis', return_value=mock_redis):
        result = find_and_mark_duplicates()

    # All kept entities should have required fields
    for entity in result['keep']:
        assert 'id' in entity
        assert 'name' in entity
        assert 'type' in entity
        assert 'created_at' in entity

    # All deleted entities should have required fields
    for entity in result['delete']:
        assert 'id' in entity
        assert 'name' in entity
        assert 'type' in entity
        assert 'created_at' in entity
