"""
Module de gestion des recettes favorites.

Ce module gère la persistance des recettes favorites de l'utilisateur
dans un fichier JSON local.
"""

import json
from pathlib import Path
from typing import List

from recipe_recommender.utils.logger import get_logger

logger = get_logger(__name__)


class FavoritesManager:
    """
    Gère la sauvegarde et le chargement des recettes favorites.

    Attributes:
        favorites_file: Chemin vers le fichier JSON de sauvegarde.
    """

    def __init__(self, favorites_file: str = "./user_favorites.json") -> None:
        """
        Initialise le gestionnaire de favoris.

        Args:
            favorites_file: Chemin vers le fichier de sauvegarde. Par défaut "./user_favorites.json".
        """
        self.favorites_file = Path(favorites_file)
        logger.info(f"FavoritesManager initialisé avec fichier: {self.favorites_file}")

    def load_favorites(self) -> List[int]:
        """
        Charge les IDs des recettes favorites depuis le fichier JSON.

        Returns:
            List[int]: Liste des IDs de recettes favorites.

        Example:
            >>> manager = FavoritesManager()
            >>> favorites = manager.load_favorites()
            >>> print(f"Loaded {len(favorites)} favorites")
        """
        if not self.favorites_file.exists():
            logger.info("Aucun fichier de favoris trouvé, création d'une liste vide")
            return []

        try:
            with open(self.favorites_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                favorites = data.get("favorites", [])
                logger.info(f"{len(favorites)} favoris chargés depuis {self.favorites_file}")
                return favorites
        except Exception as e:
            logger.error(f"Erreur lors du chargement des favoris: {str(e)}")
            return []

    def save_favorites(self, favorites: List[int]) -> bool:
        """
        Sauvegarde les IDs des recettes favorites dans le fichier JSON.

        Args:
            favorites: Liste des IDs de recettes à sauvegarder.

        Returns:
            bool: True si la sauvegarde a réussi, False sinon.

        Example:
            >>> manager = FavoritesManager()
            >>> success = manager.save_favorites([123, 456, 789])
        """
        try:
            data = {"favorites": favorites}
            with open(self.favorites_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info(f"{len(favorites)} favoris sauvegardés dans {self.favorites_file}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des favoris: {str(e)}")
            return False

    def add_favorite(self, recipe_id: int, current_favorites: List[int]) -> List[int]:
        """
        Ajoute une recette aux favoris et sauvegarde.

        Args:
            recipe_id: ID de la recette à ajouter.
            current_favorites: Liste actuelle des favoris.

        Returns:
            List[int]: Liste mise à jour des favoris.

        Example:
            >>> updated = manager.add_favorite(999, [123, 456])
        """
        if recipe_id not in current_favorites:
            current_favorites.append(recipe_id)
            self.save_favorites(current_favorites)
            logger.info(f"Recette {recipe_id} ajoutée aux favoris")
        else:
            logger.warning(f"Recette {recipe_id} déjà dans les favoris")

        return current_favorites

    def remove_favorite(self, recipe_id: int, current_favorites: List[int]) -> List[int]:
        """
        Retire une recette des favoris et sauvegarde.

        Args:
            recipe_id: ID de la recette à retirer.
            current_favorites: Liste actuelle des favoris.

        Returns:
            List[int]: Liste mise à jour des favoris.

        Example:
            >>> updated = manager.remove_favorite(123, [123, 456, 789])
        """
        if recipe_id in current_favorites:
            current_favorites.remove(recipe_id)
            self.save_favorites(current_favorites)
            logger.info(f"Recette {recipe_id} retirée des favoris")
        else:
            logger.warning(f"Recette {recipe_id} n'était pas dans les favoris")

        return current_favorites
