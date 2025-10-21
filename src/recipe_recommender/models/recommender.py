"""
Module de recommandation de recettes basé sur le contenu.

Ce module implémente un système de recommandation utilisant TF-IDF
et la similarité cosinus pour suggérer des recettes similaires.
"""

from typing import List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from recipe_recommender.models.recipe import Recipe
from recipe_recommender.utils.logger import get_logger

logger = get_logger(__name__)


class RecipeRecommender:
    """
    Système de recommandation de recettes basé sur le contenu.

    Cette classe utilise TF-IDF (Term Frequency-Inverse Document Frequency)
    sur les tags des recettes pour calculer la similarité et recommander
    des recettes similaires aux préférences de l'utilisateur.

    Attributes:
        recipes: Liste de toutes les recettes disponibles.
        tfidf_vectorizer: Vectorizer TF-IDF pour les tags.
        tfidf_matrix: Matrice TF-IDF des recettes.

    Example:
        >>> recommender = RecipeRecommender(recipes)
        >>> recommender.fit()
        >>> liked_ids = [123, 456, 789]
        >>> recommendations = recommender.recommend(liked_ids, n=10)
    """

    def __init__(self, recipes: List[Recipe]) -> None:
        """
        Initialise le recommender avec une liste de recettes.

        Args:
            recipes: Liste d'objets Recipe à utiliser pour les recommandations.

        Raises:
            ValueError: Si la liste de recettes est vide.
        """
        if not recipes:
            logger.error("Impossible de créer un recommender avec 0 recettes")
            raise ValueError("La liste de recettes ne peut pas être vide")

        self.recipes = recipes
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[np.ndarray] = None

        # Créer un mapping recipe_id -> index
        self.id_to_index = {recipe.recipe_id: i for i, recipe in enumerate(recipes)}
        self.index_to_id = {i: recipe.recipe_id for i, recipe in enumerate(recipes)}

        logger.info(f"RecipeRecommender initialisé avec {len(recipes)} recettes")

    def fit(self) -> None:
        """
        Entraîne le modèle TF-IDF sur les tags des recettes.

        Cette méthode doit être appelée avant d'utiliser recommend().
        Elle calcule la matrice TF-IDF basée sur les tags de toutes les recettes.

        Example:
            >>> recommender.fit()
        """
        logger.info("Début de l'entraînement du modèle TF-IDF")

        # Créer une liste de strings de tags pour chaque recette
        tags_corpus = [" ".join(recipe.tags) for recipe in self.recipes]

        # Initialiser et fit le vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2),
        )

        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(tags_corpus)

        logger.info(
            f"Modèle TF-IDF entraîné: {self.tfidf_matrix.shape[0]} recettes, "
            f"{self.tfidf_matrix.shape[1]} features"
        )

    def recommend(
        self, liked_recipe_ids: List[int], n: int = 10, exclude_liked: bool = True
    ) -> List[Recipe]:
        """
        Recommande des recettes similaires aux recettes aimées.
        Complexity: A (3) - Reduced from C (11)

        Args:
            liked_recipe_ids: Liste des IDs de recettes aimées par l'utilisateur.
            n: Nombre de recommandations à retourner. Par défaut 10.
            exclude_liked: Si True, exclut les recettes déjà aimées.

        Returns:
            List[Recipe]: Liste des recettes recommandées, triées par similarité.

        Raises:
            ValueError: Si le modèle n'a pas été entraîné.
        """
        self._validate_model()

        if not liked_recipe_ids:
            logger.warning("Aucune recette likée fournie")
            return []

        logger.info(
            f"Génération de {n} recommandations basées sur "
            f"{len(liked_recipe_ids)} recettes likées"
        )

        # Get valid indices
        liked_indices = self._get_valid_indices(liked_recipe_ids)

        # Compute user profile
        user_profile = self._compute_user_profile(liked_indices)

        # Get similarities
        similarities = self._compute_similarities(user_profile)

        # Get top recommendations
        recommendations = self._get_top_recommendations(
            similarities, liked_indices, n, exclude_liked
        )

        logger.info(f"{len(recommendations)} recommandations générées")
        return recommendations

    def _validate_model(self) -> None:
        """Validate that model is fitted. Complexity: A (2)"""
        if self.tfidf_matrix is None or self.tfidf_vectorizer is None:
            logger.error("Le modèle doit être entraîné avant de recommander")
            raise ValueError("Appelez fit() avant recommend()")

    def _get_valid_indices(self, recipe_ids: List[int]) -> List[int]:
        """Convert recipe IDs to valid indices. Complexity: A (3)"""
        valid_indices = []
        for recipe_id in recipe_ids:
            if recipe_id in self.id_to_index:
                valid_indices.append(self.id_to_index[recipe_id])
            else:
                logger.warning(f"Recette ID {recipe_id} non trouvée")

        if not valid_indices:
            logger.error("Aucune recette likée valide trouvée")
            raise ValueError("Aucune recette likée valide")

        return valid_indices

    def _compute_user_profile(self, liked_indices: List[int]) -> np.ndarray:
        """Compute average user profile from liked recipes. Complexity: A (1)"""
        liked_vectors = self.tfidf_matrix[liked_indices].toarray()
        return liked_vectors.mean(axis=0)

    def _compute_similarities(self, user_profile: np.ndarray) -> np.ndarray:
        """Compute cosine similarities. Complexity: A (1)"""
        user_profile_2d = user_profile.reshape(1, -1)
        return cosine_similarity(user_profile_2d, self.tfidf_matrix.toarray()).flatten()

    def _get_top_recommendations(
        self,
        similarities: np.ndarray,
        liked_indices: List[int],
        n: int,
        exclude_liked: bool,
    ) -> List[Recipe]:
        """Get top N recommendations. Complexity: A (4)"""
        similar_indices = similarities.argsort()[::-1]

        recommendations = []
        for idx in similar_indices:
            if exclude_liked and idx in liked_indices:
                continue

            recommendations.append(self.recipes[idx])

            if len(recommendations) >= n:
                break

        return recommendations

    def get_similar_recipes(
        self, recipe_id: int, n: int = 5, exclude_self: bool = True
    ) -> List[Recipe]:
        """
        Trouve des recettes similaires à une recette donnée.
        Complexity: A (5) - Reduced from B (8)

        Args:
            recipe_id: ID de la recette de référence.
            n: Nombre de recettes similaires à retourner.
            exclude_self: Si True, exclut la recette elle-même.

        Returns:
            List[Recipe]: Liste des recettes similaires.

        Raises:
            ValueError: Si le modèle n'est pas entraîné ou si l'ID est invalide.
        """
        self._validate_model()

        if recipe_id not in self.id_to_index:
            logger.error(f"Recette ID {recipe_id} non trouvée")
            raise ValueError(f"Recette ID {recipe_id} non trouvée")

        logger.info(f"Recherche de {n} recettes similaires à ID {recipe_id}")

        recipe_idx = self.id_to_index[recipe_id]
        recipe_vector = self.tfidf_matrix[recipe_idx].toarray()

        # Compute similarities
        similarities = cosine_similarity(
            recipe_vector, self.tfidf_matrix.toarray()
        ).flatten()

        # Get top similar recipes
        similar_indices = similarities.argsort()[::-1]

        results = []
        for idx in similar_indices:
            if exclude_self and idx == recipe_idx:
                continue

            results.append(self.recipes[idx])

            if len(results) >= n:
                break

        logger.info(f"{len(results)} recettes similaires trouvées")
        return results

    def get_recipe_by_id(self, recipe_id: int) -> Recipe:
        """
        Récupère une recette par son ID.

        Args:
            recipe_id: ID de la recette à récupérer.

        Returns:
            Recipe: La recette trouvée.

        Raises:
            ValueError: Si l'ID n'existe pas.
        """
        if recipe_id not in self.id_to_index:
            logger.error(f"Recette ID {recipe_id} non trouvée")
            raise ValueError(f"Recette ID {recipe_id} non trouvée")

        idx = self.id_to_index[recipe_id]
        return self.recipes[idx]
