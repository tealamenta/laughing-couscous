"""
Application Streamlit pour le système de recommandation de recettes.

Cette application web permet aux utilisateurs de rechercher des recettes,
les filtrer selon différents critères, et recevoir des recommandations
personnalisées basées sur leurs préférences.
"""

import os
from typing import List, Optional

import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv

from recipe_recommender.data.data_loader import DataLoadError, DataLoader
from recipe_recommender.models.recipe import Recipe
from recipe_recommender.models.recommender import RecipeRecommender
from recipe_recommender.utils.favorites import FavoritesManager
from recipe_recommender.utils.filters import filter_recipes, search_by_name
from recipe_recommender.utils.logger import get_logger
from recipe_recommender.utils.nutrition import format_nutrition, plot_nutrition_pie

# Charger les variables d'environnement
load_dotenv()

# Configuration du logger
logger = get_logger(__name__)

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Recipe Recommender",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Listes de référence
ETHNICITY_LIST = [
    "spanish",
    "egyptian",
    "tex-mex",
    "welsh",
    "australian",
    "polynesian",
    "pacific-northwest",
    "swiss",
    "italian",
    "german",
    "sudanese",
    "chilean",
    "costa-rican",
    "hawaiian",
    "malaysian",
    "icelandic",
    "norwegian",
    "pennsylvania-dutch",
    "somalian",
    "pakistani",
    "nepalese",
    "venezuelan",
    "asian",
    "puerto-rican",
    "nigerian",
    "ethiopian",
    "vietnamese",
    "hungarian",
    "laotian",
    "dutch",
    "chinese",
    "south-african",
    "brazilian",
    "austrian",
    "greek",
    "middle-eastern",
    "iraqi",
    "ecuadorean",
    "creole",
    "african",
    "korean",
    "cambodian",
    "caribbean",
    "thai",
    "indonesian",
    "south-american",
    "midwestern",
    "north-american",
    "mongolian",
    "libyan",
    "new-zealand",
    "russian",
    "congolese",
    "japanese",
    "mexican",
    "indian",
    "british",
    "french",
    "scandinavian",
    "irish",
    "filipino",
    "moroccan",
    "lebanese",
    "turkish",
    "portuguese",
    "cuban",
    "jamaican",
    "peruvian",
    "colombian",
    "argentine",
    "scottish",
]

DIETARY_LIST = [
    "vegetarian",
    "vegan",
    "gluten-free",
    "dairy-free",
    "low-carb",
    "low-fat",
    "low-sodium",
    "low-calorie",
    "keto",
    "paleo",
    "nut-free",
    "egg-free",
    "soy-free",
    "pescatarian",
    "kosher",
    "halal",
]


@st.cache_resource
def load_data(data_path: str) -> tuple:
    """
    Charge les données et initialise le recommender (avec cache).

    Args:
        data_path: Chemin vers le dossier de données.

    Returns:
        tuple: (recipes, ingredient_list, recommender)

    Raises:
        DataLoadError: Si le chargement échoue.
    """
    logger.info(f"Chargement des données depuis {data_path}")

    try:
        loader = DataLoader(data_path=data_path)
        loader.load_all_data(min_rating=3.0, top_n_recipes=50000)

        recipes = loader.get_recipes()
        ingredients = loader.get_ingredients()

        # Initialiser et entraîner le recommender
        recommender = RecipeRecommender(recipes)
        recommender.fit()

        logger.info(
            f"Données chargées: {len(recipes)} recettes, {len(ingredients)} ingrédients"
        )
        return recipes, ingredients, recommender

    except Exception as e:
        logger.error(f"Erreur lors du chargement: {str(e)}")
        raise


