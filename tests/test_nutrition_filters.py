"""Tests pour nutrition_filters."""

from recipe_recommender.utils.nutrition_filters import (
    check_calories_range,
    check_fat_range,
    check_carbs_range,
    check_protein_range,
    filter_by_nutrition,
)
from recipe_recommender.models.recipe import Recipe


def test_check_calories_range_valid():
    """Test verification calories valide."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_calories_range(nutrition, 400.0, 600.0) is True
    assert check_calories_range(nutrition, 600.0, 700.0) is False
    assert check_calories_range(nutrition, 100.0, 400.0) is False


def test_check_calories_range_min_only():
    """Test calories minimum seulement."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_calories_range(nutrition, 400.0, None) is True
    assert check_calories_range(nutrition, 600.0, None) is False


def test_check_calories_range_max_only():
    """Test calories maximum seulement."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_calories_range(nutrition, None, 600.0) is True
    assert check_calories_range(nutrition, None, 400.0) is False


def test_check_calories_range_empty():
    """Test avec nutrition vide."""
    assert check_calories_range([], 100.0, 500.0) is False


def test_check_fat_range_valid():
    """Test verification matiere grasse."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_fat_range(nutrition, 30.0) is True
    assert check_fat_range(nutrition, 15.0) is False


def test_check_fat_range_none():
    """Test sans limite matiere grasse."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_fat_range(nutrition, None) is True


def test_check_fat_range_empty():
    """Test matiere grasse nutrition vide."""
    assert check_fat_range([], 30.0) is False


def test_check_carbs_range_valid():
    """Test verification glucides."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_carbs_range(nutrition, 40.0) is True
    assert check_carbs_range(nutrition, 20.0) is False


def test_check_carbs_range_none():
    """Test sans limite glucides."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_carbs_range(nutrition, None) is True


def test_check_carbs_range_empty():
    """Test glucides nutrition vide."""
    assert check_carbs_range([], 40.0) is False


def test_check_protein_range_valid():
    """Test verification proteines."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_protein_range(nutrition, 20.0) is True
    assert check_protein_range(nutrition, 30.0) is False


def test_check_protein_range_none():
    """Test sans limite proteines."""
    nutrition = [500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0]

    assert check_protein_range(nutrition, None) is True


def test_check_protein_range_empty():
    """Test proteines nutrition vide."""
    assert check_protein_range([], 20.0) is False


def test_filter_by_nutrition_all_criteria():
    """Test filtrage avec tous criteres."""
    recipes = [
        Recipe(
            recipe_id=1,
            name="Low Cal",
            description="Test",
            minutes=30,
            tags=[],
            nutrition=[200.0, 10.0, 5.0, 15.0, 25.0, 8.0, 15.0],
            ingredients=[],
            steps=[],
            n_steps=0,
            n_ingredients=0,
        ),
        Recipe(
            recipe_id=2,
            name="High Cal",
            description="Test",
            minutes=30,
            tags=[],
            nutrition=[800.0, 50.0, 30.0, 40.0, 15.0, 45.0, 60.0],
            ingredients=[],
            steps=[],
            n_steps=0,
            n_ingredients=0,
        ),
    ]

    result = filter_by_nutrition(
        recipes,
        max_calories=500.0,
        min_calories=100.0,
        max_fat_pdv=30.0,
        max_carbs_pdv=40.0,
        min_protein_pdv=20.0,
    )

    assert len(result) == 1
    assert result[0].recipe_id == 1


def test_filter_by_nutrition_empty_nutrition():
    """Test filtrage avec nutrition vide."""
    recipes = [
        Recipe(
            recipe_id=1,
            name="No Nutrition",
            description="Test",
            minutes=30,
            tags=[],
            nutrition=[],
            ingredients=[],
            steps=[],
            n_steps=0,
            n_ingredients=0,
        ),
    ]

    result = filter_by_nutrition(recipes, max_calories=500.0)

    assert len(result) == 0


def test_filter_by_nutrition_incomplete():
    """Test nutrition incomplete."""
    recipes = [
        Recipe(
            recipe_id=1,
            name="Incomplete",
            description="Test",
            minutes=30,
            tags=[],
            nutrition=[500.0, 20.0],  # Seulement 2 valeurs
            ingredients=[],
            steps=[],
            n_steps=0,
            n_ingredients=0,
        ),
    ]

    result = filter_by_nutrition(recipes, max_calories=600.0)

    assert len(result) == 0


def test_filter_by_nutrition_no_criteria():
    """Test sans criteres."""
    recipes = [
        Recipe(
            recipe_id=1,
            name="Recipe",
            description="Test",
            minutes=30,
            tags=[],
            nutrition=[500.0, 20.0, 10.0, 15.0, 25.0, 12.0, 30.0],
            ingredients=[],
            steps=[],
            n_steps=0,
            n_ingredients=0,
        ),
    ]

    result = filter_by_nutrition(recipes)

    assert len(result) == 1
