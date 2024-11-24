from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # Use environment variable

# Database configuration
DATABASE = 'users.db'

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Allows fetching rows as dictionaries
    return conn

# Initialize the database
def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            first_name TEXT NOT NULL,
                            last_name TEXT NOT NULL,
                            mobile TEXT UNIQUE NOT NULL,
                            email TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL
                        );''')
    conn.close()

# Create the database table when the app starts
init_db()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        mobile = request.form['mobile']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        if password != confirm_password:
            flash("Passwords do not match. Please try again.")
            return redirect(url_for('register'))

        conn = get_db_connection()
        try:
            with conn:
                # Check if email or mobile already exists
                existing_user = conn.execute('SELECT * FROM users WHERE email = ? OR mobile = ?', 
                                             (email, mobile)).fetchone()
                if existing_user:
                    flash("Email or mobile number already registered.")
                    return redirect(url_for('register'))

                # Insert new user
                conn.execute('INSERT INTO users (first_name, last_name, mobile, email, password) VALUES (?, ?, ?, ?, ?)',
                             (first_name, last_name, mobile, email, password))
                flash("Registration successful! Please login.")
                return redirect(url_for('login'))
        except sqlite3.Error as e:
            flash(f"An error occurred: {e}")
        finally:
            conn.close()

    return render_template('registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        try:
            user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                                (email, password)).fetchone()
            if user:
                flash("Login successful!")
                return redirect(url_for('home'))
            else:
                flash("Invalid email or password.")
        except sqlite3.Error as e:
            flash(f"An error occurred: {e}")
        finally:
            conn.close()

    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
