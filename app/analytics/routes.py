from flask import render_template, session, redirect, url_for, request, flash
from app.analytics import analytics_bp
from app.models.trip import Trip, TripStop
from app.models.budget import Budget
from app.models.user import User
from app.extensions import db
from sqlalchemy import func

@analytics_bp.route('/', methods=['GET'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    user = User.query.get(user_id)
    if user and user.is_admin:
        return redirect(url_for('analytics.admin_dashboard'))
        
    # Base queries
    user_trips = Trip.query.filter_by(user_id=user_id).all()
    trip_ids = [t.id for t in user_trips]
    
    # 1. Total Trips
    total_trips = len(user_trips)
    
    # 2. Total Countries
    total_countries = db.session.query(func.count(func.distinct(TripStop.country))).filter(TripStop.trip_id.in_(trip_ids) if trip_ids else False).scalar() or 0
    
    # 3. Total Expense
    total_expense = db.session.query(func.sum(Budget.actual_cost)).filter(Budget.trip_id.in_(trip_ids) if trip_ids else False).scalar() or 0
    
    # 4. Expense by Category
    category_expenses = db.session.query(
        Budget.category, func.sum(Budget.actual_cost)
    ).filter(Budget.trip_id.in_(trip_ids) if trip_ids else False).group_by(Budget.category).all()
    
    cat_labels = [c[0] for c in category_expenses]
    cat_data = [float(c[1]) for c in category_expenses]
    
    # 5. Trips per month (based on start date)
    months_data = {}
    for trip in user_trips:
        if trip.start_date:
            m = trip.start_date.strftime("%Y-%m")
            months_data[m] = months_data.get(m, 0) + 1
            
    # Sort months
    sorted_months = sorted(months_data.keys())
    month_labels = sorted_months
    month_data = [months_data[m] for m in sorted_months]
    
    return render_template(
        'analytics/index.html',
        total_trips=total_trips,
        total_countries=total_countries,
        total_expense=total_expense,
        cat_labels=cat_labels,
        cat_data=cat_data,
        month_labels=month_labels,
        month_data=month_data
    )

@analytics_bp.route('/admin', methods=['GET'])
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        flash("You do not have permission to access the admin dashboard.", "danger")
        return redirect(url_for('main.index'))
        
    total_users = User.query.count()
    total_trips = Trip.query.count()
    
    top_cities = db.session.query(TripStop.city, func.count(TripStop.id).label('count')).group_by(TripStop.city).order_by(db.text('count DESC')).limit(5).all()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template(
        'analytics/admin.html',
        total_users=total_users,
        total_trips=total_trips,
        top_cities=top_cities,
        recent_users=recent_users
    )

