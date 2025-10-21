"""Tests unitaires pour RecipeRecommender."""

import pytest

from recipe_recommender.models.recipe import Recipe
from recipe_recommender.models.recommender import RecipeRecommender


@pytest.fixture
def sample_recipes():
    """Fixture pour créer des recettes de test."""
    return [
        Recipe(
            recipe_id=1,
            name="Chocolate Cake",
            description="Delicious chocolate dessert",
            minutes=45,
            tags=["dessert", "chocolate", "cake"],
            nutrition=[350.0, 15.0, 10.0, 5.0, 20.0, 45.0, 6.0],
            ingredients=["flour", "sugar", "cocoa"],
            steps=["Mix", "Bake"],
        ),
        Recipe(
            recipe_id=2,
            name="Chocolate Cookies",
            description="Sweet chocolate cookies",
            minutes=30,
            tags=["dessert", "chocolate", "cookies"],
            nutrition=[250.0, 10.0, 5.0, 3.0, 15.0, 35.0, 4.0],
            ingredients=["flour", "sugar", "cocoa", "butter"],
            steps=["Mix", "Bake"],
        ),
        Recipe(
            recipe_id=3,
            name="Pasta Carbonara",
            description="Italian pasta dish",
            minutes=20,
            tags=["italian", "pasta", "main-course"],
            nutrition=[500.0, 20.0, 8.0, 10.0, 30.0, 50.0, 25.0],
            ingredients=["pasta", "eggs", "bacon"],
            steps=["Boil", "Cook", "Mix"],
        ),
        Recipe(
            recipe_id=4,
            name="Spaghetti Bolognese",
            description="Classic Italian pasta",
            minutes=40,
            tags=["italian", "pasta", "main-course"],
            nutrition=[550.0, 22.0, 9.0, 12.0, 35.0, 55.0, 28.0],
            ingredients=["pasta", "beef", "tomato"],
            steps=["Cook", "Simmer", "Serve"],
        ),
        Recipe(
            recipe_id=5,
            name="Green Salad",
            description="Healthy vegetable salad",
            minutes=10,
            tags=["vegetarian", "salad", "healthy"],
            nutrition=[100.0, 5.0, 2.0, 0.0, 10.0, 15.0, 3.0],
            ingredients=["lettuce", "tomato", "cucumber"],
            steps=["Chop", "Mix"],
        ),
    ]


@pytest.fixture
def recommender(sample_recipes):
    """Fixture pour créer un recommender entraîné."""
    rec = RecipeRecommender(sample_recipes)
    rec.fit()
    return rec


def test_recommender_init(sample_recipes):
    """Test l'initialisation du recommender."""
    rec = RecipeRecommender(sample_recipes)
    rec.fit()
    assert rec.tfidf_matrix is not None
    assert rec.tfidf_matrix.shape[0] == 5


def test_recommend_basic(recommender):
    """Test les recommandations basiques."""
    recommendations = recommender.recommend(liked_recipe_ids=[1], n=2)
    assert len(recommendations) <= 2
    assert all(r.recipe_id != 1 for r in recommendations)  # Exclut la recette likée


def test_recommend_similar_tags(recommender):
    """Test que les recommandations ont des tags similaires."""
    # Liker une recette chocolat devrait recommander d'autres desserts chocolat
    recommendations = recommender.recommend(liked_recipe_ids=[1], n=3)
    # La recette 2 (Chocolate Cookies) devrait être recommandée car même tags
    recommended_ids = [r.recipe_id for r in recommendations]
    assert 2 in recommended_ids


def test_recommend_multiple_likes(recommender):
    """Test avec plusieurs recettes likées."""
    # Liker des recettes italiennes devrait recommander d'autres recettes italiennes
    recommendations = recommender.recommend(liked_recipe_ids=[3, 4], n=2)
    assert len(recommendations) <= 2


