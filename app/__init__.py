from flask import Flask, render_template
from app.config import Config
from app.extensions import db, migrate, bcrypt, jwt, cors, ma
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    ma.init_app(app)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register Blueprints
    from app.auth.routes import auth_bp
    from app.trips.routes import trips_bp
    from app.main.routes import main_bp
    from app.notes import notes_bp
    from app.analytics import analytics_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(trips_bp, url_prefix='/trips')
    app.register_blueprint(notes_bp, url_prefix='/notes')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_notifications():
        from flask import session
        notifications = []
        if 'user_id' in session:
            user_id = session['user_id']
            from app.models.trip import Trip
            from app.models.packing import PackingItem
            from datetime import date
            
            # Check for upcoming trips within 7 days
            upcoming_trips = Trip.query.filter(Trip.user_id==user_id, Trip.start_date >= date.today()).all()
            for trip in upcoming_trips:
                days_until = (trip.start_date - date.today()).days
                if days_until <= 7:
                    notifications.append({
                        'type': 'primary',
                        'icon': 'fa-plane-arrival',
                        'message': f'Your trip to {trip.name} starts in {days_until} days!' if days_until > 0 else f'Your trip to {trip.name} starts today!',
                        'time': 'Just now'
                    })
                    
                    # Also check for unpacked items for this trip
                    unpacked_count = PackingItem.query.filter_by(trip_id=trip.id, is_packed=False).count()
                    if unpacked_count > 0:
                        notifications.append({
                            'type': 'warning',
                            'icon': 'fa-triangle-exclamation',
                            'message': f'You have {unpacked_count} unpacked item{"s" if unpacked_count > 1 else ""} for {trip.name}.',
                            'time': 'Just now'
                        })
        return dict(notifications=notifications)

    return app
