from unittest.mock import MagicMock, patch
import streamlit as st
from recipe_recommender.app import main

def test_main():
    with patch.object(st, "session_state", {}):
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

            MockFavMgr.return_value.load_favorites.return_value = []

            main()

    assert True
