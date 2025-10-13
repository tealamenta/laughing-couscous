"""
Module d'utilitaires pour la nutrition.

Ce module fournit des fonctions pour formater et visualiser
les informations nutritionnelles des recettes.
"""

from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from recipe_recommender.utils.logger import get_logger

logger = get_logger(__name__)


def format_nutrition(nutrition: List[float]) -> str:
    """
    Formate les informations nutritionnelles en texte lisible.

    Args:
        nutrition: Liste des valeurs nutritionnelles
            [calories, fat_%DV, saturated_fat_%DV, cholesterol_%DV,
             sodium_%DV, carbs_%DV, protein_%DV].

    Returns:
        str: Texte formaté avec les informations nutritionnelles.

    Example:
        >>> nutrition = [350, 15, 10, 5, 20, 45, 12]
        >>> print(format_nutrition(nutrition))
        **Calories:** 350
        **Total Fat (%DV):** 15
        ...
    """
    if not nutrition or len(nutrition) < 7:
        logger.warning("Données nutritionnelles incomplètes")
        return "Nutrition data unavailable."

    labels = [
        "Calories",
        "Total Fat (%DV)",
        "Saturated Fat (%DV)",
        "Cholesterol (%DV)",
        "Sodium (%DV)",
        "Total Carbs (%DV)",
        "Protein (%DV)",
    ]

    formatted = []
    for label, value in zip(labels, nutrition):
        formatted.append(f"**{label}:** {value}")

    return "\n".join(formatted)


def calculate_macro_percentages(nutrition: List[float]) -> Optional[dict]:
    """
    Calcule les pourcentages de calories provenant de chaque macronutriment.

    Args:
        nutrition: Liste des valeurs nutritionnelles.

    Returns:
        Optional[dict]: Dictionnaire avec les pourcentages ou None si impossible.
            - fat_pct: % de calories provenant des graisses
            - carbs_pct: % de calories provenant des glucides
            - protein_pct: % de calories provenant des protéines

    Example:
        >>> macros = calculate_macro_percentages([350, 15, 10, 5, 20, 45, 12])
        >>> print(f"Fat: {macros['fat_pct']:.1f}%")
    """
    if not nutrition or len(nutrition) < 7:
        logger.warning("Données nutritionnelles incomplètes")
        return None

    # Daily Values (grams)
    DV_FAT = 78
    DV_CARB = 275
    DV_PROTEIN = 50

    # Extraction des %DV
    fat_pdv = nutrition[1]
    carb_pdv = nutrition[5]
    protein_pdv = nutrition[6]

    # Calcul des grammes
    fat_g = (fat_pdv / 100) * DV_FAT
    carb_g = (carb_pdv / 100) * DV_CARB
    protein_g = (protein_pdv / 100) * DV_PROTEIN

    # Calories par macronutriment
    cal_fat = fat_g * 9
    cal_carb = carb_g * 4
    cal_protein = protein_g * 4

    total_macro_cal = cal_fat + cal_carb + cal_protein

    if total_macro_cal == 0:
        logger.warning("Total des calories des macros est 0")
        return None

    # Calcul des pourcentages
    return {
        "fat_pct": (cal_fat / total_macro_cal) * 100,
        "carbs_pct": (cal_carb / total_macro_cal) * 100,
        "protein_pct": (cal_protein / total_macro_cal) * 100,
    }


def plot_nutrition_pie(nutrition: List[float]) -> Optional[plt.Figure]:
    """
    Crée un graphique circulaire des macronutriments.

    Args:
        nutrition: Liste des valeurs nutritionnelles.

    Returns:
        Optional[plt.Figure]: Figure matplotlib ou None si impossible.

    Example:
        >>> fig = plot_nutrition_pie([350, 15, 10, 5, 20, 45, 12])
        >>> if fig:
        ...     fig.savefig("nutrition.png")
    """
    logger.debug("Création du graphique nutritionnel")

    macros = calculate_macro_percentages(nutrition)
    if not macros:
        return None

    # Données du graphique
    labels = ["Fat", "Carbohydrates", "Protein"]
    sizes = [macros["fat_pct"], macros["carbs_pct"], macros["protein_pct"]]
    colors = ["#ff9999", "#66b3ff", "#99ff99"]
    explode = (0.05, 0, 0)  # Légèrement séparer le premier segment

    # Créer le graphique
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 12},
    )
    ax.set_title("Macronutrient Breakdown (% of Calories)", fontsize=14, fontweight="bold")
    plt.axis("equal")

    logger.debug("Graphique nutritionnel créé avec succès")
    return fig


def get_nutrition_category(calories: float) -> str:
    """
    Catégorise une recette selon son apport calorique.

    Args:
        calories: Nombre de calories de la recette.

    Returns:
        str: Catégorie ("Low", "Medium", "High", "Very High").

    Example:
        >>> category = get_nutrition_category(350)
        >>> print(category)
        'Medium'
    """
    if calories < 200:
        return "Low"
    elif calories < 400:
        return "Medium"
    elif calories < 600:
        return "High"
    else:
        return "Very High"
