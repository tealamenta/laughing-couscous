"""Module de recommandation basé sur BERT."""

from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from recipe_recommender.models.recipe import Recipe
from recipe_recommender.utils.logger import get_logger

logger = get_logger(__name__)


class BERTRecommender:
    """Systeme de recommandation base sur BERT embeddings."""

    def __init__(self, recipes: List[Recipe], model_name: str = "all-MiniLM-L6-v2"):
        """Initialise le recommender BERT.

        Args:
            recipes: Liste des recettes
            model_name: Modele Sentence-BERT
        """
        self.recipes = recipes
        self.recipe_dict = {r.recipe_id: r for r in recipes}
        self.model_name = model_name
        self.model = None
        self.embeddings = None

        logger.info("BERTRecommender initialise avec %d recettes", len(recipes))

    def fit(self) -> None:
        """Cree les embeddings BERT."""
        logger.info("Chargement modele BERT: %s", self.model_name)

        self.model = SentenceTransformer(self.model_name)

        logger.info("Creation textes recettes...")
        recipe_texts = self._create_recipe_texts()

        logger.info("Generation embeddings BERT...")
        self.embeddings = self.model.encode(
            recipe_texts, show_progress_bar=True, batch_size=32
        )

        logger.info("Embeddings crees: %s", self.embeddings.shape)

    def _create_recipe_texts(self) -> List[str]:
        """Cree texte representatif de chaque recette."""
        texts = []

        for recipe in self.recipes:
            text_parts = [
                recipe.name,
                recipe.description,
                " ".join(recipe.ingredients),
                " ".join(recipe.tags),
            ]
            texts.append(" ".join(text_parts))

        return texts

    def recommend(
        self, liked_recipe_ids: List[int], n: int = 10, exclude_liked: bool = True
    ) -> List[Recipe]:
        """Genere recommandations."""
        if self.embeddings is None:
            raise ValueError("Modele non entraine. Appelez fit().")

        logger.info("Generation %d recommandations", n)

        liked_indices = [
            i for i, r in enumerate(self.recipes) if r.recipe_id in liked_recipe_ids
        ]

        if not liked_indices:
            return []

        liked_embeddings = self.embeddings[liked_indices]
        user_profile = np.mean(liked_embeddings, axis=0).reshape(1, -1)

        similarities = cosine_similarity(user_profile, self.embeddings)[0]
        similar_indices = similarities.argsort()[::-1]

        if exclude_liked:
            similar_indices = [
                idx
                for idx in similar_indices
                if self.recipes[idx].recipe_id not in liked_recipe_ids
            ]

        top_indices = similar_indices[:n]
        return [self.recipes[idx] for idx in top_indices]

    def get_similar_recipes(self, recipe_id: int, n: int = 5) -> List[Recipe]:
        """Trouve recettes similaires."""
        recipe_index = next(
            (i for i, r in enumerate(self.recipes) if r.recipe_id == recipe_id), None
        )

        if recipe_index is None:
            return []

        recipe_embedding = self.embeddings[recipe_index].reshape(1, -1)
        similarities = cosine_similarity(recipe_embedding, self.embeddings)[0]
        similar_indices = similarities.argsort()[::-1][1 : n + 1]

        return [self.recipes[idx] for idx in similar_indices]

    def get_recipe_by_id(self, recipe_id: int) -> Recipe:
        """Recupere recette par ID."""
        return self.recipe_dict.get(recipe_id)

    def search_semantic(self, query: str, n: int = 10) -> List[Recipe]:
        """Recherche semantique."""
        if self.embeddings is None:
            raise ValueError("Modele non entraine.")

        logger.info("Recherche semantique: %s", query)

        query_embedding = self.model.encode([query])
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = similarities.argsort()[::-1][:n]

        return [self.recipes[idx] for idx in top_indices]

    def load_from_cache(self, cache_data: dict) -> bool:
        """Charge embeddings depuis cache.

        Args:
            cache_data: Donnees du cache

        Returns:
            True si succes
        """
        try:
            self.embeddings = cache_data["embeddings"]

            # Charger modele seulement si necessaire (pour search_semantic)
            if self.model is None:
                logger.info(
                    "Chargement modele BERT pour inference: %s", self.model_name
                )
                self.model = SentenceTransformer(self.model_name)

            logger.info("Embeddings charges depuis cache")
            return True

        except Exception as e:
            logger.error("Erreur chargement cache: %s", str(e))
            return False
