from flask_sqlalchemy import SQLAlchemy
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash  # Add this line

db = SQLAlchemy()


class User(db.Model, UserMixin):  # Inherit from UserMixin
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Store hashed passwords
    races = db.relationship('Race', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # flask_login required methods (provided by UserMixin)
    @property
    def is_active(self):
        return True  # All accounts are active by default in this example

    @property
    def is_authenticated(self):
        return True  # User is considered authenticated if logged in

    @property
    def is_anonymous(self):
        return False  # Not an anonymous user

    def get_id(self):
        return str(self.id)

class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    
    players = db.Column(db.Text)  # JSON formatted players data
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def get_players(self):
        # Converts players data from JSON text to Python list
        return json.loads(self.players)
