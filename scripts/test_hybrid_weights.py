"""Test differents poids Hybrid pour trouver equilibre optimal."""

import time
from recipe_recommender.data.data_loader import DataLoader
from recipe_recommender.models.recommender import RecipeRecommender
from recipe_recommender.models.bert_recommender import BERTRecommender
from recipe_recommender.models.hybrid_recommender import HybridRecommender


def print_header(title):
    """Affiche header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_section(title):
    """Affiche section."""
    print(f"\n{title}")
    print("-" * 80)


def calculate_overlap(recs1, recs2):
    """Calcule chevauchement."""
    ids1 = set(r.recipe_id for r in recs1[:10])
    ids2 = set(r.recipe_id for r in recs2[:10])
    return len(ids1 & ids2)


def main():
    print_header("TEST POIDS HYBRID - OPTIMISATION")
    print(f"\nDate: 2025-10-13 13:07:19 UTC")
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

    # Baseline TF-IDF et BERT
    print_section("BASELINE: TF-IDF ET BERT PURS")

    print("\nTF-IDF (100% mots-cles)...")
    tfidf = RecipeRecommender(recipes)
    tfidf.fit()
    tfidf_recs = tfidf.recommend(liked, n=10)

    print("BERT (100% semantique)...")
    bert = BERTRecommender(recipes)
    bert.fit()
    bert_recs = bert.recommend(liked, n=10)

    print("\nTOP 5 TF-IDF:")
    for i, r in enumerate(tfidf_recs[:5], 1):
        print(f"  {i}. {r.name}")

    print("\nTOP 5 BERT:")
    for i, r in enumerate(bert_recs[:5], 1):
        print(f"  {i}. {r.name}")

    # Test differents poids
    print_header("TEST DIFFERENTS POIDS HYBRID")

    weights_to_test = [
        (0.8, 0.2),  # 80% TF-IDF, 20% BERT
        (0.7, 0.3),  # 70% TF-IDF, 30% BERT
        (0.6, 0.4),  # 60% TF-IDF, 40% BERT (actuel)
        (0.5, 0.5),  # 50% TF-IDF, 50% BERT (equilibre)
        (0.4, 0.6),  # 40% TF-IDF, 60% BERT
        (0.3, 0.7),  # 30% TF-IDF, 70% BERT
        (0.2, 0.8),  # 20% TF-IDF, 80% BERT
    ]

    results = []

    for tfidf_w, bert_w in weights_to_test:
        print(f"\n{'='*80}")
        print(f"  CONFIGURATION: TF-IDF={tfidf_w:.0%} / BERT={bert_w:.0%}")
        print(f"{'='*80}")

        hybrid = HybridRecommender(recipes, tfidf_weight=tfidf_w, bert_weight=bert_w)

        start = time.time()
        hybrid.fit()
        fit_time = time.time() - start

        start = time.time()
        hybrid_recs = hybrid.recommend(liked, n=10)
        rec_time = time.time() - start

        # Chevauchements
        overlap_tfidf = calculate_overlap(tfidf_recs, hybrid_recs)
        overlap_bert = calculate_overlap(bert_recs, hybrid_recs)

        # Affichage
        print(f"\nPerformance:")
        print(f"  Fit: {fit_time:.3f}s | Recommend: {rec_time:.4f}s")

        print(f"\nChevauchement avec baseline:")
        print(f"  TF-IDF: {overlap_tfidf}/10 ({overlap_tfidf*10}%)")
        print(f"  BERT:   {overlap_bert}/10 ({overlap_bert*10}%)")

        print(f"\nTOP 10 RECOMMANDATIONS:")
        for i, r in enumerate(hybrid_recs, 1):
            # Identifier origine
            in_tfidf = r in tfidf_recs[:10]
            in_bert = r in bert_recs[:10]

            if in_tfidf and in_bert:
                source = "[TF-IDF+BERT]"
            elif in_tfidf:
                source = "[TF-IDF]     "
            elif in_bert:
                source = "[BERT]       "
            else:
                source = "[NOUVEAU]    "

            print(f"  {i:2d}. {source} {r.name}")

        # Stocker resultats
        results.append(
            {
                "tfidf_w": tfidf_w,
                "bert_w": bert_w,
                "overlap_tfidf": overlap_tfidf,
                "overlap_bert": overlap_bert,
                "balance_score": abs(overlap_tfidf - overlap_bert),
                "fit_time": fit_time,
                "rec_time": rec_time,
                "recs": hybrid_recs,
            }
        )

    # Analyse comparative
    print_header("ANALYSE COMPARATIVE")

    print(
        f"\n{'Config':<15} {'TF-IDF':<10} {'BERT':<10} {'Balance':<10} {'Fit(s)':<10} {'Rec(s)':<10}"
    )
    print("-" * 80)

    for r in results:
        config = f"{r['tfidf_w']:.0%}/{r['bert_w']:.0%}"
        balance = r["balance_score"]
        print(
            f"{config:<15} {r['overlap_tfidf']:>9} {r['overlap_bert']:>9} {balance:>9} {r['fit_time']:>9.3f} {r['rec_time']:>9.4f}"
        )

    # Meilleure configuration
    best_balance = min(results, key=lambda x: x["balance_score"])
    best_diversity = min(results, key=lambda x: max(x["overlap_tfidf"], x["overlap_bert"]))

    print_header("RECOMMANDATIONS")

    print(f"\n1. MEILLEUR EQUILIBRE (balance TF-IDF/BERT):")
    print(
        f"   Configuration: {best_balance['tfidf_w']:.0%} TF-IDF / {best_balance['bert_w']:.0%} BERT"
    )
    print(f"   Balance score: {best_balance['balance_score']}")
    print(
        f"   Chevauchement: TF-IDF={best_balance['overlap_tfidf']}, BERT={best_balance['overlap_bert']}"
    )

    print(f"\n2. MEILLEURE DIVERSITE:")
    print(
        f"   Configuration: {best_diversity['tfidf_w']:.0%} TF-IDF / {best_diversity['bert_w']:.0%} BERT"
    )
    print(f"   Max overlap: {max(best_diversity['overlap_tfidf'], best_diversity['overlap_bert'])}")

    print(f"\n3. RECOMMANDATION PRODUCTION:")
    if best_balance["balance_score"] <= 2:
        print(f"   Utiliser: {best_balance['tfidf_w']:.0%}/{best_balance['bert_w']:.0%}")
        print(f"   Raison: Equilibre parfait entre precision et semantique")
    else:
        print(f"   Utiliser: 50%/50%")
        print(f"   Raison: Equilibre standard, bonne diversite")

    print("\n" + "=" * 80)
    print("CONCLUSION:")
    print("-" * 80)
    print("• 80/20 ou 70/30: Trop proche de TF-IDF pur")
    print("• 50/50: Equilibre ideal, diversite maximale")
    print("• 30/70 ou 20/80: Favorise semantique BERT")
    print("\nChoix depend du use case:")
    print("  - Precision mots-cles → 60/40 ou 70/30")
    print("  - Decouverte semantique → 40/60 ou 30/70")
    print("  - Equilibre optimal → 50/50")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
