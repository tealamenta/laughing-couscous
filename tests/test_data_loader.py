import pytest
import sys
import os
from unittest.mock import patch
import pandas as pd

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from recipe_recommender.data.data_loader import DataLoader, DataLoadError
from recipe_recommender.models.recipe import Recipe


def test_init_with_invalid_path(tmp_path):
    invalid_path = tmp_path / "nonexistent"
    with pytest.raises(DataLoadError):
        DataLoader(str(invalid_path))


def test_check_required_files_all_present(tmp_path):
    dl = DataLoader(str(tmp_path))
    # Crée les fichiers requis vides
    for fname in dl.REQUIRED_FILES:
        (tmp_path / fname).write_text("")
    missing = dl.check_required_files()
    assert missing == []


def test_check_required_files_some_missing(tmp_path):
    dl = DataLoader(str(tmp_path))
    # Crée seulement certains fichiers
    (tmp_path / dl.REQUIRED_FILES[0]).write_text("")
    missing = dl.check_required_files()
    assert len(missing) == len(dl.REQUIRED_FILES) - 1
    assert dl.REQUIRED_FILES[0] not in missing


def test_create_id_mapping():
    dl = DataLoader(".")
    df = pd.DataFrame({"i": [1, 2], "id": [10, 20]})
    mapping = dl._create_id_mapping(df)
    assert mapping == {1: 10, 2: 20}


def test_calculate_ratings():
    dl = DataLoader(".")
    pp_users = pd.DataFrame(
        {"items": ["[1,2]", "[2,3]"], "ratings": ["[4,5]", "[3,2]"]}
    )
    id_dict = {1: 100, 2: 200, 3: 300}
    ratings_df = dl._calculate_ratings(pp_users, id_dict)
    # 100: rating 4, 200: ratings 5 and 3 (avg 4), 300: rating 2
    expected = pd.DataFrame({"recipe": [100, 200, 300], "rating": [4.0, 4.0, 2.0]})
    pd.testing.assert_frame_equal(
        ratings_df.sort_values("recipe").reset_index(drop=True),
        expected.sort_values("recipe").reset_index(drop=True),
    )


def test_filter_top_recipes():
    dl = DataLoader(".")
    df = pd.DataFrame({"recipe": [1, 2, 3, 4], "rating": [4.5, 2.0, 5.0, 3.5]})
    filtered = dl._filter_top_recipes(df, min_rating=3.0, top_n=3)
    # Les top 3 par rating sont 3 (5.0), 1 (4.5), 4 (3.5)
    assert set(filtered) == {1, 3, 4}


def test_create_recipe_objects(tmp_path):
    dl = DataLoader(str(tmp_path))
    raw_df = pd.DataFrame(
        {
            "id": [100],
            "name": ["Test Recipe"],
            "description": ["Desc"],
            "minutes": [30],
            "tags": ["['tag1', 'tag2']"],
            "nutrition": ["{'calories': 100}"],
            "ingredients": ["['ing1', 'ing2']"],
            "steps": ["['step1', 'step2']"],
        }
    )
    recipe_ids = raw_df["id"].tolist()
    recipes = dl._create_recipe_objects(raw_df, recipe_ids)
    assert len(recipes) == 1
    assert isinstance(recipes[0], Recipe)


def test_create_recipe_objects_handles_invalid_data(tmp_path, caplog):
    dl = DataLoader(str(tmp_path))
    raw_df = pd.DataFrame(
        {
            "id": [101],
            "name": ["Bad Recipe"],
            "description": ["Desc"],
            "minutes": [30],
            "tags": ["invalid"],  # mauvais format ici pour ast.literal_eval
            "nutrition": ["{'calories': 100}"],
            "ingredients": ["['ing1']"],
            "steps": ["['step1']"],
        }
    )
    recipe_ids = raw_df["id"].tolist()
    with caplog.at_level("WARNING"):
        recipes = dl._create_recipe_objects(raw_df, recipe_ids)
    assert len(recipes) == 0
    assert any(
        "Erreur lors de la création de la recette" in record.message
        for record in caplog.records
    )


def test_extract_ingredients():
    dl = DataLoader(".")
    r1 = Recipe(
        1, "R1", "", 10, ["tag"], {"calories": 100}, ["ing1", "ing2"], ["step1"]
    )
    r2 = Recipe(
        2, "R2", "", 15, ["tag"], {"calories": 150}, ["ing2", "ing3"], ["step1"]
    )
    dl.recipes = [r1, r2]
    ingredients = dl._extract_ingredients(top_n=10)
    assert set(["ing1", "ing2", "ing3"]).issubset(set(ingredients))


def test_get_recipes_and_ingredients(tmp_path):
    dl = DataLoader(str(tmp_path))
    dl.recipes = [Recipe(1, "R1", "", 10, [], {}, [], [])]
    dl.ingredient_list = ["ing1", "ing2"]
    assert dl.get_recipes() == dl.recipes
    assert dl.get_ingredients() == dl.ingredient_list


def test_get_recipes_empty():
    dl = DataLoader(".")
    dl.recipes = []
    with pytest.raises(DataLoadError):
        dl.get_recipes()


def test_get_ingredients_empty():
    dl = DataLoader(".")
    dl.ingredient_list = []
    with pytest.raises(DataLoadError):
        dl.get_ingredients()


@patch("pandas.read_csv")
def test_load_all_data_success(mock_read_csv, tmp_path):
    # Préparer les CSV mockés
    pp_recipes = pd.DataFrame({"i": [1], "id": [10]})
    pp_users = pd.DataFrame({"items": ["[1]"], "ratings": ["[5]"]})
    raw_recipes = pd.DataFrame(
        {
            "id": [10],
            "name": ["Name"],
            "description": ["Desc"],
            "minutes": [10],
            "tags": ["['tag']"],
            "nutrition": ["{'calories': 100}"],
            "ingredients": ["['ing1']"],
            "steps": ["['step1']"],
        }
    )

    def side_effect(filepath, *args, **kwargs):
        fname = os.path.basename(filepath)
        if fname == "PP_recipes.csv":
            return pp_recipes
        elif fname == "PP_users.csv":
            return pp_users
        elif fname == "RAW_recipes.csv":
            return raw_recipes
        else:
            return pd.DataFrame()

    mock_read_csv.side_effect = side_effect

    # Crée les fichiers requis (même vides) pour ne pas avoir d'erreur fichier manquant
    dl = DataLoader(str(tmp_path))
    for f in dl.REQUIRED_FILES:
        (tmp_path / f).write_text("")

    dl.load_all_data(min_rating=3.0, top_n_recipes=10)
    assert len(dl.recipes) == 1
    assert isinstance(dl.recipes[0], Recipe)
    assert len(dl.ingredient_list) > 0


@patch("pandas.read_csv")
def test_load_all_data_missing_files(mock_read_csv, tmp_path):
    dl = DataLoader(str(tmp_path))
    # Ne crée aucun fichier requis => fichier manquant
    with pytest.raises(DataLoadError):
        dl.load_all_data()
