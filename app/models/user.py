from app.extensions import db
from datetime import datetime

class User(db.Model):
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    trips = db.relationship('Trip', backref='owner', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"
