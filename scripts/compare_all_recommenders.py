"""Compare TF-IDF, BERT et Hybride."""

import time
from typing import List
from recipe_recommender.data.data_loader import DataLoader
from recipe_recommender.models.recipe import Recipe
from recipe_recommender.models.recommender import RecipeRecommender
from recipe_recommender.models.bert_recommender import BERTRecommender
from recipe_recommender.models.hybrid_recommender import HybridRecommender


def print_header(title: str):
    """Affiche un header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title: str):
    """Affiche une section."""
    print("\n" + "-" * 70)
    print(f"  {title}")
    print("-" * 70)


def print_recommendations(recs: List[Recipe], title: str):
    """Affiche recommandations."""
    print(f"\n{title}:")
    for i, r in enumerate(recs[:10], 1):
        print(f"  {i:2d}. {r.name}")


def calculate_overlap(recs1: List[Recipe], recs2: List[Recipe]) -> float:
    """Calcule pourcentage de chevauchement."""
    ids1 = set(r.recipe_id for r in recs1[:10])
    ids2 = set(r.recipe_id for r in recs2[:10])
    overlap = len(ids1 & ids2)
    return (overlap / 10) * 100


def main():
    print_header("COMPARAISON COMPLETE DES RECOMMENDERS")
    print(f"\nDate: 2025-10-13 13:03:01 UTC")
    print(f"User: tealamenta")

    # Chargement donnees
    print_section("CHARGEMENT DES DONNEES")
    loader = DataLoader()
    loader.load_all_data(min_rating=3.0, top_n_recipes=1000)
    recipes = loader.get_recipes()
    print(f"Recettes chargees: {len(recipes)}")

    # Recettes aimees
    liked = [recipes[0].recipe_id, recipes[5].recipe_id, recipes[10].recipe_id]
    print(f"\nRecettes aimees:")
    for i, rid in enumerate(liked, 1):
        recipe = next(r for r in recipes if r.recipe_id == rid)
        print(f"  {i}. {recipe.name}")

    # ========================================
    # TF-IDF RECOMMENDER
    # ========================================
    print_header("1. TF-IDF RECOMMENDER")

    tfidf = RecipeRecommender(recipes)

    print("\nEntrainement...")
    start = time.time()
    tfidf.fit()
    tfidf_fit_time = time.time() - start
    print(f"Temps fit(): {tfidf_fit_time:.3f}s")

    print("\nGeneration recommandations...")
    start = time.time()
    tfidf_recs = tfidf.recommend(liked, n=10)
    tfidf_rec_time = time.time() - start
    print(f"Temps recommend(): {tfidf_rec_time:.4f}s")

    print_recommendations(tfidf_recs, "TOP 10 TF-IDF")

    # ========================================
    # BERT RECOMMENDER
    # ========================================
    print_header("2. BERT RECOMMENDER")

    bert = BERTRecommender(recipes)

    print("\nEntrainement...")
    start = time.time()
    bert.fit()
    bert_fit_time = time.time() - start
    print(f"Temps fit(): {bert_fit_time:.3f}s")

    print("\nGeneration recommandations...")
    start = time.time()
    bert_recs = bert.recommend(liked, n=10)
    bert_rec_time = time.time() - start
    print(f"Temps recommend(): {bert_rec_time:.4f}s")

    print_recommendations(bert_recs, "TOP 10 BERT")

    # ========================================
    # HYBRID RECOMMENDER
    # ========================================
    print_header("3. HYBRID RECOMMENDER (60% TF-IDF + 40% BERT)")

    hybrid = HybridRecommender(recipes, tfidf_weight=0.6, bert_weight=0.4)

    print("\nEntrainement...")
    start = time.time()
    hybrid.fit()
    hybrid_fit_time = time.time() - start
    print(f"Temps fit(): {hybrid_fit_time:.3f}s")

    print("\nGeneration recommandations...")
    start = time.time()
    hybrid_recs = hybrid.recommend(liked, n=10)
    hybrid_rec_time = time.time() - start
    print(f"Temps recommend(): {hybrid_rec_time:.4f}s")

    print_recommendations(hybrid_recs, "TOP 10 HYBRID")

    # ========================================
    # COMPARAISON PERFORMANCE
    # ========================================
    print_header("COMPARAISON PERFORMANCE")

    print(f"\n{'Methode':<20} {'Fit (s)':<15} {'Recommend (s)':<15} {'Total (s)':<15}")
    print("-" * 70)
    print(
        f"{'TF-IDF':<20} {tfidf_fit_time:<15.3f} {tfidf_rec_time:<15.4f} {tfidf_fit_time+tfidf_rec_time:<15.3f}"
    )
    print(
        f"{'BERT':<20} {bert_fit_time:<15.3f} {bert_rec_time:<15.4f} {bert_fit_time+bert_rec_time:<15.3f}"
    )
    print(
        f"{'HYBRID':<20} {hybrid_fit_time:<15.3f} {hybrid_rec_time:<15.4f} {hybrid_fit_time+hybrid_rec_time:<15.3f}"
    )

    print(f"\nRapport de vitesse (vs TF-IDF):")
    print(f"  BERT fit:   {bert_fit_time/tfidf_fit_time:.1f}x plus lent")
    print(f"  BERT rec:   {bert_rec_time/tfidf_rec_time:.1f}x plus lent")
    print(f"  Hybrid fit: {hybrid_fit_time/tfidf_fit_time:.1f}x plus lent")
    print(f"  Hybrid rec: {hybrid_rec_time/tfidf_rec_time:.1f}x plus lent")

    # ========================================
    # ANALYSE QUALITE
    # ========================================
    print_header("ANALYSE QUALITE DES RECOMMANDATIONS")

    # Chevauchement
    overlap_tfidf_bert = calculate_overlap(tfidf_recs, bert_recs)
    overlap_tfidf_hybrid = calculate_overlap(tfidf_recs, hybrid_recs)
    overlap_bert_hybrid = calculate_overlap(bert_recs, hybrid_recs)

    print(f"\nChevauchement des recommandations (top 10):")
    print(f"  TF-IDF ∩ BERT:   {overlap_tfidf_bert:.0f}%")
    print(f"  TF-IDF ∩ HYBRID: {overlap_tfidf_hybrid:.0f}%")
    print(f"  BERT ∩ HYBRID:   {overlap_bert_hybrid:.0f}%")

    # Diversite
    print(f"\nDiversite (recettes uniques dans top 10):")
    all_recs = tfidf_recs[:10] + bert_recs[:10] + hybrid_recs[:10]
    unique_ids = set(r.recipe_id for r in all_recs)
    print(f"  Total recettes uniques: {len(unique_ids)}/30")
    print(f"  Taux de diversite: {(len(unique_ids)/30)*100:.1f}%")

    # ========================================
    # RECOMMANDATION FINALE
    # ========================================
    print_header("RECOMMANDATION FINALE")

    print(f"\n{'Critere':<30} {'TF-IDF':<15} {'BERT':<15} {'HYBRID':<15}")
    print("-" * 70)
    print(f"{'Vitesse fit':<30} {'+++':<15} {'--':<15} {'--':<15}")
    print(f"{'Vitesse recommend':<30} {'+++':<15} {'++':<15} {'++':<15}")
    print(f"{'Precision mots-cles':<30} {'+++':<15} {'++':<15} {'+++':<15}")
    print(f"{'Comprehension semantique':<30} {'+':<15} {'+++':<15} {'++':<15}")
    print(f"{'Diversite':<30} {'++':<15} {'+++':<15} {'+++':<15}")

    print("\n" + "=" * 70)
    print("CONCLUSION:")
    print("-" * 70)
    print(f"• TF-IDF:  Meilleur pour PERFORMANCE (ultra rapide)")
    print(f"• BERT:    Meilleur pour QUALITE (comprehension semantique)")
    print(f"• HYBRID:  EQUILIBRE optimal (60% perf + 40% qualite)")
    print(f"\nRECOMMANDATION: Utiliser HYBRID pour production")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
