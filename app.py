"""
Limeat - Application complète d'analyse nutritionnelle
avec gestion des allergies et recommandations de repas
"""
import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import base64
import json
from pathlib import Path
import anthropic
from PIL import Image
import plotly.graph_objects as go
import uuid
import numpy as np
from typing import List, Dict, Tuple


# Configuration
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Vérification de la clé API
if not API_KEY:
    st.error("🚨 Clé API Anthropic manquante ! Vérifiez votre fichier .env.")
    st.stop()

def show_config_page():
    """Affiche la page de configuration"""
    st.title("🔧 Configuration de votre profil")
    
    # Section allergies
    st.header("🚫 Allergies et intolérances")
    
    # Option "Pas d'allergie"
    has_allergies = st.radio(
        "Avez-vous des allergies ?",
        ["Non, pas d'allergie", "Oui, j'ai des allergies"],
        index=0  # Par défaut sur "Non"
    )
    
    selected_allergies = []
    if has_allergies == "Oui, j'ai des allergies":
        allergens = load_common_allergens()
        st.write("Sélectionnez vos allergies :")
        for allergen, examples in allergens.items():
            if st.checkbox(
                f"{allergen.replace('_', ' ').title()}", 
                help=f"Exemples: {', '.join(examples)}",
                key=f"allergen_{allergen}"
            ):
                selected_allergies.append(allergen)
    
    st.session_state.allergies = selected_allergies
    
    # Section petit-déjeuner (reste inchangé)
    st.header("🌅 Petit-déjeuner")
    breakfast_options = {
        "continental": "Continental (pain, beurre, confiture, café/thé)",
        "complet": "Complet (œufs, bacon, pain, fruits)",
        "healthy": "Healthy (yaourt, fruits, céréales)",
        "vegan": "Vegan (fruits, céréales, lait végétal)",
        "skip": "Pas de petit-déjeuner"
    }
    
    breakfast = st.selectbox(
        "Qu'avez-vous mangé ce matin ?",
        options=list(breakfast_options.keys()),
        format_func=lambda x: breakfast_options[x]
    )
    
    st.session_state.breakfast = breakfast
    
    if st.button("Continuer vers l'analyse de repas ➡️"):
        st.session_state.page = 'analysis'
        st.rerun()    

def load_common_allergens():
    """Liste des allergènes courants"""
    return {
        "gluten": ["blé", "orge", "seigle", "avoine"],
        "lactose": ["lait", "fromage", "yaourt", "crème"],
        "fruits_a_coque": ["amande", "noix", "noisette", "cajou", "pistache"],
        "arachides": ["cacahuète", "huile d'arachide"],
        "soja": ["sauce soja", "tofu", "edamame"],
        "oeufs": ["oeuf", "mayonnaise", "meringue"],
        "poisson": ["tous types de poissons"],
        "crustaces": ["crevette", "crabe", "homard"],
        "celeri": ["céleri", "céleri-rave"],
        "moutarde": ["moutarde", "sauce moutarde"],
        "sesame": ["graines de sésame", "huile de sésame"],
        "sulfites": ["vin", "fruits secs"],
    }

def init_session_state():
    """Initialise les variables de session"""
    if 'page' not in st.session_state:
        st.session_state.page = 'config'
    if 'allergies' not in st.session_state:
        st.session_state.allergies = []
    if 'breakfast' not in st.session_state:
        st.session_state.breakfast = None
    if 'selected_substitutions' not in st.session_state:
        st.session_state.selected_substitutions = {}

