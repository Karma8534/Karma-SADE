"""
Tests for identify_duplicates.py script.
"""
import pytest
import sys
import os

# Add karma-core to path so we can import the scripts module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function to test
from scripts.identify_duplicates import find_duplicate_entities


def test_find_duplicate_entities_returns_dict():
    """Should return dict of duplicate groups."""
    result = find_duplicate_entities()
    assert isinstance(result, dict)
    # Each value should be a list of entities
    for group, entities in result.items():
        assert isinstance(entities, list)
        assert all(isinstance(e, dict) for e in entities)
        assert all('id' in e and 'name' in e for e in entities)
