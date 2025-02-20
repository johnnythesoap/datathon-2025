import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import base64
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import plotly.graph_objects as go

class Ingredient:
    def __init__(self, id: int, gQuantity: float, groupId: int = None):
        self.id = id
        self.gQuantity = gQuantity
        self.groupId = groupId

class MealAnalyzer:
    def __init__(self):
        """Initialise l'analyseur avec les bases de données"""
        try:
            # Chemins des fichiers de données
            data_dir = Path("datathon_Schoolab-main/data")
            self.ingredients_db = pd.read_csv(data_dir / "ingredients_db.csv", sep=';')
            self.meals_db = pd.read_csv(data_dir / "meals.csv", sep=';')

            # Configuration Anthropic
            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Clé API Anthropic manquante dans .env")
            # Assuming you have an Anthropic client setup
            # self.client = anthropic.Anthropic(api_key=api_key)

        except Exception as e:
            st.error(f"Erreur d'initialisation : {str(e)}")
            raise e

    def analyze_nutritional_values(self, ingredients_detected):
        """Analyse les valeurs nutritionnelles"""
        total_nutrients = {
            'calories': 0,
            'proteines': 0,
            'glucides': 0,
            'lipides': 0,
            'fibres': 0
        }

        nutrient_codes = {
            'proteines': '203',
            'lipides': '204',
            'glucides': '205',
            'calories': '208',
            'fibres': '291'
        }

        found_ingredients = []
        not_found = []

        for ing in ingredients_detected:
            matches = self.ingredients_db[
                self.ingredients_db['FoodName'].str.contains(ing['nom'], case=False)
            ]

            if not matches.empty:
                found_ingredients.append({
                    'nom': ing['nom'],
                    'quantite': ing['quantite'],
                    'id': matches.iloc[0]['FoodID']
                })

                for nutrient, code in nutrient_codes.items():
                    value = matches.iloc[0][code]
                    total_nutrients[nutrient] += (value * ing['quantite'] / 100)
            else:
                not_found.append(ing['nom'])

        # Calculer les scores
        energy_score = min(1.0, max(0.0, 1 - abs(total_nutrients['calories'] - 700) / 700))

        if total_nutrients['calories'] > 0:
            protein_ratio = total_nutrients['proteines'] * 4 / total_nutrients['calories']
            carb_ratio = total_nutrients['glucides'] * 4 / total_nutrients['calories']
            fat_ratio = total_nutrients['lipides'] * 9 / total_nutrients['calories']

            macro_score = 1 - (
                abs(protein_ratio - 0.2) +
                abs(carb_ratio - 0.45) +
                abs(fat_ratio - 0.35)
            ) / 2
        else:
            macro_score = 0

        return {
            'nutrients': total_nutrients,
            'scores': {
                'energie': energy_score,
                'macro': macro_score,
                'global': (energy_score + macro_score) / 2
            },
            'ingredients_trouves': found_ingredients,
            'ingredients_non_trouves': not_found
        }

    def format_suggestions(self, analysis_result):
        """Génère des suggestions d'amélioration"""
        nutrients = analysis_result['nutrients']
        scores = analysis_result['scores']
        suggestions = {
            'ajouts': [],
            'remplacements': [],
            'explications': []
        }

        # Analyses et suggestions
        if nutrients['proteines'] < 20:
            suggestions['ajouts'].append("source de protéines (poulet, poisson, oeufs)")
            suggestions['explications'].append("Apport en protéines insuffisant")

        carb_ratio = (nutrients['glucides'] * 4) / nutrients['calories'] if nutrients['calories'] > 0 else 0
        if carb_ratio > 0.55:
            suggestions['remplacements'].append({
                'remplacer': "une partie des féculents",
                'par': "des légumes",
                'raison': "Trop de glucides dans le repas"
            })

        if nutrients['fibres'] < 4:
            suggestions['ajouts'].append("légumes verts ou céréales complètes")
            suggestions['explications'].append("Apport en fibres insuffisant")

        if nutrients['calories'] > 800:
            suggestions['explications'].append("Repas trop calorique")
            suggestions['remplacements'].append({
                'remplacer': "les aliments gras",
                'par': "des alternatives plus légères",
                'raison': "Réduire l'apport calorique"
            })
        elif nutrients['calories'] < 500:
            suggestions['explications'].append("Repas pas assez calorique")
            suggestions['ajouts'].append("une portion de féculent complet")

        return suggestions

    def analyze_meal_image(self, image_data):
        """Analyse une image de repas"""
        try:
            # Encoder l'image en base64
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # Prompt pour Claude
            prompt = """Analyse cette image de repas et fournis :
            1. Les ingrédients visibles avec quantités estimées
            2. Suggestions pour améliorer l'équilibre nutritionnel

            Réponds en JSON avec ce format exact :
            {
                "ingredients": [
                    {"nom": "ingredient", "quantite": nombre_grammes}
                ],
                "suggestions": {
                    "ajouts": ["ingredient1", "ingredient2"],
                    "remplacements": [
                        {"remplacer": "ingredient", "par": "alternative"}
                    ]
                }
            }"""

            # Assuming you have a method to call the Anthropic API
            # response = self.client.messages.create(...)

            # For demonstration, we'll simulate a response
            claude_result = {
                "ingredients": [
                    {"nom": "pomme", "quantite": 150},
                    {"nom": "banane", "quantite": 120}
                ],
                "suggestions": {
                    "ajouts": ["noix", "graines"],
                    "remplacements": [
                        {"remplacer": "banane", "par": "fraise"}
                    ]
                }
            }

            # Analyser les valeurs nutritionnelles
            nutritional_analysis = self.analyze_nutritional_values(claude_result['ingredients'])
            suggestions = self.format_suggestions(nutritional_analysis)

            return {
                'detection': claude_result['ingredients'],
                'analyse_nutritionnelle': {
                    'valeurs': nutritional_analysis['nutrients'],
                    'scores': nutritional_analysis['scores']
                },
                'suggestions': suggestions,
                'ingredients_non_trouves': nutritional_analysis['ingredients_non_trouves']
            }

        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {str(e)}")
            return None

