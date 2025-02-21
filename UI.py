from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from main import get_ai_suggestions  # Importing the get_ai_suggestions from main.py

# Function to adjust the size of the Text widget dynamically
def adjust_text_widget_size():
    """Dynamically adjust the height of the text widget to fit content."""
    num_lines = len(result_text_widget.toPlainText().split("\n"))
    new_height = min(max(num_lines, 5), 20)  # Set a range between 5 and 20 lines
    result_text_widget.setFixedHeight(new_height * 30)  # Adjust height dynamically

# Function to handle button click
def on_submit():
    ingredients = entry.text().strip()  # Get input from text field
    if not ingredients:
        result_text_widget.clear()  # Clear previous text
        result_text_widget.setPlainText("Please enter some ingredients.")  # Show error message
        adjust_text_widget_size()  # Adjust box size
        return

    result_text_widget.clear()  # Clear previous results
    result_text_widget.setPlainText("AI Suggestions loading...\n")  # Show loading text
    app.processEvents()  # Refresh UI

    ingredients_list = ingredients.split(", ")  # Convert input to a list

    # Fetch AI suggestions using the imported method
    suggestions = get_ai_suggestions(ingredients_list)

    if suggestions:
        result = (f"Dish Name:\n  {suggestions['dish_name']}\n\n"
                  f"➕ Add for Calories:\n  {', '.join(suggestions['add_calories'])}\n\n"
                  f"➖ Remove for Calories:\n  {', '.join(suggestions['remove_calories'])}\n\n"
                  f"💪 Add for Health:\n  {', '.join(suggestions['add_health'])}\n\n"
                  f"🚫 Remove for Health:\n  {', '.join(suggestions['remove_health'])}")
        result_text_widget.clear()
        result_text_widget.setPlainText(result)
    else:
        result_text_widget.clear()
        result_text_widget.setPlainText("Error: AI response could not be generated.")

    adjust_text_widget_size()  # Adjust text box size dynamically

# PyQt5 Application Setup
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QWidget()
window.setWindowTitle("AI Recipe Helper")
window.resize(700, 600)
window.setStyleSheet("""
    QWidget {
        background-color: #2C2F36;
        color: white;
        font-family: Arial;
    }
    QPushButton {
        background-color: #4CAF50;
        border-radius: 15px;
        padding: 10px 20px;
        font-weight: bold;
        color: white;
    }
    QLineEdit {
        background-color: #444c56;
        border-radius: 15px;
        padding: 10px;
        font-size: 14px;
    }
    QTextEdit {
        background-color: #444c56;
        color: white;
        border-radius: 15px;
        padding: 10px;
    }
    QLabel {
        font-size: 14px;
        color: white;
    }
""")

# Layout setup
layout = QtWidgets.QVBoxLayout(window)

# Input field label
label = QtWidgets.QLabel("Enter ingredients (comma-separated):")
layout.addWidget(label)

# Input field with rounded corners
entry = QtWidgets.QLineEdit()
layout.addWidget(entry)

# Submit button with rounded corners
submit_button = QtWidgets.QPushButton("Get AI Suggestions")
submit_button.clicked.connect(on_submit)
layout.addWidget(submit_button)

# Result display using QTextEdit (for multiline text with dynamic height)
result_text_widget = QtWidgets.QTextEdit()
result_text_widget.setPlainText("Your AI-generated recipe suggestions will appear here.")
result_text_widget.setReadOnly(True)
layout.addWidget(result_text_widget)

window.setLayout(layout)

# Run the application
window.show()
sys.exit(app.exec_())
