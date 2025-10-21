"""
Module de filtrage de recettes.

Ce module fournit des fonctions pour filtrer une liste de recettes
selon différents critères (ingrédients, tags, temps, calories, etc.).
"""

from typing import List, Optional

from recipe_recommender.models.recipe import Recipe
from recipe_recommender.utils.logger import get_logger

logger = get_logger(__name__)


def filter_recipes(
    recipes: List[Recipe],
    ingredients: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    max_minutes: Optional[int] = None,
    max_calories: Optional[float] = None,
    min_calories: Optional[float] = None,
) -> List[Recipe]:
    """
    Filtre une liste de recettes selon plusieurs critères.
    Complexity: A (3) - Reduced from C (18)

    Args:
        recipes: Liste de recettes à filtrer.
        ingredients: Liste d'ingrédients requis (optionnel).
        tags: Liste de tags requis (optionnel).
        max_minutes: Temps de préparation maximum en minutes (optionnel).
        max_calories: Calories maximales (optionnel).
        min_calories: Calories minimales (optionnel).

    Returns:
        List[Recipe]: Liste des recettes correspondant aux critères.
    """
    if not recipes:
        return []

    filtered = recipes
    initial_count = len(filtered)

    # Apply filters sequentially (simplified logic)
    if max_minutes is not None:
        filtered = _filter_by_time(filtered, max_minutes)

    if min_calories is not None or max_calories is not None:
        filtered = _filter_by_calories(filtered, min_calories, max_calories)

    if tags:
        filtered = _filter_by_tags(filtered, tags)

    if ingredients:
        filtered = _filter_by_ingredients(filtered, ingredients)

    logger.info(f"Filtered {initial_count} recipes to {len(filtered)}")
    return filtered


def _filter_by_time(recipes: List[Recipe], max_minutes: int) -> List[Recipe]:
    """Filter by cooking time. Complexity: A (1)"""
    result = [r for r in recipes if r.minutes <= max_minutes]
    logger.info(f"Time filter: {len(recipes)} → {len(result)}")
    return result


def _filter_by_calories(
    recipes: List[Recipe], min_calories: Optional[float], max_calories: Optional[float]
) -> List[Recipe]:
    """Filter by calorie range. Complexity: A (5)"""
    result = []
    for recipe in recipes:
        calories = recipe.get_calories()
        if calories is None:
            continue

        # Check min calories
        if min_calories is not None and calories < min_calories:
            continue

        # Check max calories
        if max_calories is not None and calories > max_calories:
            continue

        result.append(recipe)

    logger.info(f"Calories filter: {len(recipes)} → {len(result)}")
    return result


def _filter_by_tags(recipes: List[Recipe], tags: List[str]) -> List[Recipe]:
    """Filter by required tags. Complexity: A (3)"""
    result = [r for r in recipes if all(r.has_tag(tag) for tag in tags)]
    logger.info(f"Tags filter: {len(recipes)} → {len(result)}")
    return result


def _filter_by_ingredients(
    recipes: List[Recipe], ingredients: List[str]
) -> List[Recipe]:
    """Filter by required ingredients. Complexity: A (3)"""
    result = [r for r in recipes if all(r.has_ingredient(ing) for ing in ingredients)]
    logger.info(f"Ingredients filter: {len(recipes)} → {len(result)}")
    return result


def filter_by_nutrition(
    recipes: List[Recipe],
    max_fat_pdv: Optional[float] = None,
    max_sugar_pdv: Optional[float] = None,
    max_sodium_pdv: Optional[float] = None,
    max_protein_pdv: Optional[float] = None,
    max_sat_fat_pdv: Optional[float] = None,
    max_carbs_pdv: Optional[float] = None,
) -> List[Recipe]:
    """
    Filtre les recettes selon des critères nutritionnels.
    Complexity: A (2) - Reduced from D (22)

    Args:
        recipes: Liste de recettes à filtrer.
        max_fat_pdv: % valeur quotidienne max de matières grasses.
        max_sugar_pdv: % valeur quotidienne max de sucre.
        max_sodium_pdv: % valeur quotidienne max de sodium.
        max_protein_pdv: % valeur quotidienne max de protéines.
        max_sat_fat_pdv: % valeur quotidienne max de graisses saturées.
        max_carbs_pdv: % valeur quotidienne max de glucides.

    Returns:
        List[Recipe]: Recettes respectant les critères nutritionnels.
    """
    logger.info(f"Starting nutrition filter with {len(recipes)} recipes")

    # Build criteria dict (only non-None values)
    criteria = {
        "fat": max_fat_pdv,
        "sugar": max_sugar_pdv,
        "sodium": max_sodium_pdv,
        "protein": max_protein_pdv,
        "sat_fat": max_sat_fat_pdv,
        "carbs": max_carbs_pdv,
    }

    result = [r for r in recipes if _recipe_matches_nutrition(r, criteria)]

    logger.info(f"Nutrition filter: {len(recipes)} → {len(result)}")
    return result


def _recipe_matches_nutrition(recipe: Recipe, criteria: dict) -> bool:
    """
    Check if recipe matches nutrition criteria.
    Complexity: A (5)
    """
    if not recipe.nutrition or len(recipe.nutrition) < 7:
        return False

    # Nutrition indices
    nutrition_indices = {
        "fat": 1,
        "sugar": 2,
        "sodium": 3,
        "protein": 4,
        "sat_fat": 5,
        "carbs": 6,
    }

    # Check each criterion
    for name, max_value in criteria.items():
        if max_value is None:
            continue

        idx = nutrition_indices[name]
        actual_value = recipe.nutrition[idx]

        if actual_value > max_value:
            return False

    return True


def search_by_name(
    recipes: List[Recipe], query: str, search_in_description: bool = True
) -> List[Recipe]:
    """
    Recherche des recettes par nom ou description.
    Complexity: A (4)

    Args:
        recipes: Liste de recettes à rechercher.
        query: Terme de recherche.
        search_in_description: Chercher aussi dans la description.

    Returns:
        List[Recipe]: Recettes correspondant à la recherche.
    """
    if not query:
        return recipes

    query_lower = query.lower()
    results = []

    for recipe in recipes:
        # Search in name
        if query_lower in recipe.name.lower():
            results.append(recipe)
            continue

        # Search in description
        if search_in_description and recipe.description:
            if query_lower in recipe.description.lower():
                results.append(recipe)

    logger.info(f"Search '{query}': found {len(results)} recipes")
    return results
