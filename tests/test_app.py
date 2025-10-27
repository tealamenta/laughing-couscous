from unittest.mock import MagicMock, patch
import streamlit as st
from recipe_recommender.app import main

class SessionStateMock:
    def __init__(self):
        self._store = {}

    def __getitem__(self, key):
        return self._store.get(key, None)

    def __setitem__(self, key, value):
        self._store[key] = value

    def __contains__(self, key):
        return key in self._store

def mock_st_columns(num):
    return [MagicMock() for _ in range(num)]

def test_main():
    mock_session_state = SessionStateMock()

    with patch.object(st, "session_state", mock_session_state):
        with patch("recipe_recommender.app.FavoritesManager") as MockFavMgr:
            instance = MockFavMgr.return_value
            instance.load_favorites.return_value = []

            # Mock st.stop pour que l'exécution continue
            with patch("recipe_recommender.app.st.stop"):
                # Mock des tabs
                with patch(
                    "recipe_recommender.app.st.tabs",
                    return_value=[MagicMock(), MagicMock(), MagicMock()],
                ):
                    # Mock des colonnes
                    with patch(
                        "recipe_recommender.app.st.columns", side_effect=mock_st_columns
                    ):
                        # Mock des filtres
                        with patch(
                            "recipe_recommender.app.render_search_filters",
                            return_value={
                                "search_query": "",
                                "selected_ingredients": [],
                                "selected_dietary": [],
                                "selected_ethnicity": "Toutes",
                                "max_time": 60,
                                "cal_range": (0, 500),
                            },
                        ):
                            # Mock des inputs Streamlit
                            with patch(
                                "recipe_recommender.app.st.text_input", return_value=""
                            ):
                                with patch(
                                    "recipe_recommender.app.st.slider", return_value=60
                                ):
                                    # Mock **load_recipes** pour qu'il retourne toujours une liste vide
                                    # et **ne lève jamais d'exception**
                                    with patch(
                                        "recipe_recommender.app.load_recipes",
                                        return_value=[]
                                    ):
                                        main()
