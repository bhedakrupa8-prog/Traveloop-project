from flask import Blueprint

trips_bp = Blueprint('trips', __name__)

from app.trips import routes