def load_substitutions(ingredients_db: pd.DataFrame):
    """Crée un dictionnaire de substitutions basé sur la base de données"""
    substitutions = {}
    groups = ingredients_db.groupby('FoodGroupID')
    
    for _, row in ingredients_db.iterrows():
        group_id = row['FoodGroupID']
        current_food = row['FoodName']
        
        alternatives = groups.get_group(group_id)
        alternatives = alternatives[alternatives['FoodName'] != current_food]
        alternatives['nutritional_similarity'] = (
            (alternatives['203'] - row['203']).abs() +  # Protéines
            (alternatives['204'] - row['204']).abs() +  # Lipides
            (alternatives['205'] - row['205']).abs()    # Glucides
        )
        alternatives = alternatives.sort_values('nutritional_similarity')
        alternatives = alternatives['FoodName'].head(3).tolist()
        
        if alternatives:
            substitutions[current_food.lower()] = alternatives
            
    return substitutions

def calculate_daily_needs(user_profile):
    """Calcule les besoins journaliers"""
    base_calories = user_profile.get("weight", 70) * 24
    activity_factor = user_profile.get("activity_level", 1.4)
    return {
        "calories": base_calories * activity_factor,
        "proteines": (base_calories * 0.15) / 4,
        "glucides": (base_calories * 0.55) / 4,
        "lipides": (base_calories * 0.30) / 9
    }

def get_remaining_needs(daily_needs, breakfast_details, lunch_details):
    """Calcule les besoins restants pour le dîner"""
    consumed = {
        "calories": breakfast_details.get("calories", 0) + lunch_details.get("calories", 0),
        "proteines": breakfast_details.get("proteines", 0) + lunch_details.get("proteines", 0),
        "glucides": breakfast_details.get("glucides", 0) + lunch_details.get("glucides", 0),
        "lipides": breakfast_details.get("lipides", 0) + lunch_details.get("lipides", 0)
    }
    
    return {k: daily_needs[k] - consumed[k] for k in daily_needs.keys()}

#Analyse de repas
class MealAnalyzer:
    def __init__(self):
        """Initialise l'analyseur avec les bases de données"""
        try:
            self.client = anthropic.Anthropic(api_key=API_KEY)
            data_dir = Path("datathon_Schoolab-main/data")
            self.ingredients_db = pd.read_csv(data_dir / "ingredients_db.csv", sep=';')
            self.meals_db = pd.read_csv(data_dir / "meals.csv", sep=';')
            self.substitutions = load_substitutions(self.ingredients_db)
            st.success("✅ Analyseur initialisé avec succès")
        except Exception as e:
            st.error(f"❌ Erreur d'initialisation : {str(e)}")
            raise e
    import numpy as np
from typing import List, Dict, Tuple

class Ingredient:
    def __init__(self, id: int, gQuantity: float, groupId: int = None):
        self.id = id
        self.gQuantity = gQuantity
        self.groupId = groupId

class NutritionalScorer:
    def __init__(self, ingredients_db: pd.DataFrame, user_profile: Dict):
        """Initialise le calculateur nutritionnel avec la base d'ingrédients et le profil utilisateur"""
        self.ingredients_db = ingredients_db
        self.user_profile = user_profile

        self.nut_dict = {
            '203': "Protéines", '204': "Lipides", '205': "Glucides", 
            '208': "Energie", '291': "Fibres", '601': "Cholesterol", 
            '255': "Eau", '269': "Sucres", '810': "Amidon"
        }

    def analyze_meal_nutritional_score(self, ingredients: List[Dict]) -> Dict:
        """Analyse le score nutritionnel du repas"""
        meal_ingredients = [Ingredient(id=ing['id'], gQuantity=ing.get('quantite', 100)) for ing in ingredients]
        nutrients = self.get_nutrients_from_meal(meal_ingredients)
        meal_nut_score, meal_energy_sub_score, meal_macro_sub_score = self._compute_meal_score(meal_ingredients, nutrients)

        return {
            'nutritional_score': meal_nut_score,
            'energy_subscore': meal_energy_sub_score,
            'macro_subscore': meal_macro_sub_score,
            'nutrient_details': {self.nut_dict.get(k, k): v for k, v in nutrients.items()}
        }

    def _compute_meal_score(self, current_meal: List[Ingredient], summed_nutrients_info: Dict) -> Tuple[float, float, float]:
        """Calcule le score nutritionnel global d'un repas"""
        for ingredient in current_meal:
            ingredient.groupId = self.ingredients_db.loc[self.ingredients_db['FoodID'] == ingredient.id, 'FoodGroupID'].values[0]

        meal_energy_sub_score = self.compute_daily_energy_sub_score(summed_nutrients_info)
        meal_macro_sub_score = self.compute_daily_macro_sub_score(current_meal, summed_nutrients_info)

        meal_nut_sum = (1/3) * meal_energy_sub_score + (2/3) * meal_macro_sub_score
        meal_nut_score = self.sigmoid_piecewise(meal_nut_sum, k1=5, k2=7.5, x0=0.5)

        return meal_nut_score, meal_energy_sub_score, meal_macro_sub_score

