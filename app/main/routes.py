from flask import render_template, session, redirect, url_for, request, flash
from app.main import main_bp
from app.models.trip import Trip
from app.models.user import User
from app.extensions import db

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

@main_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.username = request.form.get('username', user.username)
        user.language_preference = request.form.get('language', user.language_preference)
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile.', 'danger')
        return redirect(url_for('main.profile'))
        
    return render_template('profile.html', user=user)

@main_bp.route('/profile/delete', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    if user:
        try:
            db.session.delete(user)
            db.session.commit()
            session.clear()
            flash('Your account has been deleted.', 'success')
        except Exception:
            db.session.rollback()
            flash('Error deleting account.', 'danger')
    return redirect(url_for('main.index'))