def test_recommend_exclude_liked(recommender):
    """Test que les recettes likées sont exclues."""
    recommendations = recommender.recommend(
        liked_recipe_ids=[1, 2], n=5, exclude_liked=True
    )
    recommended_ids = [r.recipe_id for r in recommendations]
    assert 1 not in recommended_ids
    assert 2 not in recommended_ids


def test_recommend_include_liked(recommender):
    """Test avec exclude_liked=False."""
    recommendations = recommender.recommend(
        liked_recipe_ids=[1], n=5, exclude_liked=False
    )
    # Devrait inclure des recettes
    assert len(recommendations) > 0


def test_recommend_not_fitted():
    """Test recommend() sans avoir appelé fit()."""
    rec = RecipeRecommender(
        [
            Recipe(
                recipe_id=1,
                name="Test",
                description="Test",
                minutes=10,
                tags=["test"],
                nutrition=[100.0, 5.0, 3.0, 2.0, 10.0, 20.0, 4.0],
                ingredients=["ingredient"],
                steps=["step"],
            )
        ]
    )
    with pytest.raises(ValueError, match="Appelez fit"):
        rec.recommend([1], n=5)


def test_recommend_empty_likes(recommender):
    """Test avec liste vide de likes."""
    recommendations = recommender.recommend(liked_recipe_ids=[], n=5)
    assert len(recommendations) == 0


def test_recommend_invalid_id(recommender):
    """Test avec un ID invalide."""
    with pytest.raises(ValueError, match=r"Aucune recette likée valide"):
        recommender.recommend(liked_recipe_ids=[999], n=5)


def test_get_similar_recipes(recommender):
    """Test la recherche de recettes similaires."""
    similar = recommender.get_similar_recipes(recipe_id=1, n=2)
    assert len(similar) <= 2
    assert all(r.recipe_id != 1 for r in similar)  # Exclut la recette elle-même


def test_get_similar_recipes_include_self(recommender):
    """Test avec exclude_self=False."""
    similar = recommender.get_similar_recipes(recipe_id=1, n=3, exclude_self=False)
    # Devrait inclure au moins 1 recette (peut-être la recette elle-même)
    assert len(similar) > 0
    # Vérifier que la recette 1 est dans les résultats
    similar_ids = [r.recipe_id for r in similar]
    assert 1 in similar_ids


def test_get_similar_recipes_not_fitted():
    """Test get_similar_recipes() sans fit()."""
    rec = RecipeRecommender(
        [
            Recipe(
                recipe_id=1,
                name="Test",
                description="Test",
                minutes=10,
                tags=["test"],
                nutrition=[100.0, 5.0, 3.0, 2.0, 10.0, 20.0, 4.0],
                ingredients=["ingredient"],
                steps=["step"],
            )
        ]
    )
    with pytest.raises(ValueError, match="Appelez fit"):
        rec.get_similar_recipes(1, n=5)


def test_get_similar_recipes_invalid_id(recommender):
    """Test avec un ID invalide."""
    with pytest.raises(ValueError, match=r"Recette (avec )?ID .* non trouvée"):
        recommender.get_similar_recipes(recipe_id=999, n=5)


def test_get_recipe_by_id(recommender):
    """Test la récupération d'une recette par ID."""
    recipe = recommender.get_recipe_by_id(1)
    assert recipe is not None
    assert recipe.recipe_id == 1
    assert recipe.name == "Chocolate Cake"


def test_get_recipe_by_id_invalid(recommender):
    """Test avec un ID inexistant."""
    with pytest.raises(ValueError, match=r"Recette (avec )?ID .* non trouvée"):
        recommender.get_recipe_by_id(999)


def test_recommender_init_attributes(sample_recipes):
    """Test que les attributs sont correctement initialisés."""
    from recipe_recommender.models.recommender import RecipeRecommender

    recommender = RecipeRecommender(sample_recipes)

    assert recommender.tfidf_vectorizer is None
    assert recommender.tfidf_matrix is None
    assert len(recommender.id_to_index) == len(sample_recipes)
    assert len(recommender.index_to_id) == len(sample_recipes)
