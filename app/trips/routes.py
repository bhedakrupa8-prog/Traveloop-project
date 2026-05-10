from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app.trips import trips_bp
from app.models.trip import Trip, TripStop, TripNote
from app.models.activity import Activity
from app.models.budget import Budget
from app.models.packing import PackingItem
from app.extensions import db
from datetime import datetime

# -------------- UI Routes --------------

@trips_bp.route('/', methods=['GET'])
def list_trips():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    
    # AJAX Request Handler
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        tab = request.args.get('tab', 'all')
        q = request.args.get('q', '').lower()
        sort = request.args.get('sort', 'newest')
        
        query = Trip.query.filter_by(user_id=session['user_id'])
        
        # Tabs
        today = datetime.utcnow().date()
        if tab == 'upcoming':
            query = query.filter(Trip.start_date >= today)
        elif tab == 'past':
            query = query.filter(Trip.end_date < today)
        elif tab == 'business':
            query = query.filter(Trip.trip_type == 'Business')
            
        # Search
        if q:
            query = query.filter(Trip.name.ilike(f'%{q}%'))
            
        # Sort
        if sort == 'newest':
            query = query.order_by(Trip.created_at.desc())
        elif sort == 'oldest':
            query = query.order_by(Trip.created_at.asc())
        elif sort == 'upcoming':
            query = query.order_by(Trip.start_date.asc())
        elif sort == 'updated':
            query = query.order_by(Trip.updated_at.desc())
        else:
            query = query.order_by(Trip.start_date.desc())
            
        trips = query.all()
        
        trip_data = []
        for t in trips:
            # Calculate budget
            est_budget = sum(b.estimated_cost for b in t.budgets) if t.budgets else 0
            
            # Progress
            total_items = len(t.packing_items)
            packed = sum(1 for p in t.packing_items if p.is_packed)
            progress = int((packed / total_items) * 100) if total_items > 0 else 0
            
            trip_data.append({
                "id": t.id,
                "name": t.name,
                "start_date": t.start_date.strftime('%b %d, %Y'),
                "end_date": t.end_date.strftime('%b %d, %Y'),
                "days": (t.end_date - t.start_date).days + 1,
                "cover_image": t.cover_image or "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=600&q=80",
                "status": t.status,
                "trip_type": t.trip_type,
                "budget": est_budget,
                "progress": progress
            })
            
        return jsonify({"trips": trip_data})
        
    return render_template('trips/list.html')

