"""Tests unitaires pour FavoritesManager."""

import json
import os
from pathlib import Path

import pytest

from recipe_recommender.utils.favorites import FavoritesManager


@pytest.fixture
def temp_favorites_file(tmp_path):
    """Fixture pour créer un fichier temporaire."""
    return str(tmp_path / "test_favorites.json")


@pytest.fixture
def favorites_manager(temp_favorites_file):
    """Fixture pour créer un FavoritesManager avec fichier temporaire."""
    return FavoritesManager(favorites_file=temp_favorites_file)


def test_init(favorites_manager, temp_favorites_file):
    """Test l'initialisation du FavoritesManager."""
    assert favorites_manager.favorites_file == Path(temp_favorites_file)


def test_load_favorites_empty(favorites_manager):
    """Test le chargement quand le fichier n'existe pas."""
    favorites = favorites_manager.load_favorites()
    assert favorites == []


def test_save_favorites(favorites_manager, temp_favorites_file):
    """Test la sauvegarde des favoris."""
    test_favorites = [123, 456, 789]
    result = favorites_manager.save_favorites(test_favorites)
    assert result is True

    # Vérifier que le fichier existe et contient les bonnes données
    with open(temp_favorites_file, "r") as f:
        data = json.load(f)
        assert data["favorites"] == test_favorites


def test_load_favorites_existing(favorites_manager, temp_favorites_file):
    """Test le chargement depuis un fichier existant."""
    # Créer un fichier avec des favoris
    test_favorites = [111, 222, 333]
    with open(temp_favorites_file, "w") as f:
        json.dump({"favorites": test_favorites}, f)

    # Charger et vérifier
    loaded = favorites_manager.load_favorites()
    assert loaded == test_favorites


def test_add_favorite_new(favorites_manager):
    """Test l'ajout d'un nouveau favori."""
    current = []
    updated = favorites_manager.add_favorite(123, current)
    assert 123 in updated
    assert len(updated) == 1


def test_add_favorite_duplicate(favorites_manager):
    """Test l'ajout d'un favori déjà présent."""
    current = [123, 456]
    updated = favorites_manager.add_favorite(123, current)
    assert updated.count(123) == 1  # Pas de doublon
    assert len(updated) == 2


def test_remove_favorite_existing(favorites_manager):
    """Test la suppression d'un favori existant."""
    current = [123, 456, 789]
    updated = favorites_manager.remove_favorite(456, current)
    assert 456 not in updated
    assert len(updated) == 2


def test_remove_favorite_nonexistent(favorites_manager):
    """Test la suppression d'un favori inexistant."""
    current = [123, 456]
    updated = favorites_manager.remove_favorite(999, current)
    assert len(updated) == 2  # Aucun changement


def test_save_load_roundtrip(favorites_manager):
    """Test complet: sauvegarde puis rechargement."""
    original = [100, 200, 300, 400]
    favorites_manager.save_favorites(original)
    loaded = favorites_manager.load_favorites()
    assert loaded == original


def test_load_corrupted_file(favorites_manager, temp_favorites_file):
    """Test le chargement d'un fichier corrompu."""
    # Créer un fichier JSON invalide
    with open(temp_favorites_file, "w") as f:
        f.write("NOT VALID JSON")

    loaded = favorites_manager.load_favorites()
    assert loaded == []  # Devrait retourner une liste vide en cas d'erreur
