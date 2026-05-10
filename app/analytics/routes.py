from flask import render_template, session, redirect, url_for
from app.analytics import analytics_bp
from app.models.trip import Trip, TripStop
from app.models.budget import Budget
from app.extensions import db
from sqlalchemy import func

@analytics_bp.route('/', methods=['GET'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    
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
