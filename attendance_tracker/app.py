from flask import Flask, render_template, request, redirect, url_for, flash
import csv
from datetime import datetime
import os # Import os module for path operations

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_flash_messages' # Required for flash messages

# Define the path for the CSV file relative to the app's root
# This makes it more robust if you run the app from a different directory
CSV_FILE_PATH = os.path.join(app.root_path, 'attendance.csv')

def init_csv():
    """Ensures the CSV file exists and has the correct headers."""
    # Check if the file exists before attempting to create
    if not os.path.exists(CSV_FILE_PATH):
        try:
            with open(CSV_FILE_PATH, 'x', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Date', 'Time'])
            print(f"CSV file '{CSV_FILE_PATH}' created with headers.")
        except IOError as e:
            print(f"Error creating CSV file: {e}")
    else:
        print(f"CSV file '{CSV_FILE_PATH}' already exists.")

@app.route('/')
def index():
    """Renders the main attendance marking page."""
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    """Handles the attendance submission."""
    name = request.form.get('name') # Use .get() for safer access

    if not name:
        flash('Name cannot be empty!', 'error') # Provide user feedback
        return redirect(url_for('index')) # Redirect back to the form

    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M:%S')

    try:
        with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([name, current_date, current_time])
        flash(f"Attendance marked for {name}!", 'success') # Success message
    except IOError as e:
        flash(f"Error marking attendance: {e}", 'error') # Error message
        print(f"Error writing to CSV: {e}")

    return redirect(url_for('dashboard')) # Use url_for for better practice

@app.route('/dashboard')
def dashboard():
    """Renders the attendance dashboard."""
    records = []
    try:
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header row safely
            records = list(reader)
    except FileNotFoundError:
        flash("Attendance file not found. Please mark some attendance!", 'warning')
        print(f"CSV file '{CSV_FILE_PATH}' not found when trying to read.")
    except Exception as e:
        flash(f"Error loading dashboard: {e}", 'error')
        print(f"Error reading CSV file: {e}")

    return render_template('dashboard.html', records=records)

if __name__ == '__main__':
    init_csv() # Initialize CSV before running the app
    app.run(debug=True)