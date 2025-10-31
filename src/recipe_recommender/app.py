"""
Application Streamlit pour le systeme de recommandation de recettes.

Cette application web permet aux utilisateurs de rechercher des recettes,
les filtrer selon differents criteres, et recevoir des recommandations
personnalisees basees sur leurs preferences.

Version 2: Utilise l'algorithme Hybrid (TF-IDF + BERT)
"""

import os
import sys
import pickle

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
from dotenv import load_dotenv

from recipe_recommender.data.data_loader import DataLoader, DataLoadError
from recipe_recommender.models.hybrid_recommender import HybridRecommender
from recipe_recommender.models.recipe import Recipe
from recipe_recommender.utils.favorites import FavoritesManager
from recipe_recommender.utils.filters import filter_recipes, search_by_name
from recipe_recommender.utils.logger import get_logger
from recipe_recommender.utils.nutrition import plot_nutrition_pie

# Charger les variables d'environnement
load_dotenv()

# Configuration du logger
logger = get_logger(__name__)

# Liste des origines ethniques pour les filtres
ETHNICITY_LIST = [
    "African",
    "American",
    "Asian",
    "British",
    "Caribbean",
    "Chinese",
    "Eastern European",
    "French",
    "Greek",
    "Indian",
    "Italian",
    "Japanese",
    "Korean",
    "Latin American",
    "Mediterranean",
    "Mexican",
    "Middle Eastern",
    "Moroccan",
    "Portuguese",
    "Southern",
    "Spanish",
    "Thai",
    "Vietnamese",
]

# Liste des régimes alimentaires pour les filtres
DIETARY_LIST = [
    "Végétarien",
    "Végétalien",
    "Sans gluten",
    "Sans lactose",
    "Paléo",
    "Cétogène",
    "Faible en calories",
    "Riche en protéines",
    "Faible en glucides",
    "Sans sucre ajouté",
]





# Configuration de la page Streamlit


def plot_calories_gauge(calories: float):
    """Crée un graphique de jauge pour les calories."""
    import plotly.graph_objects as go

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=calories,
            delta={"reference": 500, "increasing": {"color": "red"}},
            gauge={
                "axis": {"range": [None, 1000], "tickwidth": 1},
                "bar": {"color": "#FF8C42"},
                "steps": [
                    {"range": [0, 300], "color": "#E8F5E9"},
                    {"range": [300, 600], "color": "#FFF9C4"},
                    {"range": [600, 1000], "color": "#FFEBEE"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 500,
                },
            },
            title={"text": "kcal", "font": {"size": 20}},
            number={"suffix": " kcal", "font": {"size": 32}},
        )
    )

    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def plot_nutrition_radar(vq_data: dict):
    """Crée un radar chart du profil nutritionnel."""
    import plotly.graph_objects as go

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=list(vq_data.values()),
            theta=list(vq_data.keys()),
            fill="toself",
            fillcolor="rgba(76, 175, 80, 0.3)",
            line=dict(color="#4CAF50", width=2),
            marker=dict(size=8, color="#4CAF50"),
            name="% VQ",
        )
    )

    # Zones de référence
    for pct, color, name in [
        (20, "green", "Seuil 20% (Faible)"),
        (50, "orange", "Seuil 50% (Modéré)"),
        (100, "red", "100% VQ"),
    ]:
        fig.add_trace(
            go.Scatterpolar(
                r=[pct] * len(vq_data),
                theta=list(vq_data.keys()),
                line=dict(
                    color=color,
                    dash="dash" if pct < 100 else "dot",
                    width=1 if pct < 100 else 2,
                ),
                showlegend=True,
                name=name,
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, max(max(vq_data.values()), 100) * 1.2]
            )
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        height=450,
        margin=dict(l=80, r=80, t=40, b=80),
    )
    return fig


