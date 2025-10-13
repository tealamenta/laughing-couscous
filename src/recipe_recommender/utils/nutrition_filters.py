"""Filtres nutritionnels simplifies."""

from typing import List, Optional
from recipe_recommender.models.recipe import Recipe


def check_calories_range(
    nutrition: list, min_cal: Optional[float], max_cal: Optional[float]
) -> bool:
    """Verifie si les calories sont dans la plage."""
    if len(nutrition) < 1:
        return False

    calories = nutrition[0]

    if min_cal is not None and calories < min_cal:
        return False
    if max_cal is not None and calories > max_cal:
        return False

    return True


def check_fat_range(nutrition: list, max_fat_pdv: Optional[float]) -> bool:
    """Verifie le pourcentage de matiere grasse."""
    if max_fat_pdv is None:
        return True

    if len(nutrition) < 2:
        return False

    return nutrition[1] <= max_fat_pdv


def check_carbs_range(nutrition: list, max_carbs_pdv: Optional[float]) -> bool:
    """Verifie le pourcentage de glucides."""
    if max_carbs_pdv is None:
        return True

    if len(nutrition) < 7:
        return False

    return nutrition[6] <= max_carbs_pdv


def check_protein_range(nutrition: list, min_protein_pdv: Optional[float]) -> bool:
    """Verifie le pourcentage de proteines."""
    if min_protein_pdv is None:
        return True

    if len(nutrition) < 5:
        return False

    return nutrition[4] >= min_protein_pdv


def filter_by_nutrition(
    recipes: List[Recipe],
    min_calories: Optional[float] = None,
    max_calories: Optional[float] = None,
    max_fat_pdv: Optional[float] = None,
    max_carbs_pdv: Optional[float] = None,
    min_protein_pdv: Optional[float] = None,
) -> List[Recipe]:
    """Filtre les recettes selon criteres nutritionnels."""
    filtered = []

    for recipe in recipes:
        if not recipe.nutrition or len(recipe.nutrition) < 7:
            continue

        # Verifier chaque critere
        if not check_calories_range(recipe.nutrition, min_calories, max_calories):
            continue

        if not check_fat_range(recipe.nutrition, max_fat_pdv):
            continue

        if not check_carbs_range(recipe.nutrition, max_carbs_pdv):
            continue

        if not check_protein_range(recipe.nutrition, min_protein_pdv):
            continue

        filtered.append(recipe)

    return filtered
