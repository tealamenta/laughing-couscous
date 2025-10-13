"""Tests d'integration pour l'application."""

from unittest.mock import MagicMock
import sys

sys.modules["streamlit"] = MagicMock()


def test_ethnicity_list():
    """Test liste ethnicites."""
    from recipe_recommender.app import ETHNICITY_LIST

    assert "french" in ETHNICITY_LIST
    assert "italian" in ETHNICITY_LIST
    assert len(ETHNICITY_LIST) >= 10  # Au moins 10 cuisines


def test_dietary_list():
    """Test liste regimes."""
    from recipe_recommender.app import DIETARY_LIST

    assert "vegetarian" in DIETARY_LIST
    assert "vegan" in DIETARY_LIST
    assert "gluten-free" in DIETARY_LIST
