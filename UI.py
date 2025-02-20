# le fichier du user interface
import tkinter as tk
from main import get_ai_suggestions  # Import AI function from main.py

# Function to adjust the Text widget size dynamically
def adjust_text_widget_size():
    """Dynamically adjust the height of the text widget to fit content."""
    num_lines = int(result_text_widget.index("end-1c").split(".")[0])  # Get the number of lines
    new_height = min(max(num_lines, 5), 20)  # Set a range between 5 and 20 lines
    result_text_widget.config(height=new_height)  # Adjust height dynamically

# Function to handle button click
def on_submit():
    ingredients = entry.get().strip()  # Get input from text field
    if not ingredients:
        result_text_widget.delete("1.0", tk.END)  # Clear previous text
        result_text_widget.insert("1.0", "Please enter some ingredients.")  # Show error message
        adjust_text_widget_size()  # Adjust box size
        return

    result_text_widget.delete("1.0", tk.END)  # Clear previous results
    result_text_widget.insert("1.0", "AI Suggestions loading...\n")  # Show loading text
    root.update()  # Refresh UI

    ingredients_list = ingredients.split(", ")  # Convert input to a list

    suggestions = get_ai_suggestions(ingredients_list)  # Get AI response

    if suggestions:
        result = (f"Dish Name:\n  {suggestions['dish_name']}\n\n"
                  f"➕ Add for Calories:\n  {', '.join(suggestions['add_calories'])}\n\n"
                  f"➖ Remove for Calories:\n  {', '.join(suggestions['remove_calories'])}\n\n"
                  f"💪 Add for Health:\n  {', '.join(suggestions['add_health'])}\n\n"
                  f"🚫 Remove for Health:\n  {', '.join(suggestions['remove_health'])}")
        result_text_widget.delete("1.0", tk.END)  # Clear previous results
        result_text_widget.insert("1.0", result)  # Display new results
    else:
        result_text_widget.delete("1.0", tk.END)
        result_text_widget.insert("1.0", "Error: AI response could not be generated.")

    adjust_text_widget_size()  # Adjust text box size dynamically

# Create the main window
root = tk.Tk()
root.title("AI Recipe Helper")
root.geometry("700x600")
root.configure(bg="#f4f4f4")  # Light gray background

# Input field label
label = tk.Label(root, text="Enter ingredients (comma-separated):", font=("Arial", 12), bg="#f4f4f4")
label.pack(pady=5)

# Bigger, styled text entry field
entry = tk.Entry(root, width=50, font=("Arial", 14), bg="white", fg="black", bd=3, relief="sunken")
entry.pack(pady=10, ipadx=10, ipady=5)

# Styled submit button
submit_button = tk.Button(
    root, 
    text="Get AI Suggestions", 
    command=on_submit,
    font=("Arial", 12, "bold"),  
    bg="#4CAF50",  # Green background
    fg="white",  
    padx=20,  
    pady=5,  
    borderwidth=3,  
    relief="raised"  
)
submit_button.pack(pady=10)

# Result display using Text widget (instead of Label)
result_text_widget = tk.Text(
    root, 
    font=("Arial", 14),  # Bigger text
    fg="#333",  
    bg="#f4f4f4",
    wrap="word",  # Wrap text properly
    padx=10,  
    pady=10,  
    bd=2,  
    relief="groove",
    height=5,  # Initial height
)
result_text_widget.pack(pady=20, fill="both", padx=20)

# Default message inside Text widget
result_text_widget.insert("1.0", "Your AI-generated recipe suggestions will appear here.")  

# Run the application
root.mainloop()
