from app.extensions import db

class PackingItem(db.Model):
    def __init__(self, **kwargs):
        super(PackingItem, self).__init__(**kwargs)

    __tablename__ = 'packing_items'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True) # Clothing, Electronics, Documents
    is_packed = db.Column(db.Boolean, default=False)