@trips_bp.route('/create', methods=['GET', 'POST'])
def create_trip():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        try:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = datetime.strptime(start_date_str, '%d-%m-%Y').date()
                
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                end_date = datetime.strptime(end_date_str, '%d-%m-%Y').date()
            
            new_trip = Trip(
                user_id=session['user_id'],
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date
            )
            db.session.add(new_trip)
            db.session.commit()
            
            flash('Trip created successfully!', 'success')
            return redirect(url_for('trips.view_trip', trip_id=new_trip.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating trip: {str(e)}', 'danger')
            
    return render_template('trips/create.html')

@trips_bp.route('/<int:trip_id>', methods=['GET'])
def view_trip(trip_id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    trip = Trip.query.filter_by(id=trip_id, user_id=session['user_id']).first_or_404()
    return render_template('trips/view.html', trip=trip)

@trips_bp.route('/itinerary', defaults={'trip_id': None}, methods=['GET'])
@trips_bp.route('/<int:trip_id>/itinerary', methods=['GET'])
def itinerary(trip_id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    if trip_id is None:
        trip = Trip.query.filter_by(user_id=session['user_id']).order_by(Trip.start_date.desc()).first()
        if not trip:
            flash("Create a trip first to use the itinerary builder.", "info")
            return redirect(url_for('trips.create_trip'))
        return redirect(url_for('trips.itinerary', trip_id=trip.id))
        
    trip = Trip.query.filter_by(id=trip_id, user_id=session['user_id']).first_or_404()
    return render_template('trips/itinerary.html', trip=trip)

@trips_bp.route('/budget', defaults={'trip_id': None}, methods=['GET'])
@trips_bp.route('/<int:trip_id>/budget', methods=['GET'])
def budget(trip_id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    if trip_id is None:
        trip = Trip.query.filter_by(user_id=session['user_id']).order_by(Trip.start_date.desc()).first()
        if not trip:
            flash("Create a trip first to track budgets.", "info")
            return redirect(url_for('trips.create_trip'))
        return redirect(url_for('trips.budget', trip_id=trip.id))
        
    trip = Trip.query.filter_by(id=trip_id, user_id=session['user_id']).first_or_404()
    return render_template('trips/budget.html', trip=trip)

@trips_bp.route('/packing', defaults={'trip_id': None}, methods=['GET'])
@trips_bp.route('/<int:trip_id>/packing', methods=['GET'])
def packing(trip_id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    if trip_id is None:
        trip = Trip.query.filter_by(user_id=session['user_id']).order_by(Trip.start_date.desc()).first()
        if not trip:
            flash("Create a trip first to manage packing lists.", "info")
            return redirect(url_for('trips.create_trip'))
        return redirect(url_for('trips.packing', trip_id=trip.id))
        
    trip = Trip.query.filter_by(id=trip_id, user_id=session['user_id']).first_or_404()
    return render_template('trips/packing.html', trip=trip)

@trips_bp.route('/<int:trip_id>/notes', methods=['GET'])
def notes(trip_id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    trip = Trip.query.filter_by(id=trip_id, user_id=session['user_id']).first_or_404()
    return render_template('trips/notes.html', trip=trip)

@trips_bp.route('/public/<int:trip_id>', methods=['GET'])
def public_view(trip_id):
    # No auth required, this is the public shareable link
    trip = Trip.query.get_or_404(trip_id)
    return render_template('trips/public.html', trip=trip)

# -------------- API Routes --------------

@trips_bp.route('/api/<int:trip_id>/stops', methods=['POST'])
def add_stop(trip_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        new_stop = TripStop(
            trip_id=trip_id,
            city=data['city'],
            country=data['country'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        )
        db.session.add(new_stop)
        db.session.commit()
        return jsonify({"success": True, "id": new_stop.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@trips_bp.route('/api/<int:trip_id>/packing', methods=['POST'])
def add_packing_item(trip_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    try:
        item = PackingItem(
            trip_id=trip_id,
            item_name=data['item_name'],
            category=data.get('category', 'General')
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({"success": True, "id": item.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@trips_bp.route('/api/packing/<int:item_id>/toggle', methods=['POST'])
def toggle_packing_item(item_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    item = PackingItem.query.get_or_404(item_id)
    # Basic security check
    if item.trip.user_id != session['user_id']:
        return jsonify({"error": "Unauthorized"}), 403
        
    item.is_packed = not item.is_packed
    db.session.commit()
    return jsonify({"success": True, "is_packed": item.is_packed})
    
@trips_bp.route('/api/packing/<int:item_id>', methods=['DELETE'])
def delete_packing_item(item_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    item = PackingItem.query.get_or_404(item_id)
    if item.trip.user_id != session['user_id']:
        return jsonify({"error": "Unauthorized"}), 403
        
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@trips_bp.route('/api/<int:trip_id>/budget', methods=['POST'])
def add_budget(trip_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    try:
        item = Budget(
            trip_id=trip_id,
            category=data['category'],
            estimated_cost=float(data['estimated_cost']),
            actual_cost=float(data.get('actual_cost', 0))
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({"success": True, "id": item.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@trips_bp.route('/api/<int:trip_id>/stops/<int:stop_id>/activities', methods=['POST'])
def add_activity(trip_id, stop_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    # Verify ownership
    trip = Trip.query.filter_by(id=trip_id, user_id=session['user_id']).first()
    if not trip: return jsonify({"error": "Not found"}), 404
    
    data = request.json
    try:
        new_activity = Activity(
            trip_stop_id=stop_id,
            title=data['title'],
            description=data.get('description', ''),
            category=data.get('category', 'General'),
            estimated_cost=float(data.get('estimated_cost', 0))
        )
        db.session.add(new_activity)
        db.session.commit()
        return jsonify({"success": True, "id": new_activity.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@trips_bp.route('/api/trips/<int:trip_id>/notes', methods=['POST'])
def create_note(trip_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    trip = Trip.query.filter_by(id=trip_id, user_id=session['user_id']).first()
    if not trip: return jsonify({"error": "Not found"}), 404
    
    data = request.json
    try:
        note = TripNote(trip_id=trip_id, content=data.get('content', 'New Note'))
        db.session.add(note)
        db.session.commit()
        return jsonify({"success": True, "id": note.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@trips_bp.route('/api/trips/<int:trip_id>/notes/<int:note_id>', methods=['GET'])
def get_note(trip_id, note_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    note = TripNote.query.filter_by(id=note_id, trip_id=trip_id).first_or_404()
    if note.trip.user_id != session['user_id']: return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"id": note.id, "content": note.content})

@trips_bp.route('/api/trips/<int:trip_id>/notes/<int:note_id>', methods=['PUT'])
def update_note(trip_id, note_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    note = TripNote.query.filter_by(id=note_id, trip_id=trip_id).first_or_404()
    if note.trip.user_id != session['user_id']: return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    try:
        note.content = data.get('content', '')
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@trips_bp.route('/api/trips/<int:trip_id>/notes/<int:note_id>', methods=['DELETE'])
def delete_note(trip_id, note_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    note = TripNote.query.filter_by(id=note_id, trip_id=trip_id).first_or_404()
    if note.trip.user_id != session['user_id']: return jsonify({"error": "Unauthorized"}), 403
    
    try:
        db.session.delete(note)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
