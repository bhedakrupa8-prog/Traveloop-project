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
    
    from app.models.trip import TripStop
    from app.models.activity import Activity
    
    from datetime import date
    from app.models.packing import PackingItem
    
    # Financial data
    all_trips = Trip.query.filter_by(user_id=user.id).all()
    trip_ids = [t.id for t in all_trips]
    
    total_spent = 0
    total_estimated = 0
    category_totals = {'Stay': 0, 'Transport': 0, 'Food': 0, 'Activities': 0, 'Other': 0}
    
    for t in all_trips:
        for b in t.budgets:
            total_spent += b.actual_cost
            total_estimated += b.estimated_cost
            cat = b.category if b.category in category_totals else 'Other'
            category_totals[cat] += b.actual_cost
            
    budget_savings_pct = 0
    if total_estimated > 0:
        budget_savings_pct = int(((total_estimated - total_spent) / total_estimated) * 100)
        
    # Additional Stats
    from sqlalchemy import func
    from app.extensions import db
    total_countries = db.session.query(func.count(func.distinct(TripStop.country))).filter(TripStop.trip_id.in_(trip_ids) if trip_ids else False).scalar() or 0
    
    total_activities = db.session.query(func.count(Activity.id)).join(TripStop).filter(TripStop.trip_id.in_(trip_ids) if trip_ids else False).scalar() or 0
    
    upcoming_trips = Trip.query.filter_by(user_id=user.id, status='Upcoming').count()
    saved_destinations = TripStop.query.filter(TripStop.trip_id.in_(trip_ids) if trip_ids else False).count()
    
    # Dynamic Insights
    insight_budget = None
    if all_trips:
        if total_estimated > 0:
            savings = total_estimated - total_spent
            if savings >= 0:
                insight_budget = {
                    'status': 'success',
                    'icon': 'fa-circle-check',
                    'title': 'Budget on Track',
                    'message': f'Your trips are {budget_savings_pct}% under budget overall. You have ₹{"{:,.0f}".format(savings)} remaining.'
                }
            else:
                insight_budget = {
                    'status': 'danger',
                    'icon': 'fa-triangle-exclamation',
                    'title': 'Over Budget',
                    'message': f'You are {abs(budget_savings_pct)}% over budget. Consider reviewing your expenses.'
                }
        else:
            insight_budget = {
                'status': 'warning',
                'icon': 'fa-circle-info',
                'title': 'No Budgets Set',
                'message': 'You haven\'t set estimated budgets for your trips. Set them to track savings.'
            }
    else:
        insight_budget = {
            'status': 'warning',
            'icon': 'fa-wallet',
            'title': 'No Trips Yet',
            'message': 'Plan a trip and add a budget to see insights here.'
        }
        
    insight_packing = None
    upcoming_trip = Trip.query.filter(Trip.user_id==user.id, Trip.start_date >= date.today()).order_by(Trip.start_date.asc()).first()
    if upcoming_trip:
        days_until = (upcoming_trip.start_date - date.today()).days
        total_items = PackingItem.query.filter_by(trip_id=upcoming_trip.id).count()
        if total_items > 0:
            packed_items = PackingItem.query.filter_by(trip_id=upcoming_trip.id, is_packed=True).count()
            pct_packed = int((packed_items / total_items) * 100)
            if pct_packed == 100:
                insight_packing = {
                    'status': 'success',
                    'icon': 'fa-suitcase',
                    'title': 'Fully Packed',
                    'message': f'Your packing checklist for "{upcoming_trip.name}" is complete. Trip is in {days_until} days.'
                }
            else:
                insight_packing = {
                    'status': 'warning',
                    'icon': 'fa-triangle-exclamation',
                    'title': 'Packing Incomplete',
                    'message': f'Your packing checklist for "{upcoming_trip.name}" is only {pct_packed}% complete. Trip is in {days_until} days.'
                }
        else:
            insight_packing = {
                'status': 'warning',
                'icon': 'fa-suitcase-rolling',
                'title': 'No Packing List',
                'message': f'You haven\'t started a packing list for "{upcoming_trip.name}". Trip starts in {days_until} days.'
            }
    else:
        insight_packing = {
            'status': 'success',
            'icon': 'fa-plane',
            'title': 'Ready for a new adventure',
            'message': 'Plan your next trip to start tracking your packing checklist.'
        }
    
    # Dynamic Recent Activity (Mocked timestamps, but real data)
    recent_activities = []
    from app.models.activity import Activity
    from app.models.budget import Budget
    from app.models.packing import PackingItem
    from app.models.trip import TripStop
    
    if all_trips:
        latest_trip = all_trips[-1]
        
        # 1. Activity
        act = Activity.query.join(TripStop).filter(TripStop.trip_id == latest_trip.id).first()
        if act:
            recent_activities.append({
                'title': f'{act.title}',
                'type': 'Activity',
                'type_class': 'success',
                'desc': f'Added in "{latest_trip.name}"',
                'time': 'Recently'
            })
            
        # 2. Expense
        bud = Budget.query.filter_by(trip_id=latest_trip.id).first()
        if bud and bud.estimated_cost > 0:
            recent_activities.append({
                'title': f'{bud.category} Expense',
                'type': 'Expense',
                'type_class': 'primary',
                'desc': f'Logged ₹{bud.estimated_cost} estimated cost',
                'time': 'Recently'
            })
            
        # 3. Task (Packing)
        pack = PackingItem.query.filter_by(trip_id=latest_trip.id, is_packed=True).first()
        if pack:
            recent_activities.append({
                'title': 'Packing List Updated',
                'type': 'Task',
                'type_class': 'warning',
                'desc': f'Marked "{pack.item_name}" as packed',
                'time': 'Recently'
            })
            
    # Dynamic Weather Preview
    weather_destinations = []
    if upcoming_trip:
        stops = TripStop.query.filter_by(trip_id=upcoming_trip.id).order_by(TripStop.order).limit(2).all()
        import random
        for stop in stops:
            # Randomizing a bit for realism since we don't have a live API integration yet
            temp = random.randint(20, 32)
            weather_destinations.append({
                'city': stop.city,
                'country': stop.country,
                'temp': temp,
                'condition': 'Clear sky' if temp > 25 else 'Partly cloudy',
                'icon': 'fa-cloud-sun' if temp > 25 else 'fa-cloud',
                'bg_image': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=400&q=80' if 'Paris' in stop.city else 'https://images.unsplash.com/photo-1517736996303-4e64a4f87311?auto=format&fit=crop&w=400&q=80'
            })
    
    if not weather_destinations:
        # Fallback if no upcoming trips
        weather_destinations = [
            {'city': 'Paris', 'country': 'FR', 'temp': 22, 'condition': 'Perfect for sightseeing', 'icon': 'fa-cloud-sun', 'bg_image': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=400&q=80'},
            {'city': 'Amsterdam', 'country': 'NL', 'temp': 16, 'condition': 'Light rain expected', 'icon': 'fa-cloud-rain', 'bg_image': 'https://images.unsplash.com/photo-1517736996303-4e64a4f87311?auto=format&fit=crop&w=400&q=80'}
        ]
    
    return render_template('dashboard.html', user=user, trips=trips, total_trips=total_trips,
                           total_spent=total_spent, total_estimated=total_estimated,
                           budget_savings_pct=budget_savings_pct, category_totals=category_totals,
                           total_countries=total_countries, total_activities=total_activities,
                           upcoming_trips=upcoming_trips, saved_destinations=saved_destinations,
                           insight_budget=insight_budget, insight_packing=insight_packing,
                           recent_activities=recent_activities, weather_destinations=weather_destinations)

from flask import request, flash

@main_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    from app.extensions import db
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        new_name = request.form.get('username')
        if new_name and new_name.strip():
            user.username = new_name.strip()
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
        
    return render_template('profile.html', user=user)

@main_bp.route('/profile/delete', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    from app.extensions import db
    user = User.query.get(session['user_id'])
    if user:
        db.session.delete(user)
        db.session.commit()
        session.clear()
        flash('Your account has been deleted.', 'info')
        
    return redirect(url_for('main.index'))
