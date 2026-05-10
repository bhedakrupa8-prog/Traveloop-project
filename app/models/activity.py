from app.extensions import db

class Activity(db.Model):
    def __init__(self, **kwargs):
        super(Activity, self).__init__(**kwargs)

    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_stop_id = db.Column(db.Integer, db.ForeignKey('trip_stops.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True) # Adventure, Food, Sightseeing, etc.
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    estimated_cost = db.Column(db.Float, default=0.0)