class ExtendedMealAnalyzer(MealAnalyzer):
    def __init__(self):
        super().__init__()

        default_user_profile = {
            "age": 35,
            "weight": 70,
            "size": 170,
            "activityLevel": 1.4
        }

        self.nutritional_scorer = NutritionalScorer(self.ingredients_db, default_user_profile)

    def analyze_meal_image(self, image_data):
        """Ajoute une analyse nutritionnelle avancée et recommandations de repas"""
        result = super().analyze_meal_image(image_data)
        if result and 'ingredients' in result:
            nutritional_analysis = self.nutritional_scorer.analyze_meal_nutritional_score([
                {
                    'id': self.ingredients_db[self.ingredients_db['FoodName'].str.lower() == ing['nom'].lower()]['FoodID'].values[0],
                    'quantite': ing['quantite']
                } for ing in result['ingredients']
            ])
            result['nutritional_score'] = {
                'total_score': nutritional_analysis['nutritional_score'],
                'energy_subscore': nutritional_analysis['energy_subscore'],
                'macro_subscore': nutritional_analysis['macro_subscore']
            }

        return result
    

    def analyze_meal_image(self, image_data):
        """Analyse une image de repas"""
        try:
            base64_image = base64.b64encode(image_data).decode('utf-8')

            prompt = """Analyse cette image de repas et retourne uniquement du JSON au format suivant :
            {
                "ingredients": [{"nom": "ingredient", "quantite": nombre_grammes}],
                "valeurs_nutritionnelles": {
                    "calories": nombre,
                    "proteines": nombre_g,
                    "glucides": nombre_g,
                    "lipides": nombre_g,
                    "fibres": nombre_g
                },
                "analyse": {
                    "points_forts": ["point1", "point2"],
                    "points_faibles": ["point1", "point2"],
                    "description": "explication détaillée"
                },
                "suggestions": {
                    "ajouts": [{"ingredient": "nom", "raison": "explication"}],
                    "remplacements": [{"remplacer": "ingredient", "par": "alternative", "raison": "explication"}]
                },
                "repas_soir": [
                    {"nom": "nom du plat", "description": "description", "raison": "complémentarité avec le repas de midi"}
                ]
            }"""

            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }]
            )

            response_text = response.content[0].text.strip()
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                response_text = response_text[json_start:json_end]
            
            result = json.loads(response_text)
            
            # Vérifier les allergies
            if st.session_state.allergies:
                result = self.filter_allergenic_suggestions(result)
            
            # Enrichir avec les calculs de besoins
            result = self.enrich_with_daily_needs(result)
            
            return result

        except Exception as e:
            st.error(f"🚨 Erreur d'analyse : {str(e)}")
            return None

    def filter_allergenic_suggestions(self, result):
        """Filtre les suggestions selon les allergies"""
        allergies = st.session_state.allergies
        filtered_result = result.copy()
        
        # Filtrer les suggestions d'ajouts
        filtered_result['suggestions']['ajouts'] = [
            sugg for sugg in result['suggestions']['ajouts']
            if not any(allergen in sugg['ingredient'].lower() 
                      for allergen in allergies)
        ]
        
        # Filtrer les suggestions de remplacements
        filtered_result['suggestions']['remplacements'] = [
            sugg for sugg in result['suggestions']['remplacements']
            if not any(allergen in sugg['par'].lower() 
                      for allergen in allergies)
        ]
        
        return filtered_result

    def enrich_with_daily_needs(self, result):
        """Enrichit le résultat avec les calculs de besoins journaliers"""
        # Récupérer le petit-déjeuner
        breakfast_details = {
            "continental": {"calories": 400, "proteines": 8, "glucides": 65, "lipides": 12},
            "complet": {"calories": 600, "proteines": 20, "glucides": 45, "lipides": 25},
            "healthy": {"calories": 350, "proteines": 15, "glucides": 50, "lipides": 8},
            "vegan": {"calories": 380, "proteines": 12, "glucides": 60, "lipides": 10}
        }.get(st.session_state.breakfast, {"calories": 0, "proteines": 0, "glucides": 0, "lipides": 0})

        # Calculer les besoins restants
        user_profile = {"weight": 70, "activity_level": 1.4}  # À personnaliser selon l'utilisateur
        daily_needs = calculate_daily_needs(user_profile)
        remaining_needs = get_remaining_needs(
            daily_needs,
            breakfast_details,
            result['valeurs_nutritionnelles']
        )
        
        result['besoins_restants'] = remaining_needs
        return result

