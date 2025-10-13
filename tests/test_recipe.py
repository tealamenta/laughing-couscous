"""Tests unitaires pour la classe Recipe."""

import pytest

from recipe_recommender.models.recipe import Recipe


@pytest.fixture
def sample_recipe():
    """Fixture pour créer une recette de test."""
    return Recipe(
        recipe_id=12345,
        name="Chocolate Cake",
        description="A delicious chocolate cake",
        minutes=45,
        tags=["dessert", "chocolate", "vegetarian"],
        nutrition=[350.0, 15.0, 10.0, 5.0, 20.0, 45.0, 6.0],
        ingredients=["flour", "sugar", "cocoa powder", "eggs", "butter"],
        steps=["Mix ingredients", "Bake at 180C", "Let cool"],
    )


def test_recipe_creation(sample_recipe):
    """Test la création d'une recette."""
    assert sample_recipe.recipe_id == 12345
    assert sample_recipe.name == "Chocolate Cake"
    assert sample_recipe.minutes == 45
    assert len(sample_recipe.ingredients) == 5
    assert len(sample_recipe.steps) == 3


def test_recipe_post_init(sample_recipe):
    """Test que __post_init__ calcule n_steps et n_ingredients."""
    assert sample_recipe.n_steps == 3
    assert sample_recipe.n_ingredients == 5


def test_recipe_explicit_counts():
    """Test avec n_steps et n_ingredients explicites."""
    recipe = Recipe(
        recipe_id=999,
        name="Test",
        description="Test recipe",
        minutes=10,
        tags=["test"],
        nutrition=[100.0, 5.0, 3.0, 2.0, 10.0, 20.0, 4.0],
        ingredients=["ingredient1"],
        steps=["step1"],
        n_steps=10,
        n_ingredients=20,
    )
    assert recipe.n_steps == 10
    assert recipe.n_ingredients == 20


def test_get_calories(sample_recipe):
    """Test la méthode get_calories."""
    assert sample_recipe.get_calories() == 350.0


def test_get_calories_empty_nutrition():
    """Test get_calories avec nutrition vide."""
    recipe = Recipe(
        recipe_id=1,
        name="Test",
        description="Test",
        minutes=10,
        tags=[],
        nutrition=[],
        ingredients=[],
        steps=[],
    )
    assert recipe.get_calories() == 0.0


def test_get_macros(sample_recipe):
    """Test la méthode get_macros."""
    macros = sample_recipe.get_macros()
    assert macros["fat_pdv"] == 15.0
    assert macros["saturated_fat_pdv"] == 10.0
    assert macros["carbs_pdv"] == 45.0
    assert macros["protein_pdv"] == 6.0


def test_get_macros_incomplete_nutrition():
    """Test get_macros avec données incomplètes."""
    recipe = Recipe(
        recipe_id=1,
        name="Test",
        description="Test",
        minutes=10,
        tags=[],
        nutrition=[100.0, 5.0],  # Seulement 2 valeurs au lieu de 7
        ingredients=[],
        steps=[],
    )
    macros = recipe.get_macros()
    assert macros["fat_pdv"] == 0.0
    assert macros["saturated_fat_pdv"] == 0.0
    assert macros["carbs_pdv"] == 0.0
    assert macros["protein_pdv"] == 0.0


def test_has_tag(sample_recipe):
    """Test la méthode has_tag."""
    assert sample_recipe.has_tag("dessert") is True
    assert sample_recipe.has_tag("Chocolate") is True  # Case-insensitive
    assert sample_recipe.has_tag("VEGETARIAN") is True
    assert sample_recipe.has_tag("vegan") is False


def test_has_ingredient(sample_recipe):
    """Test la méthode has_ingredient."""
    assert sample_recipe.has_ingredient("flour") is True
    assert sample_recipe.has_ingredient("SUGAR") is True  # Case-insensitive
    assert sample_recipe.has_ingredient("cocoa") is True  # Partial match
    assert sample_recipe.has_ingredient("milk") is False


def test_matches_filters_time(sample_recipe):
    """Test matches_filters avec filtre de temps."""
    assert sample_recipe.matches_filters(max_minutes=60) is True
    assert sample_recipe.matches_filters(max_minutes=30) is False


def test_matches_filters_calories(sample_recipe):
    """Test matches_filters avec filtre de calories."""
    assert sample_recipe.matches_filters(max_calories=400) is True
    assert sample_recipe.matches_filters(max_calories=300) is False


def test_matches_filters_tags(sample_recipe):
    """Test matches_filters avec filtre de tags."""
    assert sample_recipe.matches_filters(required_tags=["dessert"]) is True
    assert (
        sample_recipe.matches_filters(required_tags=["dessert", "vegetarian"]) is True
    )
    assert sample_recipe.matches_filters(required_tags=["dessert", "vegan"]) is False


def test_matches_filters_ingredients(sample_recipe):
    """Test matches_filters avec filtre d'ingrédients."""
    assert sample_recipe.matches_filters(required_ingredients=["flour"]) is True
    assert (
        sample_recipe.matches_filters(required_ingredients=["flour", "sugar"]) is True
    )
    assert (
        sample_recipe.matches_filters(required_ingredients=["flour", "milk"]) is False
    )


def test_matches_filters_combined(sample_recipe):
    """Test matches_filters avec plusieurs filtres."""
    assert (
        sample_recipe.matches_filters(
            max_minutes=60,
            max_calories=400,
            required_tags=["dessert"],
            required_ingredients=["flour"],
        )
        is True
    )
    assert (
        sample_recipe.matches_filters(
            max_minutes=30,
            max_calories=400,
            required_tags=["dessert"],
            required_ingredients=["flour"],
        )
        is False
    )


def test_to_dict(sample_recipe):
    """Test la méthode to_dict."""
    recipe_dict = sample_recipe.to_dict()
    assert recipe_dict["recipe_id"] == 12345
    assert recipe_dict["name"] == "Chocolate Cake"
    assert recipe_dict["minutes"] == 45
    assert len(recipe_dict["ingredients"]) == 5
    assert len(recipe_dict["steps"]) == 3
    assert recipe_dict["n_steps"] == 3
    assert recipe_dict["n_ingredients"] == 5


def test_repr(sample_recipe):
    """Test la représentation string."""
    repr_str = repr(sample_recipe)
    assert "12345" in repr_str
    assert "Chocolate Cake" in repr_str
    assert "45" in repr_str
    assert "5" in repr_str
