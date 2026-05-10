from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app.notes import notes_bp
from app.models.trip import Trip, TripNote
from app.extensions import db
from datetime import datetime
from app.notes.services import NoteService
from app.notes.forms import NoteForm

@notes_bp.route('/', methods=['GET'])
def index():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    trip_id = request.args.get('trip_id')
    
    notes = NoteService.get_user_notes(user_id, trip_id=trip_id)
    trips = Trip.query.filter_by(user_id=user_id).order_by(Trip.name).all()
    
    # Sidebar data
    recent_notes = NoteService.get_recent_notes(user_id, limit=3)
    upcoming_reminders = NoteService.get_upcoming_reminders(user_id, limit=3)
    quick_stats = NoteService.get_quick_stats(user_id)
    
    form = NoteForm() # For CSRF if needed
    
    return render_template('notes/index.html', 
                           notes=notes, 
                           trips=trips, 
                           current_trip_id=trip_id,
                           recent_notes=recent_notes,
                           upcoming_reminders=upcoming_reminders,
                           quick_stats=quick_stats,
                           form=form)

@notes_bp.route('/create', methods=['POST'])
def create_note():
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    try:
        note = NoteService.create_note(session['user_id'], request.json)
        return jsonify({"success": True, "id": note.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@notes_bp.route('/edit/<int:note_id>', methods=['PUT', 'POST'])
def edit_note(note_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    try:
        NoteService.update_note(note_id, session['user_id'], request.json)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@notes_bp.route('/delete/<int:note_id>', methods=['DELETE', 'POST'])
def delete_note(note_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    try:
        NoteService.delete_note(note_id, session['user_id'])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@notes_bp.route('/pin/<int:note_id>', methods=['POST', 'PUT'])
def pin_note(note_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    try:
        note = NoteService.toggle_pin(note_id, session['user_id'], request.json.get('is_pinned'))
        return jsonify({"success": True, "is_pinned": note.is_pinned})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@notes_bp.route('/search', methods=['GET'])
def search_notes():
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    notes = NoteService.get_user_notes(session['user_id'], category=category, search_query=query)
    
    return jsonify({
        "notes": [{
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "note_type": n.note_type,
            "is_pinned": n.is_pinned,
            "trip_name": n.trip.name if n.trip else None,
            "updated_at": n.updated_at.strftime('%Y-%m-%d %H:%M')
        } for n in notes]
    })
