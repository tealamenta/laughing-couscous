from src.recipe_recommender.utils.favorites import FavoritesManager


def test_add_and_remove_favorite(tmp_path):
    f = tmp_path / "fav.json"
    manager = FavoritesManager(str(f))
    manager.add_favorite(1)
    favs = manager.load_favorites()
    assert 1 in favs
    manager.remove_favorite(1)
    favs = manager.load_favorites()
    assert 1 not in favs
