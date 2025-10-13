"""
Module de chargement et prétraitement des données de recettes.

Ce module gère le chargement des fichiers CSV depuis Kaggle et leur transformation
en objets Recipe utilisables par l'application.
"""

import ast
import os
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from recipe_recommender.models.recipe import Recipe
from recipe_recommender.utils.logger import get_logger

logger = get_logger(__name__)


class DataLoadError(Exception):
    """Exception levée lors d'erreurs de chargement de données."""

    pass


class DataLoader:
    """
    Charge et prétraite les données de recettes depuis les fichiers CSV.

    Cette classe encapsule toute la logique de chargement des données depuis
    le dataset Kaggle Food.com et les transforme en objets Recipe.

    Attributes:
        data_path: Chemin vers le dossier contenant les fichiers CSV.
        recipes: Liste des objets Recipe chargés.
        ingredient_list: Liste des ingrédients les plus courants.

    Example:
        >>> loader = DataLoader(data_path="./data")
        >>> loader.load_all_data()
        >>> recipes = loader.get_recipes()
        >>> print(f"Loaded {len(recipes)} recipes")
    """

    REQUIRED_FILES = [
        "interactions_train.csv",
        "PP_recipes.csv",
        "PP_users.csv",
        "RAW_interactions.csv",
        "RAW_recipes.csv",
    ]

    def __init__(self, data_path: str = "./data") -> None:
        """
        Initialise le DataLoader.

        Args:
            data_path: Chemin vers le dossier contenant les fichiers CSV.

        Raises:
            DataLoadError: Si le dossier de données n'existe pas.
        """
        self.data_path = Path(data_path)
        self.recipes: List[Recipe] = []
        self.ingredient_list: List[str] = []

        if not self.data_path.exists():
            logger.error(f"Le dossier {data_path} n'existe pas")
            raise DataLoadError(f"Le dossier {data_path} n'existe pas")

        logger.info(f"DataLoader initialisé avec data_path={data_path}")

    def check_required_files(self) -> List[str]:
        """
        Vérifie que tous les fichiers requis sont présents.

        Returns:
            List[str]: Liste des fichiers manquants (vide si tous présents).

        Example:
            >>> missing = loader.check_required_files()
            >>> if missing:
            ...     print(f"Fichiers manquants: {missing}")
        """
        missing_files = []
        for filename in self.REQUIRED_FILES:
            if not (self.data_path / filename).exists():
                missing_files.append(filename)
                logger.warning(f"Fichier manquant: {filename}")

        if missing_files:
            logger.error(f"{len(missing_files)} fichiers manquants")
        else:
            logger.info("Tous les fichiers requis sont présents")

        return missing_files

    def load_all_data(
        self, min_rating: float = 3.0, top_n_recipes: int = 50000
    ) -> None:
        """
        Charge et prétraite toutes les données.

        Cette méthode effectue les étapes suivantes:
        1. Vérifie la présence des fichiers
        2. Charge les CSV
        3. Filtre les recettes par rating
        4. Crée les objets Recipe
        5. Extrait la liste des ingrédients courants

        Args:
            min_rating: Rating minimum pour inclure une recette. Par défaut 3.0.
            top_n_recipes: Nombre de recettes les plus notées à conserver. Par défaut 50000.

        Raises:
            DataLoadError: Si des fichiers sont manquants ou si le chargement échoue.

        Example:
            >>> loader.load_all_data(min_rating=4.0, top_n_recipes=10000)
        """
        logger.info("Début du chargement des données")

        # Vérifier les fichiers
        missing = self.check_required_files()
        if missing:
            raise DataLoadError(
                f"Fichiers manquants: {', '.join(missing)}. "
                f"Téléchargez le dataset depuis Kaggle."
            )

        try:
            # Charger les DataFrames
            logger.info("Chargement des fichiers CSV...")
            pp_recipes = pd.read_csv(self.data_path / "PP_recipes.csv")
            pp_users = pd.read_csv(self.data_path / "PP_users.csv")
            raw_recipes = pd.read_csv(self.data_path / "RAW_recipes.csv")

            logger.info(
                f"Fichiers chargés: {len(pp_recipes)} recettes prétraitées, "
                f"{len(pp_users)} utilisateurs"
            )

            # Créer le dictionnaire de mapping ID
            id_dict = self._create_id_mapping(pp_recipes)

            # Calculer les ratings moyens
            ratings_df = self._calculate_ratings(pp_users, id_dict)

            # Filtrer les meilleures recettes
            filtered_ids = self._filter_top_recipes(
                ratings_df, min_rating, top_n_recipes
            )

            # Créer les objets Recipe
            self.recipes = self._create_recipe_objects(raw_recipes, filtered_ids)

            # Extraire la liste des ingrédients
            self.ingredient_list = self._extract_ingredients(top_n=1100)

            logger.info(
                f"Chargement terminé: {len(self.recipes)} recettes, "
                f"{len(self.ingredient_list)} ingrédients"
            )

        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {str(e)}")
            raise DataLoadError(f"Erreur de chargement: {str(e)}") from e

    def _create_id_mapping(self, pp_recipes: pd.DataFrame) -> Dict[int, int]:
        """
        Crée un mapping entre les IDs prétraités et originaux.

        Args:
            pp_recipes: DataFrame des recettes prétraitées.

        Returns:
            Dict[int, int]: Mapping {pp_id: raw_id}.
        """
        logger.debug("Création du mapping d'IDs")
        return dict(zip(pp_recipes["i"], pp_recipes["id"]))

    def _calculate_ratings(
        self, pp_users: pd.DataFrame, id_dict: Dict[int, int]
    ) -> pd.DataFrame:
        """
        Calcule les ratings moyens par recette.

        Args:
            pp_users: DataFrame des utilisateurs.
            id_dict: Mapping des IDs.

        Returns:
            pd.DataFrame: DataFrame avec recipe_id et rating moyen.
        """
        logger.debug("Calcul des ratings moyens")

        recipes_list = []
        ratings_list = []

        for i in range(len(pp_users)):
            items = ast.literal_eval(pp_users["items"][i])
            ratings = ast.literal_eval(pp_users["ratings"][i])

            for item, rating in zip(items, ratings):
                if item in id_dict:
                    recipes_list.append(id_dict[item])
                    ratings_list.append(rating)

        df = pd.DataFrame({"recipe": recipes_list, "rating": ratings_list})
        return df.groupby("recipe")["rating"].mean().reset_index()

    def _filter_top_recipes(
        self, ratings_df: pd.DataFrame, min_rating: float, top_n: int
    ) -> List[int]:
        """
        Filtre les meilleures recettes selon le rating.

        Args:
            ratings_df: DataFrame avec les ratings.
            min_rating: Rating minimum.
            top_n: Nombre maximum de recettes à conserver.

        Returns:
            List[int]: Liste des IDs de recettes filtrées.
        """
        logger.debug(f"Filtrage: top {top_n} recettes avec rating >= {min_rating}")

        # Prendre les top_n les plus notées
        most_rated = ratings_df.nlargest(top_n, "rating")

        # Filtrer par rating minimum
        filtered = most_rated[most_rated["rating"] >= min_rating]

        logger.info(
            f"{len(filtered)} recettes après filtrage (rating >= {min_rating})"
        )

        return filtered["recipe"].tolist()

    def _create_recipe_objects(
        self, raw_recipes: pd.DataFrame, recipe_ids: List[int]
    ) -> List[Recipe]:
        """
        Crée les objets Recipe depuis le DataFrame.

        Args:
            raw_recipes: DataFrame des recettes brutes.
            recipe_ids: Liste des IDs à inclure.

        Returns:
            List[Recipe]: Liste d'objets Recipe.
        """
        logger.debug(f"Création de {len(recipe_ids)} objets Recipe")

        filtered_recipes = raw_recipes[raw_recipes["id"].isin(recipe_ids)]
        recipes = []

        for _, row in filtered_recipes.iterrows():
            try:
                recipe = Recipe(
                    recipe_id=int(row["id"]),
                    name=str(row["name"]),
                    description=str(row["description"]),
                    minutes=int(row["minutes"]),
                    tags=ast.literal_eval(row["tags"]),
                    nutrition=ast.literal_eval(row["nutrition"]),
                    ingredients=ast.literal_eval(row["ingredients"]),
                    steps=ast.literal_eval(row["steps"]),
                )
                recipes.append(recipe)
            except Exception as e:
                logger.warning(f"Erreur lors de la création de la recette {row['id']}: {e}")
                continue

        logger.info(f"{len(recipes)} objets Recipe créés avec succès")
        return recipes

    def _extract_ingredients(self, top_n: int = 1100) -> List[str]:
        """
        Extrait les ingrédients les plus courants.

        Args:
            top_n: Nombre d'ingrédients à conserver.

        Returns:
            List[str]: Liste des ingrédients les plus fréquents.
        """
        logger.debug(f"Extraction des {top_n} ingrédients les plus courants")

        all_ingredients = []
        for recipe in self.recipes:
            all_ingredients.extend(recipe.ingredients)

        counter = Counter(all_ingredients)
        top_ingredients = [ing for ing, _ in counter.most_common(top_n)]

        logger.info(f"{len(top_ingredients)} ingrédients extraits")
        return top_ingredients

    def get_recipes(self) -> List[Recipe]:
        """
        Retourne la liste des recettes chargées.

        Returns:
            List[Recipe]: Liste d'objets Recipe.

        Raises:
            DataLoadError: Si aucune recette n'est chargée.
        """
        if not self.recipes:
            logger.error("Aucune recette chargée. Appelez load_all_data() d'abord.")
            raise DataLoadError("Aucune recette chargée")

        return self.recipes

    def get_ingredients(self) -> List[str]:
        """
        Retourne la liste des ingrédients courants.

        Returns:
            List[str]: Liste des ingrédients.

        Raises:
            DataLoadError: Si la liste n'est pas initialisée.
        """
        if not self.ingredient_list:
            logger.error("Liste d'ingrédients vide. Appelez load_all_data() d'abord.")
            raise DataLoadError("Liste d'ingrédients vide")

        return self.ingredient_list
