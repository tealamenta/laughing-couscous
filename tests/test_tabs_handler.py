"""Tests pour les gestionnaires d'onglets (tabs handlers)."""
import sys
from unittest.mock import MagicMock

# Mock Streamlit avant import
sys.modules["streamlit"] = MagicMock()

# ruff: noqa: E402
from recipe_recommender.utils.nutrition_filters import (
    check_calories_range,
    check_fat_range,
    check_carbs_range,
    check_protein_range,
)


def test_check_calories_range_valid():
    """Test avec calories valides."""
    # Format: [calories, fat%, sugar%, sodium%, protein%, sat_fat%, carbs%]
    nutrition = [500, 10, 20, 30, 15, 5, 40]
    assert check_calories_range(nutrition, 200, 800) is True
    assert check_calories_range(nutrition, 500, 800) is True
    assert check_calories_range(nutrition, 200, 500) is True


def test_check_calories_range_no_limits():
    """Test sans limites."""
    nutrition = [500, 10, 20, 30, 15, 5, 40]
    assert check_calories_range(nutrition, None, None) is True


def test_check_calories_range_empty():
    """Test avec nutrition vide."""
    # Liste vide
    nutrition = []
    result = check_calories_range(nutrition, 200, 800)
    assert result is False


def test_check_fat_range_valid():
    """Test fat range valide."""
    # nutrition[1] = fat %DV
    # Signature: check_fat_range(nutrition, max_fat_pdv)
    nutrition = [500, 10, 20, 30, 15, 5, 40]
    assert check_fat_range(nutrition, 15) is True  # 10 <= 15
    assert check_fat_range(nutrition, 10) is True  # 10 <= 10
    assert check_fat_range(nutrition, 5) is False  # 10 > 5


def test_check_fat_range_none():
    """Test fat range avec None."""
    nutrition = [500, 10, 20, 30, 15, 5, 40]
    # Si max_fat_pdv est None, retourne True
    assert check_fat_range(nutrition, None) is True

    # Liste vide
    assert check_fat_range([], 15) is False


def test_check_carbs_range_valid():
    """Test carbs range valide."""
    # nutrition[6] = carbs %DV
    # Signature: check_carbs_range(nutrition, max_carbs_pdv)
    nutrition = [500, 10, 20, 30, 15, 5, 50]
    assert check_carbs_range(nutrition, 60) is True  # 50 <= 60
    assert check_carbs_range(nutrition, 50) is True  # 50 <= 50
    assert check_carbs_range(nutrition, 40) is False  # 50 > 40


def test_check_protein_range_valid():
    """Test protein range valide."""
    # nutrition[4] = protein %DV
    # Signature: check_protein_range(nutrition, min_protein_pdv)
    nutrition = [500, 10, 20, 30, 20, 5, 40]
    assert check_protein_range(nutrition, 15) is True  # 20 >= 15
    assert check_protein_range(nutrition, 20) is True  # 20 >= 20
    assert check_protein_range(nutrition, 25) is False  # 20 < 25
