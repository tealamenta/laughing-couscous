"""Tests pour le module favorites."""

import json
from pathlib import Path

import pytest

from recipe_recommender.utils.favorites import FavoritesManager


@pytest.fixture
def temp_favorites_file(tmp_path):
    """Crée un fichier temporaire pour les favoris."""
    return tmp_path / "test_favorites.json"


@pytest.fixture
def favorites_manager(temp_favorites_file):
    """Crée un gestionnaire de favoris avec un fichier temporaire."""
    return FavoritesManager(str(temp_favorites_file))


def test_init(favorites_manager, temp_favorites_file):
    """Test l'initialisation du gestionnaire."""
    assert favorites_manager.favorites_file == Path(temp_favorites_file)
    assert favorites_manager.favorites_file.parent.exists()


def test_load_favorites_empty(favorites_manager):
    """Test le chargement quand le fichier n'existe pas."""
    result = favorites_manager.load_favorites()
    assert result == []


def test_save_favorites(favorites_manager, temp_favorites_file):
    """Test la sauvegarde des favoris."""
    test_favorites = [123, 456, 789]
    favorites_manager.save_favorites(test_favorites)

    # Vérifier que le fichier existe et contient les bonnes données
    assert temp_favorites_file.exists()
    with open(temp_favorites_file, "r") as f:
        data = json.load(f)
    assert data["favorites"] == test_favorites


def test_load_favorites_existing(favorites_manager, temp_favorites_file):
    """Test le chargement de favoris existants."""
    # Créer un fichier avec des favoris
    test_data = {"favorites": [111, 222, 333]}
    with open(temp_favorites_file, "w") as f:
        json.dump(test_data, f)

    result = favorites_manager.load_favorites()
    assert result == [111, 222, 333]


def test_add_favorite_new(favorites_manager):
    """Test l'ajout d'un nouveau favori."""
    favorites_manager.add_favorite(123)

    favorites = favorites_manager.load_favorites()
    assert 123 in favorites
    assert len(favorites) == 1


def test_add_favorite_duplicate(favorites_manager):
    """Test l'ajout d'un favori déjà présent."""
    favorites_manager.add_favorite(123)
    favorites_manager.add_favorite(123)

    favorites = favorites_manager.load_favorites()
    assert favorites.count(123) == 1


def test_remove_favorite_existing(favorites_manager):
    """Test la suppression d'un favori existant."""
    favorites_manager.save_favorites([123, 456, 789])
    favorites_manager.remove_favorite(456)

    favorites = favorites_manager.load_favorites()
    assert 456 not in favorites
    assert len(favorites) == 2


def test_remove_favorite_nonexistent(favorites_manager):
    """Test la suppression d'un favori inexistant."""
    favorites_manager.save_favorites([123, 456])
    favorites_manager.remove_favorite(999)

    favorites = favorites_manager.load_favorites()
    assert len(favorites) == 2


def test_save_load_roundtrip(favorites_manager):
    """Test sauvegarde puis chargement."""
    original = [100, 200, 300]
    favorites_manager.save_favorites(original)
    loaded = favorites_manager.load_favorites()
    assert loaded == original


def test_load_corrupted_file(favorites_manager, temp_favorites_file):
    """Test le chargement d'un fichier corrompu."""
    # Créer un fichier JSON invalide
    with open(temp_favorites_file, "w") as f:
        f.write("{ invalid json }")

    result = favorites_manager.load_favorites()
    assert result == []
