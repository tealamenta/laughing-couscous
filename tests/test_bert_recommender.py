from src.recipe_recommender.models.bert_recommender import BERTRecommender


class FakeRecipe:
    def __init__(self, id):
        self.recipe_id = id
        self.title = "Test"
        self.name = "Test recipe"
        self.description = "A simple test recipe description"
        self.ingredients = ["salt", "pepper"]
        self.tags = ["test", "easy"]


def test_bert_recommender_basic():
    recipes = [FakeRecipe(1)]
    recommender = BERTRecommender(recipes, model_name="all-MiniLM-L6-v2")
    recommender.fit()  # entraîner le modèle sur les données factices
    liked_recipe_ids = [1]
    recs = recommender.recommend(liked_recipe_ids)
    assert isinstance(recs, list)
