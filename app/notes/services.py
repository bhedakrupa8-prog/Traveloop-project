from app.models.trip import TripNote, Trip
from app.extensions import db
from datetime import datetime
from sqlalchemy import or_

class NoteService:
    @staticmethod
    def get_user_notes(user_id, trip_id=None, category=None, search_query=None):
        query = TripNote.query.filter_by(user_id=user_id)
        
        if trip_id:
            query = query.filter_by(trip_id=trip_id)
            
        if category:
            query = query.filter_by(note_type=category)
            
        if search_query:
            query = query.filter(or_(
                TripNote.title.ilike(f'%{search_query}%'),
                TripNote.content.ilike(f'%{search_query}%')
            ))
            
        return query.order_by(TripNote.is_pinned.desc(), TripNote.updated_at.desc()).all()

    @staticmethod
    def create_note(user_id, data):
        reminder_date = None
        if data.get('reminder_date'):
            if isinstance(data['reminder_date'], str):
                reminder_date = datetime.strptime(data['reminder_date'], '%Y-%m-%d')
            else:
                reminder_date = data['reminder_date']
                
        trip_id = data.get('trip_id')
        if trip_id == '' or trip_id == 'None':
            trip_id = None
            
        note = TripNote(
            user_id=user_id,
            trip_id=trip_id,
            title=data.get('title', 'Untitled Note'),
            content=data.get('content', ''),
            note_type=data.get('note_type', 'General'),
            is_pinned=data.get('is_pinned', False),
            reminder_date=reminder_date
        )
        db.session.add(note)
        db.session.commit()
        return note

    @staticmethod
    def update_note(note_id, user_id, data):
        note = TripNote.query.filter_by(id=note_id, user_id=user_id).first_or_404()
        
        if 'title' in data:
            note.title = data['title']
        if 'content' in data:
            note.content = data['content']
        if 'note_type' in data:
            note.note_type = data['note_type']
            
        if 'trip_id' in data:
            trip_id = data['trip_id']
            note.trip_id = trip_id if trip_id not in ['', 'None', None] else None
            
        if 'is_pinned' in data:
            note.is_pinned = data['is_pinned']
            
        if 'reminder_date' in data:
            if data['reminder_date']:
                if isinstance(data['reminder_date'], str):
                    note.reminder_date = datetime.strptime(data['reminder_date'], '%Y-%m-%d')
                else:
                    note.reminder_date = data['reminder_date']
            else:
                note.reminder_date = None
                
        db.session.commit()
        return note

    @staticmethod
    def delete_note(note_id, user_id):
        note = TripNote.query.filter_by(id=note_id, user_id=user_id).first_or_404()
        db.session.delete(note)
        db.session.commit()
        return True

    @staticmethod
    def toggle_pin(note_id, user_id, is_pinned=None):
        note = TripNote.query.filter_by(id=note_id, user_id=user_id).first_or_404()
        if is_pinned is not None:
            note.is_pinned = is_pinned
        else:
            note.is_pinned = not note.is_pinned
        db.session.commit()
        return note

    @staticmethod
    def get_upcoming_reminders(user_id, limit=5):
        now = datetime.utcnow()
        return TripNote.query.filter(
            TripNote.user_id == user_id,
            TripNote.reminder_date >= now
        ).order_by(TripNote.reminder_date.asc()).limit(limit).all()

    @staticmethod
    def get_recent_notes(user_id, limit=5):
        return TripNote.query.filter_by(user_id=user_id).order_by(TripNote.updated_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_quick_stats(user_id):
        total_notes = TripNote.query.filter_by(user_id=user_id).count()
        pinned_notes = TripNote.query.filter_by(user_id=user_id, is_pinned=True).count()
        return {
            "total": total_notes,
            "pinned": pinned_notes
        }
