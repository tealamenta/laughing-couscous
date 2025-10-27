# tests/test_app.py
from unittest.mock import MagicMock, patch
import streamlit as st
from recipe_recommender.app import main


class SessionStateMock:
    """Mock minimal de st.session_state (dict-like)."""
    def __init__(self):
        self._store = {}

    def __getitem__(self, key):
        return self._store.get(key)

    def __setitem__(self, key, value):
        self._store[key] = value

    def __contains__(self, key):
        return key in self._store

    def __delitem__(self, key):
        self._store.pop(key, None)


def mock_st_columns(spec):
    """Retourne spec colonnes mockées."""
    return [MagicMock() for _ in range(spec)]


def test_main():
    """Teste que main() s'exécute sans erreur."""
    session_state = SessionStateMock()

    with patch.object(st, "session_state", session_state):
        patches = [
            patch("recipe_recommender.app.st.sidebar.metric"),
            patch("recipe_recommender.app.st.sidebar.title"),
            patch("recipe_recommender.app.st.sidebar.success"),
            patch("recipe_recommender.app.st.sidebar.info"),
            patch("recipe_recommender.app.st.title"),
            patch("recipe_recommender.app.st.header"),
            patch("recipe_recommender.app.st.stop"),
            patch("recipe_recommender.app.st.tabs", return_value=[MagicMock()] * 3),
            patch("recipe_recommender.app.st.columns", side_effect=mock_st_columns),
            patch("recipe_recommender.app.st.text_input", return_value=""),
            patch("recipe_recommender.app.st.slider", return_value=60),
            patch("recipe_recommender.app.st.button", return_value=False),
            patch("recipe_recommender.app.st.pyplot"),
            patch("recipe_recommender.app.st.plotly_chart"),
            patch("recipe_recommender.app.st.success"),
            patch("recipe_recommender.app.st.info"),
            patch("recipe_recommender.app.st.warning"),
            patch("recipe_recommender.app.st.error"),
            patch("recipe_recommender.app.st.markdown"),
            patch("recipe_recommender.app.st.expander", return_value=MagicMock()),
            patch("recipe_recommender.app.st.multiselect", return_value=[]),
            patch("recipe_recommender.app.st.selectbox", return_value="Toutes"),
            patch("recipe_recommender.app.render_search_filters", return_value={
                "search_query": "",
                "selected_ingredients": [],
                "selected_dietary": [],
                "selected_ethnicity": "Toutes",
                "max_time": 60,
                "cal_range": (0, 500),
            }),
            patch("recipe_recommender.app.load_data", return_value=([], [], None)),
        ]

        for p in patches:
            p.start()

        try:
            with patch("recipe_recommender.app.FavoritesManager") as MockFavMgr:
                mock_mgr = MockFavMgr.return_value
                mock_mgr.load_favorites.return_value = []
                mock_mgr.add_favorite.return_value = []
                mock_mgr.remove_favorite.return_value = []
                main()
        finally:
            for p in patches:
                p.stop()
