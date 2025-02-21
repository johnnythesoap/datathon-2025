"""
Limeat - Application d'analyse nutritionnelle
Combine l'analyse d'image avec Claude et l'interface Streamlit
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
import uuid  # Pour générer des clés uniques pour les graphiques

# Charger les variables d'environnement
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Vérification de la clé API
if not API_KEY:
    st.error("🚨 Clé API Anthropic manquante ! Vérifiez votre fichier `.env`.")
    st.stop()


# 📌 **Classe d'analyse des repas**
class MealAnalyzer:
    def __init__(self):
        """Initialise l'analyseur avec les bases de données et l'API Anthropic"""
        try:
            self.client = anthropic.Anthropic(api_key=API_KEY)

            data_dir = Path("datathon_Schoolab-main/data")
            self.ingredients_db = pd.read_csv(data_dir / "ingredients_db.csv", sep=";")
            self.meals_db = pd.read_csv(data_dir / "meals.csv", sep=";")

            st.success("✅ Analyseur initialisé avec succès")
        except Exception as e:
            st.error(f"❌ Erreur d'initialisation : {str(e)}")
            raise e

    def analyze_meal_image(self, image_data):
        """Analyse une image de repas et retourne une réponse structurée"""
        try:
            base64_image = base64.b64encode(image_data).decode("utf-8")

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
                    "description": "explication du repas"
                },
                "suggestions": {
                    "ajouts": [{"ingredient": "nom", "raison": "explication"}],
                    "remplacements": [{"remplacer": "ingredient", "par": "alternative", "raison": "explication"}]
                },
                "repas_soir": [
                    {"nom": "nom du plat", "description": "description", "raison": "complémentarité avec le repas de midi"}
                ]
            }"""

            with st.spinner("🧐 Analyse de l'image en cours..."):
                response = self.client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": [{"type": "text", "text": prompt},
                                                     {"type": "image", "source": {
                                                         "type": "base64",
                                                         "media_type": "image/jpeg",
                                                         "data": base64_image
                                                     }}]}
                    ],
                )

            response_text = response.content[0].text.strip()

            # Vérification et parsing JSON
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                response_text = response_text[json_start:json_end]

            result = json.loads(response_text)
            return result

        except json.JSONDecodeError:
            st.error("🚨 Erreur : Impossible d'analyser la réponse JSON.")
            return None
        except Exception as e:
            st.error(f"🚨 Erreur d'analyse : {str(e)}")
            return None


# 📊 **Affichage des résultats**
def display_results(result):
    """Affiche les résultats de l'analyse"""
    try:
        st.subheader("📊 Résultats de l'analyse")

        # 📌 **Graphique des macronutriments**
        fig = go.Figure(data=[
            go.Bar(
                x=['Protéines', 'Glucides', 'Lipides'],
                y=[result['valeurs_nutritionnelles']['proteines'],
                   result['valeurs_nutritionnelles']['glucides'],
                   result['valeurs_nutritionnelles']['lipides']],
                text=[f"{result['valeurs_nutritionnelles'][key]} g"
                      for key in ['proteines', 'glucides', 'lipides']],
                textposition='auto',
            )
        ])
        fig.update_layout(title="Répartition des Macronutriments", yaxis_title="Grammes")

        # ✅ Générer un identifiant unique pour éviter les conflits
        unique_key = f"macronutrients_chart_{uuid.uuid4().hex[:8]}"
        st.plotly_chart(fig, use_container_width=True, key=unique_key)

        # 📌 **Analyse**
        with st.expander("📝 Analyse détaillée", expanded=True):
            st.success("✅ Points forts : " + ", ".join(result['analyse']['points_forts']))
            st.warning("⚠️ Points faibles : " + ", ".join(result['analyse']['points_faibles']))
            st.info("📜 " + result['analyse']['description'])

        # 📌 **Suggestions**
        with st.expander("💡 Suggestions d'amélioration"):
            for ajout in result['suggestions']['ajouts']:
                st.success(f"➕ Ajout suggéré : {ajout['ingredient']} ({ajout['raison']})")

            for remp in result['suggestions']['remplacements']:
                st.warning(f"🔄 Remplacement : **{remp['remplacer']}** → **{remp['par']}** ({remp['raison']})")

        # 📌 **Suggestions repas du soir**
        with st.expander("🌙 Repas du soir suggéré"):
            for repas in result['repas_soir']:
                st.write(f"🍽 **{repas['nom']}** - {repas['description']} ({repas['raison']})")

    except Exception as e:
        st.error(f"❌ Erreur d'affichage : {str(e)}")


# 🌍 **Application principale**
def main():
    st.set_page_config(page_title="Limeat - Analyse Nutritionnelle", page_icon="🍽️", layout="wide")

    st.title("🍽️ Limeat - Analyse Nutritionnelle")
    st.write("📷 Téléchargez une photo de votre repas et obtenez une analyse détaillée.")

    # 📌 **Disposition en colonnes**
    col1, col2 = st.columns([1, 1])

    with col1:
        uploaded_file = st.file_uploader("📤 Choisissez une photo de votre repas", type=["jpg", "jpeg", "png", "webp"])
        if uploaded_file:
            st.image(uploaded_file, caption="📷 Votre repas", use_column_width=True)

    with col2:
        if uploaded_file and st.button("🔍 Analyser le repas"):
            analyzer = MealAnalyzer()
            result = analyzer.analyze_meal_image(uploaded_file.getvalue())

            if result:
                st.session_state.analysis_result = result

        if 'analysis_result' in st.session_state:
            display_results(st.session_state.analysis_result)


if __name__ == "__main__":
    main()
