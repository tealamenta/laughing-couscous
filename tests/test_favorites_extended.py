"""Tests étendus pour FavoritesManager."""

import json
import os
import tempfile

from recipe_recommender.utils.favorites import FavoritesManager


def test_save_favorites_success():
    """Test sauvegarde des favoris."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_file = f.name

    try:
        manager = FavoritesManager(favorites_file=temp_file)
        favorites = [1, 2, 3]

        manager.save_favorites(favorites)

        with open(temp_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "favorites" in data
            assert data["favorites"] == favorites
    finally:
        os.unlink(temp_file)


def test_load_favorites_file_not_found():
    """Test chargement quand le fichier n'existe pas."""
    manager = FavoritesManager(favorites_file="/nonexistent/path/favorites.json")

    result = manager.load_favorites()

    assert result == []


def test_load_favorites_invalid_json():
    """Test chargement avec JSON invalide."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write("invalid json{{{")
        temp_file = f.name

    try:
        manager = FavoritesManager(favorites_file=temp_file)
        result = manager.load_favorites()

        assert result == []
    finally:
        os.unlink(temp_file)


def test_add_favorite_already_exists():
    """Test ajout d'un favori déjà présent."""
    manager = FavoritesManager()
    favorites = [1, 2, 3]

    result = manager.add_favorite(2, favorites)

    assert result == [1, 2, 3]
    assert len(result) == 3


def test_add_favorite_new():
    """Test ajout d'un nouveau favori."""
    manager = FavoritesManager()
    favorites = [1, 2, 3]

    result = manager.add_favorite(4, favorites)

    assert result == [1, 2, 3, 4]
    assert len(result) == 4


def test_remove_favorite_exists():
    """Test retrait d'un favori existant."""
    manager = FavoritesManager()
    favorites = [1, 2, 3, 4]

    result = manager.remove_favorite(3, favorites)

    assert result == [1, 2, 4]
    assert 3 not in result


def test_remove_favorite_not_in_list():
    """Test retrait d'un favori qui n'existe pas."""
    manager = FavoritesManager()
    favorites = [1, 2, 3]

    result = manager.remove_favorite(999, favorites)

    assert result == [1, 2, 3]


def test_save_favorites_with_io_error(monkeypatch):
    """Test gestion d'erreur lors de la sauvegarde."""

    def mock_open(*args, **kwargs):
        raise IOError("Disk full")

    monkeypatch.setattr("builtins.open", mock_open)

    manager = FavoritesManager()

    manager.save_favorites([1, 2, 3])


def test_load_favorites_success():
    """Test chargement réussi des favoris."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump({"favorites": [10, 20, 30]}, f)
        temp_file = f.name

    try:
        manager = FavoritesManager(favorites_file=temp_file)

        result = manager.load_favorites()

        assert result == [10, 20, 30]
    finally:
        os.unlink(temp_file)


def test_load_favorites_missing_key():
    """Test chargement avec clé 'favorites' manquante."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump({"other_key": [1, 2, 3]}, f)
        temp_file = f.name

    try:
        manager = FavoritesManager(favorites_file=temp_file)

        result = manager.load_favorites()

        assert result == []
    finally:
        os.unlink(temp_file)


def test_add_favorite_empty_list():
    """Test ajout à une liste vide."""
    manager = FavoritesManager()
    favorites = []

    result = manager.add_favorite(1, favorites)

    assert result == [1]


def test_remove_favorite_empty_list():
    """Test retrait d'une liste vide."""
    manager = FavoritesManager()
    favorites = []

    result = manager.remove_favorite(1, favorites)

    assert result == []


def test_multiple_operations():
    """Test série d'opérations."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_file = f.name

    try:
        manager = FavoritesManager(favorites_file=temp_file)

        favs = []
        favs = manager.add_favorite(1, favs)
        favs = manager.add_favorite(2, favs)
        favs = manager.add_favorite(3, favs)

        assert favs == [1, 2, 3]

        manager.save_favorites(favs)

        loaded = manager.load_favorites()
        assert loaded == [1, 2, 3]

        loaded = manager.remove_favorite(2, loaded)
        assert loaded == [1, 3]

    finally:
        os.unlink(temp_file)


def test_load_favorites_with_permission_error(monkeypatch):
    """Test chargement avec erreur de permission."""

    def mock_open(*args, **kwargs):
        raise PermissionError("Access denied")

    monkeypatch.setattr("builtins.open", mock_open)

    manager = FavoritesManager()

    result = manager.load_favorites()

    assert result == []
