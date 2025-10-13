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
            max_features=5000,  # Limiter le nombre de features
            min_df=2,  # Ignorer les tags qui apparaissent dans moins de 2 recettes
            max_df=0.8,  # Ignorer les tags trop fréquents
            ngram_range=(1, 2),  # Utiliser unigrammes et bigrammes
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

        Cette méthode calcule un profil moyen des recettes aimées et trouve
        les recettes les plus similaires dans le corpus.

        Args:
            liked_recipe_ids: Liste des IDs de recettes aimées par l'utilisateur.
            n: Nombre de recommandations à retourner. Par défaut 10.
            exclude_liked: Si True, exclut les recettes déjà aimées. Par défaut True.

        Returns:
            List[Recipe]: Liste des recettes recommandées, triées par similarité.

        Raises:
            ValueError: Si le modèle n'a pas été entraîné ou si aucune recette likée n'existe.

        Example:
            >>> recommendations = recommender.recommend([123, 456], n=5)
            >>> for rec in recommendations:
            ...     print(rec.name)
        """
        if self.tfidf_matrix is None or self.tfidf_vectorizer is None:
            logger.error("Le modèle doit être entraîné avant de recommander")
            raise ValueError("Appelez fit() avant recommend()")

        if not liked_recipe_ids:
            logger.warning("Aucune recette likée fournie")
            return []

        logger.info(
            f"Génération de {n} recommandations basées sur {len(liked_recipe_ids)} recettes likées"
        )

        # Convertir les IDs en indices
        liked_indices = []
        for recipe_id in liked_recipe_ids:
            if recipe_id in self.id_to_index:
                liked_indices.append(self.id_to_index[recipe_id])
            else:
                logger.warning(f"Recette ID {recipe_id} non trouvée dans le corpus")

        if not liked_indices:
            logger.error("Aucune recette likée valide trouvée")
            raise ValueError("Aucune recette likée valide")

        # Calculer le profil moyen des recettes likées
        liked_vectors = self.tfidf_matrix[liked_indices].toarray()
        user_profile = liked_vectors.mean(axis=0)

        # Calculer la similarité avec toutes les recettes
        user_profile_2d = user_profile.reshape(1, -1)
        similarities = cosine_similarity(
            user_profile_2d, self.tfidf_matrix.toarray()
        ).flatten()

        # Trier par similarité décroissante
        similar_indices = similarities.argsort()[::-1]

        # Filtrer et limiter le nombre de recommandations
        recommendations = []
        for idx in similar_indices:
            # Exclure les recettes déjà likées si demandé
            if exclude_liked and idx in liked_indices:
                continue

            recommendations.append(self.recipes[idx])

            if len(recommendations) >= n:
                break

        logger.info(f"{len(recommendations)} recommandations générées")
        return recommendations

    def get_similar_recipes(
        self, recipe_id: int, n: int = 5, exclude_self: bool = True
    ) -> List[Recipe]:
        """
        Trouve des recettes similaires à une recette donnée.

        Args:
            recipe_id: ID de la recette de référence.
            n: Nombre de recettes similaires à retourner. Par défaut 5.
            exclude_self: Si True, exclut la recette elle-même. Par défaut True.

        Returns:
            List[Recipe]: Liste des recettes similaires.

        Raises:
            ValueError: Si le modèle n'a pas été entraîné ou si la recette n'existe pas.

        Example:
            >>> similar = recommender.get_similar_recipes(123, n=3)
        """
        if self.tfidf_matrix is None or self.tfidf_vectorizer is None:
            logger.error("Le modèle doit être entraîné avant de trouver des similaires")
            raise ValueError("Appelez fit() avant get_similar_recipes()")

        if recipe_id not in self.id_to_index:
            logger.error(f"Recette ID {recipe_id} non trouvée")
            raise ValueError(f"Recette ID {recipe_id} non trouvée")

        logger.debug(f"Recherche de {n} recettes similaires à {recipe_id}")

        # Obtenir l'index de la recette
        idx = self.id_to_index[recipe_id]

        # Calculer la similarité avec toutes les recettes
        recipe_vector = self.tfidf_matrix[idx]
        similarities = cosine_similarity(
            recipe_vector, self.tfidf_matrix.toarray()
        ).flatten()

        # Trier par similarité décroissante
        similar_indices = similarities.argsort()[::-1]

        # Filtrer et limiter
        similar_recipes = []
        for sim_idx in similar_indices:
            # Exclure la recette elle-même si demandé
            if exclude_self and sim_idx == idx:
                continue

            similar_recipes.append(self.recipes[sim_idx])

            if len(similar_recipes) >= n:
                break

        return similar_recipes

    def get_recipe_by_id(self, recipe_id: int) -> Recipe:
        """
        Récupère une recette par son ID.

        Args:
            recipe_id: ID de la recette à récupérer.

        Returns:
            Recipe: L'objet Recipe.

        Raises:
            ValueError: Si la recette n'est pas trouvée.

        Example:
            >>> recipe = recommender.get_recipe_by_id(123)
            >>> print(recipe.name)
        """
        if recipe_id in self.id_to_index:
            idx = self.id_to_index[recipe_id]
            return self.recipes[idx]
        raise ValueError(f"Recette avec ID {recipe_id} non trouvée")