def show_config_page():
    """Affiche la page de configuration"""
    st.title("🔧 Configuration de votre profil")
    
    # Section allergies
    st.header("🚫 Allergies et intolérances")
    allergens = load_common_allergens()
    
    selected_allergies = []
    for allergen, examples in allergens.items():
        if st.checkbox(
            f"{allergen.replace('_', ' ').title()}", 
            help=f"Exemples: {', '.join(examples)}"
        ):
            selected_allergies.append(allergen)
    
    st.session_state.allergies = selected_allergies
    
    # Section petit-déjeuner
    st.header("🌅 Petit-déjeuner")
    breakfast_options = {
        "continental": "Continental (pain, beurre, confiture, café/thé)",
        "complet": "Complet (œufs, bacon, pain, fruits)",
        "healthy": "Healthy (yaourt, fruits, céréales)",
        "vegan": "Vegan (fruits, céréales, lait végétal)",
        "skip": "Pas de petit-déjeuner"
    }
    
    breakfast = st.selectbox(
        "Qu'avez-vous mangé ce matin ?",
        options=list(breakfast_options.keys()),
        format_func=lambda x: breakfast_options[x]
    )
    
    st.session_state.breakfast = breakfast
    
    if st.button("Continuer vers l'analyse de repas ➡️"):
        st.session_state.page = 'analysis'
        st.rerun()

