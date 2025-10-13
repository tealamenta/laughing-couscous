"""Recommender hybride combinant TF-IDF et BERT."""

from typing import List, Dict
from recipe_recommender.models.recipe import Recipe
from recipe_recommender.models.recommender import RecipeRecommender
from recipe_recommender.models.bert_recommender import BERTRecommender
from recipe_recommender.utils.logger import get_logger

logger = get_logger(__name__)


class HybridRecommender:
    """Systeme de recommandation hybride (TF-IDF + BERT)."""

    def __init__(
        self,
        recipes: List[Recipe],
        tfidf_weight: float = 0.5,
        bert_weight: float = 0.5,
        bert_model: str = "all-MiniLM-L6-v2",
    ):
        """Initialise le recommender hybride.

        Args:
            recipes: Liste des recettes
            tfidf_weight: Poids TF-IDF (defaut 60%)
            bert_weight: Poids BERT (defaut 40%)
            bert_model: Modele BERT a utiliser
        """
        self.recipes = recipes
        self.tfidf_weight = tfidf_weight
        self.bert_weight = bert_weight

        logger.info(
            "HybridRecommender init: TF-IDF=%.1f%%, BERT=%.1f%%",
            tfidf_weight * 100,
            bert_weight * 100,
        )

        self.tfidf_recommender = RecipeRecommender(recipes)
        self.bert_recommender = BERTRecommender(recipes, model_name=bert_model)
        self.recipe_dict = {r.recipe_id: r for r in recipes}

    def fit(self) -> None:
        """Entraine les deux modeles."""
        logger.info("Entrainement TF-IDF...")
        self.tfidf_recommender.fit()

        logger.info("Entrainement BERT...")
        self.bert_recommender.fit()

        logger.info("Modeles hybrides entraines")

    def recommend(
        self, liked_recipe_ids: List[int], n: int = 10, exclude_liked: bool = True
    ) -> List[Recipe]:
        """Genere recommandations hybrides."""
        logger.info("Generation recommandations hybrides")

        # Recommandations TF-IDF
        tfidf_recs = self.tfidf_recommender.recommend(
            liked_recipe_ids, n=n * 2, exclude_liked=exclude_liked
        )

        # Recommandations BERT
        bert_recs = self.bert_recommender.recommend(
            liked_recipe_ids, n=n * 2, exclude_liked=exclude_liked
        )

        # Scores hybrides
        hybrid_scores = self._compute_hybrid_scores(tfidf_recs, bert_recs)

        # Trier par score
        sorted_recipes = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)

        # Top N
        top_recipe_ids = [rid for rid, score in sorted_recipes[:n]]

        return [self.recipe_dict[rid] for rid in top_recipe_ids]

    def _compute_hybrid_scores(
        self, tfidf_recs: List[Recipe], bert_recs: List[Recipe]
    ) -> Dict[int, float]:
        """Calcule scores hybrides."""
        scores = {}

        # Scores TF-IDF (normalises par rang)
        for i, recipe in enumerate(tfidf_recs):
            score = (len(tfidf_recs) - i) / len(tfidf_recs)
            scores[recipe.recipe_id] = self.tfidf_weight * score

        # Scores BERT (normalises par rang)
        for i, recipe in enumerate(bert_recs):
            score = (len(bert_recs) - i) / len(bert_recs)
            if recipe.recipe_id in scores:
                scores[recipe.recipe_id] += self.bert_weight * score
            else:
                scores[recipe.recipe_id] = self.bert_weight * score

        return scores

    def get_recipe_by_id(self, recipe_id: int) -> Recipe:
        """Recupere recette par ID."""
        return self.recipe_dict.get(recipe_id)
