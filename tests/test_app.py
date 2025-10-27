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
    # Mock session_state comme un dictionnaire simple
    mock_session_state = SessionStateMock()

    with patch.object(st, "session_state", mock_session_state):
        with patch("recipe_recommender.app.st.sidebar.metric"), \
             patch("recipe_recommender.app.st.stop"), \
             patch("recipe_recommender.app.st.tabs", return_value=[MagicMock()] * 3), \
             patch("recipe_recommender.app.st.columns", side_effect=mock_st_columns), \
             patch("recipe_recommender.app.st.text_input", return_value=""), \
             patch("recipe_recommender.app.st.slider", return_value=60), \
             patch("recipe_recommender.app.st.button", return_value=False), \
             patch("recipe_recommender.app.st.pyplot"), \
             patch("recipe_recommender.app.st.plotly_chart"), \
             patch("recipe_recommender.app.st.success"), \
             patch("recipe_recommender.app.st.info"), \
             patch("recipe_recommender.app.st.warning"), \
             patch("recipe_recommender.app.st.error"), \
             patch("recipe_recommender.app.st.markdown"), \
             patch("recipe_recommender.app.st.expander", return_value=MagicMock()), \
             patch("recipe_recommender.app.st.multiselect", return_value=[]), \
             patch("recipe_recommender.app.st.selectbox", return_value="Toutes"), \
             patch("recipe_recommender.app.render_search_filters", return_value={
                 "search_query": "",
                 "selected_ingredients": [],
                 "selected_dietary": [],
                 "selected_ethnicity": "Toutes",
                 "max_time": 60,
                 "cal_range": (0, 500),
             }), \
             patch("recipe_recommender.app.FavoritesManager") as MockFavMgr, \
             patch("recipe_recommender.app.load_data", return_value=([], [], None)):  # CORRIGÉ ICI

            # Configuration du mock pour FavoritesManager
            mock_fav_mgr = MockFavMgr.return_value
            mock_fav_mgr.load_favorites.return_value = []
            mock_fav_mgr.add_favorite.return_value = []
            mock_fav_mgr.remove_favorite.return_value = []

            # Exécuter main()
            main()

    # Le test passe si main() s'exécute sans lever d'exception
    assert True