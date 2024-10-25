from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Race
import json, os
import csv
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash  # At the top of app.py
from werkzeug.security import check_password_hash  # Also import check_password_hash if not already


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db.init_app(app)
app.secret_key = "ureiqshyeiogveysogvweyrgvbeorvbehoqrvbhqervbhqewugfyewqtgr643tr5629341tr781023trygfugcfgyue7t91f1gtgte"
app.config['PERMANENT_SESSION_LIFETIME'] = 1800
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
with app.app_context():
    db.create_all()  # Initialize the database

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to the login page if not authenticated

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Load user by ID for flask_login


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find the user
        user = User.query.filter_by(username=username).first()
        
        # Validate the password
        if user and user.check_password(password):
            login_user(user)
            session["name"] = username
            return redirect(url_for('index'))  # Redirect to homepage after successful login
        else:
            return "Invalid username or password."  # Show an error message if invalid

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session["name"] = None
    return redirect(url_for('index'))


# Homepage
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

# File upload
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        username = request.form['username']
        file = request.files['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Parse file and save data
        race_data = parse_simulation_file(file_path)
        user = User.query.filter_by(username=username).first() or User(username=username)
        db.session.add(user)

        race = Race(date=race_data['date'], players=json.dumps(race_data['players']), user=user)
        db.session.add(race)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('upload.html')

def parse_simulation_file(file_path):
    players = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            player_data = {
                "uuid": row["UUID"],
                "place": int(row["Place"]),
                "distance_travelled": float(row["Distance Travelled"]),
                "score": int(row["Score"]),
                "total_distance": float(row["Total Distance"]),
                "rounds": int(row["Rounds"]),
                "date": row["Date"],
                "time": row["Time"]
            }
            players.append(player_data)
    
    # Extract date and time from the first entry (as the race date)
    race_date = players[0]["date"] if players else "Unknown"
    
    return {"date": race_date, "players": players}


# User profile
@app.route('/users/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    races = Race.query.filter_by(user_id=user.id).all()
    return render_template('user.html', user=user, races=races)

@app.route('/search_users', methods=['GET'])
def search_users():
    query = request.args.get('query')
    if query:
        users = User.query.filter(User.username.like(f'%{query}%')).all()
    else:
        users = User.query.all()
    return render_template('index.html', users=users, query=query)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already taken, please choose another."

        # Create new user with hashed password
        new_user = User(username=username)
        new_user.set_password(password)
        
        # Add and commit the new user to the database
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('index'))

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
