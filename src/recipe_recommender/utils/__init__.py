"""Utilitaires pour l'application Recipe Recommender."""

from recipe_recommender.utils.favorites import FavoritesManager
from recipe_recommender.utils.filters import (
    filter_by_nutrition,
    filter_recipes,
    search_by_name,
)
from recipe_recommender.utils.logger import get_logger, setup_logger
from recipe_recommender.utils.nutrition import (
    calculate_macro_percentages,
    format_nutrition,
    get_nutrition_category,
    plot_nutrition_pie,
)

__all__ = [
    "setup_logger",
    "get_logger",
    "filter_recipes",
    "filter_by_nutrition",
    "search_by_name",
    "format_nutrition",
    "calculate_macro_percentages",
    "plot_nutrition_pie",
    "get_nutrition_category",
    "FavoritesManager",
]
