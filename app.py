"""
Point d'entrée Streamlit pour le déploiement cloud.
Délègue vers l'application principale dans src/recipe_recommender/
"""
import sys
import os

# Ajouter src/ au Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Importer et exécuter l'application principale
from recipe_recommender.app import main

if __name__ == "__main__":
    main()
