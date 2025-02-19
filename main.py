#Le fichier de code principal du projet datathon-2025
# API ChatGPT qui se connecte et fournit des donnees culinaires par rapport aux donnees d'ingredients et de plats
import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Set up OpenAI API key

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("Missing OpenAI API key. Make sure to set it in the .env file.")

client = openai.OpenAI(api_key=openai_api_key)  # Update this line

def get_ai_suggestions(ingredients):
    """Fetches AI-generated dish name and ingredient suggestions."""
    prompt = f"""
    You are a chef and nutritionist. Given the following ingredients:
    {", ".join(ingredients)}
    
    1. Identify the most likely dish.
    2. Suggest ingredients to **add** to increase calorie content.
    3. Suggest ingredients to **remove** to decrease calories.
    4. Suggest ingredients to **add** to improve the Nutri-Score (health benefits).
    5. Suggest ingredients to **remove** to improve the Nutri-Score.

    All ingredients must make sense in the context of the dish!

    Return your response in this **JSON format**:
    {{
      "dish_name": "Dish Name",
      "add_calories": ["ingredient1", "ingredient2"],
      "remove_calories": ["ingredient3", "ingredient4"],
      "add_health": ["ingredient5", "ingredient6"],
      "remove_health": ["ingredient7", "ingredient8"]
    }}
    """

    response = client.chat.completions.create(  # Updated method call
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    ai_response = response.choices[0].message.content  # Updated response parsing

    try:
        return json.loads(ai_response)
    except json.JSONDecodeError:
        print("Error: AI response could not be parsed.")
        return None

def main():
    """Runs the main script when executed directly."""
    user_ingredients = input("Enter ingredients (comma-separated): ").split(", ")
    suggestions = get_ai_suggestions(user_ingredients)

    if suggestions:
        print("\n===== AI Suggestions =====")
        print(f"Dish Name: {suggestions['dish_name']}")
        print(f"Add for Calories: {', '.join(suggestions['add_calories'])}")
        print(f"Remove for Calories: {', '.join(suggestions['remove_calories'])}")
        print(f"Add for Health: {', '.join(suggestions['add_health'])}")
        print(f"Remove for Health: {', '.join(suggestions['remove_health'])}")
    else:
        print("No valid response received.")

if __name__ == "__main__":
    main()
