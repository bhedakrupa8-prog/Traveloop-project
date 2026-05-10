from flask import render_template, session, redirect, url_for
from app.main import main_bp
from app.models.trip import Trip
from app.models.user import User

@main_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.get(session['user_id'])
    trips = Trip.query.filter_by(user_id=user.id).order_by(Trip.start_date.asc()).limit(3).all()
    
    # Calculate some dashboard stats
    total_trips = Trip.query.filter_by(user_id=user.id).count()
    
    return render_template('dashboard.html', user=user, trips=trips, total_trips=total_trips)

@main_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)