def main():
    st.set_page_config(
        page_title="Limeat - Analyse Nutritionnelle",
        page_icon="🍽️",
        layout="wide"
    )

    st.title("🍽️ Limeat - Analyse Nutritionnelle")
    st.write("Analysez votre repas et obtenez des recommandations personnalisées")

    # Interface principale
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📸 Photo du Repas")
        uploaded_file = st.file_uploader(
            "Choisissez une photo de votre repas",
            type=["jpg", "jpeg", "png", "webp"]
        )

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Votre repas", use_column_width=True)

            if st.button("🔍 Analyser le repas"):
                with st.spinner("Analyse en cours..."):
                    try:
                        analyzer = MealAnalyzer()
                        result = analyzer.analyze_meal_image(uploaded_file.getvalue())
                        st.session_state.analysis_result = result
                    except Exception as e:
                        st.error(f"Erreur : {str(e)}")

    with col2:
        if 'analysis_result' in st.session_state:
            result = st.session_state.analysis_result

            st.header("📊 Résultats")

            # Scores
            scores = result['analyse_nutritionnelle']['scores']
            cols = st.columns(3)
            cols[0].metric("Score Global", f"{scores['global']:.0%}")
            cols[1].metric("Score Énergie", f"{scores['energie']:.0%}")
            cols[2].metric("Score Macro", f"{scores['macro']:.0%}")

            # Valeurs nutritionnelles
            st.subheader("Valeurs Nutritionnelles")
            nutrients = result['analyse_nutritionnelle']['valeurs']

            # Graphique des macronutriments
            fig = go.Figure(data=[
                go.Bar(
                    x=['Protéines', 'Glucides', 'Lipides'],
                    y=[
                        nutrients['proteines'],
                        nutrients['glucides'],
                        nutrients['lipides']
                    ],
                    text=[f"{val:.1f}g" for val in [
                        nutrients['proteines'],
                        nutrients['glucides'],
                        nutrients['lipides']
                    ]],
                    textposition='auto',
                )
            ])

            fig.update_layout(
                title="Répartition des Macronutriments",
                yaxis_title="Grammes"
            )

            st.plotly_chart(fig, use_container_width=True)

            # Autres valeurs
            st.metric("Calories", f"{nutrients['calories']:.0f} kcal")
            st.metric("Fibres", f"{nutrients['fibres']:.1f}g")

            # Ingredients detected
            st.subheader("Ingrédients Détectés")
            for ingredient in result['detection']:
                st.write(f"- {ingredient['nom']} ({ingredient['quantite']}g)")

            # Suggestions
            st.subheader("💡 Suggestions d'Amélioration")

            if result['suggestions']['explications']:
                with st.expander("Analyse", expanded=True):
                    for expl in result['suggestions']['explications']:
                        st.info(expl)

            if result['suggestions']['ajouts']:
                with st.expander("Ajouts recommandés", expanded=True):
                    for ajout in result['suggestions']['ajouts']:
                        st.success(f"➕ {ajout}")

            if result['suggestions']['remplacements']:
                with st.expander("Remplacements suggérés", expanded=True):
                    for remp in result['suggestions']['remplacements']:
                        st.warning(
                            f"🔄 Remplacer **{remp['remplacer']}** par **{remp['par']}**\n\n"
                            f"*Raison : {remp['raison']}*"
                        )

if __name__ == "__main__":
    main()
