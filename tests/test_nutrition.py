from src.recipe_recommender.utils.nutrition import (
    format_nutrition,
    calculate_macro_percentages,
    get_nutrition_category,
)


def test_format_nutrition_basic():
    nutrition = [350, 15, 10, 5, 20, 45, 12]
    result = format_nutrition(nutrition)
    assert isinstance(result, str)


def test_calculate_macro_percentages_basic():
    nutrition = [350, 15, 10, 5, 20, 45, 12]
    macro = calculate_macro_percentages(nutrition)
    assert isinstance(macro, dict)
    total = sum(macro.values())
    assert abs(total - 100) < 2


def test_get_nutrition_category_basic():
    cat = get_nutrition_category(350).lower()
    assert cat in ("faible", "moderee", "elevee", "medium", "low", "high")