def plot_nutrition_bars(all_vq: dict):
    """Crée un graphique de barres horizontales colorées pour %VQ."""
    import plotly.graph_objects as go

    names = list(all_vq.keys())
    pcts = list(all_vq.values())

    # Couleurs dynamiques
    colors = ["#4CAF50" if p < 20 else "#FFC107" if p < 50 else "#F44336" for p in pcts]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=pcts,
            y=names,
            orientation="h",
            marker=dict(color=colors, line=dict(color="rgba(0,0,0,0.3)", width=1.5)),
            text=[f"{p:.0f}%" for p in pcts],
            textposition="auto",
            textfont=dict(size=13, color="white", family="Arial Black"),
            hovertemplate="<b>%{y}</b><br>%{x:.1f}% VQ<br><extra></extra>",
        )
    )

    # Zones colorées
    fig.add_vrect(x0=0, x1=20, fillcolor="green", opacity=0.1, line_width=0)
    fig.add_vrect(x0=20, x1=50, fillcolor="yellow", opacity=0.1, line_width=0)
    fig.add_vrect(
        x0=50, x1=max(max(pcts), 100) * 1.2, fillcolor="red", opacity=0.1, line_width=0
    )

    # Ligne 100%
    fig.add_vline(
        x=100,
        line_dash="dash",
        line_color="black",
        line_width=2,
        annotation_text="100% VQ",
        annotation_position="top",
    )

    fig.update_layout(
        height=350,
        margin=dict(l=0, r=30, t=10, b=40),
        xaxis_title="Pourcentage de la Valeur Quotidienne (%)",
        xaxis=dict(
            range=[0, max(max(pcts), 100) * 1.2],
            ticksuffix="%",
            gridcolor="rgba(200,200,200,0.3)",
        ),
        yaxis_title="",
        showlegend=False,
        plot_bgcolor="rgba(255,255,255,0.9)",
        font=dict(size=12),
    )
    return fig


def display_recipe_nutrition(recipe):
    """Affiche informations nutritionnelles 100% graphique."""
    if not recipe.nutrition or len(recipe.nutrition) < 7:
        st.warning(" Informations nutritionnelles non disponibles")
        return

    # Extraction des données
    calories = recipe.nutrition[0]
    total_fat_pdv = recipe.nutrition[1]
    sugar_pdv = recipe.nutrition[2]
    sodium_pdv = recipe.nutrition[3]
    protein_pdv = recipe.nutrition[4]
    sat_fat_pdv = recipe.nutrition[5]
    carbs_pdv = recipe.nutrition[6]
    calories_pdv = (calories / 2000) * 100

    # === SECTION 1: PIE + GAUGE ===
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("** Répartition macronutriments**")
        fig_pie = plot_nutrition_pie(recipe.nutrition)
        if fig_pie:
            st.pyplot(fig_pie)

    with col2:
        st.markdown("** Calories**")
        fig_gauge = plot_calories_gauge(calories)
        st.plotly_chart(fig_gauge, use_container_width=True)

    # === SECTION 2: RADAR CHART ===
    st.markdown("###  Profil nutritionnel")

    vq_data = {
        "Lipides<br>totaux": total_fat_pdv,
        "Graisses<br>saturées": sat_fat_pdv,
        "Sodium": sodium_pdv,
        "Glucides": carbs_pdv,
        "Sucres": sugar_pdv,
        "Protéines": protein_pdv,
    }

    fig_radar = plot_nutrition_radar(vq_data)
    st.plotly_chart(fig_radar, use_container_width=True)

    # === SECTION 3: BARRES HORIZONTALES ===
    st.markdown("###  % Valeur Quotidienne détaillé")

    all_vq = {
        "Calories": calories_pdv,
        "Lipides totaux": total_fat_pdv,
        "Graisses saturées": sat_fat_pdv,
        "Sodium": sodium_pdv,
        "Glucides": carbs_pdv,
        "Sucres": sugar_pdv,
        "Protéines": protein_pdv,
    }

    fig_bars = plot_nutrition_bars(all_vq)
    st.plotly_chart(fig_bars, use_container_width=True)

    # === LÉGENDE ===
    col_leg1, col_leg2, col_leg3 = st.columns(3)
    with col_leg1:
        st.markdown("🟢 **<20%** : Faible")
    with col_leg2:
        st.markdown("🟡 **20-50%** : Modéré")
    with col_leg3:
        st.markdown(" **>50%** : Élevé")

    st.caption(" Valeurs basées sur un régime de 2000 calories/jour (FDA)")


