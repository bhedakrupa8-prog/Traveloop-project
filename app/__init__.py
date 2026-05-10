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
    def inject_user():
        from flask import session
        from app.models.user import User
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            return dict(user=user)
        return dict(user=None)

    return app
