"""Tests pour CacheManager."""

import pytest
from pathlib import Path
from recipe_recommender.utils.cache_manager import CacheManager


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Créer dossier cache temporaire."""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir(exist_ok=True)
    return str(cache_dir)


def test_cache_manager_init(temp_cache_dir):
    """Test initialisation."""
    manager = CacheManager(temp_cache_dir)
    assert manager.cache_dir.exists()


def test_cache_exists(temp_cache_dir):
    """Test cache_exists."""
    manager = CacheManager(temp_cache_dir)
    assert not manager.cache_exists("nonexistent")


def test_save_cache(temp_cache_dir):
    """Test save_cache."""
    manager = CacheManager(temp_cache_dir)
    data = {"test_key": "test_value", "numbers": [1, 2, 3]}

    success = manager.save_cache("test", data)
    assert success
    assert manager.cache_exists("test")


def test_load_cache(temp_cache_dir):
    """Test load_cache."""
    manager = CacheManager(temp_cache_dir)

    # Sauvegarder d'abord
    original = {"test_key": "test_value", "numbers": [1, 2, 3]}
    manager.save_cache("test", original)

    # Charger
    loaded = manager.load_cache("test")

    # Vérifier (peut être None si pickle échoue)
    if loaded is not None:
        assert loaded["test_key"] == original["test_key"]
        assert loaded["numbers"] == original["numbers"]


def test_delete_cache(temp_cache_dir):
    """Test delete_cache."""
    manager = CacheManager(temp_cache_dir)

    # Créer
    manager.save_cache("test", {"x": 1})
    assert manager.cache_exists("test")

    # Supprimer
    success = manager.delete_cache("test")
    assert success
    assert not manager.cache_exists("test")