def load_data(data_path: str) -> tuple:
    """
    Charge les donnees et initialise le recommender (avec cache).

    Args:
        data_path: Chemin vers le dossier de donnees.

    Returns:
        tuple: (recipes, ingredient_list, recommender)

    Raises:
        DataLoadError: Si le chargement echoue.
    """
    logger.info("Chargement des donnees depuis %s", data_path)

    try:
        loader = DataLoader(data_path=data_path)
        loader.load_all_data(min_rating=3.0, top_n_recipes=50000)

        recipes = loader.get_recipes()
        ingredients = loader.get_ingredients()

        # Initialiser et entrainer le recommender Hybrid
        # Initialiser le recommender avec cache BERT optimisé
        logger.info("Initialisation Hybrid Recommender (70% TF-IDF + 30% BERT)...")
        recommender = HybridRecommender(recipes, tfidf_weight=0.7, bert_weight=0.3)

        # Charger le cache BERT avant fit() pour optimiser
        cache_file = os.path.join(data_path, "cache", "bert_embeddings_50k.pkl")
        if os.path.exists(cache_file):
            logger.info(" Cache BERT trouvé: %s", cache_file)
            try:
                with open(cache_file, "rb") as f:
                    cache_data = pickle.load(f)
                # Charger le cache dans le BERTRecommender
                recommender.bert_recommender.load_from_cache(cache_data)
                # Entraîner seulement TF-IDF (rapide)
                recommender.tfidf_recommender.fit()
                logger.info(" Modèle hybride chargé depuis le cache (rapide)")
            except Exception as e:
                logger.warning(" Erreur cache: %s. Chargement normal...", str(e))
                recommender.fit()
        else:
            logger.info(" Pas de cache. Chargement complet du modèle...")
            recommender.fit()

        logger.info(
            "Donnees chargees: %s recettes, %s ingredients",
            len(recipes),
            len(ingredients),
        )
        return recipes, ingredients, recommender

    except Exception as e:
        logger.error("Erreur lors du chargement: %s", str(e))
        raise


def display_recipe(recipe: Recipe, key_prefix: str = "") -> None:
    """
    Affiche une recette dans un expander Streamlit.

    Args:
        recipe: Objet Recipe a afficher.
        key_prefix: Prefixe pour les cles des widgets (pour eviter les doublons).
    """
    is_liked = recipe.recipe_id in st.session_state.liked

    # Titre avec indicateur de favori
    title = f"{recipe.name}"
    if is_liked:
        title = f"[FAVORI] {recipe.name}"

    with st.expander(title):
        # Informations de base
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Temps", f"{recipe.minutes} min")
        with col2:
            st.metric("Ingredients", recipe.n_ingredients)
        with col3:
            st.metric("Etapes", recipe.n_steps)

        # Description
        st.write("**Description:**")
        st.write(recipe.description)

        # Ingredients
        st.write("**Ingredients:**")
        ingredients_str = ", ".join(recipe.ingredients)
        st.write(ingredients_str)

        # Etapes
        st.write("**Instructions:**")
        for i, step in enumerate(recipe.steps, 1):
            st.write(f"{i}. {step}")

        # Nutrition
        with st.expander(" Informations nutritionnelles", expanded=True):
            display_recipe_nutrition(recipe)

        # Boutons Like/Unlike
        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if not is_liked:
                if st.button(
                    "J'aime cette recette",
                    key=f"{key_prefix}_like_{recipe.recipe_id}",
                    use_container_width=True,
                ):
                    st.session_state.liked = (
                        st.session_state.favorites_manager.add_favorite(
                            recipe.recipe_id, st.session_state.liked
                        )
                    )
                    logger.info("Recette likee: %s - %s", recipe.recipe_id, recipe.name)
                    st.session_state.show_success_message = True
                    st.session_state.last_liked_recipe = recipe.name
                    st.rerun()
            else:
                st.success("Deja dans vos favoris")

        with col_btn2:
            if is_liked:
                if st.button(
                    "Retirer des favoris",
                    key=f"{key_prefix}_unlike_{recipe.recipe_id}",
                    use_container_width=True,
                ):
                    st.session_state.liked = (
                        st.session_state.favorites_manager.remove_favorite(
                            recipe.recipe_id, st.session_state.liked
                        )
                    )
                    logger.info(
                        "Recette retiree des favoris: %s - %s",
                        recipe.recipe_id,
                        recipe.name,
                    )
                    st.session_state.show_info_message = True
                    st.rerun()


