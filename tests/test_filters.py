"""Tests unitaires pour le module filters."""

import pytest

from recipe_recommender.models.recipe import Recipe
from recipe_recommender.utils.filters import (
    filter_by_nutrition,
    filter_recipes,
    search_by_name,
)


@pytest.fixture
def sample_recipes():
    """Fixture pour créer des recettes de test."""
    return [
        Recipe(
            recipe_id=1,
            name="Chocolate Cake",
            description="A delicious chocolate cake",
            minutes=45,
            tags=["dessert", "chocolate"],
            nutrition=[350.0, 15.0, 10.0, 5.0, 20.0, 45.0, 6.0],
            ingredients=["flour", "sugar", "cocoa"],
            steps=["Mix", "Bake"],
        ),
        Recipe(
            recipe_id=2,
            name="Chicken Pasta",
            description="Quick pasta with chicken",
            minutes=20,
            tags=["italian", "pasta"],
            nutrition=[500.0, 20.0, 8.0, 10.0, 30.0, 50.0, 25.0],
            ingredients=["pasta", "chicken", "tomato"],
            steps=["Boil", "Cook", "Mix"],
        ),
        Recipe(
            recipe_id=3,
            name="Green Salad",
            description="Healthy vegetable salad",
            minutes=10,
            tags=["vegetarian", "low-calorie"],
            nutrition=[100.0, 5.0, 2.0, 0.0, 10.0, 15.0, 3.0],
            ingredients=["lettuce", "tomato", "cucumber"],
            steps=["Chop", "Mix"],
        ),
    ]


def test_filter_recipes_no_filters(sample_recipes):
    """Test sans aucun filtre (devrait retourner toutes les recettes)."""
    result = filter_recipes(sample_recipes)
    assert len(result) == 3


def test_filter_recipes_by_ingredients(sample_recipes):
    """Test le filtre par ingrédients."""
    result = filter_recipes(sample_recipes, ingredients=["tomato"])
    assert len(result) == 2
    assert all("tomato" in r.ingredients for r in result)


def test_filter_recipes_by_tags(sample_recipes):
    """Test le filtre par tags."""
    result = filter_recipes(sample_recipes, tags=["vegetarian"])
    assert len(result) == 1
    assert result[0].recipe_id == 3


def test_filter_recipes_by_max_minutes(sample_recipes):
    """Test le filtre par temps maximum."""
    result = filter_recipes(sample_recipes, max_minutes=30)
    assert len(result) == 2
    assert all(r.minutes <= 30 for r in result)


def test_filter_recipes_by_max_calories(sample_recipes):
    """Test le filtre par calories maximales."""
    result = filter_recipes(sample_recipes, max_calories=400)
    assert len(result) == 2
    assert all(r.get_calories() <= 400 for r in result)


def test_filter_recipes_by_min_calories(sample_recipes):
    """Test le filtre par calories minimales."""
    result = filter_recipes(sample_recipes, min_calories=200)
    assert len(result) == 2
    assert all(r.get_calories() >= 200 for r in result)


def test_filter_recipes_combined(sample_recipes):
    """Test avec plusieurs filtres combinés."""
    result = filter_recipes(
        sample_recipes, max_minutes=30, max_calories=300, tags=["vegetarian"]
    )
    assert len(result) == 1
    assert result[0].recipe_id == 3


def test_filter_recipes_no_results(sample_recipes):
    """Test qui ne devrait retourner aucun résultat."""
    result = filter_recipes(sample_recipes, tags=["vegan"], max_calories=50)
    assert len(result) == 0


def test_filter_by_nutrition(sample_recipes):
    """Test le filtre par valeurs nutritionnelles."""
    result = filter_by_nutrition(sample_recipes, max_fat_pdv=10.0)
    assert len(result) == 1
    assert result[0].recipe_id == 3


def test_filter_by_nutrition_multiple(sample_recipes):
    """Test le filtre nutritionnel avec plusieurs critères."""
    # Toutes les recettes ont fat <= 25 et carbs <= 50, donc on devrait obtenir les 3
    result = filter_by_nutrition(sample_recipes, max_fat_pdv=25.0, max_carbs_pdv=50.0)
    assert len(result) == 3


def test_filter_by_nutrition_strict(sample_recipes):
    """Test le filtre nutritionnel strict."""
    # Seulement la salade a fat <= 10
    result = filter_by_nutrition(sample_recipes, max_fat_pdv=10.0, max_carbs_pdv=20.0)
    assert len(result) == 1
    assert result[0].recipe_id == 3


def test_search_by_name_exact(sample_recipes):
    """Test la recherche par nom exact."""
    result = search_by_name(sample_recipes, "Chocolate")
    assert len(result) == 1
    assert result[0].name == "Chocolate Cake"


def test_search_by_name_case_insensitive(sample_recipes):
    """Test que la recherche est case-insensitive."""
    result = search_by_name(sample_recipes, "PASTA")
    assert len(result) == 1
    assert result[0].recipe_id == 2


def test_search_by_description(sample_recipes):
    """Test la recherche dans la description."""
    result = search_by_name(sample_recipes, "quick")
    assert len(result) == 1
    assert result[0].recipe_id == 2


def test_search_no_results(sample_recipes):
    """Test une recherche sans résultat."""
    result = search_by_name(sample_recipes, "pizza")
    assert len(result) == 0