def display_results(result, analyzer):
    """Affiche les résultats de l'analyse"""
    try:
        st.subheader("📊 Résultats de l'analyse")

        # Afficher les apports de la journée
        st.markdown("### 📅 Apports de la journée")
        daily_totals = {
            "calories": result['valeurs_nutritionnelles']['calories'],
            "proteines": result['valeurs_nutritionnelles']['proteines'],
            "glucides": result['valeurs_nutritionnelles']['glucides'],
            "lipides": result['valeurs_nutritionnelles']['lipides']
        }
        
        cols = st.columns(4)
        for i, (nutrient, value) in enumerate(daily_totals.items()):
            with cols[i]:
                st.metric(
                    nutrient.capitalize(),
                    f"{value:.0f}{'kcal' if nutrient == 'calories' else 'g'}",
                    f"Reste: {result['besoins_restants'][nutrient]:.0f}"
                )

        # Graphique des macronutriments
        fig = go.Figure(data=[
            go.Bar(
                x=['Protéines', 'Glucides', 'Lipides'],
                y=[
                    result['valeurs_nutritionnelles']['proteines'],
                    result['valeurs_nutritionnelles']['glucides'],
                    result['valeurs_nutritionnelles']['lipides']
                ],
                text=[f"{val:.1f}g" for val in [
                    result['valeurs_nutritionnelles']['proteines'],
                    result['valeurs_nutritionnelles']['glucides'],
                    result['valeurs_nutritionnelles']['lipides']
                ]],
                textposition='auto',
            )
        ])
        
        fig.update_layout(title="Répartition des Macronutriments", yaxis_title="Grammes")
        unique_key = f"macronutrients_chart_{uuid.uuid4().hex[:8]}"
        st.plotly_chart(fig, use_container_width=True, key=unique_key)

        # Analyse détaillée
        with st.expander("📝 Analyse détaillée", expanded=True):
            st.success("✅ Points forts :\n" + "\n".join(f"- {point}" for point in result['analyse']['points_forts']))
            st.warning("⚠️ Points à améliorer :\n" + "\n".join(f"- {point}" for point in result['analyse']['points_faibles']))
            st.info("📜 " + result['analyse']['description'])

        # Suggestions pour le reste de la journée
        with st.expander("🌙 Suggestions pour le dîner", expanded=True):
            st.markdown("### En fonction de vos apports de la journée")
            st.write(f"Il vous reste à consommer :")
            st.write(f"- Calories : {result['besoins_restants']['calories']:.0f} kcal")
            st.write(f"- Protéines : {result['besoins_restants']['proteines']:.0f}g")
            st.write(f"- Glucides : {result['besoins_restants']['glucides']:.0f}g")
            st.write(f"- Lipides : {result['besoins_restants']['lipides']:.0f}g")
            
            st.markdown("### Suggestions de repas")
            for repas in result['repas_soir']:
                st.write(f"🍽️ **{repas['nom']}**")
                st.write(repas['description'])
                st.write(f"*Raison : {repas['raison']}*")

    except Exception as e:
        st.error(f"❌ Erreur d'affichage : {str(e)}")
        st.write("DEBUG - Structure des résultats:", result)

def main():
    st.set_page_config(
        page_title="Limeat - Analyse Nutritionnelle",
        page_icon="🍽️",
        layout="wide"
    )
    
    # Initialiser l'état de session
    init_session_state()
    
    if st.session_state.page == 'config':
        show_config_page()
    else:
        # Afficher un rappel des configurations dans la sidebar
        with st.sidebar:
            st.subheader("🔧 Votre profil")
            if st.session_state.allergies:
                st.write("🚫 Allergies :", ", ".join(st.session_state.allergies))
            else:
                st.write("✅ Aucune allergie déclarée")
            
            if st.session_state.breakfast != "skip":
                st.write("🌅 Petit-déjeuner :", st.session_state.breakfast)
            else:
                st.write("🌅 Pas de petit-déjeuner")
            
            if st.button("Modifier le profil"):
                st.session_state.page = 'config'
                st.rerun()
        
        # Interface principale
        st.title("🍽️ Limeat - Analyse Nutritionnelle")
        st.write("📷 Téléchargez une photo de votre repas et obtenez une analyse détaillée.")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "📤 Choisissez une photo de votre repas",
                type=["jpg", "jpeg", "png", "webp"]
            )
            
            if uploaded_file:
                st.image(uploaded_file, caption="📷 Votre repas", use_column_width=True)
        
        with col2:
            if uploaded_file and st.button("🔍 Analyser le repas"):
                analyzer = ExtendedMealAnalyzer()
                result = analyzer.analyze_meal_image(uploaded_file.getvalue())
                if result:
                    st.session_state.analysis_result = result
                    st.session_state.current_analyzer = analyzer
            
            if 'analysis_result' in st.session_state and 'current_analyzer' in st.session_state:
                display_results(st.session_state.analysis_result, st.session_state.current_analyzer)

if __name__ == "__main__":
    main()