"""
Module de gestion des recettes favorites.

Permet de sauvegarder et charger les recettes favorites
de l'utilisateur dans un fichier JSON.
"""

import json
from pathlib import Path
from typing import List

from recipe_recommender.utils.logger import get_logger

logger = get_logger(__name__)


class FavoritesManager:
    """Gestionnaire des recettes favorites."""

    def __init__(self, favorites_file: str = "data/favorites.json"):
        """
        Initialise le gestionnaire de favoris.

        Args:
            favorites_file: Chemin vers le fichier JSON des favoris.
        """
        self.favorites_file = Path(favorites_file)
        self.favorites_file.parent.mkdir(parents=True, exist_ok=True)

    def load_favorites(self) -> List[int]:
        """
        Charge la liste des IDs de recettes favorites.

        Returns:
            List[int]: Liste des IDs des recettes favorites.
        """
        if not self.favorites_file.exists():
            logger.info("Aucun fichier de favoris trouve, creation liste vide")
            return []

        try:
            with open(self.favorites_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                favorites = data.get("favorites", [])
                logger.info(
                    f"{len(favorites)} favoris charges depuis " f"{self.favorites_file}"
                )
                return favorites
        except json.JSONDecodeError:
            logger.error("Erreur lecture fichier favoris, retour liste vide")
            return []
        except PermissionError:
            logger.error("Permission refusee pour lire favoris")
            return []
        except Exception as e:
            logger.error(f"Erreur chargement favoris: {e}")
            return []

    def save_favorites(self, favorites: List[int]) -> None:
        """
        Sauvegarde la liste des favoris.

        Args:
            favorites: Liste des IDs de recettes favorites.
        """
        try:
            with open(self.favorites_file, "w", encoding="utf-8") as f:
                json.dump({"favorites": favorites}, f, indent=2)
            logger.info(
                f"{len(favorites)} favoris sauvegardes dans " f"{self.favorites_file}"
            )
        except IOError as e:
            logger.error(f"Erreur sauvegarde favoris: {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue sauvegarde favoris: {e}")

    def add_favorite(self, recipe_id: int) -> None:
        """
        Ajoute une recette aux favoris.

        Args:
            recipe_id: ID de la recette à ajouter.
        """
        favorites = self.load_favorites()
        if recipe_id not in favorites:
            favorites.append(recipe_id)
            self.save_favorites(favorites)
            logger.info(f"Recette {recipe_id} ajoutee aux favoris")
        else:
            logger.debug(f"Recette {recipe_id} deja dans favoris")

    def remove_favorite(self, recipe_id: int) -> None:
        """
        Retire une recette des favoris.

        Args:
            recipe_id: ID de la recette à retirer.
        """
        favorites = self.load_favorites()
        if recipe_id in favorites:
            favorites.remove(recipe_id)
            self.save_favorites(favorites)
            logger.info(f"Recette {recipe_id} retiree des favoris")
        else:
            logger.debug(f"Recette {recipe_id} pas dans favoris")
