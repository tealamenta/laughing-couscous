"""Tests pour tabs_handler."""

import sys
from unittest.mock import MagicMock, patch

# Mock Streamlit
sys.modules["streamlit"] = MagicMock()

from recipe_recommender.utils.nutrition_filters import (
    check_calories_range,
    check_fat_range,
    check_carbs_range,
    check_protein_range,
)


def test_check_calories_range_valid():
    """Test verification calories valide."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_calories_range(nutrition, 400.0, 600.0) is True
    assert check_calories_range(nutrition, 600.0, 700.0) is False
    assert check_calories_range(nutrition, 100.0, 400.0) is False


def test_check_calories_range_no_limits():
    """Test sans limites calories."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_calories_range(nutrition, None, None) is True
    assert check_calories_range(nutrition, None, 600.0) is True
    assert check_calories_range(nutrition, 400.0, None) is True


def test_check_calories_range_empty():
    """Test avec nutrition vide."""
    assert check_calories_range([], 100.0, 500.0) is False


def test_check_fat_range_valid():
    """Test verification matiere grasse."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_fat_range(nutrition, 30.0) is True
    assert check_fat_range(nutrition, 15.0) is False


def test_check_fat_range_none():
    """Test sans limite matiere grasse."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_fat_range(nutrition, None) is True


def test_check_carbs_range_valid():
    """Test verification glucides."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_carbs_range(nutrition, 40.0) is True
    assert check_carbs_range(nutrition, 20.0) is False


def test_check_protein_range_valid():
    """Test verification proteines."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_protein_range(nutrition, 20.0) is True
    assert check_protein_range(nutrition, 30.0) is False
