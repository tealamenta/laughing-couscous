"""Compare TF-IDF vs BERT."""

import time
from recipe_recommender.data.data_loader import DataLoader
from recipe_recommender.models.recommender import RecipeRecommender
from recipe_recommender.models.bert_recommender import BERTRecommender


def main():
    print("=" * 60)
    print("COMPARAISON TF-IDF vs BERT RECOMMENDERS")
    print("=" * 60)
    print()

    print("Chargement des donnees...")
    loader = DataLoader()
    loader.load_all_data(min_rating=3.0, top_n_recipes=1000)
    recipes = loader.get_recipes()
    print(f"Recettes chargees: {len(recipes)}")
    print()

    # TF-IDF
    print("-" * 60)
    print("TF-IDF RECOMMENDER")
    print("-" * 60)
    tfidf = RecipeRecommender(recipes)

    start = time.time()
    tfidf.fit()
    tfidf_fit = time.time() - start
    print(f"Temps fit(): {tfidf_fit:.2f}s")

    liked = [recipes[0].recipe_id, recipes[5].recipe_id, recipes[10].recipe_id]

    start = time.time()
    tfidf_recs = tfidf.recommend(liked, n=10)
    tfidf_rec = time.time() - start
    print(f"Temps recommend(): {tfidf_rec:.4f}s")
    print()

    # BERT
    print("-" * 60)
    print("BERT RECOMMENDER (all-MiniLM-L6-v2)")
    print("-" * 60)
    bert = BERTRecommender(recipes)

    start = time.time()
    bert.fit()
    bert_fit = time.time() - start
    print(f"Temps fit(): {bert_fit:.2f}s")

    start = time.time()
    bert_recs = bert.recommend(liked, n=10)
    bert_rec = time.time() - start
    print(f"Temps recommend(): {bert_rec:.4f}s")
    print()

    # Comparaison performance
    print("=" * 60)
    print("COMPARAISON PERFORMANCE")
    print("=" * 60)
    print(f"{'Methode':<20} {'Fit (s)':<15} {'Recommend (s)':<15}")
    print("-" * 60)
    print(f"{'TF-IDF':<20} {tfidf_fit:<15.2f} {tfidf_rec:<15.4f}")
    print(f"{'BERT':<20} {bert_fit:<15.2f} {bert_rec:<15.4f}")
    print()
    print(f"BERT est {bert_fit/tfidf_fit:.1f}x plus lent au fit()")
    print(f"BERT est {bert_rec/tfidf_rec:.1f}x au recommend()")
    print()

    # Comparaison resultats
    print("=" * 60)
    print("TOP 5 RECOMMANDATIONS")
    print("=" * 60)
    print()
    print("TF-IDF:")
    for i, r in enumerate(tfidf_recs[:5], 1):
        print(f"  {i}. {r.name}")

    print()
    print("BERT:")
    for i, r in enumerate(bert_recs[:5], 1):
        print(f"  {i}. {r.name}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
