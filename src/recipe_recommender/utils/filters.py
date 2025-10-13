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

    Args:
        recipes: Liste de recettes à filtrer.
        ingredients: Liste d'ingrédients requis (optionnel).
        tags: Liste de tags requis (optionnel).
        max_minutes: Temps de préparation maximum en minutes (optionnel).
        max_calories: Calories maximales (optionnel).
        min_calories: Calories minimales (optionnel).

    Returns:
        List[Recipe]: Liste des recettes correspondant aux critères.

    Example:
        >>> filtered = filter_recipes(
        ...     recipes,
        ...     ingredients=["chicken", "garlic"],
        ...     tags=["low-carb"],
        ...     max_minutes=30,
        ...     max_calories=500
        ... )
        >>> print(f"Found {len(filtered)} recipes")
    """
    logger.info(
        f"Filtrage de {len(recipes)} recettes avec critères: "
        f"ingredients={ingredients}, tags={tags}, "
        f"max_minutes={max_minutes}, max_calories={max_calories}, "
        f"min_calories={min_calories}"
    )

    filtered = recipes.copy()

    # Filtre par ingrédients
    if ingredients:
        filtered = [
            r
            for r in filtered
            if all(r.has_ingredient(ing) for ing in ingredients)
        ]
        logger.debug(f"{len(filtered)} recettes après filtre ingrédients")

    # Filtre par tags
    if tags:
        filtered = [r for r in filtered if all(r.has_tag(tag) for tag in tags)]
        logger.debug(f"{len(filtered)} recettes après filtre tags")

    # Filtre par temps
    if max_minutes is not None:
        filtered = [r for r in filtered if r.minutes <= max_minutes]
        logger.debug(f"{len(filtered)} recettes après filtre temps")

    # Filtre par calories max
    if max_calories is not None:
        filtered = [r for r in filtered if r.get_calories() <= max_calories]
        logger.debug(f"{len(filtered)} recettes après filtre calories max")

    # Filtre par calories min
    if min_calories is not None:
        filtered = [r for r in filtered if r.get_calories() >= min_calories]
        logger.debug(f"{len(filtered)} recettes après filtre calories min")

    logger.info(f"Filtrage terminé: {len(filtered)} recettes trouvées")
    return filtered


def filter_by_nutrition(
    recipes: List[Recipe],
    max_fat_pdv: Optional[float] = None,
    max_carbs_pdv: Optional[float] = None,
    max_protein_pdv: Optional[float] = None,
) -> List[Recipe]:
    """
    Filtre les recettes par critères nutritionnels.

    Args:
        recipes: Liste de recettes à filtrer.
        max_fat_pdv: % Daily Value max de graisses (optionnel).
        max_carbs_pdv: % Daily Value max de glucides (optionnel).
        max_protein_pdv: % Daily Value max de protéines (optionnel).

    Returns:
        List[Recipe]: Liste des recettes filtrées.

    Example:
        >>> low_fat = filter_by_nutrition(recipes, max_fat_pdv=20)
    """
    logger.info(f"Filtrage nutritionnel de {len(recipes)} recettes")

    filtered = recipes.copy()

    for recipe in list(filtered):
        macros = recipe.get_macros()

        # Filtre par graisses
        if max_fat_pdv is not None and macros["fat_pdv"] > max_fat_pdv:
            filtered.remove(recipe)
            continue

        # Filtre par glucides
        if max_carbs_pdv is not None and macros["carbs_pdv"] > max_carbs_pdv:
            filtered.remove(recipe)
            continue

        # Filtre par protéines
        if max_protein_pdv is not None and macros["protein_pdv"] > max_protein_pdv:
            filtered.remove(recipe)
            continue

    logger.info(f"{len(filtered)} recettes après filtrage nutritionnel")
    return filtered


def search_by_name(recipes: List[Recipe], query: str) -> List[Recipe]:
    """
    Recherche des recettes par nom ou description.

    Args:
        recipes: Liste de recettes à rechercher.
        query: Texte à rechercher (case-insensitive).

    Returns:
        List[Recipe]: Liste des recettes correspondantes.

    Example:
        >>> chocolate_recipes = search_by_name(recipes, "chocolate")
    """
    logger.info(f"Recherche de '{query}' dans {len(recipes)} recettes")

    query_lower = query.lower()
    results = [
        r
        for r in recipes
        if query_lower in r.name.lower() or query_lower in r.description.lower()
    ]

    logger.info(f"{len(results)} recettes trouvées pour '{query}'")
    return results
