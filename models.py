from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    races = db.relationship('Race', backref='user', lazy=True)

class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    players = db.Column(db.Text)  # JSON formatted players data
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def get_players(self):
        # Converts players data from JSON text to Python list
        return json.loads(self.players)
