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
    from datetime import datetime
    for trip in user_trips:
        if trip.start_date:
            # use a tuple to sort properly, or just format
            m_key = trip.start_date.strftime("%Y-%m")
            m_label = trip.start_date.strftime("%b %Y")
            if m_key not in months_data:
                months_data[m_key] = {'label': m_label, 'count': 0}
            months_data[m_key]['count'] += 1
            
    # Sort months chronologically by the YYYY-MM key
    sorted_months = sorted(months_data.keys())
    month_labels = [months_data[m]['label'] for m in sorted_months]
    month_data = [months_data[m]['count'] for m in sorted_months]
    
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

import csv
from io import StringIO
from flask import Response

@analytics_bp.route('/export', methods=['GET'])
def export_report():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    user_trips = Trip.query.filter_by(user_id=user_id).all()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Trip Name', 'Start Date', 'End Date', 'Type', 'Status', 'Total Estimated Budget', 'Total Actual Expense'])
    
    for trip in user_trips:
        est_budget = sum(b.estimated_cost for b in trip.budgets) if trip.budgets else 0
        act_budget = sum(b.actual_cost for b in trip.budgets) if trip.budgets else 0
        cw.writerow([
            trip.name, 
            trip.start_date.strftime('%Y-%m-%d') if trip.start_date else '', 
            trip.end_date.strftime('%Y-%m-%d') if trip.end_date else '', 
            trip.trip_type,
            trip.status,
            est_budget,
            act_budget
        ])
        
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=traveloop_analytics_report.csv"}
    )

