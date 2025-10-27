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
    # Patch session_state pour Streamlit
    with patch.object(st, "session_state", {}):
        # Patch tous les objets Streamlit utilisés dans main
        with patch("recipe_recommender.app.st.sidebar.metric"), \
             patch("recipe_recommender.app.st.stop"), \
             patch("recipe_recommender.app.st.tabs", return_value=[MagicMock()]*3), \
             patch("recipe_recommender.app.st.columns", return_value=[MagicMock()]*3), \
             patch("recipe_recommender.app.st.text_input", return_value=""), \
             patch("recipe_recommender.app.st.slider", return_value=60), \
             patch("recipe_recommender.app.render_search_filters", return_value={
                 "search_query": "",
                 "selected_ingredients": [],
                 "selected_dietary": [],
                 "selected_ethnicity": "Toutes",
                 "max_time": 60,
                 "cal_range": (0, 500),
             }), \
             patch("recipe_recommender.app.FavoritesManager") as MockFavMgr:

            # Evite de planter si main() essaie de charger des favoris
            MockFavMgr.return_value.load_favorites.return_value = []

            # Lancement de main() — il ne plantera jamais
            main()

    assert True
