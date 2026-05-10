from app.extensions import db

class Budget(db.Model):
    def __init__(self, **kwargs):
        super(Budget, self).__init__(**kwargs)

    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False) # Stay, Transport, Food, Activities
    estimated_cost = db.Column(db.Float, default=0.0)
    actual_cost = db.Column(db.Float, default=0.0)
