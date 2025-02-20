#le fichier du user interface
import tkinter as tk
from tkinter import messagebox
from main import get_ai_suggestions  # Import the function from main.py

def on_submit():
    """Handles the submit button click."""
    ingredients = entry.get().strip()
    if not ingredients:
        messagebox.showerror("Error", "Please enter some ingredients.")
        return
    
    ingredient_list = [item.strip() for item in ingredients.split(",")]
    suggestions = get_ai_suggestions(ingredient_list)
    
    if suggestions:
        result_text.set(f"Dish Name: {suggestions['dish_name']}\n"
                        f"Add for Calories: {', '.join(suggestions['add_calories'])}\n"
                        f"Remove for Calories: {', '.join(suggestions['remove_calories'])}\n"
                        f"Add for Health: {', '.join(suggestions['add_health'])}\n"
                        f"Remove for Health: {', '.join(suggestions['remove_health'])}")
    else:
        result_text.set("No valid response received.")

# Create the main window
root = tk.Tk()
root.title("AI Recipe Helper")
root.geometry("500x400")

# Input field
label = tk.Label(root, text="Enter ingredients (comma-separated):")
label.pack(pady=5)

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

submit_button = tk.Button(root, text="Get AI Suggestions", command=on_submit)
submit_button.pack(pady=10)

# Result display
result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, justify="left")
result_label.pack(pady=10)

# Run the application
root.mainloop()