def render_search_filters(ingredient_list):
    """Affiche les filtres de recherche et retourne les valeurs selectionnees."""
    search_query = st.text_input(
        "Rechercher par nom ou description",
        placeholder="Ex: chocolate cake, pasta carbonara...",
        help="Recherchez une recette par son nom ou sa description",
    )

    with st.expander("Filtres avances", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            selected_ingredients = st.multiselect(
                "Ingredients requis",
                options=ingredient_list,
                help="Selectionnez les ingredients que vous avez",
            )

            selected_ethnicity = st.selectbox(
                "Origine ethnique",
                options=["Toutes"] + sorted(ETHNICITY_LIST),
                help="Filtrer par origine culinaire",
            )

            selected_dietary = st.multiselect(
                "Restrictions alimentaires",
                options=DIETARY_LIST,
                help="Selectionnez vos restrictions alimentaires",
            )

        with col2:
            max_time = st.slider(
                "Temps maximum (minutes)",
                min_value=0,
                max_value=500,
                value=120,
                step=10,
                help="Temps de preparation maximum",
            )

            cal_range = st.slider(
                "Calories",
                min_value=0,
                max_value=2000,
                value=(0, 1000),
                step=50,
                help="Plage de calories souhaitee",
            )

    return {
        "search_query": search_query,
        "selected_ingredients": selected_ingredients,
        "selected_ethnicity": selected_ethnicity,
        "selected_dietary": selected_dietary,
        "max_time": max_time,
        "cal_range": cal_range,
    }


def display_search_results(filtered_recipes) -> None:
    """Affiche les resultats de recherche."""
    if not filtered_recipes:
        st.warning(
            "Aucune recette ne correspond a vos criteres. Essayez d'elargir vos filtres."
        )
        logger.info("Aucun resultat trouve")
    else:
        st.success(f"{len(filtered_recipes)} recette(s) trouvee(s)")
        logger.info("%s resultats trouves", len(filtered_recipes))

        # Limiter l'affichage a 20 recettes
        for recipe in filtered_recipes[:20]:
            display_recipe(recipe, key_prefix="search")

        if len(filtered_recipes) > 20:
            st.info(
                f"{len(filtered_recipes) - 20} recettes supplementaires disponibles. "
                "Affinez vos filtres pour voir plus de resultats."
            )


def handle_search_tab(recipes, ingredient_list, recommender) -> None:
    """Gere l'onglet de recherche de recettes."""
    st.header("Recherche de Recettes")

    # Afficher les filtres et recuperer les valeurs
    filters = render_search_filters(ingredient_list)

    # Bouton de recherche
    if st.button("Rechercher", type="primary"):
        logger.info(
            "Recherche lancee - Query: '%s', Ingredients: %s, Dietary: %s, "
            "Ethnicity: %s, Max time: %s, Calories: %s",
            filters["search_query"],
            len(filters["selected_ingredients"]),
            filters["selected_dietary"],
            filters["selected_ethnicity"],
            filters["max_time"],
            filters["cal_range"],
        )

        # Appliquer les filtres
        filtered_recipes = recipes.copy()

        # Recherche textuelle
        if filters["search_query"]:
            filtered_recipes = search_by_name(filtered_recipes, filters["search_query"])

        # Preparer les tags
        tags = filters["selected_dietary"].copy() if filters["selected_dietary"] else []
        if filters["selected_ethnicity"] and filters["selected_ethnicity"] != "Toutes":
            tags.append(filters["selected_ethnicity"])

        # Filtrer
        filtered_recipes = filter_recipes(
            filtered_recipes,
            ingredients=filters["selected_ingredients"]
            if filters["selected_ingredients"]
            else None,
            tags=tags if tags else None,
            max_minutes=filters["max_time"],
            max_calories=filters["cal_range"][1],
            min_calories=filters["cal_range"][0],
        )

        # Afficher les resultats
        display_search_results(filtered_recipes)


def handle_favorites_tab(recommender, fav_count) -> None:
    """Gere l'onglet des favoris."""
    st.header(f"Mes Recettes Favorites ({fav_count})")

    if not st.session_state.liked:
        st.info(
            "Vous n'avez pas encore de recettes favorites. "
            "Explorez et aimez des recettes pour les retrouver ici !"
        )
        logger.debug("Aucune recette favorite")
    else:
        logger.info("Affichage de %s recettes favorites", len(st.session_state.liked))

        st.success(f"Vous avez {fav_count} recette(s) favorite(s) !")

        for recipe_id in st.session_state.liked:
            recipe = recommender.get_recipe_by_id(recipe_id)
            if recipe:
                display_recipe(recipe, key_prefix="favorites")


def handle_recommendations_tab(recommender, fav_count) -> None:
    """Gere l'onglet des recommandations."""
    st.header("Recommandations Personnalisees")

    if not st.session_state.liked:
        st.info(
            "Aimez quelques recettes pour recevoir des recommandations "
            "personnalisees basees sur vos gouts !"
        )
        logger.debug("Pas de recommandations (aucune recette likee)")
    else:
        st.success(f"Base sur vos {fav_count} recette(s) favorite(s)")
        logger.info(
            "Generation de recommandations basees sur %s recettes likees",
            len(st.session_state.liked),
        )

        try:
            # Generer des recommandations
            n_recommendations = st.slider(
                "Nombre de recommandations",
                min_value=5,
                max_value=20,
                value=10,
                help="Nombre de recettes a recommander",
            )

            if st.button("Generer des recommandations", type="primary"):
                with st.spinner("Generation des recommandations..."):
                    recommendations = recommender.recommend(
                        st.session_state.liked,
                        n=n_recommendations,
                        exclude_liked=True,
                    )

                    st.session_state.recommendations = recommendations
                    logger.info("%s recommandations generees", len(recommendations))
                    st.success(f"{len(recommendations)} nouvelles recettes pour vous !")

            # Afficher les recommandations si elles existent
            if "recommendations" in st.session_state:
                st.success(
                    f"Voici {len(st.session_state.recommendations)} recettes "
                    "que vous pourriez aimer :"
                )

                for recipe in st.session_state.recommendations:
                    display_recipe(recipe, key_prefix="recommend")

        except Exception as e:
            logger.error("Erreur lors de la generation des recommandations: %s", str(e))
            st.error("Erreur lors de la generation des recommandations")


def main() -> None:
    """Point d'entree principal de l'application."""
    logger.info("Demarrage de l'application Recipe Recommender")

    # Initialiser le gestionnaire de favoris
    if "favorites_manager" not in st.session_state:
        st.session_state.favorites_manager = FavoritesManager()
        logger.debug("FavoritesManager initialise")

    # Initialiser le session state avec les favoris sauvegardes
    if "liked" not in st.session_state:
        st.session_state.liked = st.session_state.favorites_manager.load_favorites()
        logger.info(
            "Session state initialise avec %s favoris", len(st.session_state.liked)
        )

    # Initialiser les flags de messages
    if "show_success_message" not in st.session_state:
        st.session_state.show_success_message = False
    if "show_info_message" not in st.session_state:
        st.session_state.show_info_message = False
    if "last_liked_recipe" not in st.session_state:
        st.session_state.last_liked_recipe = ""

    # Charger les donnees
    data_path = os.getenv("DATA_PATH", "./data")

    # Initialize variables with defaults to prevent UnboundLocalError
    recipes = []
    ingredient_list = []
    recommender = None

    try:
        recipes, ingredient_list, recommender = load_data(data_path)
    except Exception as e:
        logger.critical("Impossible de charger les donnees: %s", str(e))
        st.error("Erreur de chargement des donnees")
        st.error(
            f"Verifiez que les fichiers CSV sont presents dans `{data_path}/`\n\n"
            "Telechargez le dataset depuis: "
            "[Kaggle - Food.com Recipes](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions)"
        )
        try:
            st.stop()
        except (SystemExit, Exception):
            pass  # Dans les tests, st.stop() peut lever SystemExit
        return  

    # Titre principal
    st.title("Recipe Recommender")
    st.markdown(
        "*Trouvez la recette parfaite selon vos preferences et restrictions alimentaires*"
    )

    # Afficher les messages de notification
    if st.session_state.show_success_message:
        st.success(
            f"Recette '{st.session_state.last_liked_recipe}' ajoutee a vos favoris ! Consultez l'onglet 'Mes Favoris' pour la retrouver."
        )
        st.session_state.show_success_message = False

    if st.session_state.show_info_message:
        st.info("Recette retiree de vos favoris.")
        st.session_state.show_info_message = False

    # Sidebar - Statistiques
    st.sidebar.title("Statistiques")
    #st.sidebar.metric("Total de recettes", f"{len(recipes):,}")
    st.sidebar.metric("Ingredients disponibles", f"{len(ingredient_list):,}")

    # Badge dynamique pour les favoris
    fav_count = len(st.session_state.liked)
    st.sidebar.metric("Recettes favorites", fav_count)

    if fav_count > 0:
        st.sidebar.success(f"Vous avez {fav_count} recette(s) favorite(s) !")
        st.sidebar.info("Consultez l'onglet 'Mes Favoris' pour les voir")

    # Tabs principales avec badges
    tab1, tab2, tab3 = st.tabs(
        ["Rechercher", f"Mes Favoris ({fav_count})", "Recommandations"]
    )

    # ==================== TAB 1: RECHERCHE ====================
    with tab1:
        handle_search_tab(recipes, ingredient_list, recommender)
    with tab2:
        handle_favorites_tab(recommender, fav_count)
    # ==================== TAB 3: RECOMMANDATIONS ====================
    with tab3:
        handle_recommendations_tab(recommender, fav_count)
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center'>
            <p>Made with love by <a href='https://github.com/tealamenta'>tealamenta</a> |
            Data from <a href='https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions'>Kaggle Food.com</a></p>
            <p style='font-size: 0.8em; color: gray;'>Session: {fav_count} favoris | Algorithme: Hybrid (TF-IDF + BERT)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    logger.debug("Rendu de la page termine")


if __name__ == "__main__":
    main()
