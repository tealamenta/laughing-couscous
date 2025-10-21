"""Tests d'integration pour l'application."""
import sys
from unittest.mock import MagicMock

# Mock Streamlit
sys.modules["streamlit"] = MagicMock()

from recipe_recommender.app import ETHNICITY_LIST, DIETARY_LIST


def test_ethnicity_list():
    """Test que ETHNICITY_LIST contient les types attendus."""
    assert isinstance(ETHNICITY_LIST, list)
    assert len(ETHNICITY_LIST) > 0
    # Vérifier quelques cuisines clés (en anglais car c'est le format dans app.py)
    assert "French" in ETHNICITY_LIST or "Français" in ETHNICITY_LIST
    assert "Italian" in ETHNICITY_LIST or "Italien" in ETHNICITY_LIST
    assert len(ETHNICITY_LIST) >= 20  # Au moins 20 cuisines


def test_dietary_list():
    """Test que DIETARY_LIST contient les régimes attendus."""
    assert isinstance(DIETARY_LIST, list)
    assert len(DIETARY_LIST) > 0
    # Vérifier quelques régimes clés (français ou anglais)
    assert "Végétarien" in DIETARY_LIST or "Vegetarian" in DIETARY_LIST
    assert "Végétalien" in DIETARY_LIST or "Vegan" in DIETARY_LIST
    assert len(DIETARY_LIST) >= 8  # Au moins 8 régimes
