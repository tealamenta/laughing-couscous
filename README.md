# Recipe Recommender

![CI Status](https://github.com/tealamenta/recipe-recommender/workflows/CI%20-%20Tests%20%26%20Quality/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
![Code Grade](https://img.shields.io/badge/complexity-A%20(3.27)-brightgreen.svg)
![Tests](https://img.shields.io/badge/tests-101%20passing-success.svg)
![Coverage](https://img.shields.io/badge/coverage-41%25-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## Présentation

Recipe Recommender est une application web qui propose des recettes personnalisées selon vos goûts, vos ingrédients disponibles et vos restrictions alimentaires.

Cette app combine des filtres avancés, des visualisations nutritionnelles interactives, un système de favoris et un moteur de recommandation basé sur l’apprentissage automatique.

---

## Démo

- Démo en ligne : [https://recipe-recommender-tealamenta.streamlit.app](https://recipe-recommender-tealamenta.streamlit.app)

---

## Fonctionnalités

- Recherche avancée : filtrage par ingrédients, cuisine, régimes alimentaires, calories, temps de cuisson
- Visualisation nutritionnelle : graphiques interactifs (Plotly) des macronutriments et des profils nutritionnels
- Système de favoris : sauvegarde et gestion des recettes préférées (user_favorites.json)
- Recommandations personnalisées : suggestions basées sur vos préférences et historiques
- Dashboard utilisateur : suivi des favoris et des découvertes
- CI/CD complet : tests, lint, build Docker, déploiement Streamlit Cloud via GitHub Actions

---

## Stack technique

- Python 3.12
- Streamlit 1.50.0
- Plotly 6.3.1
- Pandas 2.3.3
- Scikit-learn 1.6.1
- Poetry (gestion des dépendances)
- Docker (déploiement)
- GitHub Actions (.github/workflows)

---

## Structure du projet

```
recipe-recommender/
├── data/
│   ├── cache/
│   │   └── bert_embeddings_50k.pkl
│   ├── RAW_recipes.csv
│   ├── RAW_interactions.csv
│   ├── PP_recipes.csv
│   ├── PP_users.csv
│   ├── interactions_train.csv
├── docker-build.sh
├── docker-compose.yml
├── docker-run.sh
├── docker-stop.sh
├── Dockerfile
├── Dockerfile.test
├── docs/
├── notebooks/
│   ├── analyze_data.ipynb
│   ├── eda_bivariate.ipynb
│   ├── eda_categorical.ipynb
│   ├── eda_complexity.ipynb
│   ├── eda_nutrition_profiles.ipynb
│   ├── eda_temporal.ipynb
│   ├── eda_text_analysis.ipynb
│   └── eda_topic_modeling.ipynb
├── poetry.lock
├── pyproject.toml
├── README.md
├── ruff.toml
├── scripts/
│   ├── cache_bert_embeddings.py
│   ├── compare_all_recommenders.py
│   ├── compare_recommenders.py
│   └── test_hybrid_weights.py
├── setup-cicd.sh
├── src/
│   └── recipe_recommender/
│       ├── __init__.py
│       ├── app.py
│       ├── config.py
│       ├── data/
│       │   ├── __init__.py
│       │   └── data_loader.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── bert_recommender.py
│       │   ├── hybrid_recommender.py
│       │   ├── recipe.py
│       │   └── recommender.py
│       └── utils/
│           ├── __init__.py
│           ├── cache_manager.py
│           ├── favorites.py
│           ├── filters.py
│           ├── logger.py
│           ├── nutrition_filters.py
│           └── nutrition.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_app_integration.py
│   ├── test_cache_manager.py
│   ├── test_config.py
│   ├── test_favorites.py
│   ├── test_filters.py
│   ├── test_hybrid_recommender.py
│   ├── test_logger.py
│   ├── test_nutrition_extended.py.skip
│   ├── test_nutrition_filters.py
│   ├── test_nutrition.py.skip
│   ├── test_recipe.py
│   ├── test_recommender.py
│   └── test_tabs_handler.py
└── user_favorites.json
```

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/tealamenta/recipe-recommender.git
cd recipe-recommender
```

### 2. Installer les dépendances

```bash
poetry install
```

### 3. Lancer l’application

```bash
poetry run streamlit run src/recipe_recommender/app.py
```

### 4.  Utiliser Docker
Pour utiliser Docker avec les scripts fournis :

```bash
./docker-build.sh       # Build l'image Docker
./docker-run.sh         # Lance le conteneur (accès : http://localhost:8501)
./docker-stop.sh        # Stoppe et nettoie le conteneur
```

---

## Tests et qualité

- Tests unitaires : `poetry run pytest tests/`
- Couverture : `poetry run pytest --cov=src/recipe_recommender`
- Lint : `poetry run ruff check src/ tests/`
- Formatage : `poetry run black src/ tests/`
- Complexité : `poetry run radon cc src/recipe_recommender/ -a`

---

## CI/CD

- CI : tests, lint, formatage, complexité, couverture automatisés
- Docker : build et test de l’image à chaque push
- Déploiement : automatique sur Streamlit Cloud à chaque push sur `main`
- Releases : changelog et publication Docker Hub sur tag

---

## Exemples d’utilisation

- Recherche par ingrédient : saisissez un ingrédient pour afficher les recettes associées.
- Ajout aux favoris : cliquez sur l’icône étoile pour sauvegarder une recette.
- Visualisation nutritionnelle : consultez le radar nutritionnel et le graphique des calories.
».

---

## FAQ

**Quels formats de données sont supportés ?**  
Le projet utilise des fichiers CSV pour les recettes et interactions.

**Comment déployer sur Streamlit Cloud ?**  
Poussez sur la branche `main`, le déploiement est automatique.

**Comment ajouter un nouvel algorithme de recommandation ?**  
Ajoutez votre modèle dans `src/recipe_recommender/models/recommender.py`.


---

## Licence

Projet sous licence MIT.

---

## Remerciements

Projet maintenu par [@tealamenta](https://github.com/tealamenta)