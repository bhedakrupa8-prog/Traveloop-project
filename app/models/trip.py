from app.extensions import db
from datetime import datetime

class Trip(db.Model):
    def __init__(self, **kwargs):
        super(Trip, self).__init__(**kwargs)

    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    cover_image = db.Column(db.String(255), nullable=True)
    trip_type = db.Column(db.String(50), default='Personal') # Personal, Business
    status = db.Column(db.String(50), default='Upcoming') # Upcoming, Active, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stops = db.relationship('TripStop', backref='trip', lazy=True, cascade="all, delete-orphan", order_by="TripStop.order")
    budgets = db.relationship('Budget', backref='trip', lazy=True, cascade="all, delete-orphan")
    packing_items = db.relationship('PackingItem', backref='trip', lazy=True, cascade="all, delete-orphan")
    notes = db.relationship('TripNote', backref='trip', lazy=True, cascade="all, delete-orphan")

class TripStop(db.Model):
    def __init__(self, **kwargs):
        super(TripStop, self).__init__(**kwargs)

    __tablename__ = 'trip_stops'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    order = db.Column(db.Integer, default=0)
    
    # Relationships
    activities = db.relationship('Activity', backref='trip_stop', lazy=True, cascade="all, delete-orphan", order_by="Activity.start_time")

class TripNote(db.Model):
    def __init__(self, **kwargs):
        super(TripNote, self).__init__(**kwargs)

    __tablename__ = 'trip_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False, default="Untitled Note")
    content = db.Column(db.Text, nullable=True)
    note_type = db.Column(db.String(50), default='General')
    is_pinned = db.Column(db.Boolean, default=False)
    reminder_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
