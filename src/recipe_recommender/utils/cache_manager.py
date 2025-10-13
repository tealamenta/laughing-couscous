"""Gestionnaire de cache pour embeddings BERT."""

import pickle
from pathlib import Path
from typing import Optional, Dict, Any
from recipe_recommender.utils.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Gestion du cache des embeddings BERT."""

    def __init__(self, cache_dir: str = "data/cache"):
        """Initialise le gestionnaire de cache.

        Args:
            cache_dir: Repertoire du cache
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_path(self, cache_name: str) -> Path:
        """Retourne chemin du fichier cache.

        Args:
            cache_name: Nom du cache

        Returns:
            Chemin complet du fichier
        """
        return self.cache_dir / f"{cache_name}.pkl"

    def cache_exists(self, cache_name: str) -> bool:
        """Verifie si cache existe.

        Args:
            cache_name: Nom du cache

        Returns:
            True si cache existe
        """
        cache_path = self.get_cache_path(cache_name)
        exists = cache_path.exists()

        if exists:
            file_size = cache_path.stat().st_size / (1024 * 1024)
            logger.info("Cache trouve: %s (%.1f MB)", cache_path, file_size)
        else:
            logger.warning("Cache introuvable: %s", cache_path)

        return exists

    def load_cache(self, cache_name: str) -> Optional[Dict[str, Any]]:
        """Charge cache depuis disque.

        Args:
            cache_name: Nom du cache

        Returns:
            Donnees du cache ou None si erreur
        """
        cache_path = self.get_cache_path(cache_name)

        if not cache_path.exists():
            logger.error("Cache introuvable: %s", cache_path)
            return None

        try:
            logger.info("Chargement cache: %s", cache_path)
            with open(cache_path, "rb") as f:
                data = pickle.load(f)

            logger.info("Cache charge avec succes")
            logger.info("  - Recettes: %d", data.get("n_recipes", 0))
            logger.info("  - Shape: %s", data.get("embeddings").shape)

            return data

        except Exception as e:
            logger.error("Erreur chargement cache: %s", str(e))
            return None

    def save_cache(self, cache_name: str, data: Dict[str, Any]) -> bool:
        """Sauvegarde cache sur disque.

        Args:
            cache_name: Nom du cache
            data: Donnees a sauvegarder

        Returns:
            True si succes
        """
        cache_path = self.get_cache_path(cache_name)

        try:
            logger.info("Sauvegarde cache: %s", cache_path)
            with open(cache_path, "wb") as f:
                pickle.dump(data, f)

            file_size = cache_path.stat().st_size / (1024 * 1024)
            logger.info("Cache sauvegarde: %.1f MB", file_size)

            return True

        except Exception as e:
            logger.error("Erreur sauvegarde cache: %s", str(e))
            return False

    def delete_cache(self, cache_name: str) -> bool:
        """Supprime cache.

        Args:
            cache_name: Nom du cache

        Returns:
            True si succes
        """
        cache_path = self.get_cache_path(cache_name)

        if not cache_path.exists():
            logger.warning("Cache inexistant: %s", cache_path)
            return False

        try:
            cache_path.unlink()
            logger.info("Cache supprime: %s", cache_path)
            return True

        except Exception as e:
            logger.error("Erreur suppression cache: %s", str(e))
            return False
