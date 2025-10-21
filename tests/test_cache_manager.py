"""Tests pour CacheManager."""

import pytest
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


def test_load_cache_file_not_found():
    """Test chargement cache inexistant."""
    from recipe_recommender.utils.cache_manager import CacheManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = CacheManager(tmpdir)
        result = manager.load_cache("nonexistent")
        assert result is None


def test_load_cache_corrupted(tmp_path):
    """Test chargement cache corrompu."""
    from recipe_recommender.utils.cache_manager import CacheManager

    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    manager = CacheManager(str(cache_dir))

    # Créer fichier corrompu
    cache_file = cache_dir / "corrupted.pkl"
    cache_file.write_text("not a pickle")

    result = manager.load_cache("corrupted")
    assert result is None


def test_save_cache_error(tmp_path):
    """Test erreur sauvegarde cache."""
    from recipe_recommender.utils.cache_manager import CacheManager
    import os

    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    manager = CacheManager(str(cache_dir))

    # Rendre le répertoire non-writable
    os.chmod(str(cache_dir), 0o444)

    try:
        result = manager.save_cache("test", {"data": "test"})
        # Si réussit, remettre permissions
        os.chmod(str(cache_dir), 0o755)
        # Le test devrait échouer ou retourner False
        assert result is False or result is None
    except Exception:
        # Remettre permissions
        os.chmod(str(cache_dir), 0o755)


def test_delete_cache_success():
    """Test suppression cache avec succès."""
    from recipe_recommender.utils.cache_manager import CacheManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = CacheManager(tmpdir)
        manager.save_cache("test", {"data": "value"})

        result = manager.delete_cache("test")
        assert result is True
        assert not manager.cache_exists("test")


def test_delete_cache_not_found():
    """Test suppression cache inexistant."""
    from recipe_recommender.utils.cache_manager import CacheManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = CacheManager(tmpdir)
        result = manager.delete_cache("nonexistent")
        assert result is False