def display_recipe(recipe: Recipe, key_prefix: str = "") -> None:
    """
    Affiche une recette dans un expander Streamlit.

    Args:
        recipe: Objet Recipe à afficher.
        key_prefix: Préfixe pour les clés des widgets (pour éviter les doublons).
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

        # Ingrédients
        st.write("**Ingredients:**")
        ingredients_str = ", ".join(recipe.ingredients)
        st.write(ingredients_str)

        # Étapes
        st.write("**Instructions:**")
        for i, step in enumerate(recipe.steps, 1):
            st.write(f"{i}. {step}")

        # Nutrition
        st.write("**Informations nutritionnelles:**")
        col_nut1, col_nut2 = st.columns([1, 1])

        with col_nut1:
            st.markdown(format_nutrition(recipe.nutrition))

        with col_nut2:
            fig = plot_nutrition_pie(recipe.nutrition)
            if fig:
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.warning("Impossible de generer le graphique nutritionnel")

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
                    logger.info(f"Recette likee: {recipe.recipe_id} - {recipe.name}")
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
                        f"Recette retiree des favoris: {recipe.recipe_id} - {recipe.name}"
                    )
                    st.session_state.show_info_message = True
                    st.rerun()


def main() -> None:
    """Point d'entrée principal de l'application."""
    logger.info("Demarrage de l'application Recipe Recommender")

    # Initialiser le gestionnaire de favoris
    if "favorites_manager" not in st.session_state:
        st.session_state.favorites_manager = FavoritesManager()
        logger.debug("FavoritesManager initialise")

    # Initialiser le session state avec les favoris sauvegardés
    if "liked" not in st.session_state:
        st.session_state.liked = st.session_state.favorites_manager.load_favorites()
        logger.info(
            f"Session state initialise avec {len(st.session_state.liked)} favoris"
        )

    # Initialiser les flags de messages
    if "show_success_message" not in st.session_state:
        st.session_state.show_success_message = False
    if "show_info_message" not in st.session_state:
        st.session_state.show_info_message = False
    if "last_liked_recipe" not in st.session_state:
        st.session_state.last_liked_recipe = ""

    # Charger les données
    data_path = os.getenv("DATA_PATH", "./data")

    try:
        recipes, ingredient_list, recommender = load_data(data_path)
    except DataLoadError as e:
        logger.critical(f"Impossible de charger les donnees: {str(e)}")
        st.error("Erreur de chargement des donnees")
        st.error(
            f"Verifiez que les fichiers CSV sont presents dans `{data_path}/`\n\n"
            "Telechargez le dataset depuis: "
            "[Kaggle - Food.com Recipes](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions)"
        )
        st.stop()

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
    st.sidebar.metric("Total de recettes", f"{len(recipes):,}")
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
        st.header("Recherche de Recettes")

        # Recherche par texte
        search_query = st.text_input(
            "Rechercher par nom ou description",
            placeholder="Ex: chocolate cake, pasta carbonara...",
            help="Recherchez une recette par son nom ou sa description",
        )

        # Filtres dans un expander
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

        # Bouton de recherche
        if st.button("Rechercher", type="primary"):
            logger.info(
                f"Recherche lancee - Query: '{search_query}', "
                f"Ingredients: {len(selected_ingredients)}, "
                f"Dietary: {selected_dietary}, "
                f"Ethnicity: {selected_ethnicity}, "
                f"Max time: {max_time}, "
                f"Calories: {cal_range}"
            )

            # Appliquer les filtres
            filtered_recipes = recipes.copy()

            # Recherche textuelle
            if search_query:
                filtered_recipes = search_by_name(filtered_recipes, search_query)

            # Préparer les tags
            tags = selected_dietary.copy() if selected_dietary else []
            if selected_ethnicity and selected_ethnicity != "Toutes":
                tags.append(selected_ethnicity)

            # Filtrer
            filtered_recipes = filter_recipes(
                filtered_recipes,
                ingredients=selected_ingredients if selected_ingredients else None,
                tags=tags if tags else None,
                max_minutes=max_time,
                max_calories=cal_range[1],
                min_calories=cal_range[0],
            )

            # Afficher les résultats
            if not filtered_recipes:
                st.warning(
                    "Aucune recette ne correspond a vos criteres. Essayez d'elargir vos filtres."
                )
                logger.info("Aucun resultat trouve")
            else:
                st.success(f"{len(filtered_recipes)} recette(s) trouvee(s)")
                logger.info(f"{len(filtered_recipes)} resultats trouves")

                # Limiter l'affichage à 20 recettes
                for recipe in filtered_recipes[:20]:
                    display_recipe(recipe, key_prefix="search")

                if len(filtered_recipes) > 20:
                    st.info(
                        f"{len(filtered_recipes) - 20} recettes supplementaires disponibles. Affinez vos filtres pour voir plus de resultats."
                    )

    # ==================== TAB 2: FAVORIS ====================
    with tab2:
        st.header(f"Mes Recettes Favorites ({fav_count})")

        if not st.session_state.liked:
            st.info(
                "Vous n'avez pas encore de recettes favorites. Explorez et aimez des recettes pour les retrouver ici !"
            )
            logger.debug("Aucune recette favorite")
        else:
            logger.info(
                f"Affichage de {len(st.session_state.liked)} recettes favorites"
            )

            st.success(f"Vous avez {fav_count} recette(s) favorite(s) !")

            for recipe_id in st.session_state.liked:
                recipe = recommender.get_recipe_by_id(recipe_id)
                if recipe:
                    display_recipe(recipe, key_prefix="favorites")

    # ==================== TAB 3: RECOMMANDATIONS ====================
    with tab3:
        st.header("Recommandations Personnalisees")

        if not st.session_state.liked:
            st.info(
                "Aimez quelques recettes pour recevoir des recommandations personnalisees basees sur vos gouts !"
            )
            logger.debug("Pas de recommandations (aucune recette likee)")
        else:
            st.success(f"Base sur vos {fav_count} recette(s) favorite(s)")
            logger.info(
                f"Generation de recommandations basees sur {len(st.session_state.liked)} recettes likees"
            )

            try:
                # Générer des recommandations
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
                        logger.info(f"{len(recommendations)} recommandations generees")
                        st.success(
                            f"{len(recommendations)} nouvelles recettes pour vous !"
                        )

                # Afficher les recommandations si elles existent
                if "recommendations" in st.session_state:
                    st.success(
                        f"Voici {len(st.session_state.recommendations)} recettes que vous pourriez aimer :"
                    )

                    for recipe in st.session_state.recommendations:
                        display_recipe(recipe, key_prefix="recommend")

            except Exception as e:
                logger.error(
                    f"Erreur lors de la generation des recommandations: {str(e)}"
                )
                st.error("Erreur lors de la generation des recommandations")

    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center'>
            <p>Made with love by <a href='https://github.com/tealamenta'>tealamenta</a> | 
            Data from <a href='https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions'>Kaggle Food.com</a></p>
            <p style='font-size: 0.8em; color: gray;'>Session: {fav_count} favoris | Persistance activee</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    logger.debug("Rendu de la page termine")


if __name__ == "__main__":
    main()
