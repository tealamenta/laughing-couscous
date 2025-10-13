"""
Module contenant la classe Recipe pour représenter une recette.

Ce module définit la structure de données d'une recette avec tous ses attributs
et méthodes pour manipuler et afficher les informations.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Recipe:
    """
    Représente une recette avec toutes ses caractéristiques.

    Cette classe encapsule les données d'une recette incluant son identifiant,
    son nom, ses ingrédients, sa nutrition, et d'autres métadonnées.

    Attributes:
        recipe_id: Identifiant unique de la recette.
        name: Nom de la recette.
        description: Description textuelle de la recette.
        minutes: Temps de préparation en minutes.
        tags: Liste des tags (ethnicity, dietary, etc.).
        nutrition: Liste des valeurs nutritionnelles [calories, fat, sugar, ...].
        ingredients: Liste des ingrédients nécessaires.
        steps: Liste des étapes de préparation.
        n_steps: Nombre d'étapes (optionnel).
        n_ingredients: Nombre d'ingrédients (optionnel).

    Example:
        >>> recipe = Recipe(
        ...     recipe_id=12345,
        ...     name="Chocolate Cake",
        ...     description="Delicious chocolate cake",
        ...     minutes=45,
        ...     tags=["dessert", "chocolate"],
        ...     nutrition=[350, 15, 30, 5, 200, 45, 6],
        ...     ingredients=["flour", "sugar", "cocoa"],
        ...     steps=["Mix ingredients", "Bake at 180°C"]
        ... )
        >>> recipe.get_calories()
        350
    """

    recipe_id: int
    name: str
    description: str
    minutes: int
    tags: List[str]
    nutrition: List[float]
    ingredients: List[str]
    steps: List[str]
    n_steps: Optional[int] = None
    n_ingredients: Optional[int] = None

    def __post_init__(self) -> None:
        """
        Initialise les attributs calculés après la création de l'objet.

        Cette méthode est appelée automatiquement après __init__.
        Elle calcule n_steps et n_ingredients s'ils ne sont pas fournis.
        """
        if self.n_steps is None:
            self.n_steps = len(self.steps)
        if self.n_ingredients is None:
            self.n_ingredients = len(self.ingredients)

    def get_calories(self) -> float:
        """
        Retourne le nombre de calories de la recette.

        Returns:
            float: Nombre de calories (nutrition[0]).

        Example:
            >>> recipe.get_calories()
            350.0
        """
        return self.nutrition[0] if self.nutrition else 0.0

    def get_macros(self) -> Dict[str, float]:
        """
        Retourne les macronutriments (graisses, glucides, protéines).

        Returns:
            Dict[str, float]: Dictionnaire avec les pourcentages de DV.
                - fat_pdv: % Daily Value de graisses totales
                - saturated_fat_pdv: % DV de graisses saturées
                - carbs_pdv: % DV de glucides
                - protein_pdv: % DV de protéines

        Example:
            >>> recipe.get_macros()
            {'fat_pdv': 15.0, 'saturated_fat_pdv': 10.0, ...}
        """
        if not self.nutrition or len(self.nutrition) < 7:
            return {
                "fat_pdv": 0.0,
                "saturated_fat_pdv": 0.0,
                "carbs_pdv": 0.0,
                "protein_pdv": 0.0,
            }

        return {
            "fat_pdv": self.nutrition[1],
            "saturated_fat_pdv": self.nutrition[2],
            "carbs_pdv": self.nutrition[5],
            "protein_pdv": self.nutrition[6],
        }

    def has_tag(self, tag: str) -> bool:
        """
        Vérifie si la recette contient un tag spécifique.

        Args:
            tag: Le tag à rechercher (case-insensitive).

        Returns:
            bool: True si le tag est présent, False sinon.

        Example:
            >>> recipe.has_tag("vegetarian")
            True
        """
        return tag.lower() in [t.lower() for t in self.tags]

    def has_ingredient(self, ingredient: str) -> bool:
        """
        Vérifie si la recette contient un ingrédient spécifique.

        Args:
            ingredient: L'ingrédient à rechercher (case-insensitive).

        Returns:
            bool: True si l'ingrédient est présent, False sinon.

        Example:
            >>> recipe.has_ingredient("flour")
            True
        """
        return any(ingredient.lower() in ing.lower() for ing in self.ingredients)

    def matches_filters(
        self,
        max_minutes: Optional[int] = None,
        max_calories: Optional[float] = None,
        required_tags: Optional[List[str]] = None,
        required_ingredients: Optional[List[str]] = None,
    ) -> bool:
        """
        Vérifie si la recette correspond aux filtres spécifiés.

        Args:
            max_minutes: Temps de préparation maximum (optionnel).
            max_calories: Calories maximales (optionnel).
            required_tags: Liste de tags requis (optionnel).
            required_ingredients: Liste d'ingrédients requis (optionnel).

        Returns:
            bool: True si tous les filtres sont satisfaits, False sinon.

        Example:
            >>> recipe.matches_filters(max_minutes=60, max_calories=400)
            True
        """
        # Filtre par temps
        if max_minutes is not None and self.minutes > max_minutes:
            return False

        # Filtre par calories
        if max_calories is not None and self.get_calories() > max_calories:
            return False

        # Filtre par tags
        if required_tags:
            if not all(self.has_tag(tag) for tag in required_tags):
                return False

        # Filtre par ingrédients
        if required_ingredients:
            if not all(self.has_ingredient(ing) for ing in required_ingredients):
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la recette en dictionnaire.

        Returns:
            Dict[str, Any]: Dictionnaire contenant toutes les données de la recette.

        Example:
            >>> recipe.to_dict()
            {'recipe_id': 12345, 'name': 'Chocolate Cake', ...}
        """
        return {
            "recipe_id": self.recipe_id,
            "name": self.name,
            "description": self.description,
            "minutes": self.minutes,
            "tags": self.tags,
            "nutrition": self.nutrition,
            "ingredients": self.ingredients,
            "steps": self.steps,
            "n_steps": self.n_steps,
            "n_ingredients": self.n_ingredients,
        }

    def __repr__(self) -> str:
        """
        Représentation string de la recette.

        Returns:
            str: Représentation formatée de la recette.
        """
        return (
            f"Recipe(id={self.recipe_id}, name='{self.name}', "
            f"minutes={self.minutes}, ingredients={self.n_ingredients})"
        )
