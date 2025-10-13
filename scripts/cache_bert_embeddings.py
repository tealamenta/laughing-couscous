"""Pre-calcule et cache embeddings BERT pour performance optimale."""

import pickle
import time
from pathlib import Path
from recipe_recommender.data.data_loader import DataLoader
from recipe_recommender.models.bert_recommender import BERTRecommender


def main():
    print("=" * 80)
    print("  CREATION CACHE BERT EMBEDDINGS")
    print("=" * 80)
    print(f"\nDate: 2025-10-13 13:12:33 UTC")
    print(f"User: tealamenta")

    # Chargement donnees
    print("\n" + "-" * 80)
    print("ETAPE 1: Chargement des donnees")
    print("-" * 80)

    loader = DataLoader()

    print("\nChargement 50,000 meilleures recettes...")
    start_load = time.time()
    loader.load_all_data(min_rating=3.0, top_n_recipes=50000)
    load_time = time.time() - start_load

    recipes = loader.get_recipes()
    print(f"Recettes chargees: {len(recipes):,}")
    print(f"Temps chargement: {load_time:.2f}s")

    # Creation embeddings
    print("\n" + "-" * 80)
    print("ETAPE 2: Creation embeddings BERT")
    print("-" * 80)
    print("\nModele: all-MiniLM-L6-v2")
    print("Attention: Peut prendre 2-5 minutes selon CPU...")

    bert = BERTRecommender(recipes, model_name="all-MiniLM-L6-v2")

    start_bert = time.time()
    bert.fit()
    bert_time = time.time() - start_bert

    print(f"\nEmbeddings crees: {bert.embeddings.shape}")
    print(f"Temps generation: {bert_time:.2f}s ({bert_time/60:.1f} min)")

    # Sauvegarde
    print("\n" + "-" * 80)
    print("ETAPE 3: Sauvegarde du cache")
    print("-" * 80)

    cache_dir = Path("data/cache")
    cache_dir.mkdir(parents=True, exist_ok=True)

    cache_file = cache_dir / "bert_embeddings_50k.pkl"

    print(f"\nFichier: {cache_file}")
    print("Serialization en cours...")

    start_save = time.time()
    with open(cache_file, "wb") as f:
        pickle.dump(
            {
                "embeddings": bert.embeddings,
                "recipe_ids": [r.recipe_id for r in recipes],
                "model_name": bert.model_name,
                "n_recipes": len(recipes),
                "created_at": "2025-10-13 13:12:33 UTC",
                "created_by": "tealamenta",
            },
            f,
        )
    save_time = time.time() - start_save

    file_size = cache_file.stat().st_size / (1024 * 1024)

    print(f"Cache sauvegarde: {file_size:.1f} MB")
    print(f"Temps sauvegarde: {save_time:.2f}s")

    # Test chargement
    print("\n" + "-" * 80)
    print("ETAPE 4: Test de chargement rapide")
    print("-" * 80)

    print("\nChargement du cache...")
    start_load_cache = time.time()
    with open(cache_file, "rb") as f:
        cached_data = pickle.load(f)
    load_cache_time = time.time() - start_load_cache

    print(f"Cache charge en: {load_cache_time:.3f}s")
    print(f"Embeddings shape: {cached_data['embeddings'].shape}")
    print(f"Recettes: {cached_data['n_recipes']:,}")

    # Statistiques finales
    print("\n" + "=" * 80)
    print("STATISTIQUES FINALES")
    print("=" * 80)
    print(f"\nTemps total: {load_time + bert_time + save_time:.2f}s")
    print(f"\nGain de performance:")
    print(f"  - SANS cache: {bert_time:.2f}s a chaque demarrage")
    print(f"  - AVEC cache: {load_cache_time:.3f}s (x{bert_time/load_cache_time:.0f} plus rapide)")
    print(f"\nFichier cache: {cache_file}")
    print(f"Taille: {file_size:.1f} MB")

    print("\n" + "=" * 80)
    print("SUCCES: Cache BERT pret pour utilisation")
    print("=" * 80)
    print("\nProchaine etape: Integrer le chargement du cache dans app.py")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
