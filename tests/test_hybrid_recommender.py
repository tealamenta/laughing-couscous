from typing import List
import pytest

from src.recipe_recommender.models.hybrid_recommender import HybridRecommender


class FakeRecipe:
    """Objet recette factice utilisé pour les tests."""

    def __init__(self, id: int, tags: List[str]) -> None:
        self.recipe_id: int = id
        self.title: str = f"Test {id}"
        self.tags: List[str] = tags
        self.name: str = f"Test recipe {id}"
        self.description: str = "Desc"
        self.ingredients: List[str] = ["ing1"]


@pytest.fixture
def recipes() -> List[FakeRecipe]:
    """
    Fournit un petit jeu de recettes factices. Le tag 'common' apparaît
    exactement dans deux recettes pour satisfaire min_df=2 du TfidfVectorizer.
    """
    return [
        FakeRecipe(1, ["common", "test"]),
        FakeRecipe(2, ["common", "hybrid"]),
        FakeRecipe(3, ["recommendation", "other"]),
    ]


@pytest.fixture
def interactions() -> List[dict]:
    """Interactions factices minimalistes."""
    return [{"user_id": 1, "recipe_id": 1}]


def test_hybrid_recommender_basic(recipes: List[FakeRecipe], interactions: List[dict]):
    """
    Test basique du HybridRecommender sur un petit jeu factice.
    Vérifie que fit() puis recommend() renvoient une liste.
    """
    recommender = HybridRecommender(recipes, interactions)

    # Forcer des poids numériques pour éviter toute ambiguïté dans le calcul
    recommender.tfidf_weight = 0.5
    recommender.bert_weight = 0.5

    recommender.fit()
    liked_recipe_ids = [1]
    recs = recommender.recommend(liked_recipe_ids)

    assert isinstance(recs, list)
    # Optionnel : vérifier qu'on reçoit au moins une recommandation
    assert len(recs) >= 1
