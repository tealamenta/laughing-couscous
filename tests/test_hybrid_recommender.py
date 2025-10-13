"""Tests pour HybridRecommender."""

import pytest
from recipe_recommender.models.hybrid_recommender import HybridRecommender
from recipe_recommender.models.recipe import Recipe


@pytest.fixture
def many_recipes():
    """Créer 30 recettes pour TF-IDF."""
    flavors = [
        "chocolate",
        "vanilla",
        "strawberry",
        "lemon",
        "orange",
        "apple",
        "banana",
        "coconut",
        "caramel",
        "peanut",
        "almond",
        "walnut",
        "pecan",
        "hazelnut",
        "cashew",
        "cinnamon",
        "ginger",
        "nutmeg",
        "cardamom",
        "clove",
        "maple",
        "honey",
        "mint",
        "raspberry",
        "blueberry",
        "cherry",
        "mango",
        "pineapple",
        "lime",
        "grape",
    ]

    return [
        Recipe(
            recipe_id=i + 1,
            name=f"{flavors[i]} Cookies",
            description=f"Delicious {flavors[i]} flavored cookies recipe with unique ingredients",
            minutes=30 + i,
            tags=["dessert", "cookies", flavors[i], "homemade"],
            nutrition=[200.0 + i * 5, 10.0, 5.0, 15.0, 25.0, 8.0, 15.0],
            ingredients=[flavors[i], "flour", "sugar", "butter", "eggs"],
            steps=["Mix all ingredients", "Form cookies", "Bake until golden"],
            n_steps=3,
            n_ingredients=5,
        )
        for i in range(30)
    ]


def test_hybrid_init(many_recipes):
    """Test initialisation."""
    hybrid = HybridRecommender(many_recipes, tfidf_weight=0.5, bert_weight=0.5)
    assert len(hybrid.recipes) == 30
    assert hybrid.tfidf_weight == 0.5


def test_hybrid_get_recipe_by_id(many_recipes):
    """Test get_recipe_by_id."""
    hybrid = HybridRecommender(many_recipes)

    recipe = hybrid.get_recipe_by_id(1)
    assert recipe.recipe_id == 1

    recipe = hybrid.get_recipe_by_id(999)
    assert recipe is None
