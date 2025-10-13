"""Tests pour config."""

from recipe_recommender.config import HYBRID_WEIGHTS, DEFAULT_HYBRID_CONFIG


def test_hybrid_weights_exists():
    """Test configurations poids existent."""
    assert "balanced" in HYBRID_WEIGHTS
    assert "precision" in HYBRID_WEIGHTS
    assert "semantic" in HYBRID_WEIGHTS


def test_hybrid_weights_values():
    """Test valeurs poids."""
    balanced = HYBRID_WEIGHTS["balanced"]
    assert balanced["tfidf"] == 0.5
    assert balanced["bert"] == 0.5

    precision = HYBRID_WEIGHTS["precision"]
    assert precision["tfidf"] == 0.6
    assert precision["bert"] == 0.4


def test_default_config():
    """Test config par defaut."""
    assert DEFAULT_HYBRID_CONFIG == "balanced"
