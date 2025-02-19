# README

## Bienvenue dans le dossier code & Data pour le datathon (Projet Limeat) ! 🎉

Limeat est une application qui souhaite utiliser le jeu pour sensibiliser à une alimentation plus saine et durable, notamment en restauration collective et entreprise.

---

## 📂 Contenu du Dossier

### 📜 Notebooks
- **`datathon.ipynb`** : Ce notebook contient le code principal pour ce hackathon. Vous y trouverez les fonctions à optimiser et à modifier directement pour atteindre les objectifs du projet. Il contient également les méthodes nécessaires pour importer les données, ainsi qu'un profil utilisateur par défaut et des repas type, à optimiser. 
- **`search_matching_food.ipynb`** : Ce notebook permet, à partir d'un string d'aliment (exemple : `"Apple"`), de trouver le ou les ingrédients dans la base de données d'ingrédients qui sont les plus proches. Son utilisation est facultative, mais peut être utile si besoin.

### 📊 Dossier Data
- **`ingredients_db.csv`** : Une base de données de **1300 ingrédients** avec leurs valeurs nutritionnelles. C'est la base de données principale du projet.
- **`meals.csv`** : Contient des repas qui peuvent être suggérés pour le soir, ainsi que leurs valeurs nutritionnelles, mais sans le détail des ingrédients.
- **`recipesDataset`** : Une base de données de recettes avec les ingrédients, qui peut potentiellement être utilisée comme base pour tester si des ingrédients vont bien ensemble.

---

## ⚙️ Installation

Pour utiliser ce projet, vous devez d'abord installer les packages nécessaires dans un environnement virtuel. Voici comment faire :

### 1️⃣ Créez un environnement virtuel :

```bash
python -m venv env
```

### 2️⃣ Activez l'environnement virtuel :

- **Sur macOS/Linux** :
  ```bash
  source env/bin/activate
  ```
- **Sur Windows** :
  ```bash
  env\Scripts\activate
  ```

### 3️⃣ Installez les packages requis :

```bash
pip install -r requirements.txt
```

---

## 🔍 Problématique à Résoudre

### 🎯 Contexte
Lorsqu'un utilisateur entre son repas dans l'application (**liste d'ingrédients et quantités**), il reçoit une **analyse nutritionnelle et environnementale**.  
Nous nous intéressons ici à la **partie nutritionnelle**.  

👉 **Savoir l'analyse c'est bien, mais avoir des conseils pour l'améliorer, c'est encore mieux !**  

En plus de conseils de nutritionnistes, nous souhaitons pouvoir suggérer des **ajouts ou remplacements d'ingrédients** dans le plat pour **améliorer le score nutritionnel**, en se basant sur de **vraies informations nutritionnelles**.

---

## 🎯 Objectif

Le **score nutritionnel** se base sur deux composantes :
1. **Un sous-score énergie**  
2. **Un sous-score macro-nutriments**  

Les méthodes permettant de calculer le score nutritionnel et ces sous-scores sont définies dans le **notebook `datathon.ipynb`**.  
L'objectif est d'implémenter une méthode qui permet, **en fonction des ingrédients du repas et des méthodes précédemment présentées**, de **suggérer des ingrédients à ajouter ou à remplacer** pour améliorer le score nutritionnel et donc la qualité du repas.

---

## 🛠️ Méthodologie

L'idéal est de suggérer des ingrédients qui sont **cohérents avec le reste du repas** :  
✅ **Exemple :** Ne pas suggérer d'ajouter une saucisse dans un burger, mais plutôt une tomate, une entrée/dessert, ou un condiment.  

L'**IA générative** peut être un atout pour cela, ou bien se baser sur des **recettes existantes**, par exemple celles du fichier `recipesDataset`.  
La méthode est **laissée libre**, et c'est ici que nous attendons de la **créativité**.  

---

## ⭐ Bonus

Il est aussi possible de suggérer **des aliments ou même des repas pour le soir**, afin d'optimiser un **score journalier**. *(Partie 2 du notebook.)*

---

## 🏆 Objectifs par Paliers

1. 🔹 **Générer des suggestions** d'ajout et/ou remplacements d'ingrédients pour **augmenter le score nutritionnel**.
2. 🔹 Objectif précédent + **suggestions cohérentes d'un point de vue goût**: les ingrédients suggérés sont cohérents avec le reste du repas.
3. 🔹 Objectif précédent + **suggestions d'ingrédients/repas pour le soir**, pour **optimiser le score journalier**.
4. 🔹 Objectif précédent + **habillage** :  
   - Utiliser **l'IA générative** pour **résumer ce qui ne va pas** dans le repas.  
   - Expliquer **pourquoi** on suggère ces ingrédients/repas.

---

## 🎉 Bonne chance et amusez-vous bien !

Nous vous souhaitons **bonne chance** et **beaucoup de plaisir** dans ce hackathon !  
Soyez **créatifs** et **expérimentez** ! 🚀  