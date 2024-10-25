from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Race
import json, os
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db.init_app(app)

with app.app_context():
    db.create_all()  # Initialize the database

# Homepage
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

# File upload
@app.route('/upload', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
