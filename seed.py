from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.trip import Trip, TripStop
from app.models.budget import Budget
from app.models.packing import PackingItem
from datetime import date, timedelta

app = create_app()

def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("Seeding database...")

        # Create Demo User
        hashed_password = bcrypt.generate_password_hash("password123").decode('utf-8')
        demo_user = User(username="demouser", email="demo@traveloop.com", password_hash=hashed_password)
        db.session.add(demo_user)
        db.session.commit()

        # Create Trip
        today = date.today()
        trip = Trip(
            user_id=demo_user.id,
            name="Euro Trip 2026",
            description="A beautiful summer trip across Western Europe.",
            start_date=today + timedelta(days=30),
            end_date=today + timedelta(days=45)
        )
        db.session.add(trip)
        db.session.commit()

        # Add Stops
        stop1 = TripStop(trip_id=trip.id, city="Paris", country="France", start_date=today + timedelta(days=30), end_date=today + timedelta(days=35), order=1)
        stop2 = TripStop(trip_id=trip.id, city="Amsterdam", country="Netherlands", start_date=today + timedelta(days=35), end_date=today + timedelta(days=40), order=2)
        stop3 = TripStop(trip_id=trip.id, city="Berlin", country="Germany", start_date=today + timedelta(days=40), end_date=today + timedelta(days=45), order=3)
        db.session.add_all([stop1, stop2, stop3])

        # Add Budget
        b1 = Budget(trip_id=trip.id, category="Stay", estimated_cost=1500.0, actual_cost=1450.0)
        b2 = Budget(trip_id=trip.id, category="Transport", estimated_cost=800.0, actual_cost=850.0)
        b3 = Budget(trip_id=trip.id, category="Food", estimated_cost=1000.0, actual_cost=0.0)
        db.session.add_all([b1, b2, b3])

        # Add Packing Items
        p1 = PackingItem(trip_id=trip.id, item_name="Passport", category="Documents", is_packed=True)
        p2 = PackingItem(trip_id=trip.id, item_name="Jackets", category="Clothing", is_packed=False)
        p3 = PackingItem(trip_id=trip.id, item_name="Power Bank", category="Electronics", is_packed=False)
        db.session.add_all([p1, p2, p3])

        db.session.commit()
        print("Database seeded successfully! Login with demo@traveloop.com / password123")

if __name__ == "__main__":
    seed_data()
