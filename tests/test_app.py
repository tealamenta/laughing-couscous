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


# Mock pour st.columns avec nombre variable de colonnes
def mock_st_columns(num):
    return [MagicMock() for _ in range(num)]


def test_main():
    mock_session_state = SessionStateMock()

    with patch.object(st, "session_state", mock_session_state):
        with patch("recipe_recommender.app.FavoritesManager") as MockFavMgr:
            instance = MockFavMgr.return_value
            instance.load_favorites.return_value = []

            #  AJOUTEZ CE MOCK POUR st.stop()
            with patch("recipe_recommender.app.st.stop"):
                with patch(
                    "recipe_recommender.app.st.tabs",
                    return_value=[MagicMock(), MagicMock(), MagicMock()],
                ):
                    with patch(
                        "recipe_recommender.app.st.columns", side_effect=mock_st_columns
                    ):
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
                            with patch(
                                "recipe_recommender.app.st.text_input", return_value=""
                            ):
                                with patch(
                                    "recipe_recommender.app.st.slider", return_value=60
                                ):
                                    
                                    main()
                                   
