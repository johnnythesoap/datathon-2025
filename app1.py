from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
import anthropic
import pandas as pd
import base64
import json
from pathlib import Path
import os
from dotenv import load_dotenv

# Configuration
load_dotenv()
app = FastAPI(title="Limeat API")

from pathlib import Path
import os

# Définition du bon chemin absolu
BASE_DIR = Path(__file__).resolve().parent
templates_dir = BASE_DIR / "templates"

# Debug pour vérifier le chemin
print("📂 Chemin absolu des templates :", templates_dir.resolve())

# Vérifier si index.html existe
if not (templates_dir / "index.html").exists():
    print("🚨 Le fichier index.html est manquant dans :", templates_dir.resolve())
    raise FileNotFoundError("⚠️ Le fichier index.html est introuvable dans le dossier templates/")

# Définition de FastAPI avec le bon dossier
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory=str(templates_dir))


# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os

if not os.path.exists(templates_dir / "index.html"):
    print("🚨 Le fichier index.html est introuvable dans :", templates_dir.resolve())
    raise FileNotFoundError("⚠️ index.html est manquant dans le dossier templates/")

# Route pour la page d'accueil
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )
# Modèles de données
class Ingredient(BaseModel):
    nom: str
    quantite: float
    apports_nutritionnels: List[str]

class ValeurNutritionnelle(BaseModel):
    valeur: float
    sources: List[str]

class Nutriments(BaseModel):
    calories: float
    proteines: ValeurNutritionnelle
    glucides: ValeurNutritionnelle
    lipides: ValeurNutritionnelle
    fibres: ValeurNutritionnelle

class Analyse(BaseModel):
    points_forts: List[str]
    points_faibles: List[str]
    description: str

class Suggestion(BaseModel):
    ingredient: str
    quantite: str
    raison: str
    apports: List[str]

class Remplacement(BaseModel):
    remplacer: str
    par: str
    raison: str
    benefices: List[str]

class Complementarite(BaseModel):
    nutritionnelle: List[str]
    equilibre_global: str
    gout: str

class RepasSoir(BaseModel):
    nom: str
    description: str
    complementarite: Complementarite

class AnalyseResponse(BaseModel):
    ingredients: List[Ingredient]
    valeurs_nutritionnelles: Nutriments
    analyse: Analyse
    suggestions: Dict[str, List[Union[Suggestion, Remplacement]]]
    repas_soir: List[RepasSoir]

class MealAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        data_dir = Path("datathon_Schoolab-main/data")
        self.ingredients_db = pd.read_csv(data_dir / "ingredients_db.csv", sep=';')
        self.meals_db = pd.read_csv(data_dir / "meals.csv", sep=';')

    async def analyze_image(self, image: bytes) -> dict:
        base64_image = base64.b64encode(image).decode('utf-8')

        prompt = """Analyse cette image de repas et fournis UNIQUEMENT une réponse au format JSON exact suivant.
Important:
- Identifie précisément la source des nutriments
- Fournis des suggestions cohérentes avec les goûts
- Ne suggère pas de remplacements non pertinents

{
    "ingredients": [
        {
            "nom": "ingredient",
            "quantite": nombre_grammes,
            "apports_nutritionnels": ["proteines", "glucides", etc.]
        }
    ],
    "valeurs_nutritionnelles": {
        "calories": nombre,
        "proteines": {
            "valeur": nombre_g,
            "sources": ["ingredient1: Xg", "ingredient2: Yg"]
        },
        "glucides": {
            "valeur": nombre_g,
            "sources": ["ingredient1: Xg", "ingredient2: Yg"]
        },
        "lipides": {
            "valeur": nombre_g,
            "sources": ["ingredient1: Xg", "ingredient2: Yg"]
        },
        "fibres": {
            "valeur": nombre_g,
            "sources": ["ingredient1: Xg", "ingredient2: Yg"]
        }
    },
    "analyse": {
        "points_forts": ["point1", "point2"],
        "points_faibles": ["point1", "point2"],
        "description": "explication détaillée"
    },
    "suggestions": {
        "ajouts": [
            {
                "ingredient": "nom",
                "quantite": "quantité suggérée",
                "raison": "explication nutritionnelle",
                "apports": ["protéines Xg", "glucides Yg", etc.]
            }
        ],
        "remplacements": [
            {
                "remplacer": "ingredient",
                "par": "alternative",
                "raison": "justification nutritionnelle",
                "benefices": ["bénéfice1", "bénéfice2"]
            }
        ]
    },
    "repas_soir": [
        {
            "nom": "nom du plat",
            "description": "description détaillée",
            "complementarite": {
                "nutritionnelle": ["complément1", "complément2"],
                "equilibre_global": "explication équilibre journée",
                "gout": "explication harmonie gustative"
            }
        }
    ]
}"""

        try:
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

            # Parser la réponse
            result = json.loads(response.content[0].text)
            
            # Enrichir avec les données de la base
            result = self.enrich_with_database(result)
            
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def enrich_with_database(self, result: dict) -> dict:
        """Enrichit l'analyse avec les données de la base"""
        try:
            for ingredient in result['ingredients']:
                matches = self.ingredients_db[
                    self.ingredients_db['FoodName'].str.contains(
                        ingredient['nom'], 
                        case=False
                    )
                ]
                if not matches.empty:
                    details = matches.iloc[0]
                    ingredient['details_db'] = {
                        'id': int(details['FoodID']),
                        'groupe': details['FoodGroupName'],
                        'nutriments_100g': {
                            'proteines': float(details['203']),
                            'lipides': float(details['204']),
                            'glucides': float(details['205']),
                            'fibres': float(details['291'])
                        }
                    }
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Erreur d'enrichissement : {str(e)}"
            )

# Routes API
@app.post("/analyze", response_model=AnalyseResponse)
async def analyze_meal(file: UploadFile = File(...)):
    """Analyse une image de repas"""
    try:
        contents = await file.read()
        analyzer = MealAnalyzer()
        result = await analyzer.analyze_image(contents)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)